import json
import logging
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agent.blogger_client import BloggerClient
from agent.config import (
    BLOG_ID,
    BLOG_URL,
    DATA_DIR,
    POST_HISTORY_PATH,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("GPTTypeAgent.MonthlyReport")

METRICS_PATH = DATA_DIR / "monthly_metrics.json"


def fetch_blogger_traffic():
    """Fetches real live pageviews (7d, 30d, all-time) via Blogger API v3."""
    stats = {"SEVEN_DAYS": 0, "THIRTY_DAYS": 0, "ALL_TIME": 0}
    try:
        blogger = BloggerClient(dry_run=False)
        res = blogger.service.pageViews().get(
            blogId=BLOG_ID, range=["7DAYS", "30DAYS", "all"]
        ).execute()
        for item in res.get("counts", []):
            tr = item.get("timeRange")
            if tr in stats:
                stats[tr] = int(item.get("count", 0))
        logger.info(f"Fetched live Blogger traffic: {stats}")
    except Exception as e:
        logger.error(f"Could not fetch Blogger traffic stats: {e}")
    return stats


def run_live_seo_health_check():
    """Verifies live site HTTP 200, canonical tag presence, and sitemap URL count."""
    health = {
        "homepage_ok": False,
        "canonical_ok": False,
        "sitemap_count": 0,
    }
    try:
        r_home = requests.get(f"{BLOG_URL}/", timeout=15)
        health["homepage_ok"] = r_home.status_code == 200
        health["canonical_ok"] = (
            'rel="canonical"' in r_home.text.lower()
            or "rel='canonical'" in r_home.text.lower()
        )
    except Exception as e:
        logger.warning(f"Homepage health check error: {e}")

    try:
        r_map = requests.get(f"{BLOG_URL}/sitemap.xml", timeout=15)
        if r_map.status_code == 200:
            health["sitemap_count"] = len(re.findall(r"<loc>(.*?)</loc>", r_map.text))
    except Exception as e:
        logger.warning(f"Sitemap health check error: {e}")

    return health


def load_previous_snapshot():
    if METRICS_PATH.exists():
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            snaps = data.get("snapshots", [])
            if snaps:
                return data, snaps[-1]
        except Exception:
            pass
    return {"snapshots": []}, None


def save_snapshot(data, traffic, live_posts_count, posts_28d):
    now_iso = datetime.now(timezone.utc).isoformat()
    data.setdefault("snapshots", []).append(
        {
            "timestamp": now_iso,
            "traffic_7d": traffic["SEVEN_DAYS"],
            "traffic_30d": traffic["THIRTY_DAYS"],
            "traffic_all_time": traffic["ALL_TIME"],
            "live_posts": live_posts_count,
            "posts_last_28d": posts_28d,
        }
    )
    try:
        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved metrics snapshot to {METRICS_PATH}")
    except Exception as e:
        logger.error(f"Failed to save monthly_metrics.json: {e}")


def format_delta(current, previous):
    if previous is None:
        return "Baseline"
    diff = current - previous
    sign = "+" if diff >= 0 else ""
    if previous > 0:
        pct = (diff / previous) * 100
        return f"{sign}{diff:,} ({sign}{pct:.0f}%)"
    return f"{sign}{diff:,}"


def send_telegram_report(message_html):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials missing. Printing report only:\n" + message_html)
        return False

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    res = requests.post(api_url, json=payload, timeout=20)
    if res.status_code == 200:
        logger.info("✅ 4-Week Traffic & SEO Report sent to Telegram successfully!")
        return True
    logger.error(f"Failed to send Telegram report: {res.status_code} {res.text}")
    return False


def generate_and_send_report():
    now_utc = datetime.now(timezone.utc)
    cutoff_28d = now_utc - timedelta(days=28)

    # 1. Analyze post_history.json
    live_posts = []
    if POST_HISTORY_PATH.exists():
        with open(POST_HISTORY_PATH, "r", encoding="utf-8") as f:
            hist = json.load(f)
        live_posts = [
            p for p in hist.get("published_posts", []) if p.get("status", "LIVE") == "LIVE"
        ]

    recent_28d = []
    for p in live_posts:
        pub_str = p.get("published_at", "")
        try:
            dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            if dt >= cutoff_28d:
                recent_28d.append(p)
        except Exception:
            pass

    titles = [p.get("title", "").strip().lower() for p in live_posts if p.get("title")]
    dup_count = len(titles) - len(set(titles))

    cluster_counts = Counter(p.get("cluster_name", "General") for p in recent_28d)
    top_clusters_lines = "\n".join(
        f"  • {cname}: <b>{cnt}</b>" for cname, cnt in cluster_counts.most_common(5)
    ) or "  • Starting fresh 4x/week cycle"

    # 2. Fetch Live Blogger Traffic & SEO Health
    traffic = fetch_blogger_traffic()
    health = run_live_seo_health_check()
    metrics_data, prev_snap = load_previous_snapshot()

    delta_30d = format_delta(
        traffic["THIRTY_DAYS"], prev_snap.get("traffic_30d") if prev_snap else None
    )
    delta_7d = format_delta(
        traffic["SEVEN_DAYS"], prev_snap.get("traffic_7d") if prev_snap else None
    )

    date_str = now_utc.strftime("%d %b %Y")
    home_badge = "✅ HTTP 200" if health["homepage_ok"] else "⚠️ Check"
    canon_badge = "✅ Active" if health["canonical_ok"] else "❌ Missing"

    report_html = (
        f"📊 <b>GPT-TYPE 4-Week Traffic &amp; SEO Report</b>\n"
        f"<i>Date: {date_str} | gpttype.blogspot.com</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📈 <b>LIVE SITE TRAFFIC (Blogger Stats)</b>\n"
        f"• Last 7 Days: <b>{traffic['SEVEN_DAYS']:,} views</b> ({delta_7d})\n"
        f"• Last 30 Days: <b>{traffic['THIRTY_DAYS']:,} views</b> ({delta_30d})\n"
        f"• All-Time Total: <b>{traffic['ALL_TIME']:,} views</b>\n\n"
        f"📝 <b>PUBLISHING SUMMARY (Last 4 Weeks)</b>\n"
        f"• Published (28d): <b>{len(recent_28d)} guides</b>\n"
        f"• Total Clean Live Posts: <b>{len(live_posts)}</b>\n"
        f"• Duplicate Titles: <b>{dup_count}</b> ✅\n"
        f"{top_clusters_lines}\n\n"
        f"🛡️ <b>LIVE SEO HEALTH CHECK</b>\n"
        f"• Site Status: {home_badge}\n"
        f"• Canonical Tag: {canon_badge}\n"
        f"• Sitemap URLs: <b>{health['sitemap_count']}</b>\n\n"
        f"🧾 <b>MONTHLY COST STATEMENT</b>\n"
        f"• AI Engine (Groq 120B): <b>$0.00</b>\n"
        f"• Cloud Automation (GitHub): <b>$0.00</b>\n"
        f"• Hosting (Blogger): <b>$0.00</b>\n"
        f"• <b>Total Monthly Cost: $0.00</b>\n\n"
        f"👉 <a href=\"https://search.google.com/search-console?resource_id=https%3A%2F%2Fgpttype.blogspot.com%2F\">Open Google Search Console</a> | "
        f"<a href=\"{BLOG_URL}\">Open GPT-TYPE</a>"
    )

    sent = send_telegram_report(report_html)
    save_snapshot(metrics_data, traffic, len(live_posts), len(recent_28d))
    return sent


if __name__ == "__main__":
    generate_and_send_report()
