import logging
import requests
from agent.config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_SECRET,
    FACEBOOK_PAGE_ACCESS_TOKEN,
    FACEBOOK_PAGE_ID,
    INSTAGRAM_ACCOUNT_ID,
    LINKEDIN_ACCESS_TOKEN,
    LINKEDIN_AUTHOR_URN,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USERNAME,
    REDDIT_PASSWORD,
    REDDIT_SUBREDDIT,
    SOCIAL_WEBHOOK_URL
)

logger = logging.getLogger("GPTTypeAgent.Social")

class SocialPublisher:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def broadcast(self, post_meta, social_posts):
        """
        Broadcasts the newly published article across:
        - X (Twitter)
        - Facebook Page
        - Instagram
        - LinkedIn
        - Reddit
        - Telegram
        - Universal Webhook (Make.com, Zapier, Publer, Ayrshare, Discord)
        """
        post_url = post_meta.get("url", "")
        post_title = post_meta.get("title", "")

        results = {
            "telegram": self._post_to_telegram(social_posts.get("telegram", ""), post_url),
            "twitter": self._post_to_twitter(social_posts.get("twitter", ""), post_url),
            "facebook": self._post_to_facebook(social_posts.get("facebook", social_posts.get("facebook_linkedin", "")), post_url),
            "linkedin": self._post_to_linkedin(social_posts.get("linkedin", social_posts.get("facebook_linkedin", "")), post_url, post_title),
            "reddit": self._post_to_reddit(social_posts.get("reddit", {}), post_url, post_title),
            "instagram": self._post_to_instagram(social_posts.get("instagram", ""), post_url),
            "universal_webhook": self._post_to_webhook(post_meta, social_posts)
        }
        return results

    def _post_to_telegram(self, text, url):
        if not text:
            return {"status": "skipped", "reason": "No text provided"}

        formatted_msg = text.replace("{{LINK}}", url)
        if self.dry_run:
            logger.info(f"[DRY-RUN] Telegram Message Preview:\n{formatted_msg}")
            return {"status": "dry_run_success"}

        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.info("Telegram credentials not configured. Skipping.")
            return {"status": "skipped", "reason": "Credentials missing"}

        try:
            api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": formatted_msg,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            res = requests.post(api_url, json=payload, timeout=15)
            if res.status_code == 200:
                logger.info("Successfully posted to Telegram!")
                return {"status": "success"}
            return {"status": "failed", "error": res.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _post_to_twitter(self, text, url):
        if not text:
            return {"status": "skipped"}

        formatted_tweet = text.replace("{{LINK}}", url)
        if len(formatted_tweet) > 280:
            formatted_tweet = formatted_tweet[:276] + "..."

        if self.dry_run:
            logger.info(f"[DRY-RUN] X / Twitter Post Preview:\n{formatted_tweet}")
            return {"status": "dry_run_success"}

        if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
            logger.info("Twitter credentials not configured. Skipping.")
            return {"status": "skipped", "reason": "Credentials missing"}

        try:
            from requests_oauthlib import OAuth1
            auth = OAuth1(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
            res = requests.post("https://api.twitter.com/2/tweets", json={"text": formatted_tweet}, auth=auth, timeout=20)
            if res.status_code in [200, 201]:
                logger.info("Successfully posted to X/Twitter!")
                return {"status": "success"}
            return {"status": "failed", "error": res.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _post_to_facebook(self, text, url):
        if not text:
            return {"status": "skipped"}

        formatted_post = text.replace("{{LINK}}", url)
        if self.dry_run:
            logger.info(f"[DRY-RUN] Facebook Post Preview:\n{formatted_post}")
            return {"status": "dry_run_success"}

        if not FACEBOOK_PAGE_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
            logger.info("Facebook credentials not configured. Skipping.")
            return {"status": "skipped", "reason": "Credentials missing"}

        try:
            api_url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/feed"
            payload = {"message": formatted_post, "link": url, "access_token": FACEBOOK_PAGE_ACCESS_TOKEN}
            res = requests.post(api_url, data=payload, timeout=20)
            if res.status_code == 200:
                logger.info("Successfully posted to Facebook Page!")
                return {"status": "success"}
            return {"status": "failed", "error": res.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _post_to_linkedin(self, text, url, title):
        if not text:
            return {"status": "skipped"}

        formatted_post = text.replace("{{LINK}}", url)
        if self.dry_run:
            logger.info(f"[DRY-RUN] LinkedIn Post Preview:\n{formatted_post}")
            return {"status": "dry_run_success"}

        if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_AUTHOR_URN:
            logger.info("LinkedIn credentials not configured. Skipping.")
            return {"status": "skipped", "reason": "Credentials missing"}

        try:
            # LinkedIn UGC Post API
            api_url = "https://api.linkedin.com/v2/ugcPosts"
            headers = {
                "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            author = LINKEDIN_AUTHOR_URN if LINKEDIN_AUTHOR_URN.startswith("urn:li:") else f"urn:li:person:{LINKEDIN_AUTHOR_URN}"
            payload = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": formatted_post},
                        "shareMediaCategory": "ARTICLE",
                        "media": [{
                            "status": "READY",
                            "originalUrl": url,
                            "title": {"text": title}
                        }]
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
            }
            res = requests.post(api_url, json=payload, headers=headers, timeout=20)
            if res.status_code in [200, 201]:
                logger.info("Successfully posted to LinkedIn!")
                return {"status": "success"}
            return {"status": "failed", "error": res.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _post_to_reddit(self, reddit_data, url, title):
        if isinstance(reddit_data, dict):
            post_title = reddit_data.get("title", title)
            post_body = reddit_data.get("body", "").replace("{{LINK}}", url)
        else:
            post_title = title
            post_body = str(reddit_data).replace("{{LINK}}", url)

        if not post_title:
            return {"status": "skipped"}

        if self.dry_run:
            logger.info(f"[DRY-RUN] Reddit Post Preview:\nTitle: {post_title}\nBody: {post_body[:200]}...")
            return {"status": "dry_run_success"}

        if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD]):
            logger.info("Reddit credentials not configured. Skipping.")
            return {"status": "skipped", "reason": "Credentials missing"}

        try:
            # 1. Get Reddit OAuth Token
            auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
            headers = {"User-Agent": "GPTTypeBot/1.0 by GPT-TYPE"}
            data = {
                "grant_type": "password",
                "username": REDDIT_USERNAME,
                "password": REDDIT_PASSWORD
            }
            token_res = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers, timeout=15)
            if token_res.status_code != 200:
                return {"status": "failed", "error": "Reddit Auth Failed: " + token_res.text}

            token = token_res.json().get("access_token")
            api_headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "GPTTypeBot/1.0 by GPT-TYPE"
            }

            # 2. Submit link or self-post to subreddit
            payload = {
                "sr": REDDIT_SUBREDDIT,
                "kind": "link",
                "title": post_title,
                "url": url,
                "resubmit": "true"
            }
            submit_res = requests.post("https://oauth.reddit.com/api/submit", data=payload, headers=api_headers, timeout=20)
            if submit_res.status_code == 200 and "json" in submit_res.text:
                logger.info(f"Successfully posted to Reddit r/{REDDIT_SUBREDDIT}!")
                return {"status": "success"}
            return {"status": "failed", "error": submit_res.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _post_to_instagram(self, text, url):
        if not text:
            return {"status": "skipped"}

        formatted_caption = text.replace("{{LINK}}", url)
        if self.dry_run:
            logger.info(f"[DRY-RUN] Instagram Caption Preview:\n{formatted_caption}")
            return {"status": "dry_run_success"}

        if not FACEBOOK_PAGE_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
            logger.info("Instagram Account ID not configured. Skipping.")
            return {"status": "skipped", "reason": "Credentials missing"}

        try:
            # Instagram requires an image_url or media container.
            # If default OG image or banner is available:
            og_image = "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/DESCRIPTION.en_us.html" # fallback or blog cover
            container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
            payload = {
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=1080&auto=format&fit=crop", # High quality typing keyboard stock
                "caption": formatted_caption,
                "access_token": FACEBOOK_PAGE_ACCESS_TOKEN
            }
            res = requests.post(container_url, data=payload, timeout=20)
            if res.status_code == 200:
                creation_id = res.json().get("id")
                # Publish container
                publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
                pub_res = requests.post(publish_url, data={"creation_id": creation_id, "access_token": FACEBOOK_PAGE_ACCESS_TOKEN}, timeout=20)
                if pub_res.status_code == 200:
                    logger.info("Successfully posted to Instagram!")
                    return {"status": "success"}
            return {"status": "failed", "error": res.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _post_to_webhook(self, post_meta, social_posts):
        """
        Universal Webhook: Allows 1-click integration with:
        - Make.com (formerly Integromat) -> distributes to all platforms automatically
        - Zapier
        - Ayrshare / Publer / Buffer
        - Discord Server
        """
        if not SOCIAL_WEBHOOK_URL:
            return {"status": "skipped", "reason": "No webhook URL configured"}

        payload = {
            "title": post_meta.get("title"),
            "url": post_meta.get("url"),
            "published_at": post_meta.get("published"),
            "summary": social_posts.get("facebook", ""),
            "twitter_text": social_posts.get("twitter", ""),
            "linkedin_text": social_posts.get("linkedin", ""),
            "instagram_text": social_posts.get("instagram", ""),
            "reddit_text": social_posts.get("reddit", "")
        }

        if self.dry_run:
            logger.info(f"[DRY-RUN] Universal Webhook Payload Preview ready for: {SOCIAL_WEBHOOK_URL}")
            return {"status": "dry_run_success"}

        try:
            res = requests.post(SOCIAL_WEBHOOK_URL, json=payload, timeout=15)
            if res.status_code in [200, 201, 204]:
                logger.info("Successfully sent payload to Universal Social Webhook!")
                return {"status": "success"}
            return {"status": "failed", "error": res.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}
