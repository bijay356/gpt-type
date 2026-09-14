# 📜 GPT-TYPE Official Publishing & Editorial Quality Standards

This document defines the **unbreakable quality, formatting, design, and editorial rules** for all articles, social posts, and community updates published across **GPT-TYPE** (https://gpttype.blogspot.com).

Both the AI prompt directives (`agent/content_generator.py`) and the Python post-processing engine (`_enforce_quality_rules()` and `_enforce_human_voice()`) enforce these rules programmatically.

---

## 1. 🛡️ 100% Authentic Human Editorial Voice (Strict Zero-Bot Policy)

> **CRITICAL RULE**: The audience and search engines must always experience GPT-TYPE content as written by real, passionate educators and engineers.

- **Strictly Prohibited Words & Phrases**:
  - ❌ `"AI"`, `"Artificial Intelligence"`
  - ❌ `"Agent"`, `"24/7 Agent"`, `"24/7 Autonomous Agent"`
  - ❌ `"Autonomous"`, `"Auto-publisher"`, `"Auto publisher"`
  - ❌ `"Bot"`, `"Robot"`, `"Automated system"`
  - ❌ Cliché AI openers like *"In today's fast-paced digital world..."* or *"As an AI language model..."*
- **Approved Editorial Persona**:
  - Written as the **GPT-TYPE Research & Development Team**, typing coaches, educators, and software engineers.
  - Perspective: First-person plural (*"we built"*, *"in our typing lab"*, *"we recommend"*) or encouraging second-person (*"when you practice"*).
  - Tone: Knowledgeable, practical, motivating, and authoritative (E-E-A-T compliant).

---

## 2. 📑 Interactive Table of Contents (TOC) Standard

Every published guide must include a jump-to **Table of Contents** directly beneath the Executive Summary callout box:

1. **Visual Styling**:
   - Container: `#1e293b` dark background, `#334155` subtle border, 8px border radius, 18px-22px padding.
   - Header: `📑 Table of Contents` in bold `#38bdf8` (sky blue).
   - Links: Clean unordered list (`<ul>`) with `#38bdf8` color and underline.
2. **Anchor Link Integrity**:
   - Each TOC link (`<a href="#section-X">`) must map directly to an `<h2 id="section-X">` heading.
   - Programmatic Safeguard: Even if the LLM omits the TOC or anchor IDs, `_enforce_quality_rules()` scans all `<h2>` tags, assigns anchor IDs, and injects the TOC box automatically.

---

## 3. 📊 High-Contrast Dark Table Styling Standard

> **CRITICAL RULE**: Because Blogger's custom template uses a modern dark theme, tables must **never** use default white backgrounds or unstyled cells that result in invisible white-on-white text.

1. **Container Styling (`<table>`)**:
   `<table style="width: 100%; border-collapse: collapse; margin: 25px 0; background: #0f172a; color: #f8fafc; border-radius: 8px; overflow: hidden; border: 1px solid #334155; font-size: 0.95rem;">`
2. **Header Styling (`<th>`)**:
   - Background: Vibrant `#0ea5e9` (sky blue).
   - Text color: Explicit `#ffffff` (pure white, bold 700).
   - Border: `1px solid #334155`.
3. **Alternating Row Styling (`<tr>` & `<td>`)**:
   - Odd rows: Background `#1e293b`.
   - Even rows: Background `#0f172a`.
   - Data cells: Explicit `color: #f8fafc;` with `1px solid #334155` border.
4. **Programmatic Safeguard**:
   - `_enforce_quality_rules()` regex-parses all `<table>` elements, strips any white background overrides, and enforces the full high-contrast styling suite prior to publication.

---

## 3.1 🔆 Strict High-Contrast Dark-Theme Typography (Never Dark-on-Dark Text)

> **CRITICAL RULE**: Because the website template uses a modern dark theme background (`#0b0f19` / `#0f172a`), no text element can ever use dark grey, slate, or black text (`#0f172a`, `#1e293b`, `#334155`, `#475569`, `#64748b`).

1. **Headings (`<h2>`, `<h3>`)**:
   - Must use high-contrast Sky Blue (`color: #38bdf8;`) or Pure White (`color: #ffffff;`).
2. **Body Text (`<p>`, `<li>`, `<span>`)**:
   - Must use high-contrast Crisp Light Slate (`color: #e2e8f0;`) with `line-height: 1.8;`.
3. **Callout & Executive Summary Boxes**:
   - Must use dark containers (`background: #1e293b; border: 1px solid #334155; color: #f8fafc;`).
4. **Programmatic Safeguard**:
   - `_enforce_quality_rules()` automatically inspects all tags in Python, strips any dark colors, enforces high-contrast hex values, and wraps the entire article in a `.gpttype-article-container` with `#e2e8f0` text.

---

## 4. 🎯 Core Brand Pillars & Platform Features

Articles must naturally showcase the signature capabilities of **GPT-TYPE** (https://gpttype.blogspot.com):

| Signature Pillar | Key Features Highlighted |
| :--- | :--- |
| **⚡ Typing Speed Test** | Real-time WPM, accuracy %, errors, characters, 15s/30s/60s/120s modes, Monkeytype-style cubic-bezier speed graph with rhythm consistency. |
| **📚 Classic Typing Tutor** | Step-by-step curriculum (home row, finger placement, top/bottom rows) with authentic **Nepali Typeshala** (Preeti & Unicode layouts) and dynamic finger guidance. |
| **🏹 Ramayan Archery Game** | 5-level retro arcade game typing falling demon arrows to protect the Lakshman Rekha against Shurpanakha, Khardushan, Kumbhakaran, Meghnad, and Raavan. |
| **✏️ Free Form Typing** | Distraction-free open writing canvas with real-time word/character count for transcription and copy-typing drills. |

### Technical Accents to Highlight:
- **🌍 122+ Languages**: South Asian (Nepali, Hindi, Bengali, Tamil, etc.), Middle Eastern (Arabic, Persian, Hebrew), East Asian (Japanese, Chinese, Korean), and European languages.
- **🎨 7 Pro Color Themes**: Dark Slate, Retro Cyberpunk, Nord Frost, Neon Violet, Emerald Code, Sunset Amber, Paper White.
- **🔊 7 Mechanical Switch Sounds**: 0ms latency Web Audio synthesizer (Mechanical Thock, Cherry MX Click, Typewriter, 8-Bit Arcade, Soft Pop, Mute).
- **🔒 Privacy First**: 100% client-side in-browser processing, zero keylogging, no accounts or passwords required.

---

## 5. 🔍 Google AdSense & Search Essentials Compliance

To guarantee high search rankings and AdSense safety:

1. **Valuable Inventory (No Thin Content)**:
   - Articles must contain between **1,200 and 1,800 words** of actionable, original instruction.
   - Must include realistic WPM target tiers, finger placement coordinates, and ergonomic degree angles.
2. **SEO-Friendly Permalinks**:
   - Article title must be clean (50–60 characters).
   - **NO colons (`:`), NO question marks (`?`), NO quotation marks (`"`, `'`), and NO emojis** in titles.
   - When published, Blogger's permalink engine automatically generates a clean, keyword-matched slug directly from the title (e.g., `/2026/09/how-to-type-100-wpm-consistently-and.html`).
3. **Search Description & Rich Snippets**:
   - Every article includes a 145–155 character compelling search description.
   - Because the Blogger API does not expose the internal dashboard "Search Description" field, our engine enforces this directly in the content:
     * **Executive Summary Box**: Placed at the very top so Google's crawler uses it as the SERP featured snippet.
     * **Schema.org JSON-LD**: Embedded at the bottom with `"@type": "BlogPosting"` containing `"description"` and `"headline"` so search engines read the exact meta description.
4. **Structured Data**:
   - Every article includes Schema.org `BlogPosting` and `FAQPage` JSON-LD for rich snippets and question carousels in Google Search.
5. **Interactive Practice Drill Card**:
   - Contains a 60–80 word practice passage, WPM/accuracy targets, and a direct CTA link to practice on `gpttype.blogspot.com`.
6. **E-E-A-T Footer**:
   - Closes with the official GPT-TYPE Research Team note and link to the Official Feedback Form.

---

## 6. 🔄 Multi-Platform Social Syndication Rules

- **Telegram**: Clean announcement with headline, 3 key takeaways, and practice test link.
- **LinkedIn**: Professional educator/engineer perspective discussing typing mechanics, developer ergonomics, or focus habits.
- **Twitter / X**: Catchy hook, actionable tip, relevant hashtags (`#TouchTyping #TypingSpeed #GPTType`).
- **Facebook / Instagram / Reddit**: Community-focused discussions encouraging readers to share their baseline WPM.
