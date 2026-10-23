import difflib
import json
import logging
import re
import requests
from datetime import datetime
from agent.config import KEYWORD_DB_PATH, POST_HISTORY_PATH, BLOG_URL, GEMINI_API_KEY

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

    def _save_db(self):
        try:
            with open(KEYWORD_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(self.db, f, indent=2, ensure_ascii=False)
            logger.info("Successfully updated keyword_database.json with fresh keywords.")
        except Exception as e:
            logger.error(f"Failed to save keyword database: {e}")

    def get_published_keywords(self):
        """Returns normalized set of all published primary keywords."""
        return {
            p.get("primary_keyword", "").lower().strip()
            for p in self.history.get("published_posts", [])
            if p.get("primary_keyword")
        }

    def get_published_titles(self):
        """Returns normalized list of all published post titles."""
        return [
            p.get("title", "").strip()
            for p in self.history.get("published_posts", [])
            if p.get("title")
        ]

    def is_keyword_too_similar(self, candidate_kw, published_keywords, published_titles, threshold=0.65):
        """
        Calculates similarity against all published keywords and titles to prevent cannibalization.
        """
        cand_clean = candidate_kw.lower().strip()
        if cand_clean in published_keywords:
            return True, f"exact match with published keyword '{cand_clean}'"

        for pub_kw in published_keywords:
            ratio = difflib.SequenceMatcher(None, cand_clean, pub_kw).ratio()
            if ratio >= threshold:
                return True, f"too similar to published keyword '{pub_kw}' (ratio: {ratio:.2f})"

        for pub_title in published_titles:
            pub_title_clean = pub_title.lower().strip()
            ratio = difflib.SequenceMatcher(None, cand_clean, pub_title_clean).ratio()
            if ratio >= threshold:
                return True, f"too similar to published title '{pub_title}' (ratio: {ratio:.2f})"

        return False, ""

    def _generate_fresh_cluster_keywords_with_gemini(self, cluster, published_keywords):
        """
        Uses Gemini to dynamically generate 5 brand new, non-repeating, high-intent SEO keywords
        for a cluster when static keywords run low.
        """
        if not GEMINI_API_KEY:
            return []

        c_name = cluster.get("name", "Typing")
        c_id = cluster.get("id", "general")
        recent_pub = list(published_keywords)[-30:] if published_keywords else []

        prompt = f"""You are a Senior SEO Strategist for GPT-TYPE ({BLOG_URL}), a global touch typing and web tools platform.
Topical Cluster: '{c_name}' (ID: {c_id})

We have already published articles targeting these keywords (DO NOT REPEAT OR CLOSELY RESEMBLE ANY OF THESE):
{json.dumps(recent_pub, indent=2)}

Generate 5 brand new, highly specific, long-tail search keywords that real learners, students, coders, or exam takers search for on Google.
Focus on high search intent, specific niches, real tools, techniques, benchmarks, or languages.

Respond ONLY with a valid JSON array of objects:
[
  {{
    "primary": "clean lowercase long-tail keyword between 4 to 8 words",
    "intent": "guide/informational/benchmark",
    "secondary": ["secondary keyword 1", "secondary keyword 2", "secondary keyword 3"]
  }}
]"""

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.85,
                "responseMimeType": "application/json"
            }
        }

        models_to_try = [
            "gemini-3.6-flash",
            "gemini-3.1-flash-lite",
            "gemini-3-flash-preview",
            "gemini-flash-latest"
        ]

        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            try:
                res = requests.post(url, headers=headers, json=payload, timeout=30)
                if res.status_code == 200:
                    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    clean_text = text.strip()
                    if clean_text.startswith("```"):
                        clean_text = re.sub(r"^```(?:json)?\n?", "", clean_text)
                        clean_text = re.sub(r"\n?```$", "", clean_text)
                    items = json.loads(clean_text)
                    if isinstance(items, list):
                        valid_items = []
                        for it in items:
                            pk = it.get("primary", "").strip().lower()
                            if pk and pk not in published_keywords:
                                valid_items.append({
                                    "primary": pk,
                                    "intent": it.get("intent", "guide"),
                                    "secondary": it.get("secondary", [])
                                })
                        if valid_items:
                            logger.info(f"Gemini dynamically generated {len(valid_items)} new keywords for cluster '{c_name}'")
                            return valid_items
            except Exception as e:
                logger.debug(f"Dynamic keyword generation with {model} failed: {e}")

        return []

    def select_next_topic(self, force_cluster_id=None):
        clusters = self.db.get("clusters", [])
        if not clusters:
            raise ValueError("Keyword database is empty!")

        published_keywords = self.get_published_keywords()
        published_titles = self.get_published_titles()

        # 1. Determine Cluster
        if force_cluster_id:
            cluster = next((c for c in clusters if c.get("id") == force_cluster_id), None)
            if not cluster:
                raise ValueError(f"Cluster '{force_cluster_id}' not found.")
        else:
            rotation_idx = self.history.get("cluster_rotation_index", 0) % len(clusters)
            cluster = clusters[rotation_idx]

        # 2. Pick next unwritten and non-similar keyword in this cluster
        keywords = cluster.get("keywords", [])
        chosen_keyword = None

        for kw in keywords:
            pk = kw.get("primary", "").strip()
            too_similar, reason = self.is_keyword_too_similar(pk, published_keywords, published_titles, threshold=0.65)
            if not too_similar:
                chosen_keyword = kw
                break

        # 3. If all static keywords in this cluster are exhausted or too similar, dynamically generate fresh ones
        if not chosen_keyword:
            logger.info(f"All pre-configured keywords in cluster '{cluster.get('name')}' have been used. Dynamically generating fresh long-tail topics...")
            new_generated = self._generate_fresh_cluster_keywords_with_gemini(cluster, published_keywords)
            for new_kw in new_generated:
                too_sim, _ = self.is_keyword_too_similar(new_kw["primary"], published_keywords, published_titles, threshold=0.60)
                if not too_sim:
                    cluster["keywords"].append(new_kw)
                    chosen_keyword = new_kw
                    self._save_db()
                    break

        # 4. Ultimate Fallback (guarantees non-duplicate unique long-tail topic)
        if not chosen_keyword:
            counter = len(published_keywords) + 1
            unique_kw = f"advanced touch typing drills and speed secrets part {counter}"
            chosen_keyword = {
                "primary": unique_kw,
                "intent": "guide/advanced",
                "secondary": ["wpm improvement drills", "typing accuracy benchmarks", "touch typing technique"]
            }

        # 5. Formulate deep-link for GPT-TYPE
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
