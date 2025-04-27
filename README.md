# pear-anthropic-hack-425

An intelligent AI agent that uses Claude AI to identify and engage with relevant discussions in Reddit in a helpful, authentic way.
Overview

This agent monitors specified subreddits and uses Claude AI to:
- Analyze posts for relevance to your business
- Generate helpful, authentic responses
- Engage with users who have relevant pain points
- Maintain natural conversation flow while subtly mentioning your product when appropriate

Tech Stack

- Python - Core programming language
- Anthropic Claude - AI model for post analysis and response generation
- PRAW - Python Reddit API Wrapper for Reddit interactions
- File-based storage - Simple text files for tracking posts and business information

Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install anthropic praw
   ```
3. Set up your environment variables:
   - `API_KEY` - Your Anthropic API key
   - Reddit API credentials (configure in `praw.ini`)

4. Create a `business_info.txt` file with your business information

Configuration

1. Edit `business_info.txt` with your business details
2. Configure your target subreddits in the script
3. Adjust rate limiting and post limits as needed

Usage

Run the agent:
```bash
python app.py
```

The agent will:
- Monitor specified subreddits
- Analyze posts for relevance
- Generate and post responses
- Track interactions to avoid duplicates
- Respect rate limits

Features

- Intelligent Post Analysis: Uses Claude AI to identify relevant discussions
- Authentic Responses: Generates helpful, human-like responses
- Anti-Spam Measures: Implements rate limiting and post tracking
- Value-First Approach: Focuses on helping users before mentioning products
- Error Handling: Robust error handling for API calls and rate limits
