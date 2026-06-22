import base64
import re
import requests
import gradio as gr

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

THEMES = {
    "Minimalist Academic": {
        "font": "Inter, -apple-system, Arial, Helvetica, sans-serif",
        "name_size": "20px", "sub_size": "12px", "body_size": "11.5px",
        "accent": "#2563EB", "name_color": "#0f172a", "meta_color": "#64748b",
        "link_color": "#2563EB",
        "line_height": "1.0", "row_gap": "6px", "bar_color": "#2563EB",
    },
    "Corporate Clean": {
        "font": "Inter, -apple-system, Arial, Helvetica, sans-serif",
        "name_size": "19px", "sub_size": "12px", "body_size": "11.5px",
        "accent": "#0C2340", "name_color": "#0C2340", "meta_color": "#334155",
        "link_color": "#0C2340",
        "line_height": "1.0", "row_gap": "5px", "bar_color": "#0C2340",
    },
    "Modern Accent": {
        "font": "Inter, -apple-system, Arial, Helvetica, sans-serif",
        "name_size": "21px", "sub_size": "12.5px", "body_size": "12px",
        "accent": "#7C3AED", "name_color": "#1e1b4b", "meta_color": "#6b7280",
        "link_color": "#7C3AED",
        "line_height": "1.0", "row_gap": "7px", "bar_color": "#7C3AED",
    },
    "Institutional Serif": {
        "font": "Georgia, 'Times New Roman', serif",
        "name_size": "20px", "sub_size": "12.5px", "body_size": "12px",
        "accent": "#7f1d1d", "name_color": "#1c1917", "meta_color": "#57534e",
        "link_color": "#7f1d1d",
        "line_height": "1.0", "row_gap": "6px", "bar_color": "#7f1d1d",
    },
}

SOCIAL_BASES = {
    "linkedin":     "https://www.linkedin.com/in/",
    "twitter":      "https://x.com/",
    "github":       "https://github.com/",
    "tiktok":       "https://www.tiktok.com/@",
    "orcid":        "https://orcid.org/",
    "researchgate": "https://www.researchgate.net/profile/",
    "bluesky":      "https://bsky.app/profile/",
    "mastodon":     "",
    "scholar":      "",
}

SOCIAL_LABELS = {
    "linkedin": "LinkedIn", "twitter": "X / Twitter", "github": "GitHub",
    "tiktok": "TikTok", "orcid": "ORCID", "researchgate": "ResearchGate",
    "bluesky": "Bluesky", "mastodon": "Mastodon", "scholar": "Google Scholar",
}

