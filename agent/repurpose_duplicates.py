import argparse
import difflib
import json
import logging
import sys
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
        title = p.get("title", "")
        for prev_idx, prev_p in enumerate(posts[:idx]):
            ratio = difflib.SequenceMatcher(None, title.lower(), prev_p.get("title", "").lower()).ratio()
            if ratio >= 0.75:
                duplicates.append({
                    "post_index": idx,
                    "post_id": p.get("id"),
                    "current_title": title,
                    "current_url": p.get("url"),
                    "duplicate_of_index": prev_idx + 1,
                    "duplicate_of_title": prev_p.get("title", ""),
                    "cluster_id": p.get("cluster_id", "speed_boosters")
                })
                break
    return duplicates

def repurpose_duplicates(dry_run=True, limit=None):
    duplicates = find_duplicate_posts()
    logger.info(f"Found {len(duplicates)} duplicate / near-duplicate posts.")

    if not duplicates:
        logger.info("No duplicate posts found! Everything is unique.")
        return

    if limit:
        duplicates = duplicates[:limit]
        logger.info(f"Processing first {limit} duplicate posts...")

    blogger = BloggerClient(dry_run=dry_run)
    generator = ContentGenerator(dry_run=dry_run)
    engine = KeywordEngine()

    with open(POST_HISTORY_PATH, "r", encoding="utf-8") as f:
        history = json.load(f)

    updated_count = 0
    for dup in duplicates:
        post_idx = dup["post_index"]
        post_id = dup["post_id"]
        old_title = dup["current_title"]
        cluster_id = dup["cluster_id"]

        logger.info("=" * 60)
        logger.info(f"Fixing Post #{post_idx + 1} (Blogger ID: {post_id})")
        logger.info(f"Old Title: '{old_title}' (Duplicate of Post #{dup['duplicate_of_index']})")

        # Select a fresh, unwritten topic in this cluster
        topic = engine.select_next_topic(force_cluster_id=cluster_id)
        logger.info(f"New Target Keyword: '{topic['primary_keyword']}'")

        # Generate unique, in-depth content
        article = generator.generate_article_and_social(topic)
        new_title = article["title"]
        new_html = article["html_content"]
        new_labels = article.get("labels", ["Typing Tutorials", "GPT-TYPE"])

        logger.info(f"New Unique Title: '{new_title}'")
        logger.info(f"New Content Length: {len(new_html)} characters")

        # Update in Blogger
        if not dry_run and post_id:
            try:
                res = blogger.update_post(post_id, title=new_title, html_content=new_html, labels=new_labels)
                logger.info(f"✅ Successfully updated Blogger post {post_id} on live site!")
                
                # Update record in post_history.json
                history["published_posts"][post_idx]["title"] = new_title
                history["published_posts"][post_idx]["primary_keyword"] = topic["primary_keyword"]
                history["published_posts"][post_idx]["cluster_id"] = topic["cluster_id"]
                history["published_posts"][post_idx]["cluster_name"] = topic["cluster_name"]
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to update Blogger post {post_id}: {e}")
        else:
            logger.info(f"[DRY-RUN] Would update Blogger post {post_id} with new title '{new_title}'")
            updated_count += 1

    if not dry_run and updated_count > 0:
        with open(POST_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logger.info(f"Updated post_history.json with {updated_count} fresh titles and keywords.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repurpose duplicate Blogger posts into unique high-ranking articles")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without modifying Blogger")
    parser.add_argument("--execute", action="store_true", help="Actually update posts in Blogger")
    parser.add_argument("--limit", type=int, default=None, help="Number of duplicate posts to update")
    args = parser.parse_args()

    is_dry = not args.execute
    repurpose_duplicates(dry_run=is_dry, limit=args.limit)
