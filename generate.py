from anthropic import Anthropic
from prawcore import NotFound
import praw
import os
import time
import glob
from prawcore.exceptions import RequestException, ResponseException

#Creating the Reddit instance
reddit = praw.Reddit(
    client_id=os.environ.get("CLIENT_ID"),
    client_secret=os.environ.get("CLIENT_SECRET"),
    username=os.environ.get("GENERATE_USERNAME"),
    password=os.environ.get("GENERATE_PASSWORD"),
    user_agent="script:your_app_name:v1.0 (by /u/Cute_Philosopher_745)",
    ratelimit_seconds=900
)

print(reddit.user.me())

def sub_exists(sub):
    exists = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except NotFound:
        exists = False
    return exists


def get_latest_file(pattern):
   files = glob.glob(pattern)
   if not files:
       raise FileNotFoundError(f"No files found for pattern: {pattern}")
   return max(files, key=os.path.getctime)

# Create a mock business_info.txt file for testing
startup_info = get_latest_file("submissions/startup-description-*.txt")

#A file that consists of already made posts
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []
else:
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read().split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))

# Initialize Claude client
anthropic = Anthropic(api_key=os.environ.get('API_KEY'))

# Load business information
with open(startup_info, "r") as f:
    business_info = f.read()

def should_reply_to_post(post_title, post_content, business_info):
    """Determine if we should reply to this post based on its relevance to our business."""
    prompt = f"""
    Analyze this Reddit post and determine if replying would be beneficial for our business. Consider the following:
    1. Does the post discuss challenges or needs that our product could help address?
    2. Is the poster someone who could benefit from our product or service?
    3. Can we provide genuine value in our response while subtly mentioning our product, only when it directly relates to their needs or situation?
    
    Business information:
    {business_info}
    
    Post title: {post_title}
    Post content: {post_content}
    
    Return ONLY 'yes' if we should reply, or 'no' if we should skip this post.
    """
    
    response = anthropic.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=100,
        system="You are a post relevance analyzer. Return only 'yes' or 'no'.",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text.strip().lower() == 'yes'

def generate_reply(post_title, post_content, subreddit_name):
    prompt = f"""
   You are a helpful assistant for a business. Based on the following business information, 
   generate a reply to this Reddit post that is informative and genuinely helpful. The reply 
   should focus on offering useful advice or solutions first, and make sure to mention the specific 
   product name as inputed by the user aswell as the given link provided and show how it directly adds value to the response. 
   Make sure the tone is human, authentic and empathetic to the original poster's situation. Don't be too long, a 150 word limit.
    
    Business information:
    {business_info}
    
    Subreddit: {subreddit_name}
    Post title: {post_title}
    Post content: {post_content}
    
    Your reply:
    """
    
    response = anthropic.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        system="Generate helpful, human-sounding, and authentic-sounding Reddit comments that subtly mention the product only when relevant.",
        messages=[{"role": "user", "content": prompt}]
    )

    print("About to return")
    
    return response.content[0].text

def reply_and_post(subreddit_list):
    for subreddit_name in subreddit_list:
        print(f"\nProcessing subreddit: {subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)
        if (not sub_exists(subreddit)):
            continue
        
        # Get 200 most recent posts
        posts_to_process = []
        for submission in subreddit.new(limit=10):
            if submission.id not in posts_replied_to:
                posts_to_process.append(submission)
                print(submission)
        
        print(f"Found {len(posts_to_process)} new posts to analyze")
        
        # Process posts and determine relevance
        for submission in posts_to_process:
            try:
                print(f"\nAnalyzing post: '{submission.title}'")

                if (not should_reply_to_post(submission.title, submission.selftext, business_info)):
                    print(f"Skipping post - not relevant to our business: {submission.title}")
                    continue
                
                # Check if we should reply to this post
               # if should_reply_to_post(submission.title, submission.selftext, business_info):
                print(f"Post is relevant. Generating reply for: {submission.title}")  
                # Generate reply using Claude
                reply_text = generate_reply(submission.title, submission.selftext, subreddit_name)
                    
                # Post the reply
                submission.reply(reply_text)
                print(f"Replied to: {submission.title}")
                    
                # Remember we replied to this post
                posts_replied_to.append(submission.id)
                    
                # Save progress after each successful reply
                with open("posts_replied_to.txt", "w") as f:
                    for post_id in posts_replied_to:
                        f.write(post_id + "\n")
                    
                # Wait 5 minutes between comments to avoid rate limits
                print("Waiting 1 minute before next comment...")
                time.sleep(60)  # 5 minutes
                
            except Exception as e:
                if "RATELIMIT" in str(e):
                    wait_time = 120  # Default to 2 minutes
                    if "Take a break for" in str(e):
                        # Try to extract the wait time from the error message
                        try:
                            wait_time = int(str(e).split("Take a break for")[1].split()[0]) * 60
                        except:
                            pass
                    print(f"Rate limit hit. Waiting {wait_time/60} minutes...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Error occurred: {str(e)}")
                    continue