# Compact 16×16 SVG icons, monochrome, color injected at runtime
SVG = {
    "linkedin":     '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="COLOR"><path d="M19 0H5C2.239 0 0 2.239 0 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5V5c0-2.761-2.238-5-5-5zM8 19H5V8h3v11zM6.5 6.732c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zM20 19h-3v-5.604c0-3.368-4-3.113-4 0V19h-3V8h3v1.765c1.396-2.586 7-2.777 7 2.476V19z"/></svg>',
    "twitter":      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="COLOR"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.259 5.631zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
    "github":       '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="COLOR"><path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg>',
    "orcid":        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="COLOR"><path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.016-5.325 5.016h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 3.872-2.862 3.872-3.722 0-2.016-1.284-3.722-3.872-3.722h-2.297z"/></svg>',
    "researchgate": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="COLOR"><path d="M19.586 0c-.818 0-1.508.19-2.073.565-.563.377-.97.936-1.213 1.68a12.193 12.193 0 0 0-.198.876c-.09.478-.09.68-.09.876 0 .197 0 .399.09.874.064.39.128.661.198.876.243.744.65 1.303 1.213 1.68.565.375 1.255.565 2.073.565s1.508-.19 2.073-.565c.563-.377.97-.936 1.213-1.68.07-.215.134-.486.198-.876.09-.475.09-.677.09-.874 0-.197 0-.398-.09-.876a12.62 12.62 0 0 0-.198-.876c-.243-.744-.65-1.303-1.213-1.68C21.094.19 20.404 0 19.586 0zM0 4.568v14.87h5.068v-5.457h2.775c.933 0 1.656.233 2.162.694.507.462.76 1.132.76 2.008v2.755h5.068v-3.254c0-1.18-.315-2.137-.948-2.865-.632-.728-1.526-1.178-2.68-1.348 1.064-.22 1.89-.69 2.476-1.41.586-.72.878-1.625.878-2.717 0-1.637-.564-2.89-1.692-3.757C12.74 5.02 11.2 4.568 9.25 4.568H0zm5.068 3.767h3.705c.728 0 1.286.156 1.672.47.386.313.579.77.579 1.37 0 .598-.193 1.06-.579 1.386-.386.325-.944.487-1.672.487H5.068V8.335z"/></svg>',
    "bluesky":      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="COLOR"><path d="M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479.815 2.736 3.713 3.66 6.383 3.364-.138.022-.276.04-.415.056-3.912.58-7.387 2.005-2.83 7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 7.733 4.308 4.267-4.308 1.172-6.498-2.74-7.078a8.741 8.741 0 0 1-.415-.056c2.67.297 5.568-.628 6.383-3.364.246-.828.624-5.79.624-6.478 0-.69-.139-1.861-.902-2.204-.659-.299-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 12 10.8z"/></svg>',
    "scholar":      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="COLOR"><path d="M5.242 13.769L0 9.5 12 0l12 9.5-5.242 4.269C17.548 12.63 14.978 12 12 12c-2.977 0-5.548.63-6.758 1.769zM12 10a3 3 0 1 0 0 6 3 3 0 0 0 0-6zm0 8c-3.866 0-7 1.79-7 4h14c0-2.21-3.134-4-7-4z"/></svg>',
    "tiktok":       '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="COLOR"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.33 6.33 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34V8.69a8.18 8.18 0 0 0 4.78 1.52V6.75a4.84 4.84 0 0 1-1.01-.06z"/></svg>',
    "mastodon":     '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="COLOR"><path d="M23.268 5.313c-.35-2.578-2.617-4.61-5.228-5.001-3.289-.476-8.034-.476-8.034-.476h-.002s-4.743 0-8.034.476c-2.609.39-4.877 2.422-5.228 5-.325 2.396-.328 4.791 0 7.187.35 2.578 2.617 4.61 5.228 5.001 3.289.476 8.034.476 8.034.476h.002s4.743 0 8.034-.476c2.609-.39 4.877-2.423 5.228-5 .325-2.396.328-4.791 0-7.187zM17.12 8.918v5.53h-2.187V9.09c0-1.127-.475-1.699-1.428-1.699-.947 0-1.428.614-1.428 1.834v2.626H9.89V9.225c0-1.22-.48-1.834-1.428-1.834-.953 0-1.428.572-1.428 1.699v5.358H4.846V8.918c0-1.127.286-2.022.864-2.686.59-.664 1.367-.998 2.337-.998 1.118 0 1.965.43 2.524 1.287l.541.912.542-.912c.56-.857 1.407-1.287 2.524-1.287.97 0 1.747.334 2.337.998.578.664.864 1.559.864 2.686h-.259z"/></svg>',
    # contact field icons
    "email":        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>',
    "website":      '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>',
    "phone":        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 1.27h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.9a16 16 0 0 0 6 6l.91-.91a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
    "address":      '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "namecoach":    '<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>',
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def encode_image(path):
    if not path:
        return None
    with open(path, "rb") as f:
        data = f.read()
    ext = path.split(".")[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def smart_cap(text):
    if not text:
        return text
    skip = {"of", "the", "and", "in", "at", "for", "a", "an", "on", "to", "by", "de", "van", "von"}
    words = text.strip().split()
    return " ".join(
        w[0].upper() + w[1:] if (i == 0 or w.lower() not in skip) else w.lower()
        for i, w in enumerate(words)
    )


def norm_url(handle, platform):
    if not handle:
        return None
    h = handle.strip()
    if h.startswith(("http://", "https://")):
        return h
    if h.startswith("www."):
        return f"https://{h}"
    h = h.lstrip("@")
    base = SOCIAL_BASES.get(platform, "")
    return f"{base}{h}" if base else h


def resolve_doi(doi):
    doi = re.sub(r'^(https?://(?:dx\.)?doi\.org/|doi:)', '', doi.strip())
    try:
        r = requests.get(
            f"https://api.crossref.org/works/{doi}",
            timeout=12,
            headers={"User-Agent": "EmailSigBuilder/2.0 (mailto:user@example.com)"}
        )
        if r.status_code != 200:
            return None
        m = r.json().get("message", {})

        def fmt(a):
            g, f2 = a.get("given", ""), a.get("family", "")
            if f2 and g:
                return f"{f2}, {'. '.join(x[0] for x in g.split())}."
            return f2 or g

        raw_authors = m.get("author", [])
        authors = ", ".join(fmt(a) for a in raw_authors[:6])
        if len(raw_authors) > 6:
            authors += ", et al."

        dp = m.get("published", m.get("published-print", m.get("published-online", {})))
        parts = dp.get("date-parts", [[]])[0] if isinstance(dp, dict) else []
        year = str(parts[0]) if parts else "n.d."

        title = (m.get("title") or [""])[0]
        journal = (m.get("container-title") or [""])[0]
        volume, issue, pages = m.get("volume", ""), m.get("issue", ""), m.get("page", "")

        apa = f"{authors} ({year}). {title}."
        if journal:
            apa += f" <em>{journal}</em>"
            if volume:
                apa += f", <em>{volume}</em>"
                if issue:
                    apa += f"({issue})"
            if pages:
                apa += f", {pages}"
            apa += "."
        url = f"https://doi.org/{doi}"
        apa += f' <a href="{url}" style="color:inherit;word-break:break-all;">{url}</a>'
        return apa
    except Exception:
        return None


def parse_bibtex(bib_text):
    entries = []
    for entry in re.finditer(r'@\w+\{[^,]+,(.*?)\}(?=\s*@|\s*$)', bib_text, re.DOTALL):
        body = entry.group(1)
        f = {}
        for fld in re.finditer(r'(\w+)\s*=\s*[{"](.*?)[}"],?\s*\n', body, re.DOTALL):
            f[fld.group(1).lower()] = fld.group(2).strip().replace("{", "").replace("}", "")
        raw = f.get("author", "")
        parts = [a.strip() for a in re.split(r'\s+and\s+', raw, flags=re.IGNORECASE)] if raw else []

        def bfmt(a):
            if "," in a:
                last, first = a.split(",", 1)
                return f"{last.strip()}, {'. '.join(x[0] for x in first.strip().split() if x)}."
            return a.strip()

        auth_str = (", ".join(bfmt(p) for p in parts[:-1]) + ", & " + bfmt(parts[-1])) if len(parts) > 1 else (bfmt(parts[0]) if parts else "")
        year = f.get("year", "n.d.")
        title = f.get("title", "")
        journal = f.get("journal", f.get("booktitle", ""))
        vol, num, pages = f.get("volume", ""), f.get("number", ""), f.get("pages", "")
        doi = f.get("doi", "")
        url = f.get("url", f"https://doi.org/{doi}" if doi else "")
        apa = f"{auth_str} ({year}). {title}."
        if journal:
            apa += f" <em>{journal}</em>"
            if vol:
                apa += f", <em>{vol}</em>"
                if num:
                    apa += f"({num})"
            if pages:
                apa += f", {pages}"
            apa += "."
        if url:
            apa += f' <a href="{url}" style="color:inherit;word-break:break-all;">{url}</a>'
        entries.append(apa)
    return entries


def fetch_scholar(profile_url, max_n):
    """Fetch publications via the scholarly library (handles Scholar's anti-bot)."""
    try:
        from scholarly import scholarly as _sch

        # Extract user ID from URL or treat the whole string as an ID
        m = re.search(r'user=([A-Za-z0-9_-]+)', profile_url)
        user_id = m.group(1) if m else profile_url.strip()

        author = _sch.search_author_id(user_id)
        author = _sch.fill(author, sections=["publications"])

        pubs = []
        for pub in (author.get("publications") or [])[:int(max_n)]:
            bib     = pub.get("bib", {})
            title   = bib.get("title", "")
            authors = bib.get("author", "")
            year    = bib.get("pub_year", "n.d.")
            venue   = bib.get("venue", bib.get("journal", bib.get("booktitle", "")))
            url     = pub.get("pub_url", "")

            # APA-style: Authors (year). Title. Venue.
            apa = f"{authors} ({year}). {title}."
            if venue:
                apa += f" <em>{venue}</em>."
            if url:
                apa += f' <a href="{url}" style="color:inherit;">[link]</a>'
            pubs.append(apa)

        return pubs
    except Exception as exc:
        return []


# ─────────────────────────────────────────────────────────────────────────────
# SIGNATURE HTML BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def icon_tag(platform, color):
    raw = SVG.get(platform, "")
    return raw.replace("COLOR", color) if raw else ""


def ic(key, color, size=13):
    """Return a vertically-centred inline SVG span at the given size."""
    raw = SVG.get(key, "")
    if not raw:
        return ""
    scaled = raw.replace('width="16"', f'width="{size}"') \
                .replace('height="16"', f'height="{size}"') \
                .replace('width="13"', f'width="{size}"') \
                .replace('height="13"', f'height="{size}"') \
                .replace("COLOR", color)
    return (
        f'<span style="display:inline-block;vertical-align:middle;'
        f'line-height:0;margin-right:4px;">{scaled}</span>'
    )


def build_sig(
    full_name, title_f, dept, faculty, org, phone, email, website, address, namecoach,
    logo1, logo2, logo3, placement, logo_h,
    theme_name, font_ov, size_ov, lh_ov, accent_ov,
    linkedin, twitter, github, tiktok, orcid, researchgate,
    mastodon, bluesky, scholar_handle,
    use_icons, pubs_list,
):
    # ── resolve theme ────────────────────────────────────────────────────────
    th = dict(THEMES.get(theme_name, THEMES["Minimalist Academic"]))
    FONT_MAP = {
        "Arial":   "Arial, Helvetica, sans-serif",
        "Inter":   "Inter, -apple-system, Arial, Helvetica, sans-serif",
        "Georgia": "Georgia, 'Times New Roman', serif",
        "Times":   "'Times New Roman', serif",
    }
    if font_ov and font_ov != "Theme Default":
        th["font"] = FONT_MAP.get(font_ov, th["font"])
    SIZE_D = {"S": (-2, -1, -1), "M": (0, 0, 0), "L": (2, 1, 1)}
    if size_ov and size_ov != "Theme Default":
        d = SIZE_D.get(size_ov, (0, 0, 0))
        for key, idx in [("name_size", 0), ("sub_size", 1), ("body_size", 2)]:
            th[key] = f"{int(th[key].replace('px','')) + d[idx]}px"
    if accent_ov:
        th["accent"] = th["link_color"] = th["bar_color"] = accent_ov

    ac  = th["accent"]
    ff  = th["font"]
    nc  = th["name_color"]
    mc  = th["meta_color"]
    lc  = th["link_color"]
    ns  = th["name_size"]
    ss  = th["sub_size"]
    bs  = th["body_size"]
    gap_px = th["row_gap"]

    full_name = smart_cap(full_name or "")
    title_f   = smart_cap(title_f or "")
    dept      = smart_cap(dept or "")
    faculty   = smart_cap(faculty or "")
    org       = smart_cap(org or "")

    # ── logos — always rendered below the text block ──────────────────────────
    logos = [encode_image(p) for p in [logo1, logo2, logo3] if p]
    h = int(logo_h)

    def logo_img(data):
        return (
            f'<img src="{data}" alt="" '
            f'style="display:block;max-height:{h}px;max-width:{h*4}px;'
            f'width:auto;height:auto;background-color:#ffffff;" />'
        )

    align_map = {"Left": "left", "Center": "center", "Right": "right",
                 "Left Stack": "left", "Right Micro": "right", "Top Row": "center"}
    logo_align = align_map.get(placement, "left")

    bottom_logo_row = ""
    if logos:
        inner = "".join(
            f'<span style="display:inline-block;margin-right:12px;vertical-align:middle;'
            f'line-height:0;">{logo_img(d)}</span>'
            for d in logos
        )
        bottom_logo_row = (
            f'<tr><td style="padding-top:18px;background-color:#ffffff;'
            f'line-height:0;text-align:{logo_align};">{inner}</td></tr>'
        )

    # ── row helper ────────────────────────────────────────────────────────────
    def row(content, pb=None):
        _pb = pb if pb is not None else gap_px
        return (
            f'<tr><td style="padding:0 0 {_pb} 0;line-height:1.0;'
            f'font-family:{ff};">{content}</td></tr>'
        )

    # ── inline icon helper ────────────────────────────────────────────────────
    def icon_inline(key, color, size=12):
        return ic(key, color, size)

    # ── text helpers ──────────────────────────────────────────────────────────
    def txt(text, size, color, weight="400", italic=False, ls="0"):
        s = (f'font-family:{ff};font-size:{size};color:{color};font-weight:{weight};'
             f'letter-spacing:{ls};line-height:1.0;')
        if italic:
            s += "font-style:italic;"
        return f'<span style="{s}">{text}</span>'

    def link(href, text, size, color, icon_key=None, icon_color=None):
        prefix = icon_inline(icon_key, icon_color or color, 12) if icon_key else ""
        return (
            f'<a href="{href}" style="font-family:{ff};font-size:{size};color:{color};'
            f'text-decoration:none;line-height:1.0;vertical-align:middle;display:inline-block;">'
            + prefix
            + f'<span style="vertical-align:middle;">{text}</span></a>'
        )

    # ── separator ─────────────────────────────────────────────────────────────
    dot  = f'<span style="color:#d1d5db;margin:0 5px;font-size:10px;vertical-align:middle;">•</span>'
    pipe = f'<span style="color:#d1d5db;margin:0 7px;font-size:10px;vertical-align:middle;">|</span>'

    rows = []

    # ── 1. FULL NAME  |  TITLE — same size · same color · same weight ─────────
    name_parts = []
    if full_name:
        name_parts.append(txt(full_name, ns, nc, weight="700", ls="-0.3px"))
    if title_f:
        title_size = f"{max(11, int(ns.replace('px','')) - 3)}px"
        name_parts.append(txt(title_f, title_size, mc, weight="400", ls="0"))
    if name_parts:
        hard_pipe = f'<span style="color:#d1d5db;margin:0 9px;font-size:{ns};font-weight:300;vertical-align:middle;">|</span>'
        rows.append(row(hard_pipe.join(name_parts), pb="4px"))

    # ── 2. DEPT  |  FACULTY  |  UNIVERSITY — same size · same color ──────────
    affil_parts = []
    if dept:
        affil_parts.append(txt(dept, ss, ac, weight="600"))
    if faculty:
        affil_parts.append(txt(faculty, ss, ac, weight="600"))
    if org:
        affil_parts.append(txt(org, ss, ac, weight="600"))
    if affil_parts:
        affil_pipe = f'<span style="color:#d1d5db;margin:0 7px;font-size:{ss};font-weight:300;vertical-align:middle;">|</span>'
        rows.append(row(affil_pipe.join(affil_parts), pb="10px"))

    # ── 3. CONTACT ROW: website  |  email  |  phone ──────────────────────────
    contact = []
    if website:
        ws = website if website.startswith("http") else f"https://{website}"
        contact.append(link(ws, website, bs, lc, "website", lc))
    if email:
        contact.append(link(f"mailto:{email}", email, bs, mc, "email", mc))
    if phone:
        contact.append(
            f'<span style="display:inline-block;vertical-align:middle;">'
            + icon_inline("phone", mc, 12)
            + txt(phone, bs, mc)
            + '</span>'
        )
    if contact:
        rows.append(row(pipe.join(contact), pb="5px"))

    # ── 5. ADDRESS ────────────────────────────────────────────────────────────
    if address:
        addr_html = address.replace("\n", " · ")
        rows.append(row(
            f'<span style="display:inline-block;vertical-align:middle;">'
            + icon_inline("address", mc, 12)
            + txt(addr_html, bs, mc)
            + '</span>',
            pb="7px"
        ))

    # ── 6. SOCIAL ROW ─────────────────────────────────────────────────────────
    handles = {
        "linkedin": linkedin, "twitter": twitter, "github": github,
        "tiktok": tiktok, "orcid": orcid, "researchgate": researchgate,
        "mastodon": mastodon, "bluesky": bluesky, "scholar": scholar_handle,
    }
    social_items = []
    for platform, handle in handles.items():
        url = norm_url(handle, platform)
        if not url:
            continue
        label = SOCIAL_LABELS.get(platform, platform.title())
        if use_icons:
            raw_icon = icon_tag(platform, ac)
            if raw_icon:
                social_items.append(
                    f'<a href="{url}" title="{label}" '
                    f'style="text-decoration:none;display:inline-block;'
                    f'vertical-align:middle;margin-right:10px;line-height:0;">'
                    f'{raw_icon}</a>'
                )
                continue
        social_items.append(
            f'<a href="{url}" style="font-family:{ff};font-size:{bs};color:{lc};'
            f'text-decoration:none;line-height:1.0;vertical-align:middle;">{label}</a>'
        )
    if social_items:
        sep = "" if use_icons else pipe
        rows.append(row(sep.join(social_items), pb="7px"))

    # ── 7. NAMECOACH PILL ────────────────────────────────────────────────────
    if namecoach:
        nc_url = namecoach if namecoach.startswith("http") else f"https://{namecoach}"
        rows.append(row(
            f'<a href="{nc_url}" style="display:inline-block;padding:3px 11px 4px 8px;'
            f'background-color:transparent;border:1.5px solid {ac};border-radius:99px;'
            f'text-decoration:none;font-family:{ff};font-size:10.5px;color:{ac};'
            f'font-weight:600;line-height:1.4;white-space:nowrap;vertical-align:middle;">'
            + ic("namecoach", ac, 11).replace('margin-right:4px', 'margin-right:5px')
            + f'<span style="vertical-align:middle;">Hear my name</span></a>',
            pb="7px"
        ))

    # ── 8. PUBLICATIONS ───────────────────────────────────────────────────────
    if pubs_list:
        li_items = "".join(
            f'<li style="margin-bottom:5px;font-family:{ff};font-size:{bs};'
            f'color:{mc};line-height:1.45;">{p}</li>'
            for p in pubs_list
        )
        rows.append(row(
            f'<p style="margin:0 0 5px;font-family:{ff};font-size:{bs};'
            f'font-weight:700;color:{nc};letter-spacing:0.02em;">Selected Publications</p>'
            f'<ul style="margin:0;padding-left:15px;">{li_items}</ul>',
            pb="4px"
        ))

    # ── assemble ──────────────────────────────────────────────────────────────
    content_table = (
        '<table cellpadding="0" cellspacing="0" border="0" '
        'style="border-collapse:collapse;border:none;">'
        + "".join(rows)
        + '</table>'
    )

    body_row = (
        '<tr valign="top">'
        f'<td style="vertical-align:top;padding:2px 0 0;">{content_table}</td>'
        '</tr>'
    )

    return (
        '<table cellpadding="0" cellspacing="0" border="0" '
        'style="border-collapse:collapse;border:none;" id="sig-root">'
        + body_row + bottom_logo_row
        + '</table>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# GRADIO CALLBACKS
# ─────────────────────────────────────────────────────────────────────────────

def cb_doi(doi_text):
    if not doi_text or not doi_text.strip():
        return [], '<span class="st-err">No DOIs entered.</span>'
    results, ok = [], 0
    for doi in [d.strip() for d in doi_text.splitlines() if d.strip()]:
        r = resolve_doi(doi)
        results.append(r if r else f'[Could not resolve: {doi}]')
        if r:
            ok += 1
    return results, f'<span class="st-ok">✅ Resolved {ok}/{len(results)} DOI(s).</span>'


def cb_scholar(url, max_n):
    if not url or not url.strip():
        return [], '<span class="st-err">No URL entered.</span>'
    pubs = fetch_scholar(url.strip(), max_n)
    if pubs:
        return pubs, f'<span class="st-ok">✅ Fetched {len(pubs)} publications.</span>'
    return [], '<span class="st-err">⚠️ Could not fetch — check the profile URL contains ?user=... or paste just the user ID.</span>'


def cb_bibtex(bib):
    if not bib or not bib.strip():
        return [], '<span class="st-err">No BibTeX entered.</span>'
    entries = parse_bibtex(bib)
    return entries, f'<span class="st-ok">✅ Parsed {len(entries)} entries.</span>'


def _build_pubs(doi_state, bib_state, scholar_state, manual_pubs, max_pubs, show_links):
    all_pubs = []
    all_pubs.extend(doi_state or [])
    all_pubs.extend(bib_state or [])
    all_pubs.extend(scholar_state or [])
    if manual_pubs and manual_pubs.strip():
        all_pubs.extend(l.strip() for l in manual_pubs.splitlines() if l.strip())
    if not show_links:
        all_pubs = [re.sub(r'<a[^>]*>.*?</a>', '', p) for p in all_pubs]
    return all_pubs[:int(max_pubs)]


def generate_full(
    full_name, title_f, dept, faculty, org, phone, email, website, address, namecoach,
    logo1, logo2, logo3, placement, logo_h,
    theme_name, font_ov, size_ov, lh_ov, accent_ov,
    linkedin, twitter, github, tiktok, orcid, researchgate,
    mastodon, bluesky, scholar_handle, use_icons,
    doi_state, bib_state, scholar_state,
    manual_pubs, max_pubs, show_links,
):
    pubs = _build_pubs(doi_state, bib_state, scholar_state, manual_pubs, max_pubs, show_links)
    html = build_sig(
        full_name, title_f, dept, faculty, org, phone, email, website, address, namecoach,
        logo1, logo2, logo3, placement, logo_h,
        theme_name, font_ov, size_ov, lh_ov, accent_ov,
        linkedin, twitter, github, tiktok, orcid, researchgate,
        mastodon, bluesky, scholar_handle, use_icons, pubs,
    )
    return html, html


def live_gen(
    full_name, title_f, dept, faculty, org, phone, email, website, address, namecoach,
    logo1, logo2, logo3, placement, logo_h,
    theme_name, font_ov, size_ov, lh_ov, accent_ov,
    linkedin, twitter, github, tiktok, orcid, researchgate,
    mastodon, bluesky, scholar_handle, use_icons,
    manual_pubs, max_pubs, show_links,
):
    pubs = _build_pubs([], [], [], manual_pubs, max_pubs, show_links)
    html = build_sig(
        full_name, title_f, dept, faculty, org, phone, email, website, address, namecoach,
        logo1, logo2, logo3, placement, logo_h,
        theme_name, font_ov, size_ov, lh_ov, accent_ov,
        linkedin, twitter, github, tiktok, orcid, researchgate,
        mastodon, bluesky, scholar_handle, use_icons, pubs,
    )
    return html, html


# ─────────────────────────────────────────────────────────────────────────────
# CSS & JS
# ─────────────────────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body, .gradio-container {
    background: #f5f6fa !important;
    font-family: Inter, -apple-system, Arial, sans-serif !important;
}
.gradio-container { max-width:1320px !important; margin:0 auto !important; padding:0 16px !important; }

/* reset all table borders in preview */
#preview-wrap table { border-collapse:collapse !important; border:none !important; }
#preview-wrap td, #preview-wrap th { border:none !important; }

#preview-wrap {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 40px 36px;
    min-height: 220px;
    box-shadow: 0 4px 24px rgba(0,0,0,.06);
    transition: max-width .3s ease;
}
#preview-wrap.mob { max-width:420px !important; margin:0 auto; }

/* email-client email-like envelope chrome */
#preview-wrap::before {
    content: "Preview — how your signature looks in an email client";
    display: block;
    font-family: Inter, Arial, sans-serif;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f3f4f6;
}

