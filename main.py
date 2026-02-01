import os
import tweepy
import google.generativeai as genai
import random
import traceback
from datetime import datetime

# 1. Setup Data & Rotation
# This list will be shuffled every time to keep the feed fresh
hashtag_pool = [
    "#GoMining", "#GOMINING", "#Bitcoin", "#PassiveIncome", 
    "#Hashrate", "#CryptoMining", "#BTC", "#MiningFarm", 
    "#DigitalGold", "#FinancialFreedom"
]
selected_tags = " ".join(random.sample(hashtag_pool, 3))

# Automatically get the current month name (e.g., "February")
current_month = datetime.now().strftime("%B")

try:
    # 2. Setup Gemini
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 3. Setup X (Twitter)
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"]
    )

    # 4. Smart Dynamic Prompt
    # This automatically tells the AI what month it is!
    prompt = (
        f"Write a short, engaging tweet about my GoMining farm. "
        f"Stats: 10.39 TH/s power and 15W/TH efficiency. "
        f"The current month is {current_month}. If it's February, talk about savings mode. "
        f"If it's March, talk about reinvesting for growth. Otherwise, be creative. "
        f"End with these exact hashtags: {selected_tags}"
    )

    # 5. Generate and Post
    response = model.generate_content(prompt)
    tweet_text = response.text.strip().replace('"', '')

    # Post it!
    client.create_tweet(text=tweet_text)
    print(f"Successfully posted for {current_month}: {tweet_text}")

except Exception as e:
    print("--- ERROR LOG ---")
    print(traceback.format_exc())
    exit(1)
