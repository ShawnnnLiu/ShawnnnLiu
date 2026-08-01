#!/usr/bin/env python3
"""Rebuild the live blocks in README.md.

Three injected regions, each delimited by HTML comment markers:

    NEWS     <- parsed from the #news timeline on shawnnnliu.github.io
    CAT      <- one of the cat photos on the portfolio, rotated daily
    SPOTIFY  <- top albums + recent tracks from the existing Vercel endpoint

Design notes:
  * stdlib only. No pip install, no third-party actions, nothing to audit.
  * every source is fetched independently and failures are contained: if one
    upstream is down, that block keeps its previous content and the others
    still update. The script only rewrites what it successfully rendered.
  * output is deterministic for a given (date, upstream payload), so a run
    that changes nothing produces no diff and therefore no commit.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

PORTFOLIO = "https://shawnnnliu.github.io/"
SPOTIFY_API = "https://personal-website-mauve-tau.vercel.app/api/spotify"
README = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")

NEWS_ITEMS = 4
ALBUM_COUNT = 6
RECENT_COUNT = 3
TIMEOUT = 20

UA = {"User-Agent": "shawnnnliu-profile-readme (+https://github.com/ShawnnnLiu)"}

# Fallback pool, used only if the portfolio can't be reached. Kept short on
# purpose; the live list is scraped so new photos appear without a code change.
CAT_FALLBACK = [
    "assets/cats/IMG_6549.jpg",
    "assets/cats/IMG_6707.jpg",
    "assets/cats/IMG_6985.jpg",
    "assets/cats/IMG_7259.jpg",
]


# --------------------------------------------------------------------------- io


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", "replace")


# ------------------------------------------------------------------ html -> md


def absolutise(href: str) -> str:
    """Portfolio anchors are relative; from GitHub they must be absolute."""
    if href.startswith("#"):
        return PORTFOLIO + href
    if href.startswith("/"):
        return PORTFOLIO.rstrip("/") + href
    return href


def html_to_md(fragment: str) -> str:
    s = fragment
    s = re.sub(r"<a\b[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>",
               lambda m: f"[{strip_tags(m.group(2))}]({absolutise(m.group(1))})", s, flags=re.S)
    s = re.sub(r"</?(strong|b)>", "**", s)
    s = re.sub(r"</?(em|i)>", "*", s)
    s = strip_tags(s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


# ------------------------------------------------------------------- renderers


def render_news(page: str) -> str:
    items = re.findall(
        r'<div class="tl__date">(.*?)</div>\s*<div class="tl__body">(.*?)</div>',
        page, flags=re.S)
    if not items:
        raise ValueError("no timeline entries found in #news")

    lines = []
    for date, body in items[:NEWS_ITEMS]:
        lines.append(f"- **{html.unescape(strip_tags(date)).strip()}** · {html_to_md(body)}")
    return "\n".join(lines)


def render_cat(page: str | None) -> str:
    pool = []
    if page:
        pool = sorted(set(re.findall(r"assets/cats/[A-Za-z0-9_.-]+\.(?:jpg|jpeg|png|JPG|PNG)", page)))
    if not pool:
        pool = CAT_FALLBACK

    # Rotate daily, deterministically: same day -> same cat -> no spurious diff.
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    idx = int(hashlib.md5(day.encode()).hexdigest(), 16) % len(pool)
    src = PORTFOLIO + pool[idx]

    return (
        f'<a href="{PORTFOLIO}#about">'
        f'<img src="{src}" alt="Coconut and Kumquat, my cats" width="100%"></a>\n'
        f'<sub><b>Cat of the day</b> · Coconut &amp; Kumquat 🐱 · '
        f'rotates daily from a pool of {len(pool)}</sub>'
    )


def render_spotify(payload: dict) -> str:
    albums = (payload.get("albums") or {}).get("short_term") or []
    recent = payload.get("recentTracks") or []
    if not albums and not recent:
        raise ValueError("spotify payload had neither albums nor recent tracks")

    out = ["<b>On repeat lately</b><br>", ""]

    covers = []
    for a in albums[:ALBUM_COUNT]:
        name = html.escape(a.get("name", ""), quote=True)
        artist = html.escape(a.get("artist", ""), quote=True)
        label = f"{name} · {artist}"
        covers.append(
            f'<a href="{html.escape(a.get("url", ""), quote=True)}">'
            f'<img src="{html.escape(a.get("image", ""), quote=True)}" '
            f'width="84" height="84" alt="{label}" title="{label}"></a>'
        )
    if covers:
        out.append("".join(covers))
        out.append("")

    if recent:
        played = " · ".join(
            f'{html.escape(t.get("name", ""))} <i>{html.escape(t.get("artist", ""))}</i>'
            for t in recent[:RECENT_COUNT]
        )
        out.append(f"<sub><b>Just played</b> · {played}</sub><br>")

    out.append(f'<sub><a href="{PORTFOLIO}#about">Full listening stats →</a></sub>')
    return "\n".join(out)


# ------------------------------------------------------------------ injection


def replace_block(text: str, name: str, body: str) -> str:
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise ValueError(f"markers for {name} not found in README.md")
    return pattern.sub(f"{start}\n{body}\n{end}", text)


def main() -> int:
    with open(README, encoding="utf-8") as f:
        original = f.read()
    readme = original

    page = None
    try:
        page = fetch(PORTFOLIO)
    except (urllib.error.URLError, OSError) as e:
        print(f"warn: portfolio unreachable ({e}); news + cat keep previous content")

    if page:
        for name, fn in (("NEWS", render_news), ("CAT", render_cat)):
            try:
                readme = replace_block(readme, name, fn(page))
                print(f"ok: {name}")
            except Exception as e:  # noqa: BLE001 - one bad block must not sink the rest
                print(f"warn: {name} not updated ({e})")
    else:
        try:
            readme = replace_block(readme, "CAT", render_cat(None))
            print("ok: CAT (fallback pool)")
        except Exception as e:  # noqa: BLE001
            print(f"warn: CAT not updated ({e})")

    try:
        readme = replace_block(readme, "SPOTIFY", render_spotify(json.loads(fetch(SPOTIFY_API))))
        print("ok: SPOTIFY")
    except Exception as e:  # noqa: BLE001
        print(f"warn: SPOTIFY not updated ({e})")

    if readme == original:
        print("no changes")
        return 0

    with open(README, "w", encoding="utf-8") as f:
        f.write(readme)
    print("README.md updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
