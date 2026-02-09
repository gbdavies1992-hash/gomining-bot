import os
import tweepy
from google import genai  # Modern google-genai SDK
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
        f.write(
