import json
import logging
from datetime import datetime, timezone
import requests
from agent.config import POST_HISTORY_PATH, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger("GPTTypeAgent.Analytics")

class AnalyticsReporter:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.history = self._load_history()

    def _load_history(self):
        if POST_HISTORY_PATH.exists():
            try:
                with open(POST_HISTORY_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading history: {e}")
        return {
            "total_posts_published": 0,
            "last_run_timestamp": None,
            "published_posts": [],
            "cluster_rotation_index": 0
        }

    def record_publication(self, topic, post_meta, social_results):
        now_iso = datetime.now(timezone.utc).isoformat()
        
        record = {
            "id": post_meta.get("id"),
            "title": post_meta.get("title"),
            "url": post_meta.get("url"),
            "status": post_meta.get("status", "LIVE"),
            "primary_keyword": topic.get("primary_keyword"),
            "cluster_id": topic.get("cluster_id"),
            "cluster_name": topic.get("cluster_name"),
            "published_at": now_iso,
            "social_broadcast": social_results
        }

        if not self.dry_run:
            self.history["published_posts"].append(record)
            self.history["total_posts_published"] = len(self.history["published_posts"])
            self.history["last_run_timestamp"] = now_iso
            self._save_history()

        self._send_admin_digest(record)
        return record

    def _save_history(self):
        try:
            with open(POST_HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            logger.info("Successfully updated post_history.json.")
        except Exception as e:
            logger.error(f"Failed to persist post_history.json: {e}")

    def _send_admin_digest(self, record):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return

        digest = (
            f"🤖 <b>GPT-TYPE 24/7 Agent Report</b>\n\n"
            f"✅ <b>New Post Published:</b>\n"
            f"📰 <i>{record['title']}</i>\n\n"
            f"🎯 <b>Target Keyword:</b> <code>{record['primary_keyword']}</code>\n"
            f"📂 <b>Cluster:</b> {record['cluster_name']}\n"
            f"🌐 <b>URL:</b> <a href=\"{record['url']}\">{record['url']}</a>\n\n"
            f"📊 <b>Total Articles Published:</b> {self.history.get('total_posts_published', 1)}\n"
            f"⏰ <b>Timestamp:</b> {record['published_at']}"
        )

        try:
            api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": digest,
                "parse_mode": "HTML"
            }
            requests.post(api_url, json=payload, timeout=15)
        except Exception as e:
            logger.warning(f"Failed to send admin digest: {e}")
