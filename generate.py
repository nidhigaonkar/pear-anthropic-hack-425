from anthropic import Anthropic
import praw
import os
import time
from prawcore.exceptions import RequestException, ResponseException

#Creating the Reddit instance
reddit = praw.Reddit('bot1')

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
with open("business_info.txt", "r") as f:
    business_info = f.read()

def should_reply_to_post(post_title, post_content, business_info):
    """Determine if we should reply to this post based on its relevance to our business."""
    prompt = f"""
    Analyze this Reddit post and determine if we should reply to it. Consider if:
    1. The post discusses problems or needs that our product could help with
    2. The post is from someone who could benefit from our product
    3. We can provide genuine value in our response
    
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
    generate a helpful, authentic-sounding reply to this Reddit post. The reply should be
    helpful first and only subtly mention the product if relevant.
    
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
    
    return response.content[0].text

def reply_and_post(subreddit_list):
    for subreddit_name in subreddit_list:
        print(f"\nProcessing subreddit: {subreddit_name}")
        subreddit = reddit.subreddit(subreddit_name)
        
        # Get 200 most recent posts
        posts_to_process = []
        for submission in subreddit.new(limit=200):
            if submission.id not in posts_replied_to:
                posts_to_process.append(submission)
        
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
                    
                # Wait 2 minutes between comments to avoid rate limits
                print("Waiting 2 minutes before next comment...")
                time.sleep(120)  # 2 minutes
                
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
