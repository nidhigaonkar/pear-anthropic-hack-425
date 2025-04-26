from anthropic import Anthropic
import praw
import os

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
anthropic = Anthropic(api_key="")

# Load business information
with open("business_info.txt", "r") as f:
    business_info = f.read()

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
        system="Generate helpful, authentic-sounding Reddit comments that subtly mention the product only when relevant.",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

def reply_and_post(subreddit_list):
    for subreddit_name in subreddit_list:
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.new(limit=10):
            # Skip if we've already replied
            if submission.id in posts_replied_to:
                continue
                
            # Generate reply using Claude
            reply_text = generate_reply(submission.title, submission.selftext, subreddit_name)
            
            # Post the reply
            submission.reply(reply_text)
            print(f"Replied to: {submission.title}")
            
            # Remember we replied to this post
            posts_replied_to.append(submission.id)
            
    # Save the updated list of posts we've replied to
    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")
