import logging
from agent.config import (
    BLOGGER_CLIENT_ID,
    BLOGGER_CLIENT_SECRET,
    BLOGGER_REFRESH_TOKEN,
    BLOG_ID,
    BLOG_URL,
    POST_STATUS
)

logger = logging.getLogger("GPTTypeAgent.Blogger")

class BloggerClient:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.service = None
        if not dry_run:
            self._authenticate()

    def _authenticate(self):
        if not all([BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN, BLOG_ID]):
            raise ValueError(
                "Missing Google Blogger API credentials! Ensure BLOGGER_CLIENT_ID, "
                "BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN, and BLOG_ID are set in environment."
            )

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials(
                None,
                refresh_token=BLOGGER_REFRESH_TOKEN,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=BLOGGER_CLIENT_ID,
                client_secret=BLOGGER_CLIENT_SECRET,
                scopes=["https://www.googleapis.com/auth/blogger"]
            )
            self.service = build("blogger", "v3", credentials=creds)
            logger.info("Successfully authenticated with Google Blogger API v3.")
        except ImportError:
            raise ImportError(
                "Google API libraries not installed. Please run: pip install -r requirements.txt"
            )
        except Exception as e:
            logger.error(f"Failed to authenticate with Blogger API: {e}")
            raise e


    def get_blog_info(self):
        if self.dry_run:
            return {"id": "dry-run-id", "name": "GPT-TYPE (Dry Run)", "url": BLOG_URL}
        
        try:
            blog = self.service.blogs().get(blogId=BLOG_ID).execute()
            return {
                "id": blog.get("id"),
                "name": blog.get("name"),
                "url": blog.get("url"),
                "total_posts": blog.get("posts", {}).get("totalItems", 0)
            }
        except Exception as e:
            logger.error(f"Error fetching blog info for {BLOG_ID}: {e}")
            raise e

    def publish_post(self, title, html_content, labels=None, is_draft=False):
        import re

        # Sanitize title so Blogger generates a clean, readable permalink without messy symbols
        clean_title = re.sub(r'[:?"\'`<>*|#]', '', title).strip()

        # Sanitize and deduplicate labels for clean categorization
        clean_labels = []
        if labels:
            for l in labels:
                lbl = str(l).strip()
                if lbl and lbl not in clean_labels:
                    clean_labels.append(lbl)
        if not clean_labels:
            clean_labels = ["Typing Tutorials", "GPT-TYPE", "Speed Test"]

        if is_draft or POST_STATUS == "DRAFT":
            draft_flag = True
        else:
            draft_flag = False

        if self.dry_run:
            slug = clean_title.lower().replace(" ", "-")
            mock_url = f"{BLOG_URL}/{slug}.html"
            logger.info(f"[DRY-RUN] Would publish post to Blogger: '{clean_title}' (Draft: {draft_flag})")
            return {
                "id": "dry_run_post_12345",
                "title": clean_title,
                "url": mock_url,
                "status": "DRAFT" if draft_flag else "LIVE"
            }

        try:
            body = {
                "kind": "blogger#post",
                "title": clean_title,
                "content": html_content,
                "labels": clean_labels
            }


            request = self.service.posts().insert(
                blogId=BLOG_ID,
                body=body,
                isDraft=draft_flag
            )
            result = request.execute()

            post_id = result.get("id")
            post_url = result.get("url")
            logger.info(f"Successfully published to Blogger! Post ID: {post_id} | URL: {post_url}")

            return {
                "id": post_id,
                "title": title,
                "url": post_url,
                "status": "DRAFT" if draft_flag else "LIVE"
            }
        except Exception as e:
            logger.error(f"Failed to publish post '{title}' to Blogger: {e}")
            raise e
