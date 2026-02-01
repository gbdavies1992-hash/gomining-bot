import os
import tweepy
import google.generativeai as genai

# Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Setup X (Twitter)
client = tweepy.Client(
    consumer_key=os.environ["X_API_KEY"],
    consumer_secret=os.environ["X_API_SECRET"],
    access_token=os.environ["X_ACCESS_TOKEN"],
    access_token_secret=os.environ["X_ACCESS_SECRET"]
)

# The Prompt
prompt = "Write a short, punchy tweet about my GoMining farm. Stats: 10.39 TH/s and 15W/TH efficiency. Topic: Savings February (stacking tokens to reinvest in March). Use hashtags #GoMining #GOMINING #Bitcoin."

# Generate and Post
response = model.generate_content(prompt)
tweet_text = response.text.strip()

# Safety check for length
if len(tweet_text) > 280:
    tweet_text = tweet_text[:277] + "..."

client.create_tweet(text=tweet_text)
print(f"Posted: {tweet_text}")
