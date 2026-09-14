import json
import logging
from datetime import datetime
from agent.config import KEYWORD_DB_PATH, POST_HISTORY_PATH, BLOG_URL

logger = logging.getLogger("GPTTypeAgent.Keywords")

class KeywordEngine:
    def __init__(self):
        self.db = self._load_json(KEYWORD_DB_PATH, {"clusters": []})
        self.history = self._load_json(POST_HISTORY_PATH, {
            "total_posts_published": 0,
            "published_posts": [],
            "cluster_rotation_index": 0
        })

    def _load_json(self, path, default):
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading {path}: {e}")
        return default

    def _save_history(self):
        try:
            with open(POST_HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def get_published_keywords(self):
        return {p.get("primary_keyword", "").lower() for p in self.history.get("published_posts", [])}

    def select_next_topic(self, force_cluster_id=None):
        clusters = self.db.get("clusters", [])
        if not clusters:
            raise ValueError("Keyword database is empty!")

        published = self.get_published_keywords()

        # 1. Determine Cluster
        if force_cluster_id:
            cluster = next((c for c in clusters if c.get("id") == force_cluster_id), None)
            if not cluster:
                raise ValueError(f"Cluster '{force_cluster_id}' not found.")
        else:
            rotation_idx = self.history.get("cluster_rotation_index", 0) % len(clusters)
            cluster = clusters[rotation_idx]

        # 2. Pick next unwritten keyword in this cluster
        keywords = cluster.get("keywords", [])
        chosen_keyword = None

        for kw in keywords:
            if kw.get("primary", "").lower() not in published:
                chosen_keyword = kw
                break

        # If all keywords in this cluster have been used, pick the least recently used
        if not chosen_keyword and keywords:
            logger.info(f"All keywords in cluster '{cluster.get('name')}' were published. Recycling oldest topic with fresh perspective.")
            chosen_keyword = keywords[0]

        if not chosen_keyword:
            chosen_keyword = {
                "primary": "free online speed typing test tool",
                "intent": "high intent tool",
                "secondary": ["wpm typing tester", "best typing speed practice", "instant typing score"]
            }

        # 3. Formulate deep-link for GPT-TYPE
        test_mode = cluster.get("target_test_mode", "60s")
        if test_mode == "code":
            deep_link = f"{BLOG_URL}#code"
            cta_text = "🚀 Test Your Code Typing Speed on GPT-TYPE"
        elif test_mode == "multilingual":
            deep_link = f"{BLOG_URL}#languages"
            cta_text = "🌍 Practice Multilingual Typing in 122+ Languages on GPT-TYPE"

        elif test_mode == "300s":
            deep_link = f"{BLOG_URL}#exam-5min"
            cta_text = "⏱️ Take the Official 5-Minute Typing Speed Test on GPT-TYPE"
        elif test_mode == "120s":
            deep_link = f"{BLOG_URL}#endurance"
            cta_text = "⚡ Start 2-Minute Endurance Typing Test on GPT-TYPE"
        else:
            deep_link = f"{BLOG_URL}"
            cta_text = "🔥 Start Live 60-Second Speed Test on GPT-TYPE"

        topic_payload = {
            "cluster_id": cluster.get("id"),
            "cluster_name": cluster.get("name"),
            "primary_keyword": chosen_keyword.get("primary"),
            "intent": chosen_keyword.get("intent", "informational"),
            "secondary_keywords": chosen_keyword.get("secondary", []),
            "target_test_mode": test_mode,
            "deep_link": deep_link,
            "cta_text": cta_text
        }

        # Advance rotation index
        if not force_cluster_id:
            self.history["cluster_rotation_index"] = (self.history.get("cluster_rotation_index", 0) + 1) % len(clusters)
            self._save_history()

        return topic_payload
