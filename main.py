import os
import tweepy
import google.generativeai as genai
import random
import traceback
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

# --- 3. UK TIME WINDOW LOGIC (11am - 11pm) ---
def should_post_now():
    """Checks if we are in the 11am-11pm window and if we haven't posted in the current hour."""
    now = datetime.now()
    current_hour = now.hour

    # Restriction: Only post between 11:00 and 23:00 (11pm)
    if not (11 <= current_hour <= 23):
        return False, "quiet_hours"

    # To get 12 posts between 11am and 11pm, we post roughly every hour.
    # We use the date + hour as the unique ID for this post.
    timestamp = f"{now.strftime('%Y-%m-%d')}_hour_{current_hour}"
    
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            if f.read().strip() == timestamp:
                return False, "already_posted_this_hour"
                
    return True, timestamp

# --- 4. API SETUP ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')
client = tweepy.Client(
    bearer_token=os.getenv("X_BEARER_TOKEN"),
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET")
)

# --- 5. MAIN RUN ---
def run_bot():
    can_post, window_id = should_post_now()
    selected_tags = " ".join(random.sample(HASHTAG_POOL, 4))
    
    try:
        # --- PART A: THE DAYTIME POSTS ---
        if can_post:
            logger.info(f"Inside UK active hours. Posting for hour {datetime.now().hour}...")
            
            prompt = (
                f"Write a short, hype tweet for GoMining. Farm stats: 10.39 TH/s. "
                f"Make it relevant to a UK audience and mention Bitcoin's potential. "
                f"End with these exact hashtags: {selected_tags}"
            )
            
            response = model.generate_content(prompt)
            tweet_text = response.text.strip().replace('"', '')
            
            client.create_tweet(text=tweet_text)
            with open(LAST_POST_FILE, "w") as f: f.write(window_id)
            logger.info(f"Daily post sent: {tweet_text}")
        else:
            if window_id == "quiet_hours":
                logger.info("Bot is in 'Quiet Mode' (11pm - 11am). No new posts.")

        # --- PART B: REPLIES (Always active, 24/7) ---
        bot_user = client.get_me()
        bot_id = bot_user.data.id
        mentions = client.get_users_mentions(id=bot_id)
        replied_ids = get_replied_ids()

        if mentions.data:
            for tweet in mentions.data:
                tid = str(tweet.id)
                if tid not in replied_ids:
                    logger.info(f"Replying to mention from {tid}")
                    reply_prompt = f"Reply to this GoMining mention: '{tweet.text}'. Keep it short."
                    reply_text = model.generate_content(reply_prompt).text.strip()
                    client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet.id)
                    save_replied_id(tid)
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    run_bot()
