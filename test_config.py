import os
from dotenv import load_dotenv
import tweepy
import google.generativeai as genai

# 1. Test .env Loading
load_dotenv()
print("--- ENV CHECK ---")
keys = ["GEMINI_API_KEY", "X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]
for key in keys:
    val = os.getenv(key)
    status = "✅ FOUND" if val else "❌ MISSING"
    # Shows first 4 chars of key to verify it's the right one without leaking it
    preview = f"({val[:4]}...)" if val else ""
    print(f"{key}: {status} {preview}")

print("\n--- API CONNECTION CHECK ---")

# 2. Test Gemini Connection
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Gemini is online!'")
    print(f"Gemini: ✅ {response.text.strip()}")
except Exception as e:
    print(f"Gemini: ❌ FAILED - {e}")

# 3. Test X (Twitter) Connection
try:
    client = tweepy.Client(
        bearer_token=os.getenv("X_BEARER_TOKEN"),
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET")
    )
    user = client.get_me()
    print(f"X (Twitter): ✅ CONNECTED as @{user.data.username}")
except Exception as e:
    print(f"X (Twitter): ❌ FAILED - {e}")
