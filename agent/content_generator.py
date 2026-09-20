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

        # Enforce unbreakable quality rules (Table contrast, TOC presence, Human voice, SEO Schema)
        parsed["html_content"] = self._enforce_quality_rules(
            parsed.get("html_content", ""),
            topic,
            meta_description=parsed.get("meta_description", ""),
            title=parsed.get("title", "")
        )
        parsed = self._enforce_human_voice(parsed)

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

THE 5 SIGNATURE PILLARS OF GPT-TYPE:
1. ⚡ Typing Speed Test: Real-time benchmarking tracking WPM, accuracy, errors, characters typed, test duration, and personal bests across custom timed modes (15s, 30s, 60s, custom).
2. 📚 Classic Typing Tutor: Systematic step-by-step curriculum (home-row, finger-placement exercises, individual keys, words, sentences) with dynamic visual keyboard and interactive finger guidance (including authentic Nepali Typeshala with Preeti & Unicode layouts).
3. 🏎️ Multilingual Typing Car Racing Game: Real-time dynamic racing competition across 122+ languages where typing speed and accuracy directly control car acceleration. Fast, flawless typing unleashes turbo acceleration to overtake opponent cars and secure victory, while slow typing or keystroke errors decelerate your car and cause you to fall behind.
4. 🏹 Ramayan Typing Archery Game: Thrilling progressive speed-up arcade challenge where words and falling demon arrows continuously accelerate faster and faster over time—typing words quickly and accurately shoots divine arrows to defend the sacred Lakshman Rekha before the accelerating demons reach the boundary.
5. ✏️ Free Form Typing: Frictionless open writing environment with live word and character counters for transcription, copy typing, and keyboard testing.

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
1. VALUABLE INVENTORY (NO THIN CONTENT): Word count MUST be between 1,200 and 1,800 words. Provide deep, educational, step-by-step guidance with real benchmarks, exact finger placement coordinates, ergonomic degree angles, and muscle memory science. Naturally recommend trying GPT-TYPE's 5 core tools (Speed Test, Classic Tutor, Car Racing Game, Ramayan Archery Game, Free Form Typing), 7 mechanical sound options, or 7 themes to build deliberate practice habits.
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
   Start immediately with a search-description callout box for Google Featured Snippets (Dark Theme):
   <div style="background: #1e293b; border-left: 5px solid #0ea5e9; border: 1px solid #334155; padding: 18px 22px; border-radius: 8px; margin-bottom: 25px; color: #f8fafc; font-size: 1.05rem; line-height: 1.7;">
     <strong style="color: #38bdf8;">Quick Summary:</strong> [Direct, actionable 2-3 sentence answer explaining the core takeaway of {primary_kw}]
   </div>

2. Interactive Table of Contents (TOC Box):
   Include an elegant Table of Contents box right under the Quick Summary:
   <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 18px 22px; margin: 25px 0; color: #f8fafc;">
     <strong style="color: #38bdf8; font-size: 1.15rem; display: block; margin-bottom: 10px;">📑 Table of Contents</strong>
     <ul style="margin: 0; padding-left: 20px; color: #94a3b8; line-height: 1.8; font-size: 0.95rem;">
       [List 4-5 key sections with clean anchor links: <li><a href="#section-id" style="color: #38bdf8; text-decoration: underline;">Section Title</a></li>]
     </ul>
   </div>

