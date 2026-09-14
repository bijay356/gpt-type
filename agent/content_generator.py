import json
import logging
import re
import requests
from agent.config import GEMINI_API_KEY, BLOG_URL

logger = logging.getLogger("GPTTypeAgent.Generator")

class ContentGenerator:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        if not GEMINI_API_KEY and not dry_run:
            logger.warning("GEMINI_API_KEY is not set. Generator will fail if called without an API key.")

    def generate_article_and_social(self, topic):
        """
        Uses Gemini to generate complete SEO article, JSON-LD schema,
        practice drills, and social media captions.
        """
        if self.dry_run and not GEMINI_API_KEY:
            logger.info("[DRY-RUN] GEMINI_API_KEY not configured. Generating realistic mock article payload.")
            return self._generate_mock_article(topic)

        prompt = self._build_prompt(topic)
        raw_response = self._call_gemini(prompt)
        parsed = self._parse_json_response(raw_response)
        return parsed

    def _generate_mock_article(self, topic):
        kw = topic["primary_keyword"]
        title = f"{kw.title()}: Complete Expert Guide & Speed Benchmark"
        return {
            "title": title,
            "meta_description": f"Master {kw} with pro techniques, speed drills, and benchmarks on GPT-TYPE. Measure your WPM live.",
            "labels": ["Typing Speed", "Touch Typing", "GPT-TYPE", topic.get("cluster_name", "Typing")],
            "html_content": f"""<p>Welcome to the definitive guide on <strong>{kw}</strong>.</p>
<h2>Why Typing Mastery Matters</h2>
<p>Achieving top-tier typing performance requires systematic practice, ergonomic finger posture, and consistent benchmarking.</p>
<div style="background: #1e293b; color: #f8fafc; border-radius: 12px; padding: 24px; margin: 30px 0; border: 1px solid #334155;">
  <h3 style="color: #38bdf8; margin-top: 0;">⚡ Practice Drill: {kw.title()}</h3>
  <p>Practice typing the drill text below into GPT-TYPE:</p>
  <div style="background: #0f172a; padding: 16px; border-radius: 8px; font-family: monospace; color: #a5f3fc; margin: 15px 0;">
    Speed and accuracy are the pillars of touch typing. Focus on smooth rhythm rather than sudden finger bursts.
  </div>
  <a href="{topic['deep_link']}" style="display: inline-block; background: #0ea5e9; color: #ffffff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold;">{topic['cta_text']}</a>
</div>
<h2>Frequently Asked Questions</h2>
<h3>How fast should you type?</h3>
<p>The global average is 40 WPM, while professionals aim for 70 to 100+ WPM.</p>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{{
    "@type": "Question",
    "name": "How fast should you type?",
    "acceptedAnswer": {{
      "@type": "Answer",
      "text": "The global average is 40 WPM, while professionals aim for 70 to 100+ WPM."
    }}
  }}]
}}
</script>""",
            "social_posts": {
                "twitter": f"Want to master {kw}? Here is our comprehensive guide + speed drill 🚀 Test your WPM on GPT-TYPE: {{{{LINK}}}} #TypingSpeed #TouchTyping",
                "facebook_linkedin": f"Level up your keyboard skills! Learn the proven methods behind {kw} and test your speed on GPT-TYPE: {{{{LINK}}}}",
                "telegram": f"🚀 <b>New Article Published:</b> {title}\n\nRead the guide and take the live speed test here: {{{{LINK}}}}"
            }
        }


    def _build_prompt(self, topic):
        primary_kw = topic["primary_keyword"]
        secondaries = ", ".join(topic["secondary_keywords"])
        deep_link = topic["deep_link"]
        cta_text = topic["cta_text"]
        cluster_name = topic["cluster_name"]
        test_mode = topic["target_test_mode"]

        return f"""
You are the Senior Touch-Typing Researcher and Global Content Lead for GPT-TYPE ({BLOG_URL}), the world's premier, next-generation multilingual typing platform and educational web suite.

═══════════════════════════════════════════════════════════════════════════════
OFFICIAL BRAND IDENTITY, MISSION & CORE PILLARS OF GPT-TYPE ({BLOG_URL}):
═══════════════════════════════════════════════════════════════════════════════
MISSION: Make typing practice accessible, useful, and enjoyable for everyone (students, teachers, office workers, writers, freelancers, job seekers, competitive-exam candidates, and professional typists) without requiring complicated registration or accounts.

THE 4 SIGNATURE PILLARS OF GPT-TYPE:
1. ⚡ Typing Speed Test: Real-time benchmarking tracking WPM, accuracy, errors, characters typed, test duration, and personal bests across custom timed modes (15s, 30s, 60s, custom).
2. 📚 Classic Typing Tutor: Systematic step-by-step curriculum (home-row, finger-placement exercises, individual keys, words, sentences) with dynamic visual keyboard and interactive finger guidance (including authentic Nepali Typeshala with Preeti & Unicode layouts).
3. 🏹 Ramayan Typing Archery Game: Thrilling 5-level retro arcade combat game where typing falling demon arrows defends the sacred Lakshman Rekha against Shurpanakha, Khardushan, Kumbhakaran, Meghnad, and 10-Headed King Raavan.
4. ✏️ Free Form Typing: Frictionless open writing environment with live word and character counters for transcription, copy typing, and keyboard testing.

SIGNATURE PLATFORM CAPABILITIES:
- 🌍 Deep Multilingual Engine: Native support for 122+ languages and regional scripts:
  * South Asian / Indic: Nepali, Hindi, Bengali, Gujarati, Punjabi, Marathi, Tamil, Telugu, Malayalam, Kannada, Odia, Sanskrit.
  * Middle Eastern: Arabic, Persian, Hebrew.
  * Asian: Thai, Vietnamese, Japanese, Chinese, Korean.
  * European / Cyrillic: Russian, Ukrainian, Greek, Spanish, French, German, Italian, Portuguese, Dutch, Polish, etc.
- 🎨 7 Pro Color Themes: Instant zero-lag theme switcher (Dark Slate, Retro Cyberpunk, Nord Frost, Neon Violet, Emerald Code, Sunset Amber, Paper White) to prevent visual fatigue.
- 🔊 7 Procedural Mechanical Switch Sounds (0ms Latency): Real-time Web Audio API sound synthesizer: Mechanical Thock (Holy Panda/Gateron Ink), Crisp Click (Cherry MX Blue), Vintage Typewriter, 8-Bit Arcade Blip, Soft Pop, and Mute Toggle.
- 🔒 Privacy-First Design: 100% client-side in-browser processing, zero keylogging, no signup required, with preferences and scores saved safely in local storage.
- 📈 Monkeytype-Style Telemetry: Second-by-second cubic bezier WPM/accuracy graph with error scatter markers and Rhythm Consistency Score (%).

Your primary mission is to create a 100% GOOGLE ADSENSE & SEARCH ESSENTIALS COMPLIANT article. It must NEVER trigger penalties for thin content, scraped content, or unhelpful AI generation.

TARGET DETAILS:
- Primary Keyword: "{primary_kw}"
- Topical Cluster: {cluster_name}
- Secondary Keywords: {secondaries}
- Target Test Mode: {test_mode}
- Interactive Platform Link: {deep_link}
- CTA Text: {cta_text}

STRICT GOOGLE ADSENSE & MONETIZATION POLICIES TO FOLLOW:
1. VALUABLE INVENTORY (NO THIN CONTENT): Word count MUST be between 1,200 and 1,800 words. Provide deep, educational, step-by-step guidance with real benchmarks, exact finger placement coordinates, ergonomic degree angles, and muscle memory science. Naturally recommend trying GPT-TYPE's 4 core tools (Speed Test, Classic Tutor, Ramayan Archery Game, Free Form Typing), 7 mechanical sound options, or 7 themes to build deliberate practice habits.
2. E-E-A-T (EXPERIENCE, EXPERTISE, AUTHORITATIVENESS, TRUST): Write in an authoritative, encouraging human educator voice. Never sound robotic or generic. Avoid cliché AI openings like "In today's fast-paced digital world...".
3. CLEAN PERMALINK TITLE: The title must be clean, punchy (50-60 chars), and contain NO colons (:), NO question marks (?), NO quotes, and NO emojis. (Clean alphanumeric titles ensure Blogger generates a beautiful, SEO-friendly permalink).
4. SEARCH DESCRIPTION: Provide a crisp, high-CTR 145-155 character Search Description for search engine snippet display.
5. STANDARDIZED BLOGGER LABELS: Provide 3 to 4 clean, capitalized, high-CPC labels (e.g., "Typing Tutorials", "WPM Benchmarks", "GPT-TYPE", "Exam Preparation").
6. 100% AUTHENTIC HUMAN VOICE (STRICTLY NO BOT / ROBOT / AUTOMATION TALK):
   - ABSOLUTELY NEVER mention words like "AI", "Agent", "24/7 Agent", "Autonomous", "Auto-publisher", "Bot", "Robot", "Automated system", or similar phrases anywhere in the article, titles, captions, or social media posts!
   - Write EVERYTHING as if it is written by a real, passionate human educator, typing coach, or the human software creator behind GPT-TYPE sharing genuine lessons and tools with their community.
   - For LinkedIn: Write thoughtfully as an authentic human developer/creator sharing genuine productivity insights (e.g. "We just published a breakdown on how to build keyboard muscle memory...", "Here are 3 subtle habits that helped our learners break the 80 WPM barrier...").
   - For Telegram: Write an engaging, friendly community update with key takeaways and the practice link.

OUTPUT FORMAT:
Respond ONLY with a valid JSON object (no extra commentary, valid JSON):
{{
  "title": "Clean Title Without Colons Or Emojis (e.g. How To Type 100 WPM Consistently And Accurately)",
  "meta_description": "Search description between 145 and 155 characters that summarizes the post and drives clicks.",
  "labels": ["Typing Tutorials", "Speed Drills", "GPT-TYPE", "{cluster_name}"],
  "html_content": "Full HTML body strictly adhering to formatting specifications below",
  "social_posts": {{
    "twitter": "Clean tweet with hook, bullet takeaways, relevant hashtags, and link placeholder {{LINK}}",
    "facebook": "Engaging community post with key insight and link placeholder {{LINK}}",
    "instagram": "Engaging visual caption with typing tip, call to action, and 10 relevant hashtags (link in bio / {{LINK}})",
    "linkedin": "Professional educational post with actionable career/coding typing advice and link placeholder {{LINK}}",
    "reddit": {{
      "title": "Community-friendly discussion title for Reddit (e.g. Tips to overcome typing speed plateau)",
      "body": "Helpful markdown post for Reddit sharing advice and linking to the practice test: {{LINK}}"
    }},
    "telegram": "Formatted announcement with bold title, key points, and link placeholder {{LINK}}"
  }}
}}


HTML BODY FORMATTING SPECIFICATIONS:
1. Executive Summary Box (Top of article):
   Start immediately with a search-description callout box for Google Featured Snippets:
   <div style="background: #f1f5f9; border-left: 5px solid #0ea5e9; padding: 18px 22px; border-radius: 6px; margin-bottom: 25px; color: #1e293b; font-size: 1.05rem; line-height: 1.6;">
     <strong>Quick Summary:</strong> [Direct, actionable 2-3 sentence answer explaining the core takeaway of {primary_kw}]
   </div>

2. Structured Educational Subheadings:
   - Use semantic <h2> and <h3> tags.
   - Include comparison <table> elements (e.g., WPM tiers, finger allocation charts, or exam standards) with inline styling.
   - Use numbered lists (<ol>) and bullet points (<ul>).

3. Embedded Interactive Practice Drill Card:
   <div style="background: #1e293b; color: #f8fafc; border-radius: 12px; padding: 24px; margin: 35px 0; border: 1px solid #334155; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
     <h3 style="color: #38bdf8; margin-top: 0; font-size: 1.3rem;">Interactive Speed Drill for {primary_kw.title()}</h3>
     <p style="color: #cbd5e1; font-size: 0.95rem;">Practice typing the target passage below directly into <strong>GPT-TYPE</strong> to test your real-time muscle memory:</p>
     <div style="background: #0f172a; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 1.05rem; color: #a5f3fc; line-height: 1.6; margin: 15px 0; border-left: 4px solid #38bdf8;">
       [Provide a 60-80 word engaging practice text snippet relevant to the article topic]
     </div>
     <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 18px;">
       <span style="background: #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">Target Speed: 70+ WPM</span>
       <span style="background: #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">Target Accuracy: 98%+</span>
       <span style="background: #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem;">Test Mode: {test_mode}</span>
     </div>
     <a href="{deep_link}" style="display: inline-block; background: linear-gradient(135deg, #0ea5e9, #6366f1); color: #ffffff; text-decoration: none; font-weight: 700; padding: 14px 28px; border-radius: 8px; font-size: 1.05rem; box-shadow: 0 4px 10px rgba(14, 165, 233, 0.4);">{cta_text}</a>
   </div>

4. In-Body FAQ Section & Schema.org JSON-LD:
   - Provide 3 to 4 detailed FAQs under <h2>Frequently Asked Questions</h2>.
   - At the bottom, include a valid Schema.org "FAQPage" <script type="application/ld+json">.

5. Editorial Transparency & Community Feedback (E-E-A-T):
   End with a professional note linking to the official contact form:
   <div style="margin-top: 40px; padding: 20px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; font-size: 0.9rem; color: #64748b;">
     <strong>About the GPT-TYPE Research Team:</strong> Published by the educators and developers behind GPT-TYPE. We build accessible, privacy-friendly typing speed tests, classic typing tutors, and multilingual drills across 122+ languages with zero registration required. Have feedback or want to request a new language? Reach us via our <a href="https://docs.google.com/forms/d/e/1FAIpQLSfm_Aj4LAzlewK3C-cJ6e8SPoUofwsonO-qRpwXP0nR0y_luw/viewform?usp=header" style="color: #0ea5e9; text-decoration: underline;" target="_blank" rel="noopener">Official Feedback Form</a>.
   </div>

"""


    def _call_gemini(self, prompt):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json"
            }
        }

        models_to_try = [
            "gemini-flash-lite-latest",
            "gemini-flash-latest",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite"
        ]

        last_error = ""
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=90)
                if response.status_code == 200:
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    last_error = f"{model} returned {response.status_code}: {response.text}"
                    logger.warning(last_error)
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Error calling {model}: {e}")

        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


    def _parse_json_response(self, text):
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        # 1. Direct JSON parse with strict=False (allows unescaped control characters)
        try:
            return json.loads(cleaned, strict=False)
        except json.JSONDecodeError:
            pass

        # 2. Extract outermost JSON object
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group(0), strict=False)
            except json.JSONDecodeError:
                pass

        # 3. Robust Regex Fallback Parser for long HTML articles
        logger.warning("Standard JSON parsing encountered delimiter error. Using resilient regex field recovery...")
        fallback = {}

        title_m = re.search(r'"title"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
        if title_m:
            try:
                fallback["title"] = title_m.group(1).encode().decode('unicode-escape', errors='replace')
            except Exception:
                fallback["title"] = title_m.group(1)
        else:
            fallback["title"] = "Mastering Touch Typing Speed And Accuracy"

        desc_m = re.search(r'"meta_description"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
        if desc_m:
            try:
                fallback["meta_description"] = desc_m.group(1).encode().decode('unicode-escape', errors='replace')
            except Exception:
                fallback["meta_description"] = desc_m.group(1)
        else:
            fallback["meta_description"] = "Comprehensive guide to mastering touch typing on GPT-TYPE."

        labels_m = re.search(r'"labels"\s*:\s*\[(.*?)\]', cleaned, re.DOTALL)
        if labels_m:
            labels_raw = labels_m.group(1)
            fallback["labels"] = [l.strip().strip('"').strip("'") for l in labels_raw.split(",") if l.strip()]
        else:
            fallback["labels"] = ["Typing Tutorials", "GPT-TYPE", "Touch Typing"]

        # Extract html_content
        html_m = re.search(r'"html_content"\s*:\s*"([\s\S]*?)(?:",\s*"(?:social_posts|social)"|\s*\}\s*$)', cleaned)
        if html_m:
            raw_html = html_m.group(1)
            raw_html = raw_html.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t').replace('\\/', '/')
            fallback["html_content"] = raw_html
        else:
            fallback["html_content"] = f"<p>{cleaned[:1000]}</p>"

        # Extract social_posts block
        social_m = re.search(r'"social_posts"\s*:\s*(\{[\s\S]*?\})', cleaned)
        if social_m:
            try:
                fallback["social_posts"] = json.loads(social_m.group(1), strict=False)
            except Exception:
                fallback["social_posts"] = {}
        else:
            fallback["social_posts"] = {}

        return fallback
