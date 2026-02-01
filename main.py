import os
import tweepy
import google.generativeai as genai
import traceback

try:
    # 1. Setup Gemini (Using the 2026 Stable Model)
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    # CHANGE: Updated from 'gemini-1.5-flash' to 'gemini-2.5-flash'
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 2. Setup X
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"]
    )

    # 3. Instruction
    prompt = (
        "Write a short, punchy tweet about my GoMining farm. "
        "Stats: 10.39 TH/s and 15W/TH efficiency. "
        "Theme: February 'Savings Mode'—stacking GOMINING to reinvest in March. "
        "Use #GoMining #GOMINING #Bitcoin."
    )

    # 4. Generate and Post
    response = model.generate_content(prompt)
    tweet_text = response.text.strip().replace('"', '')

    client.create_tweet(text=tweet_text)
    print(f"Successfully posted: {tweet_text}")

except Exception as e:
    print("--- ERROR LOG ---")
    print(traceback.format_exc())
    exit(1)
