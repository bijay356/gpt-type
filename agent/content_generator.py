import json
import logging
import re
import time
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
            parsed = self._generate_mock_article(topic)
        else:
            prompt = self._build_prompt(topic)
            try:
                raw_response = self._call_gemini(prompt)
                parsed = self._parse_json_response(raw_response)
            except Exception as e:
                logger.warning(f"AI generation encountered an error after all retries ({e}). Using high-depth structured article generator.")
                parsed = self._generate_mock_article(topic)

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
        kw_title = kw.title()
        clean_title = re.sub(r'[:?"\'`<>*|#]', '', f"{kw_title} Complete Guide And Speed Benchmarks").strip()
        secondaries = topic.get("secondary_keywords", ["touch typing speed", "typing accuracy", "WPM test", "keyboard ergonomics"])
        sec_str = ", ".join(secondaries[:4])
        cluster_name = topic.get("cluster_name", "Typing Tutorials")
        test_mode = topic.get("target_test_mode", "60s Speed Test")
        deep_link = topic.get("deep_link", BLOG_URL)
        cta_text = topic.get("cta_text", "Take the Live Typing Test on GPT-TYPE")

        meta_desc = f"Master {kw} with proven finger placement techniques, WPM benchmarks, and interactive drills on GPT-TYPE. Boost speed and accuracy today."[:154]

        html_content = f"""<div style="background: #1e293b; border-left: 5px solid #0ea5e9; border: 1px solid #334155; padding: 18px 22px; border-radius: 8px; margin-bottom: 25px; color: #f8fafc; font-size: 1.05rem; line-height: 1.7;">
  <strong style="color: #38bdf8;">Quick Summary:</strong> Mastering <strong style="color: #ffffff;">{kw}</strong> requires prioritizing 98%+ keystroke accuracy before pushing raw velocity, maintaining a neutral 15-degree wrist angle on the home row, and practicing consistent rhythm bursts using interactive telemetry on GPT-TYPE.
</div>

<div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 18px 22px; margin: 25px 0; color: #f8fafc;">
  <strong style="color: #38bdf8; font-size: 1.15rem; display: block; margin-bottom: 10px;">📑 Table of Contents</strong>
  <ul style="margin: 0; padding-left: 20px; color: #94a3b8; line-height: 1.8; font-size: 0.95rem;">
    <li><a href="#fundamentals" style="color: #38bdf8; text-decoration: underline;">1. The Core Biomechanics of {kw_title}</a></li>
    <li><a href="#benchmarks" style="color: #38bdf8; text-decoration: underline;">2. Global WPM &amp; Accuracy Benchmarks</a></li>
    <li><a href="#technique" style="color: #38bdf8; text-decoration: underline;">3. Step-by-Step Technique &amp; Finger Placement</a></li>
    <li><a href="#practice-drill" style="color: #38bdf8; text-decoration: underline;">4. Interactive Speed Drill for {kw_title}</a></li>
    <li><a href="#faq" style="color: #38bdf8; text-decoration: underline;">5. Frequently Asked Questions</a></li>
  </ul>
</div>

<h2 id="fundamentals" style="color: #38bdf8; margin-top: 35px; font-weight: 700;">1. The Core Biomechanics of {kw_title}</h2>
<p style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; margin-bottom: 20px;">Whether you are preparing for competitive typing assessments, writing software code, or handling high-volume documentation, understanding the mechanics behind <strong style="color: #ffffff;">{kw}</strong> separates casual keyboard users from elite touch typists. Most learners hit a speed ceiling because they rely on visual confirmation—glancing down at the keycaps—or type in erratic bursts followed by hesitation.</p>
<p style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; margin-bottom: 20px;">True fluency comes from procedural muscle memory stored in the motor cortex. When you train systematically across related areas like {sec_str}, your fingers begin executing whole n-grams and common syllables as a single fluid motion rather than isolated letter lookups. On <strong style="color: #38bdf8;">GPT-TYPE</strong>, you can reinforce this neural pathway using five dedicated practice modes: the real-time Typing Speed Test, the step-by-step Classic Typing Tutor, the Multilingual Typing Car Racing Game, the progressive Ramayan Typing Archery Game, and Free Form Typing.</p>

<h2 id="benchmarks" style="color: #38bdf8; margin-top: 35px; font-weight: 700;">2. Global WPM &amp; Accuracy Benchmarks</h2>
<p style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; margin-bottom: 20px;">Before adjusting your daily routine, compare your current metrics against standardized performance tiers. Every uncalibrated error costs roughly 1.5 to 2.2 seconds when factoring in mental detection, reaching for the Backspace key, and re-typing the character.</p>

<table style="width: 100%; border-collapse: collapse; margin: 25px 0; background: #0f172a; color: #f8fafc; border-radius: 8px; overflow: hidden; border: 1px solid #334155; font-size: 0.95rem;">
  <thead>
    <tr style="background: #0ea5e9; color: #ffffff;">
      <th style="padding: 12px; text-align: left; border: 1px solid #334155; color: #ffffff; font-weight: 700;">Skill Tier</th>
      <th style="padding: 12px; text-align: left; border: 1px solid #334155; color: #ffffff; font-weight: 700;">Net Speed (WPM)</th>
      <th style="padding: 12px; text-align: left; border: 1px solid #334155; color: #ffffff; font-weight: 700;">Minimum Accuracy</th>
      <th style="padding: 12px; text-align: left; border: 1px solid #334155; color: #ffffff; font-weight: 700;">Recommended GPT-TYPE Mode</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background: #1e293b;">
      <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc; font-weight: 600;">Foundation Builder</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #38bdf8;">25 – 40 WPM</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #4ade80;">94% – 96%</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc;">Classic Typing Tutor (Home Row)</td>
    </tr>
    <tr style="background: #0f172a;">
      <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc; font-weight: 600;">Proficient Professional</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #38bdf8;">45 – 65 WPM</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #4ade80;">97% – 98%</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc;">60s Speed Test &amp; Car Racing Game</td>
    </tr>
    <tr style="background: #1e293b;">
      <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc; font-weight: 600;">Advanced Specialist</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #38bdf8;">70 – 95 WPM</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #4ade80;">98.5%+</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc;">Ramayan Archery Progressive Mode</td>
    </tr>
    <tr style="background: #0f172a;">
      <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc; font-weight: 600;">Competitive Master</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #38bdf8;">100 – 140+ WPM</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #4ade80;">99.2%+</td>
      <td style="padding: 12px; border: 1px solid #334155; color: #f8fafc;">Custom Telemetry &amp; Free Form Drills</td>
    </tr>
  </tbody>
</table>

<h2 id="technique" style="color: #38bdf8; margin-top: 35px; font-weight: 700;">3. Step-by-Step Technique &amp; Finger Placement</h2>
<p style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; margin-bottom: 20px;">To build sustainable speed in <strong style="color: #ffffff;">{kw}</strong>, apply these four ergonomic and cognitive habits during every practice session:</p>
<ul style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; margin-bottom: 20px;">
  <li><strong style="color: #ffffff;">Anchor on the Tactile Home Row:</strong> Rest your left index finger on <code style="color: #38bdf8;">F</code> and your right index finger on <code style="color: #38bdf8;">J</code>. Return immediately to the home row after every top-row or bottom-row reach to minimize travel distance.</li>
  <li><strong style="color: #ffffff;">Maintain a Floating Wrist Posture:</strong> Keep your elbows at a 90-to-100-degree open angle and hover your wrists slightly above the desk surface. Resting heavy weight on the base of the palm compresses the carpal tunnel and restricts pinky reach.</li>
  <li><strong style="color: #ffffff;">Read 2 to 3 Words Ahead:</strong> Train your eyes to scan the upcoming word group rather than staring at the character currently being struck. This look-ahead buffer eliminates micro-pauses between words.</li>
  <li><strong style="color: #ffffff;">Use Acoustic &amp; Visual Feedback:</strong> Enable GPT-TYPE's zero-latency mechanical switch synthesizer (such as Mechanical Thock or Crisp Click) and choose a high-contrast theme like Dark Slate or Emerald Code to lock in a metronome-like typing cadence.</li>
</ul>

<div id="practice-drill" style="background: #1e293b; color: #f8fafc; border-radius: 12px; padding: 24px; margin: 35px 0; border: 1px solid #334155; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  <h3 style="color: #38bdf8; margin-top: 0; font-size: 1.3rem;">Interactive Speed Drill for {kw_title}</h3>
  <p style="color: #cbd5e1; font-size: 0.95rem;">Practice typing the target passage below directly into <strong>GPT-TYPE</strong> to test your real-time muscle memory:</p>
  <div style="background: #0f172a; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 1.05rem; color: #a5f3fc; line-height: 1.6; margin: 15px 0; border-left: 4px solid #38bdf8;">
    Consistent rhythm always beats frantic bursts when building keyboard mastery. Keep your fingers curved gently over the home row keys, relax your shoulders, and let each keystroke flow into the next with steady precision. When you prioritize clean accuracy above ninety-eight percent, raw speed follows naturally without finger fatigue.
  </div>
  <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 18px;">
    <span style="background: #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; color: #f8fafc;">Target Speed: 70+ WPM</span>
    <span style="background: #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; color: #f8fafc;">Target Accuracy: 98%+</span>
    <span style="background: #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; color: #f8fafc;">Test Mode: {test_mode}</span>
  </div>
  <a href="{deep_link}" style="display: inline-block; background: linear-gradient(135deg, #0ea5e9, #6366f1); color: #ffffff; text-decoration: none; font-weight: 700; padding: 14px 28px; border-radius: 8px; font-size: 1.05rem; box-shadow: 0 4px 10px rgba(14, 165, 233, 0.4);">{cta_text}</a>
</div>

<h2 id="faq" style="color: #38bdf8; margin-top: 35px; font-weight: 700;">5. Frequently Asked Questions</h2>
<h3 style="color: #ffffff; margin-top: 25px; font-weight: 700;">How long does it take to improve {kw}?</h3>
<p style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; margin-bottom: 20px;">With 15 to 20 minutes of deliberate daily practice on GPT-TYPE, most typists gain 12 to 20 WPM within two to three weeks while cutting their error rate in half.</p>

<h3 style="color: #ffffff; margin-top: 25px; font-weight: 700;">Should I focus on speed or accuracy first?</h3>
<p style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; margin-bottom: 20px;">Always lock in 98% or higher accuracy first. Practicing fast with frequent typos trains incorrect neuromuscular patterns that must later be unlearned.</p>

<h3 style="color: #ffffff; margin-top: 25px; font-weight: 700;">Which GPT-TYPE tools help overcome a speed plateau?</h3>
<p style="line-height: 1.8; color: #e2e8f0; font-size: 1.05rem; margin-bottom: 20px;">Combine a 60-second benchmark in the Typing Speed Test with the Multilingual Car Racing Game and the Ramayan Typing Archery Game to build both steady rhythm and high-pressure reflex speed.</p>

<div style="margin-top: 40px; padding: 20px; background: #1e293b; border-radius: 8px; border: 1px solid #334155; font-size: 0.95rem; color: #94a3b8; line-height: 1.6;">
  <strong style="color: #38bdf8;">About the GPT-TYPE Research Team:</strong> Published by the educators and developers behind GPT-TYPE. We build accessible, privacy-friendly typing speed tests, classic typing tutors, dynamic car racing games, and multilingual drills across 122+ languages with zero registration required. Have feedback or want to request a new language? Reach us via our <a href="https://docs.google.com/forms/d/e/1FAIpQLSfm_Aj4LAzlewK3C-cJ6e8SPoUofwsonO-qRpwXP0nR0y_luw/viewform?usp=header" style="color: #38bdf8; text-decoration: underline;" target="_blank" rel="noopener">Official Feedback Form</a>.
</div>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "How long does it take to improve {kw}?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "With 15 to 20 minutes of deliberate daily practice on GPT-TYPE, most typists gain 12 to 20 WPM within two to three weeks while cutting their error rate in half."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Should I focus on speed or accuracy first?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Always lock in 98% or higher accuracy first. Practicing fast with frequent typos trains incorrect neuromuscular patterns that must later be unlearned."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Which GPT-TYPE tools help overcome a speed plateau?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Combine a 60-second benchmark in the Typing Speed Test with the Multilingual Car Racing Game and the Ramayan Typing Archery Game to build both steady rhythm and high-pressure reflex speed."
      }}
    }}
  ]
}}
</script>"""

        return {
            "title": clean_title,
            "meta_description": meta_desc,
            "labels": ["Typing Tutorials", "WPM Benchmarks", "GPT-TYPE", cluster_name][:4],
            "html_content": html_content,
            "social_posts": {
                "twitter": f"Want to master {kw}? Check out our new breakdown + interactive drill 🚀\n• Keep 98%+ accuracy\n• Lock in steady rhythm\n• Benchmark live: {{{{LINK}}}} #TypingSpeed #TouchTyping #GPTTYPE",
                "facebook": f"Level up your keyboard skills! We just published a complete guide on {kw} with practical posture tips and an interactive drill. Test your WPM live on GPT-TYPE: {{{{LINK}}}}",
                "instagram": f"Master {kw} with smooth rhythm and 98%+ accuracy! ⚡ Practice our latest speed drill live on GPT-TYPE: {{{{LINK}}}} #TypingSpeed #TouchTyping #KeyboardSkills #Productivity #LearnToType",
                "linkedin": f"We just published a practical breakdown on {kw}.\n\nOne of the biggest misconceptions in keyboard training is trying to force raw finger speed before stabilizing rhythm and accuracy. By keeping accuracy above 98% and reading 2 words ahead, you eliminate costly backspace pauses.\n\nRead the full guide and test your live telemetry here: {{{{LINK}}}}",
                "reddit": {
                    "title": f"Practical guide and drills for {kw}",
                    "body": f"Here is a breakdown of the biomechanics, WPM benchmarks, and daily drills for {kw}: {{{{LINK}}}}"
                },
                "telegram": f"🚀 <b>{clean_title}</b>\n\n• Prioritize 98%+ accuracy before raw speed bursts\n• Anchor on the home row and read 2-3 words ahead\n• Includes a live practice drill &amp; benchmark table\n\n👉 Read &amp; practice here: {{{{LINK}}}}"
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

        headers = {"Content-Type": "application/json"}

        models_to_try = [
            "gemini-3.6-flash",
            "gemini-3.1-flash-lite",
            "gemini-3-flash-preview",
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite",
            "gemini-flash-latest",
            "gemini-flash-lite-latest",
            "gemma-4-26b-a4b-it"
        ]

        # Dynamically append any newer Gemini Flash models discovered from the API
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
            r_list = requests.get(list_url, timeout=15)
            if r_list.status_code == 200:
                for m in r_list.json().get("models", []):
                    m_name = m.get("name", "").replace("models/", "")
                    methods = m.get("supportedGenerationMethods", [])
                    if "generateContent" in methods and ("flash" in m_name or "gemma-4" in m_name):
                        if m_name not in models_to_try and "tts" not in m_name and "image" not in m_name and "audio" not in m_name:
                            models_to_try.append(m_name)
        except Exception as e:
            logger.debug(f"Dynamic model list lookup skipped: {e}")

        last_error = ""
        for attempt in range(2):
            for model in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                gen_config = {
                    "temperature": 0.7,
                    "topP": 0.95,
                    "maxOutputTokens": 8192,
                }
                # Gemma models do not support responseMimeType="application/json"
                if not model.startswith("gemma"):
                    gen_config["responseMimeType"] = "application/json"

                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": gen_config
                }
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=90)
                    if response.status_code == 200:
                        data = response.json()
                        text_out = data["candidates"][0]["content"]["parts"][0]["text"]
                        logger.info(f"Successfully generated content using model: {model}")
                        return text_out
                    else:
                        last_error = f"{model} returned {response.status_code}: {response.text[:300]}"
                        logger.warning(last_error)
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Error calling {model}: {e}")

            if attempt == 0:
                logger.info("Retrying model cascade after 5s cooldown...")
                time.sleep(5)

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
