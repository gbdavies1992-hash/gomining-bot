import os
import tweepy
from google import genai
import random
import logging
from datetime import datetime
from dotenv import load_dotenv

# --- 1. CONFIG & HASHTAGS ---
load_dotenv()
DB_FILE = "replied_ids.txt"
LAST_POST_FILE = "last_post_window.txt"
# Corrected Model ID for 2026
MODEL_ID = "gemini-2.0-flash" 

HASHTAG_POOL = [
    "#GoMining", "#Bitcoin", "#BTC", "#Hashrate", "#PassiveIncome", 
    "#MiningFarm", "#DigitalGold", "#FinancialFreedom", "#ProofOfWork"
]

# --- 2. LOGGING ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

# --- 3. DATABASE HELPERS ---
def get_replied_ids():
    if not os.path.exists(DB_FILE): return set()
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

# --- 5. MAIN RUN ---
def run_bot():
    can_post, window_id = should_post_now()
    
    try:
        # API Clients
        gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        x_client = tweepy.Client(
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_SECRET")
        )

        # --- PART A: HOURLY POSTS ---
        if can_post:
            logger.info(f"🚀 Generating post for hour {datetime.now().hour}...")
            tags = " ".join(random.sample(HASHTAG_POOL, 3))
            prompt = (
                f"Write a high-energy hype tweet for my GoMining farm (10.39 TH/s). "
                f"Include a question for the community. Max 240 chars. Tags: {tags}"
            )
            
            # Using the correct SDK method: generate_content
            response = gemini_client.models.generate_content(model=MODEL_ID, contents=prompt)
            tweet_text = response.text.strip().replace('"', '')

            x_client.create_tweet(text=tweet_text)
            
            # --- FIXED: Correctly closed parenthesis for f.write ---
            with open(LAST_POST_FILE, "w") as f: 
                f.write(window_id)
            
            logger.info(f"✅ Post sent: {tweet_text}")
        else:
            logger.info(f"⏸️ Skipping hourly post: {window_id}")

        # --- PART B: MENTIONS & REPLIES ---
        bot_user = x_client.get_me()
        if bot_user and bot_user.data:
            # user_auth=True is REQUIRED for OAuth 1.0a on the Free Tier
            mentions = x_client.get_users_mentions(id=bot_user.data.id, user_auth=True)
            replied_ids = get_replied_ids()
            
            if mentions.data:
                for tweet in mentions.data:
                    tid = str(tweet.id)
                    if tid not in replied_ids:
                        logger.info(f"💬 Replying to mention: {tid}")
                        
                        reply_prompt = f"Reply hype/helpful to this GoMining mention: '{tweet.text}'"
                        reply_resp = gemini_client.models.generate_content(model=MODEL_ID, contents=reply_prompt)
                        
                        x_client.create_tweet(text=reply_resp.text[:280], in_reply_to_tweet_id=tweet.id)
                        save_replied_id(tid)
                        logger.info(f"✅ Replied to tweet ID {tid}")

    except Exception as e:
        logger.error(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    run_bot()
