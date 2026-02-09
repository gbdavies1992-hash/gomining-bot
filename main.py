import os
import tweepy
import google.generativeai as genai
import random
import logging
from datetime import datetime
from dotenv import load_dotenv

# --- 1. CONFIG & EXTENDED HASHTAGS ---
load_dotenv()
DB_FILE = "replied_ids.txt"
LAST_POST_FILE = "last_post_window.txt"

HASHTAG_POOL = [
    "#GoMining", "#Bitcoin", "#BTC", "#Hashrate", "#PassiveIncome", 
    "#MiningFarm", "#DigitalGold", "#FinancialFreedom", "#ProofOfWork", 
    "#Sats", "#CloudMining", "#WealthBuilding", "#BullMarket", "#HODL",
    "#CryptoMining", "#BitcoinMining", "#PassiveWealth", "#MiningRig"
]

# --- 2. LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger()

# --- 3. DATABASE HELPERS ---
def get_replied_ids():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_replied_id(tweet_id):
    with open(DB_FILE, "a") as f:
        f.write(f"{tweet_id}\n")

# --- 4. UK TIME WINDOW LOGIC (11am - 11pm) ---
def should_post_now():
    now = datetime.now()
    current_hour = now.hour
    if not (11 <= current_hour <= 23):
        return False, "quiet_hours"

    timestamp = f"{now.strftime('%Y-%m-%d')}_hour_{current_hour}"
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            if f.read().strip() == timestamp:
                return False, "already_posted_this_hour"
    return True, timestamp

# --- 5. API SETUP & SANITY CHECK ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("❌ GEMINI_API_KEY is empty!")
else:
    logger.info(f"✅ Gemini Key found: {api_key[:5]}...{api_key[-5:]}")

genai.configure(api_key=api_key)
# Using 'gemini-flash-latest' to avoid future 404 version errors
model = genai.GenerativeModel('gemini-flash-latest')

client = tweepy.Client(
    bearer_token=os.getenv("X_BEARER_TOKEN"),
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET")
)

# --- 6. MAIN RUN ---
def run_bot():
    can_post, window_id = should_post_now()
    selected_tags = " ".join(random.sample(HASHTAG_POOL, 4))
    
    try:
        # --- PART A: THE DAYTIME POSTS (HYPE TWEETS) ---
        if can_post:
            logger.info(f"Posting for hour {datetime.now().hour}...")
            
            # PROMPT UPDATED: Now includes Engagement Hooks
            prompt = (
                f"Write a short, high-energy hype tweet for my GoMining farm. "
                f"Stats: 10.39 TH/s. Make it relevant to a UK audience and Bitcoin. "
                f"CRITICAL: End with a question to the community about passive income "
                f"or BTC mining to encourage them to reply! "
                f"Hashtags: {selected_tags}"
            )
            
            response = model.generate_content(prompt)
            tweet_text = response.text.strip().replace('"', '')
            
            client.create_tweet(text=tweet_text)
            with open(LAST_POST_FILE, "w") as f: f.write(window_id)
            logger.info(f"Daily post sent: {tweet_text}")
        else:
            logger.info(f"Skipping post: {window_id}")

        # --- PART B: REPLIES (Mention Checking) ---
        bot_user = client.get_me()
        if not bot_user.data:
            logger.error("❌ Could not verify X User. Check your X API Keys!")
            return

        bot_id = bot_user.data.id
        mentions = client.get_users_mentions(id=bot_id)
        replied_ids = get_replied_ids()

        if mentions.data:
            for tweet in mentions.data:
                tid = str(tweet.id)
                if tid not in replied_ids:
                    logger.info(f"New mention from ID {tid}. Like and Reply triggered.")
                    
                    # NEW: Like the tweet before replying
                    try:
                        client.like(tweet.id)
                    except Exception as le:
                        logger.warning(f"Could not like tweet: {le}")

                    reply_prompt = f"Reply to this GoMining mention: '{tweet.text}'. Keep it helpful and hype."
                    reply_text = model.generate_content(reply_prompt).text.strip()
                    
                    client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet.id)
                    save_replied_id(tid)
                    logger.info(f"Replied: {reply_text}")
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")

if __name__ == "__main__":
    run_bot()
