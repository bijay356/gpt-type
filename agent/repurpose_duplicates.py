import argparse
import difflib
import json
import logging
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agent.config import POST_HISTORY_PATH, KEYWORD_DB_PATH
from agent.blogger_client import BloggerClient
from agent.content_generator import ContentGenerator
from agent.keyword_engine import KeywordEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("GPTTypeAgent.DuplicateFixer")

def find_duplicate_posts():
    if not POST_HISTORY_PATH.exists():
        return []
    with open(POST_HISTORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    posts = data.get("published_posts", [])

    duplicates = []
    for idx, p in enumerate(posts):
        title = p.get("title", "").strip()
        pk = p.get("primary_keyword", "").strip().lower()

        for prev_idx, prev_p in enumerate(posts[:idx]):
            prev_title = prev_p.get("title", "").strip()
            prev_pk = prev_p.get("primary_keyword", "").strip().lower()

            same_pk = (pk == prev_pk and bool(pk))
            ratio = difflib.SequenceMatcher(None, title.lower(), prev_title.lower()).ratio()

            if same_pk or ratio >= 0.82:
                duplicates.append({
                    "post_index": idx,
                    "post_id": p.get("id"),
                    "current_title": title,
                    "current_url": p.get("url"),
                    "primary_keyword": pk,
                    "duplicate_of_index": prev_idx + 1,
                    "duplicate_of_title": prev_title,
                    "cluster_id": p.get("cluster_id", "speed_boosters"),
                    "ratio": ratio,
                    "same_pk": same_pk
                })
                break
    return duplicates

def repurpose_duplicates(dry_run=True, limit=None):
    duplicates = find_duplicate_posts()
    logger.info(f"Found {len(duplicates)} genuine duplicate posts to clean up.")

    if not duplicates:
        logger.info("✅ No duplicate posts found! All articles are unique.")
        return

    if limit:
        duplicates = duplicates[:limit]
        logger.info(f"Processing batch of {limit} duplicate posts...")

    blogger = BloggerClient(dry_run=dry_run)
    generator = ContentGenerator(dry_run=dry_run)
    engine = KeywordEngine()

    with open(POST_HISTORY_PATH, "r", encoding="utf-8") as f:
        history = json.load(f)

    updated_count = 0
    total_to_process = len(duplicates)

    for dup in duplicates:
        post_idx = dup["post_index"]
        post_id = dup["post_id"]
        old_title = dup["current_title"]
        cluster_id = dup["cluster_id"]

        logger.info("=" * 70)
        logger.info(f"🔄 Repurposing [{updated_count + 1}/{total_to_process}] Post #{post_idx + 1} (Blogger ID: {post_id})")
        logger.info(f"   Old Title: '{old_title}'")
        logger.info(f"   Duplicate Of: Post #{dup['duplicate_of_index']} ('{dup['duplicate_of_title']}')")

        # Select a fresh, unwritten topic in this cluster from the 209-keyword database
        topic = engine.select_next_topic(force_cluster_id=cluster_id)
        logger.info(f"   New Target Keyword: '{topic['primary_keyword']}' ({topic['cluster_name']})")

        # Generate unique, in-depth 1,400+ word content meeting Google monetization criteria
        article = generator.generate_article_and_social(topic)
        new_title = article["title"]
        new_html = article["html_content"]
        new_labels = article.get("labels", ["Typing Tutorials", "GPT-TYPE"])

        logger.info(f"   New Unique Title: '{new_title}'")
        logger.info(f"   Content Length: {len(new_html)} chars")

        # Update post in Blogger
        if not dry_run and post_id:
            try:
                res = blogger.update_post(post_id, title=new_title, html_content=new_html, labels=new_labels)
                logger.info(f"   ✅ Successfully updated Blogger post {post_id} live!")

                history["published_posts"][post_idx]["title"] = new_title
                history["published_posts"][post_idx]["primary_keyword"] = topic["primary_keyword"]
                history["published_posts"][post_idx]["cluster_id"] = topic["cluster_id"]
                history["published_posts"][post_idx]["cluster_name"] = topic["cluster_name"]
                engine.history = history
                updated_count += 1

                # Save history immediately so progress is never lost
                with open(POST_HISTORY_PATH, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                logger.info(f"   💾 Saved post_history.json ({updated_count}/{total_to_process} completed)")

                time.sleep(2)  # Cooldown between API calls
            except Exception as e:
                logger.error(f"   ❌ Failed to update Blogger post {post_id}: {e}")
        else:
            logger.info(f"   [DRY-RUN] Would update Blogger post {post_id} with new title '{new_title}'")
            history["published_posts"][post_idx]["title"] = new_title
            history["published_posts"][post_idx]["primary_keyword"] = topic["primary_keyword"]
            engine.history = history
            updated_count += 1

    logger.info("=" * 70)
    logger.info(f"🎉 COMPLETED: Successfully repurposed {updated_count}/{total_to_process} duplicate posts!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repurpose duplicate Blogger posts into unique high-ranking articles")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without modifying Blogger")
    parser.add_argument("--execute", action="store_true", help="Actually update posts in Blogger")
    parser.add_argument("--limit", type=int, default=None, help="Number of duplicate posts to update")
    args = parser.parse_args()

    is_dry = not args.execute
    repurpose_duplicates(dry_run=is_dry, limit=args.limit)
