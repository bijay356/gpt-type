"""
Interactive Social Media Setup Assistant for GPT-TYPE Agent.
Saves your social media API keys directly into .env.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Console encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

def update_env(key, val):
    val = val.strip()
    if not val:
        return
    if not ENV_PATH.exists():
        content = ""
    else:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            content = f.read()

    prefix = f"{key}="
    if prefix in content:
        lines = content.splitlines()
        new_lines = [f"{key}={val}" if l.startswith(prefix) else l for l in lines]
        content = "\n".join(new_lines)
    else:
        content += f"\n{key}={val}"

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ Saved {key} to .env!")

def setup_telegram():
    print("\n--- ✈️ Setting Up Telegram (Instant Phone Alerts) ---")
    print("1. Open Telegram and search for '@BotFather'")
    print("2. Send '/newbot', choose a name, and copy the Bot HTTP API Token")
    print("3. Search for '@userinfobot' and send '/start' to get your Chat ID\n")
    token = input("Enter TELEGRAM_BOT_TOKEN (or press Enter to skip): ").strip()
    if token:
        update_env("TELEGRAM_BOT_TOKEN", token)
    chat_id = input("Enter TELEGRAM_CHAT_ID (or press Enter to skip): ").strip()
    if chat_id:
        update_env("TELEGRAM_CHAT_ID", chat_id)

def setup_twitter():
    print("\n--- 🐦 Setting Up X / Twitter ---")
    print("1. Go to https://developer.x.com/en/portal/dashboard")
    print("2. Create a Project & App -> Set User Authentication to 'Read and Write'")
    print("3. Generate Consumer Keys & Access Tokens\n")
    k = input("Enter TWITTER_API_KEY (Consumer Key): ").strip()
    if k: update_env("TWITTER_API_KEY", k)
    s = input("Enter TWITTER_API_SECRET (Consumer Secret): ").strip()
    if s: update_env("TWITTER_API_SECRET", s)
    at = input("Enter TWITTER_ACCESS_TOKEN: ").strip()
    if at: update_env("TWITTER_ACCESS_TOKEN", at)
    ats = input("Enter TWITTER_ACCESS_SECRET: ").strip()
    if ats: update_env("TWITTER_ACCESS_SECRET", ats)

def setup_facebook_instagram():
    print("\n--- 📘 Setting Up Facebook & Instagram ---")
    print("1. Go to https://developers.facebook.com -> Create App")
    print("2. Under Graph API Explorer, generate a Page Access Token with 'pages_manage_posts'")
    print("3. Connect your Instagram Professional account to the Facebook Page\n")
    token = input("Enter FACEBOOK_PAGE_ACCESS_TOKEN: ").strip()
    if token: update_env("FACEBOOK_PAGE_ACCESS_TOKEN", token)
    page_id = input("Enter FACEBOOK_PAGE_ID (Found in Page About section): ").strip()
    if page_id: update_env("FACEBOOK_PAGE_ID", page_id)
    ig_id = input("Enter INSTAGRAM_ACCOUNT_ID (Optional, if connecting Instagram): ").strip()
    if ig_id: update_env("INSTAGRAM_ACCOUNT_ID", ig_id)

def setup_linkedin():
    print("\n--- 💼 Setting Up LinkedIn ---")
    print("1. Go to https://www.linkedin.com/developers -> Create App")
    print("2. Add 'Share on LinkedIn' and 'Sign In with LinkedIn' products")
    print("3. Use OAuth 2.0 Tools to generate an Access Token with 'w_member_social'\n")
    token = input("Enter LINKEDIN_ACCESS_TOKEN: ").strip()
    if token: update_env("LINKEDIN_ACCESS_TOKEN", token)
    urn = input("Enter LINKEDIN_AUTHOR_URN (Your LinkedIn Member/Page ID, e.g. 12345678): ").strip()
    if urn: update_env("LINKEDIN_AUTHOR_URN", urn)

def setup_reddit():
    print("\n--- 🤖 Setting Up Reddit ---")
    print("1. Go to https://www.reddit.com/prefs/apps")
    print("2. Click 'are you a developer? create an app...' -> Choose 'script'")
    print("3. Copy the Client ID (under the app name) and the Secret\n")
    cid = input("Enter REDDIT_CLIENT_ID: ").strip()
    if cid: update_env("REDDIT_CLIENT_ID", cid)
    sec = input("Enter REDDIT_CLIENT_SECRET: ").strip()
    if sec: update_env("REDDIT_CLIENT_SECRET", sec)
    user = input("Enter REDDIT_USERNAME: ").strip()
    if user: update_env("REDDIT_USERNAME", user)
    pwd = input("Enter REDDIT_PASSWORD: ").strip()
    if pwd: update_env("REDDIT_PASSWORD", pwd)
    sub = input("Enter REDDIT_SUBREDDIT to post to (default: typing): ").strip()
    if sub: update_env("REDDIT_SUBREDDIT", sub)

def setup_webhook():
    print("\n--- ⚡ Setting Up Universal All-in-One Webhook ---")
    print("Use a free automation tool (Make.com, Zapier, or Ayrshare) to broadcast to ALL platforms in 1 click!")
    print("1. Create a free webhook on Make.com or Zapier")
    print("2. Connect your Facebook, Instagram, LinkedIn, X, and Pinterest accounts to the webhook\n")
    wh = input("Enter SOCIAL_WEBHOOK_URL: ").strip()
    if wh: update_env("SOCIAL_WEBHOOK_URL", wh)

def main():
    while True:
        print("\n" + "=" * 65)
        print("🌐 GPT-TYPE Social Media Configuration Assistant")
        print("=" * 65)
        print("Select which platform you want to set up right now:")
        print("1. ✈️  Telegram (Instant Mobile Alerts & Channel Broadcast - Easiest)")
        print("2. 🐦  X / Twitter")
        print("3. 📘  Facebook & Instagram")
        print("4. 💼  LinkedIn")
        print("5. 🤖  Reddit")
        print("6. ⚡  Universal All-in-One Webhook (Make.com / Zapier)")
        print("7. 🚪  Exit")
        print("=" * 65)

        choice = input("Enter your choice (1-7): ").strip()
        if choice == "1": setup_telegram()
        elif choice == "2": setup_twitter()
        elif choice == "3": setup_facebook_instagram()
        elif choice == "4": setup_linkedin()
        elif choice == "5": setup_reddit()
        elif choice == "6": setup_webhook()
        elif choice == "7":
            print("\nSetup complete! Your .env file is updated.")
            break
        else:
            print("Invalid choice, please select 1-7.")

if __name__ == "__main__":
    main()