.copy-row { display:flex; gap:10px; margin-top:14px; }
.cbtn {
    flex:1; padding:10px 6px; border-radius:10px;
    border:1.5px solid #e5e7eb; background:#ffffff;
    font-size:12.5px; font-weight:600; cursor:pointer; color:#374151;
    transition:all .15s; font-family:Inter,Arial,sans-serif;
}
.cbtn:hover { background:#f9fafb; border-color:#9ca3af; }
.cbtn.ok    { background:#ecfdf5; border-color:#6ee7b7; color:#065f46; }

.st-ok  { font-size:11.5px; color:#065f46; font-weight:600; }
.st-err { font-size:11.5px; color:#b91c1c; font-weight:600; }

.section-label {
    font-size:9.5px; font-weight:700; text-transform:uppercase;
    letter-spacing:.14em; color:#9ca3af;
    margin:0 0 10px; padding-bottom:8px;
    border-bottom:1.5px solid #f3f4f6;
    font-family:Inter,Arial,sans-serif;
}
label { font-size:12px !important; font-weight:600 !important; color:#374151 !important; font-family:Inter,Arial,sans-serif !important; }
.gradio-accordion .label-wrap { font-weight:700 !important; font-family:Inter,Arial,sans-serif !important; }
"""

JS = """
function copyRich() {
    var p = document.getElementById('preview-wrap');
    if (!p) return;
    var b = new Blob([p.innerHTML], {type:'text/html'});
    var t = new Blob([p.innerText],  {type:'text/plain'});
    navigator.clipboard.write([new ClipboardItem({'text/html':b,'text/plain':t})])
        .then(function(){ flash('br','✅ Rich text copied!'); });
}
function copyHtml() {
    var ta = document.querySelector('#hcode textarea');
    if (!ta) return;
    navigator.clipboard.writeText(ta.value).then(function(){ flash('bh','✅ HTML copied!'); });
}
function flash(id, msg) {
    var b = document.getElementById(id); if (!b) return;
    var o = b.innerText; b.classList.add('ok'); b.innerText = msg;
    setTimeout(function(){ b.innerText = o; b.classList.remove('ok'); }, 2200);
}
function toggleMob(on) {
    var w = document.getElementById('preview-wrap'); if (!w) return;
    if (on) { w.classList.add('mob'); } else { w.classList.remove('mob'); }
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Email Signature Builder") as demo:

    doi_state     = gr.State([])
    bib_state     = gr.State([])
    scholar_state = gr.State([])

    gr.HTML(
        "<div style='padding:18px 4px 12px;'>"
        "<h1 style='font-size:23px;font-weight:800;color:#1a1a2e;margin:0 0 3px;'>"
        "✉️ Premium Email Signature Builder</h1>"
        "<p style='color:#aaa;font-size:12.5px;margin:0;'>"
        "Academic &amp; Professional · DOI auto-cite · BibTeX · Multi-logo · 4 theme presets</p>"
        "</div>"
    )

    with gr.Row(equal_height=False):

        # ── LEFT ─────────────────────────────────────────────────────────
        with gr.Column(scale=4, min_width=330):

            with gr.Accordion("👤 Identity", open=True):
                full_name  = gr.Textbox(label="Full Name",    placeholder="Hakan Mehmetcik")
                title_f    = gr.Textbox(label="Title",        placeholder="Prof. of International Relations")
                dept       = gr.Textbox(label="Department",
                                        placeholder="International Relations")
                faculty    = gr.Textbox(label="Faculty / Institute",
                                        placeholder="Faculty of Political Science")
                org        = gr.Textbox(label="University / Organization",
                                        placeholder="Marmara University")
                website    = gr.Textbox(label="Website",
                                        placeholder="avesis.marmara.edu.tr/hakan.mehmetcik")
                with gr.Row():
                    email = gr.Textbox(label="Email", placeholder="hakan@marmara.edu.tr")
                    phone = gr.Textbox(label="Phone", placeholder="+90 216 777 4310")
                address   = gr.Textbox(label="Address", lines=2,
                                       placeholder="Küçükçamlıca Mah.\nMaltepe, İstanbul 34854")
                namecoach = gr.Textbox(label="NameCoach URL",
                                       placeholder="https://name.coach/hakanmehmetcik")

            with gr.Accordion("🖼️ Logos", open=True):
                with gr.Row():
                    logo1 = gr.Image(label="Primary",   type="filepath", sources=["upload"])
                    logo2 = gr.Image(label="Secondary", type="filepath", sources=["upload"])
                    logo3 = gr.Image(label="Tertiary",  type="filepath", sources=["upload"])
                placement = gr.Radio(
                    ["Left", "Center", "Right"],
                    label="Logo Alignment (always below text)", value="Left"
                )
                logo_h = gr.Slider(40, 130, value=80, step=5, label="Logo Height (px)")

            with gr.Accordion("🎨 Theme & Typography", open=False):
                theme_name = gr.Radio(list(THEMES.keys()), value="Minimalist Academic",
                                      label="Theme Preset")
                with gr.Row():
                    font_ov = gr.Dropdown(["Theme Default","Arial","Inter","Georgia","Times"],
                                          value="Theme Default", label="Font Family")
                    size_ov = gr.Dropdown(["Theme Default","S","M","L"],
                                          value="Theme Default", label="Size Scale")
                with gr.Row():
                    lh_ov     = gr.Slider(1.0, 1.6, value=1.4, step=0.05, label="Line Height")
                    accent_ov = gr.ColorPicker(label="Accent Color", value="#2563EB")

            with gr.Accordion("🔗 Social & Academic", open=False):
                use_icons = gr.Checkbox(label="Inline SVG icons (email-safe)", value=False)
                with gr.Row():
                    linkedin = gr.Textbox(label="LinkedIn",  placeholder="handle or URL")
                    twitter  = gr.Textbox(label="X/Twitter", placeholder="handle or URL")
                with gr.Row():
                    github   = gr.Textbox(label="GitHub",    placeholder="handle or URL")
                    tiktok   = gr.Textbox(label="TikTok",    placeholder="handle or URL")
                with gr.Row():
                    orcid        = gr.Textbox(label="ORCID",        placeholder="0000-0000-0000-0000")
                    researchgate = gr.Textbox(label="ResearchGate", placeholder="handle or URL")
                with gr.Row():
                    mastodon = gr.Textbox(label="Mastodon", placeholder="@user@instance.social")
                    bluesky  = gr.Textbox(label="Bluesky",  placeholder="handle or URL")
                scholar_handle = gr.Textbox(label="Google Scholar",
                                            placeholder="https://scholar.google.com/citations?user=...")

            with gr.Accordion("📚 Publications", open=False):
                with gr.Row():
                    max_pubs   = gr.Dropdown(["3","5","10"], value="5", label="Max shown")
                    show_links = gr.Checkbox(label="Show citation links", value=True)

                gr.HTML("<p style='margin:10px 0 4px;font-size:12px;font-weight:700;color:#555;'>DOI → APA (one per line)</p>")
                doi_input  = gr.Textbox(label="", lines=3,
                                        placeholder="10.1007/978-3-031-90815-6")
                with gr.Row():
                    doi_btn    = gr.Button("🔍 Resolve DOIs", size="sm", variant="secondary")
                    doi_status = gr.HTML("")

                gr.HTML("<p style='margin:10px 0 4px;font-size:12px;font-weight:700;color:#555;'>Google Scholar Auto-Fetch</p>")
                scholar_url_inp = gr.Textbox(label="",
                                             placeholder="https://scholar.google.com/citations?user=EP6861cAAAAJ")
                with gr.Row():
                    scholar_btn    = gr.Button("📥 Fetch Publications", size="sm", variant="secondary")
                    scholar_status = gr.HTML("")

                gr.HTML("<p style='margin:10px 0 4px;font-size:12px;font-weight:700;color:#555;'>BibTeX Paste</p>")
                bib_input  = gr.Textbox(label="", lines=4, placeholder="@article{...}")
                with gr.Row():
                    bib_btn    = gr.Button("📑 Parse BibTeX", size="sm", variant="secondary")
                    bib_status = gr.HTML("")

                gr.HTML("<p style='margin:10px 0 4px;font-size:12px;font-weight:700;color:#555;'>Manual (one per line)</p>")
                manual_pubs = gr.Textbox(label="", lines=3,
                                         placeholder="Smith, J. (2024). Title. Journal Name.")

            generate_btn = gr.Button("⚡ Generate Signature", variant="primary", size="lg")

        # ── RIGHT ────────────────────────────────────────────────────────
        with gr.Column(scale=6, min_width=460):

            gr.HTML("<p class='section-label'>👁️ Live Preview</p>")
            mobile_toggle = gr.Checkbox(label="📱 Mobile view (420 px)", value=False)
            preview = gr.HTML(elem_id="preview-wrap")

            gr.HTML("""
                <div class='copy-row'>
                    <button id='br' class='cbtn' onclick='copyRich()'>
                        📋 Copy as Rich Text
                        <span style='font-weight:400;opacity:.55;font-size:11px;'> — paste into Gmail / Outlook</span>
                    </button>
                    <button id='bh' class='cbtn' onclick='copyHtml()'>&lt;/&gt; Copy Raw HTML</button>
                </div>
            """)

            gr.HTML("<p class='section-label' style='margin-top:24px;'>📄 HTML Source</p>")
            html_out = gr.Code(label="", language="html", lines=18, elem_id="hcode")

    # ── pub buttons ──────────────────────────────────────────────────────
    doi_btn.click(cb_doi,       inputs=[doi_input],                  outputs=[doi_state,     doi_status])
    scholar_btn.click(cb_scholar, inputs=[scholar_url_inp, max_pubs], outputs=[scholar_state, scholar_status])
    bib_btn.click(cb_bibtex,    inputs=[bib_input],                  outputs=[bib_state,     bib_status])

    # mobile toggle (pure JS, no server round-trip)
    mobile_toggle.change(
        fn=None, inputs=[mobile_toggle], outputs=[mobile_toggle],
        js="(v) => { toggleMob(v); return v; }"
    )

    # ── generate button ───────────────────────────────────────────────────
    full_inputs = [
        full_name, title_f, dept, faculty, org, phone, email, website, address, namecoach,
        logo1, logo2, logo3, placement, logo_h,
        theme_name, font_ov, size_ov, lh_ov, accent_ov,
        linkedin, twitter, github, tiktok, orcid, researchgate,
        mastodon, bluesky, scholar_handle, use_icons,
        doi_state, bib_state, scholar_state,
        manual_pubs, max_pubs, show_links,
    ]
    generate_btn.click(fn=generate_full, inputs=full_inputs, outputs=[preview, html_out])

    # ── live preview ──────────────────────────────────────────────────────
    live_inputs = [
        full_name, title_f, dept, faculty, org, phone, email, website, address, namecoach,
        logo1, logo2, logo3, placement, logo_h,
        theme_name, font_ov, size_ov, lh_ov, accent_ov,
        linkedin, twitter, github, tiktok, orcid, researchgate,
        mastodon, bluesky, scholar_handle, use_icons,
        manual_pubs, max_pubs, show_links,
    ]
    for inp in live_inputs:
        if hasattr(inp, "change"):
            inp.change(fn=live_gen, inputs=live_inputs, outputs=[preview, html_out])

import os
PORT = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=PORT, css=CSS, head=f"<script>{JS}</script>")
