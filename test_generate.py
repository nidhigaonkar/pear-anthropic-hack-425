import os
from unittest.mock import patch, MagicMock
import sys
import generate
import glob

def get_latest_file(pattern):
   files = glob.glob(pattern)
   if not files:
       raise FileNotFoundError(f"No files found for pattern: {pattern}")
   return max(files, key=os.path.getctime)

# Create a mock business_info.txt file for testing
test_business_info = get_latest_file("submissions/startup-description-*.txt")
# Create the test business info file
with open("business_info.txt", "w") as f:
   f.write(test_business_info)
# ... previous code ...

# Get the most recent subreddits file and turn it into a list
subreddits_file = get_latest_file("submissions/subreddits-*.txt")
with open(subreddits_file, "r") as f:
   subreddits_to_test = [line.strip()[2:] for line in f if line.strip() and not line.startswith("#")]

print(f"Testing reply_and_post with subreddits: {', '.join(subreddits_to_test)}")

# Run the reply and post function
generate.reply_and_post(subreddits_to_test)

print("Test completed")