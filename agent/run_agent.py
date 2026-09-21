import argparse
import logging
import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agent.keyword_engine import KeywordEngine

from agent.content_generator import ContentGenerator
from agent.blogger_client import BloggerClient
from agent.social_publisher import SocialPublisher
from agent.analytics_reporter import AnalyticsReporter

# Setup logging and UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("GPTTypeAgent.Main")


def write_github_step_summary(markdown_text):
    import os
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        try:
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(markdown_text + "\n")
        except Exception:
            pass

def run(dry_run=False, cluster_id=None, draft=False):
    logger.info("=" * 60)
    logger.info("🚀 STARTING 24/7 AUTONOMOUS AGENT FOR GPT-TYPE")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'PRODUCTION'} | Force Draft: {draft}")
    logger.info("=" * 60)

    # Step 0: Pre-flight Verification
    logger.info("\n--- [Pre-flight] Verifying Blogger API Connection & Token ---")
    blogger = BloggerClient(dry_run=dry_run)
    blogger.verify_credentials()

    # Step 1: Select Topic & Keyword
    logger.info("\n--- [1/5] Selecting Target SEO Keyword & Cluster ---")
    engine = KeywordEngine()
    topic = engine.select_next_topic(force_cluster_id=cluster_id)
    logger.info(f"Target Keyword: '{topic['primary_keyword']}'")
    logger.info(f"Topic Cluster: {topic['cluster_name']} ({topic['cluster_id']})")
    logger.info(f"Target Test Mode: {topic['target_test_mode']} | Deep Link: {topic['deep_link']}")

    # Step 2: Generate Content via Gemini AI
    logger.info("\n--- [2/5] Generating High-Ranking SEO Article & Schema ---")
    generator = ContentGenerator(dry_run=dry_run)
    article_data = generator.generate_article_and_social(topic)

    logger.info(f"Generated Title: {article_data['title']}")
    logger.info(f"Meta Description: {article_data['meta_description']}")
    logger.info(f"Labels: {', '.join(article_data['labels'])}")
    logger.info(f"HTML Content Length: {len(article_data['html_content'])} characters")

    # Step 3: Publish to Blogger.com
    logger.info("\n--- [3/5] Publishing to Blogger (gpttype.blogspot.com) ---")
    post_meta = blogger.publish_post(
        title=article_data["title"],
        html_content=article_data["html_content"],
        labels=article_data["labels"],
        is_draft=draft
    )
    logger.info(f"Publication Result: Status={post_meta['status']} | URL={post_meta['url']}")

    # Step 4: Broadcast to Social Media Channels
    logger.info("\n--- [4/5] Broadcasting to Social Channels ---")
    social = SocialPublisher(dry_run=dry_run)
    social_results = social.broadcast(post_meta, article_data.get("social_posts", {}))
    logger.info(f"Social Broadcast Results: {social_results}")

    # Step 5: Save Memory & Send Analytics
    logger.info("\n--- [5/5] Updating Agent Memory & Analytics ---")
    reporter = AnalyticsReporter(dry_run=dry_run)
    record = reporter.record_publication(topic, post_meta, social_results)
    logger.info(f"Saved to post_history.json. Total posts published: {reporter.history.get('total_posts_published', 0)}")

    # GitHub Actions Step Summary
    summary = f"""### 🚀 GPT-TYPE Autonomous Agent Execution Report

| Property | Value |
| :--- | :--- |
| **Article Title** | **{article_data['title']}** |
| **Status** | `{post_meta['status']}` |
| **Live Article URL** | [{post_meta['url']}]({post_meta['url']}) |
| **Primary Keyword** | `{topic['primary_keyword']}` |
| **Topic Cluster** | {topic['cluster_name']} (`{topic['cluster_id']}`) |
| **Target Test Mode** | `{topic['target_test_mode']}` |
| **Social Media** | Telegram: `{social_results.get('telegram', {}).get('status', 'n/a')}` | LinkedIn: `{social_results.get('linkedin', {}).get('status', 'n/a')}` |
"""
    write_github_step_summary(summary)

    logger.info("=" * 60)
    logger.info("✅ AUTONOMOUS CYCLE COMPLETED SUCCESSFULLY!")
    logger.info("=" * 60)
    return record

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GPT-TYPE 24/7 Autonomous SEO & Social Agent")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without modifying Blogger or social media")
    parser.add_argument("--cluster", type=str, default=None, help="Force a specific cluster ID (e.g. speed_boosters, programming_typing)")
    parser.add_argument("--draft", action="store_true", help="Publish as draft instead of live post")
    args = parser.parse_args()

    try:
        run(dry_run=args.dry_run, cluster_id=args.cluster, draft=args.draft)
    except Exception as e:
        logger.exception(f"Fatal error during agent execution: {e}")
        err_text = str(e)
        troubleshoot = ""
        if "invalid_grant" in err_text.lower() or "expired or revoked" in err_text.lower():
            troubleshoot = """
> [!CAUTION]
> **Google Blogger Refresh Token Expired (`invalid_grant`)**
>
> 1. Set OAuth Consent Screen to **"In Production"** in [Google Cloud Console](https://console.cloud.google.com/apis/credentials/consent).
> 2. Run `python setup_blogger_auth.py` locally to generate a permanent refresh token.
> 3. Update the `BLOGGER_REFRESH_TOKEN` secret in GitHub Repository Settings.
"""
        fail_summary = f"""### ❌ GPT-TYPE Autonomous Agent Run Failed

> **Error**: `{err_text}`
{troubleshoot}
"""
        write_github_step_summary(fail_summary)
        sys.exit(1)
