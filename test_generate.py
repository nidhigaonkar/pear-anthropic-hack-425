import os
from unittest.mock import patch, MagicMock
import sys
import generate

# Create a mock business_info.txt file for testing
test_business_info = """
ProductName: CodeAssist AI
Description: An AI-powered coding assistant that helps developers write better code faster.
Features:
- Real-time code suggestions
- Bug detection and fixing
- Code optimization recommendations
- Integration with popular IDEs like VS Code, IntelliJ, and PyCharm
- Support for multiple programming languages including Python, JavaScript, Java, and C++

Our product helps developers save time, reduce errors, and learn best practices while coding.
Website: https://codeassist-ai.example.com
Pricing: Free tier available, Pro plan at $9.99/month
"""

# Create the test business info file
with open("business_info.txt", "w") as f:
    f.write(test_business_info)

subreddits_to_test = ["learnpython", "Python", "coding"]

print(f"Testing reply_and_post with subreddits: {', '.join(subreddits_to_test)}")

# Run the reply and post function
generate.reply_and_post(subreddits_to_test)

print("Test completed")
