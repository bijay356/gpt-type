"""
free_typing_lead_finder.py - Find real people actively asking for free typing practice across Reddit & Web.
"""

import sys
import time
import requests
from datetime import datetime

# Configure Windows console encoding for UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Headers to prevent 429 rate limit
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (GPT-TYPE Lead Finder)"
}

SUBREDDITS = ["typing", "learnprogramming", "nepal", "pcmasterrace", "productivity"]
SEARCH_QUERIES = [
    "free typing",
    "typing tutor",
    "learn to type",
    "typeshala",
    "typing test without ads",
    "typing speed test"
]

def search_reddit_leads():
    found_leads = []
    print("\n🔍 Scanning public Reddit discussions for active 'free typing' seekers...")

    for sub in SUBREDDITS:
        for q in SEARCH_QUERIES[:3]:
            url = f"https://www.reddit.com/r/{sub}/search.json?q={requests.utils.quote(q)}&restrict_sr=1&sort=new&limit=10"
            try:
                res = requests.get(url, headers=HEADERS, timeout=8)
                if res.status_code == 200:
                    data = res.json().get("data", {}).get("children", [])
                    for item in data:
                        post = item.get("data", {})
                        title = post.get("title", "")
                        selftext = post.get("selftext", "")
                        combined = (title + " " + selftext).lower()

                        if any(k in combined for k in ["free", "tutor", "practice", "recommend", "how to", "where can i"]):
                            lead = {
                                "platform": "Reddit",
                                "subreddit": f"r/{sub}",
                                "author": post.get("author", "unknown"),
                                "title": title,
                                "url": f"https://reddit.com{post.get('permalink', '')}",
                                "created_utc": datetime.fromtimestamp(post.get("created_utc", time.time())).strftime("%Y-%m-%d %H:%M"),
                                "num_comments": post.get("num_comments", 0)
                            }
                            # Avoid duplicates
                            if not any(l["url"] == lead["url"] for l in found_leads):
                                found_leads.append(lead)
                time.sleep(0.8) # respect rate limit
            except Exception as e:
                pass

    return found_leads

def display_leads(leads):
    print(f"\n🎯 Found {len(leads)} High-Intent Discussions from people looking for typing tools:")
    print("=" * 80)
    for i, lead in enumerate(leads[:15], 1):
        print(f"[{i}] [{lead['subreddit']}] by u/{lead['author']} ({lead['created_utc']})")
        print(f"    Title: {lead['title']}")
        print(f"    Link : {lead['url']}")
        print(f"    💬 Recommended Pitch:")
        print(f"       \"Hey u/{lead['author']}, if you're looking for a 100% free typing tutor with zero ads, check out GPT-TYPE (supports 124+ languages, authentic Typeshala, and an offline Windows app): https://gpttype.blogspot.com\"")
        print("-" * 80)

if __name__ == "__main__":
    leads = search_reddit_leads()
    display_leads(leads)
