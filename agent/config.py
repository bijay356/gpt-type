import os
from pathlib import Path
from dotenv import load_dotenv

# Load local .env if present (useful for local testing)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# 1. Gemini AI Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# 2. Google Blogger API v3 Settings
BLOGGER_CLIENT_ID = os.getenv("BLOGGER_CLIENT_ID", "").strip()
BLOGGER_CLIENT_SECRET = os.getenv("BLOGGER_CLIENT_SECRET", "").strip()
BLOGGER_REFRESH_TOKEN = os.getenv("BLOGGER_REFRESH_TOKEN", "").strip()
BLOG_ID = os.getenv("BLOG_ID", "").strip()
BLOG_URL = os.getenv("BLOG_URL", "https://gpttype.blogspot.com").strip().rstrip("/")
POST_STATUS = os.getenv("POST_STATUS", "LIVE").upper()  # 'LIVE' or 'DRAFT'

# 3. Telegram Instant Reporting (Optional, free alerts to your phone)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# 4. Social Media Integrations (Optional)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "").strip()
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "").strip()
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "").strip()
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "").strip()

FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "").strip()

# Instagram (Connected to Facebook Page)
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()

# LinkedIn Integration
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
LINKEDIN_AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN", "").strip()

# Reddit Integration
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "").strip()
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "").strip()
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "").strip()
REDDIT_SUBREDDIT = os.getenv("REDDIT_SUBREDDIT", "typing").strip()

# Universal Social Webhook (Make.com, Zapier, Ayrshare, Publer, Discord)
SOCIAL_WEBHOOK_URL = os.getenv("SOCIAL_WEBHOOK_URL", "").strip()


# 5. Paths
DATA_DIR = BASE_DIR / "data"
KEYWORD_DB_PATH = DATA_DIR / "keyword_database.json"
POST_HISTORY_PATH = DATA_DIR / "post_history.json"
