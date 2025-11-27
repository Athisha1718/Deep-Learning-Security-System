import os
from dotenv import load_dotenv

load_dotenv()
pwd = os.getenv("GMAIL_APP_PASSWORD")
print(f"Password: '{pwd}'")
print(f"Length: {len(pwd)}")  # Must output 16