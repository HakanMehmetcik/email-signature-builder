# ✉️ Premium Email Signature Builder

[![Live Demo](https://img.shields.io/badge/Live%20Demo-email--signature--builder.onrender.com-2563EB?style=for-the-badge&logo=render&logoColor=white)](https://email-signature-builder.onrender.com)

> 🚀 **Deployed and ready to use → [email-signature-builder.onrender.com](https://email-signature-builder.onrender.com)**

A modern, production-ready email signature builder for academics and professionals — built with Python + Gradio. Generate email-client-safe HTML signatures with live preview, DOI auto-citation, BibTeX parsing, Google Scholar integration, and multi-logo support.

---

## ✨ Features

### Identity & Contact
- Full Name · Title on one line
- Department · Organization on one line
- Website, Email, Phone with inline SVG icons
- Address with map-pin icon
- NameCoach "Hear my name" pill button

### Branding & Logos
- Upload up to **3 logos** (Primary / Secondary / Tertiary)
- Placement: Left Stack · Right Micro · Top Row
- Adjustable logo height (40–130 px)
- Transparent PNG support (white background forced)

### Social & Academic Profiles
- LinkedIn, X/Twitter, GitHub, TikTok
- ORCID, ResearchGate, Mastodon, Bluesky
- Google Scholar
- Text links **or** inline monochrome SVG icons

### Publication Ingestion
| Source | How |
|--------|-----|
| **DOI → APA** | Paste DOIs → CrossRef API → formatted citation + link |
| **Google Scholar** | Paste profile URL → `scholarly` library fetches latest papers |
| **BibTeX** | Paste raw BibTeX → parsed & converted to APA |
| **Manual** | One citation per line |

### Theme Presets
| Theme | Font | Accent |
|-------|------|--------|
| Minimalist Academic | Inter | Blue `#2563EB` |
| Corporate Clean | Inter | Navy `#0C2340` |
| Modern Accent | Inter | Violet `#7C3AED` |
| Institutional Serif | Georgia | Crimson `#7f1d1d` |

Font family, size scale (S/M/L), line height, and accent color are all overridable per session.

### Output
- **Live preview** — updates on every keystroke
- **Copy as Rich Text** — pastes rendered into Gmail / Outlook
- **Copy Raw HTML** — for email client signature settings panels
- **📱 Mobile preview** — 420 px narrow view; logo moves to bottom

---

## 🚀 Run locally

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/email-signature-builder.git
cd email-signature-builder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start
python app.py
```

Open **http://localhost:7860** in your browser.

---

## 🌐 Deploy on Render.com

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New Web Service**.
3. Connect your GitHub repo.
4. Render auto-detects `render.yaml` — click **Deploy**.

The `render.yaml` sets:
- **Build:** `pip install -r requirements.txt`
- **Start:** `python app.py`
- **Port:** `7860`

> **Free tier note:** Render free instances spin down after 15 min of inactivity. The first request after sleep takes ~30 s to wake up.

---

## 🛠 Tech stack

| Layer | Library |
|-------|---------|
| UI | [Gradio](https://www.gradio.app) 6.x |
| Scholar fetch | [scholarly](https://scholarly.readthedocs.io) |
| DOI metadata | [CrossRef REST API](https://api.crossref.org) |
| HTTP | requests |
| Logo encoding | base64 (stdlib) |

---

## 📄 License

MIT — free to use, modify, and deploy.
