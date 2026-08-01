#!/usr/bin/env python3
"""Rebuild the live block in README.md.

One injected region, delimited by HTML comment markers:

    NEWS  <- parsed from the #news timeline on shawnnnliu.github.io

Design notes:
  * stdlib only. No pip install, no third-party actions, nothing to audit.
  * failures are contained: if the upstream is down, the block keeps its
    previous content. The script only rewrites what it successfully rendered.
  * output is deterministic for a given upstream payload, so a run that
    changes nothing produces no diff and therefore no commit.
"""

from __future__ import annotations

import html
import os
import re
import sys
import urllib.error
import urllib.request

PORTFOLIO = "https://shawnnnliu.github.io/"
README = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")

NEWS_ITEMS = 4
TIMEOUT = 20

UA = {"User-Agent": "shawnnnliu-profile-readme (+https://github.com/ShawnnnLiu)"}


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


# -------------------------------------------------------------------- renderer


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

    try:
        readme = replace_block(readme, "NEWS", render_news(fetch(PORTFOLIO)))
        print("ok: NEWS")
    except (urllib.error.URLError, OSError) as e:
        print(f"warn: portfolio unreachable ({e}); news keeps previous content")
    except Exception as e:  # noqa: BLE001 - a bad render must not fail the run
        print(f"warn: NEWS not updated ({e})")

    if readme == original:
        print("no changes")
        return 0

    with open(README, "w", encoding="utf-8") as f:
        f.write(readme)
    print("README.md updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
