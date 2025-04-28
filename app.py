from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import os
from flask_cors import CORS
import requests
import subprocess

app = Flask(__name__)
CORS(app)

# Directory to save submissions
data_dir = 'submissions'
os.makedirs(data_dir, exist_ok=True)

# Route to serve the main page
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Route to serve the JavaScript file
@app.route('/script.js')
def serve_script():
    return send_from_directory('.', 'script.js')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    user_input = data.get('description', '').strip()
    if not user_input:
        return jsonify({'success': False, 'message': 'No description provided.'}), 400

    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    filename = f'startup-description-{timestamp}.txt'
    filepath = os.path.join(data_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Startup Description\n\n{user_input}\n\nSubmitted on: {datetime.now().isoformat()}")

    return jsonify({'success': True, 'message': 'Submission saved.'})

# Anthropic API key
ANTHROPIC_API_KEY = os.environ.get('API_KEY')

def get_relevant_subreddits(description):
    prompt = (
        "Given the following startup description, list 5-10 relevant subreddits where the founders could find potential customers. "
        "Return only the subreddit names, one per line, no extra text.\n\n"
        f"Startup Description:\n{description}\n\nSubreddits:"
    )
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 256,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        raise Exception("Error contacting Anthropic API.")
    except ValueError:
        print("Error parsing response.")
        raise Exception("Invalid response format from API.")

@app.route('/find_subreddits', methods=['POST'])
def find_subreddits():
    data = request.get_json()
    description = data.get('description', '').strip()
    if not description:
        return jsonify({'success': False, 'message': 'No description provided.'}), 400

    try:
        subreddits = get_relevant_subreddits(description)
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        filename = f'subreddits-{timestamp}.txt'
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(subreddits)
        print(f"Saved subreddits to {filepath}")
        subprocess.run(["python", "test_generate.py"])
        return jsonify({'success': True, 'subreddits': subreddits.splitlines(), 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)