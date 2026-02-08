# --- ADD THIS TO YOUR CONFIG AREA ---
LAST_POST_FILE = "last_post.txt"

def has_posted_today():
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists(LAST_POST_FILE):
        return False
    with open(LAST_POST_FILE, "r") as f:
        return f.read().strip() == today

def mark_as_posted():
    today = datetime.now().strftime("%Y-%m-%d")
    with open(LAST_POST_FILE, "w") as f:
        f.write(today)

# --- UPDATED RUN_BOT FUNCTION ---
def run_bot():
    current_month = datetime.now().strftime("%B")
    replied_ids = get_replied_ids()
    
    try:
        # 1. POST DAILY UPDATE (If not already done today)
        if not has_posted_today():
            logger.info("Posting daily farm update...")
            daily_prompt = (
                f"Write a short, hype tweet about my GoMining farm. "
                f"Stats: 10.39 TH/s power. It's {current_month}. "
                f"Be creative and bullish on Bitcoin!"
            )
            daily_response = model.generate_content(daily_prompt)
            tweet_text = daily_response.text.strip().replace('"', '')
            
            client.create_tweet(text=tweet_text)
            mark_as_posted()
            logger.info(f"Daily update posted: {tweet_text}")
        
        # 2. CHECK & REPLY TO MENTIONS
        bot_user = client.get_me()
        bot_id = bot_user.data.id
        mentions = client.get_users_mentions(id=bot_id)

        if mentions.data:
            for tweet in mentions.data:
                tweet_id = str(tweet.id)
                if tweet_id not in replied_ids:
                    # (Insert the reply logic we built in the previous step here)
                    # ...
                    save_replied_id(tweet_id)
        
        logger.info("Bot cycle complete.")

    except Exception:
        logger.error(f"Bot execution failed: {traceback.format_exc()}")