3. Strict Dark-Theme Typography & Subheadings:
   - CRITICAL TEXT CONTRAST RULE (NEVER USE DARK TEXT):
     The blog uses a sleek dark theme (#0b0f19 / #0f172a). All text MUST have high contrast:
     * Headings (<h2 id="section-id">, <h3>): MUST use style="color: #38bdf8; margin-top: 35px; font-weight: 700;" or style="color: #ffffff;". NEVER use #0f172a, #1e293b, #334155, or dark colors!
     * Paragraphs (<p>): MUST use style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; margin-bottom: 20px;". NEVER use #334155, #475569, #64748b, or dark grey!
     * Lists (<ul>, <ol>, <li>): MUST use style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem;".
     * Bold text (<strong>): MUST use style="color: #ffffff;" or style="color: #38bdf8;".
   - STRICT TABLE STYLING (CRITICAL: NEVER USE WHITE-ON-WHITE TEXT):
     Every <table> MUST have explicit dark high-contrast styling matching the GPT-TYPE theme:
     <table style="width: 100%; border-collapse: collapse; margin: 25px 0; background: #0f172a; color: #f8fafc; border-radius: 8px; overflow: hidden; border: 1px solid #334155; font-size: 0.95rem;">
       <thead>
         <tr style="background: #0ea5e9; color: #ffffff;">
           <th style="padding: 12px; text-align: left; border: 1px solid #334155; color: #ffffff; font-weight: 700;">Column 1</th>
           <th style="padding: 12px; text-align: left; border: 1px solid #334155; color: #ffffff; font-weight: 700;">Column 2</th>
         </tr>
       </thead>
       <tbody>
         <tr style="background: #1e293b;">
           <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc; font-weight: 600;">Row text</td>
           <td style="padding: 12px; border: 1px solid #334155; color: #38bdf8;">Data value</td>
         </tr>
         <tr style="background: #0f172a;">
           <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc; font-weight: 600;">Row text</td>
           <td style="padding: 12px; border: 1px solid #334155; color: #4ade80;">Data value</td>
         </tr>
       </tbody>
     </table>

4. Embedded Interactive Practice Drill Card:
   <div style="background: #1e293b; color: #f8fafc; border-radius: 12px; padding: 24px; margin: 35px 0; border: 1px solid #334155; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
     <h3 style="color: #38bdf8; margin-top: 0; font-size: 1.3rem;">Interactive Speed Drill for {primary_kw.title()}</h3>
     <p style="color: #cbd5e1; font-size: 0.95rem;">Practice typing the target passage below directly into <strong>GPT-TYPE</strong> to test your real-time muscle memory:</p>
     <div style="background: #0f172a; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 1.05rem; color: #a5f3fc; line-height: 1.6; margin: 15px 0; border-left: 4px solid #38bdf8;">
       [Provide a 60-80 word engaging practice text snippet relevant to the article topic]
     </div>
     <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 18px;">
       <span style="background: #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; color: #f8fafc;">Target Speed: 70+ WPM</span>
       <span style="background: #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; color: #f8fafc;">Target Accuracy: 98%+</span>
       <span style="background: #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; color: #f8fafc;">Test Mode: {test_mode}</span>
     </div>
     <a href="{deep_link}" style="display: inline-block; background: linear-gradient(135deg, #0ea5e9, #6366f1); color: #ffffff; text-decoration: none; font-weight: 700; padding: 14px 28px; border-radius: 8px; font-size: 1.05rem; box-shadow: 0 4px 10px rgba(14, 165, 233, 0.4);">{cta_text}</a>
   </div>

5. In-Body FAQ Section & Schema.org JSON-LD:
   - Provide 3 to 4 detailed FAQs under <h2 id="faq" style="color: #38bdf8;">Frequently Asked Questions</h2>.
   - At the bottom, include a valid Schema.org "FAQPage" <script type="application/ld+json">.

6. Editorial Transparency & Community Feedback (E-E-A-T):
   End with a professional note linking to the official contact form (Dark Theme):
   <div style="margin-top: 40px; padding: 20px; background: #1e293b; border-radius: 8px; border: 1px solid #334155; font-size: 0.95rem; color: #94a3b8; line-height: 1.6;">
      <strong style="color: #38bdf8;">About the GPT-TYPE Research Team:</strong> Published by the educators and developers behind GPT-TYPE. We build accessible, privacy-friendly typing speed tests, classic typing tutors, dynamic car racing games, and multilingual drills across 122+ languages with zero registration required. Have feedback or want to request a new language? Reach us via our <a href="https://docs.google.com/forms/d/e/1FAIpQLSfm_Aj4LAzlewK3C-cJ6e8SPoUofwsonO-qRpwXP0nR0y_luw/viewform?usp=header" style="color: #38bdf8; text-decoration: underline;" target="_blank" rel="noopener">Official Feedback Form</a>.
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

    def _enforce_quality_rules(self, html, topic, meta_description="", title=""):
        """
        Guarantees that every article strictly complies with:
        1. Dark high-contrast styling on all tables (no white-on-white text).
        2. Fully interactive Table of Contents (TOC) with working anchor IDs.
        3. High-contrast dark theme typography across all headings and paragraphs.
        4. Schema.org BlogPosting metadata with explicit search description.
        """
        if not html:
            return html

        # 1. Fix Table Styling: Force dark high-contrast styling and prevent white-on-white text
        def fix_table(match):
            table_html = match.group(0)
            # Remove any light/white backgrounds
            table_html = re.sub(r'background(?:-color)?\s*:\s*(?:#f[0-9a-f]{5}|white|#ffffff);?', '', table_html, flags=re.IGNORECASE)
            
            # Format header th
            table_html = re.sub(
                r'<th[^>]*>',
                '<th style="padding: 12px 14px; text-align: left; border: 1px solid #334155; background: #0ea5e9; color: #ffffff; font-weight: 700;">',
                table_html,
                flags=re.IGNORECASE
            )

            # Format rows and cells
            rows = re.findall(r'<tr[^>]*>[\s\S]*?</tr>', table_html, flags=re.IGNORECASE)
            new_rows = []
            for i, row in enumerate(rows):
                if '<th' in row.lower():
                    row_styled = re.sub(r'<tr[^>]*>', '<tr style="background: #0ea5e9; color: #ffffff;">', row, count=1, flags=re.IGNORECASE)
                    new_rows.append(row_styled)
                    continue

                bg = "#1e293b" if (len(new_rows) % 2 == 1) else "#0f172a"
                row_styled = re.sub(r'<tr[^>]*>', f'<tr style="background: {bg};">', row, count=1, flags=re.IGNORECASE)
                
                # Ensure all <td> have explicit light text color
                row_styled = re.sub(
                    r'<td[^>]*>',
                    '<td style="padding: 12px 14px; border: 1px solid #334155; color: #f8fafc; font-weight: 500;">',
                    row_styled,
                    flags=re.IGNORECASE
                )
                new_rows.append(row_styled)

            if new_rows:
                return f'<table style="width: 100%; border-collapse: collapse; margin: 25px 0; background: #0f172a; color: #f8fafc; border-radius: 8px; overflow: hidden; border: 1px solid #334155; font-size: 0.95rem;">\n{"".join(new_rows)}\n</table>'
            return table_html

        html = re.sub(r'<table[\s\S]*?</table>', fix_table, html, flags=re.IGNORECASE)

        # 2. Enforce Table of Contents (TOC) & Section Anchor IDs
        toc_links = []
        h2_counter = 0

        def process_h2(match):
            nonlocal h2_counter
            h2_counter += 1
            attrs = match.group(1) or ""
            inner = match.group(2)
            clean_heading = re.sub(r'<[^>]+>', '', inner).strip()
            anchor_id = f"section-{h2_counter}"
            
            # Check if an id is already defined
            id_match = re.search(r'id=["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
            if id_match:
                anchor_id = id_match.group(1)
            else:
                attrs = f' id="{anchor_id}"' + attrs

            # Skip adding FAQ or Conclusion to primary TOC if list is already long
            toc_links.append(f'<li><a href="#{anchor_id}" style="color: #38bdf8; text-decoration: underline;">{clean_heading}</a></li>')
            return f'<h2{attrs}>{inner}</h2>'

        # Ensure all h2 tags have IDs and collect headings
        html = re.sub(r'<h2([^>]*)>(.*?)</h2>', process_h2, html, flags=re.IGNORECASE | re.DOTALL)

        # If Table of Contents is not in the HTML, generate and insert it
        if "Table of Contents" not in html and toc_links:
            toc_box = f'''<div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 18px 22px; margin: 25px 0; color: #f8fafc;">
  <strong style="color: #38bdf8; font-size: 1.15rem; display: block; margin-bottom: 12px;">📑 Table of Contents</strong>
  <ul style="margin: 0; padding-left: 20px; color: #94a3b8; line-height: 1.8; font-size: 0.95rem;">
    {"".join(toc_links)}
  </ul>
</div>'''
            if '</div>' in html:
                summary_idx = html.find('</div>') + 6
                html = html[:summary_idx] + '\n' + toc_box + html[summary_idx:]
            else:
                html = toc_box + '\n' + html

        # 3. Enforce Strict High-Contrast Dark-Theme Typography (Never dark-on-dark)
        dark_colors_pattern = re.compile(
            r'color\s*:\s*(?:#0f172a|#1e293b|#334155|#475569|#64748b|#000000|#111827|#1f2937|black|#000)\b',
            re.IGNORECASE
        )

        # Headings (h2, h3): Force high-contrast sky blue #38bdf8
        def fix_heading(match):
            tag = match.group(0)
            tag = dark_colors_pattern.sub('color: #38bdf8', tag)
            if 'color:' not in tag:
                tag = re.sub(r'<(h[23])', r'<\1 style="color: #38bdf8;"', tag, count=1)
            return tag
        html = re.sub(r'<h[23][^>]*>', fix_heading, html, flags=re.IGNORECASE)

        # Paragraphs, lists, spans: Force crisp light slate #e2e8f0
        def fix_text_tag(match):
            tag = match.group(0)
            tag = dark_colors_pattern.sub('color: #e2e8f0', tag)
            return tag
        html = re.sub(r'<(?:p|ul|ol|li|span|strong)[^>]*>', fix_text_tag, html, flags=re.IGNORECASE)

        # Quick summary box: Replace light background with dark slate
        html = re.sub(
            r'background\s*:\s*#f1f5f9;?',
            'background: #1e293b; border: 1px solid #334155;',
            html,
            flags=re.IGNORECASE
        )
        html = re.sub(
            r'(<div[^>]*background:\s*#1e293b[^>]*color:\s*)#1e293b',
            r'\g<1>#f8fafc',
            html,
            flags=re.IGNORECASE
        )

        # Footer box: Replace light background with dark container
        html = re.sub(
            r'background\s*:\s*#f8fafc;?',
            'background: #1e293b; border: 1px solid #334155;',
            html,
            flags=re.IGNORECASE
        )

        # Wrap in high-contrast styling container if not already present
        if 'gpttype-article-container' not in html:
            html = f'<div class="gpttype-article-container" style="color: #e2e8f0; font-size: 1.05rem; line-height: 1.8;">\n{html}\n</div>'

        # 4. Inject Schema.org BlogPosting with explicit Search Description for Google SERP
        if meta_description and '"BlogPosting"' not in html:
            clean_title = re.sub(r'[:?"\'`<>*|#]', '', title).strip() if title else topic.get("primary_keyword", "").title()
            clean_desc = meta_description.replace('"', '\\"')
            deep_link = topic.get("deep_link", BLOG_URL)
            blog_schema = f'''\n<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{clean_title}",
  "description": "{clean_desc}",
  "url": "{deep_link}"
}}
</script>'''
            html = html + blog_schema

        return html

    def _enforce_human_voice(self, parsed):
        """
        Strips any lingering robotic, AI, or automated phrases to guarantee 100% human voice.
        """
        robotic_replacements = [
            (r'24/7 Autonomous Agent', 'GPT-TYPE Team'),
            (r'24/7 Agent Report', 'GPT-TYPE Editorial Update'),
            (r'Autonomous Agent', 'GPT-TYPE Team'),
            (r'Auto-publisher', 'GPT-TYPE'),
            (r'Auto publisher', 'GPT-TYPE'),
            (r'As an AI language model,?', 'In our typing research,'),
            (r'As an AI,?', 'In our typing research,'),
            (r'our AI agent', 'our research team'),
            (r'our automated system', 'our platform'),
            (r'robot', 'coach'),
        ]

        def sanitize_str(text):
            if not isinstance(text, str):
                return text
            for pattern, rep in robotic_replacements:
                text = re.sub(pattern, rep, text, flags=re.IGNORECASE)
            return text

        parsed["title"] = sanitize_str(parsed.get("title", ""))
        parsed["meta_description"] = sanitize_str(parsed.get("meta_description", ""))
        parsed["html_content"] = sanitize_str(parsed.get("html_content", ""))

        if "social_posts" in parsed and isinstance(parsed["social_posts"], dict):
            for platform, post in parsed["social_posts"].items():
                if isinstance(post, str):
                    parsed["social_posts"][platform] = sanitize_str(post)
                elif isinstance(post, dict):
                    parsed["social_posts"][platform] = {k: sanitize_str(v) for k, v in post.items()}

        return parsed
