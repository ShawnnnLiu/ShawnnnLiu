#!/usr/bin/env python3
"""Verify every link in README.md actually resolves.

A profile README with dead links is a profile README that lies, so this runs
in CI on every push and fails the build.

Three classes of link, checked three ways:

  external   http(s)  -> HEAD, falling back to GET for hosts that reject HEAD
  local      ./path   -> the file must exist in the repo
  anchor     #foo     -> must match a heading slug in this same file

Stdlib only, same as the updater. Live network flakiness is tolerated
(timeouts and 429s are warnings), but a genuine 404 is a failure.
"""

from __future__ import annotations

import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
TIMEOUT = 25
UA = {"User-Agent": "Mozilla/5.0 (compatible; readme-link-check; +https://github.com/ShawnnnLiu)"}

# Hosts that are fine but hostile to automated HEAD/GET from CI runners.
# A hard failure here would be noise, not signal.
SOFT_HOSTS = ("linkedin.com", "doi.org", "openreview.net")


def slugify(heading: str) -> str:
    """Approximate GitHub's heading-anchor slugger."""
    s = heading.strip().lower()
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def collect(text: str) -> list[str]:
    links: list[str] = []
    links += re.findall(r"(?<!!)\[[^\]]*\]\(([^)\s]+)", text)   # markdown links
    links += re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text)        # markdown images
    links += re.findall(r'href="([^"]+)"', text)
    links += re.findall(r'src="([^"]+)"', text)
    links += re.findall(r'srcset="([^"]+)"', text)
    seen, out = set(), []
    for l in links:
        if l not in seen:
            seen.add(l)
            out.append(l)
    return out


def check_external(url: str) -> tuple[bool, str]:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=UA)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return True, f"{r.status}"
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 429) and method == "HEAD":
                continue  # retry with GET
            if e.code in (403, 429) or any(h in url for h in SOFT_HOSTS):
                return True, f"{e.code} (tolerated)"
            return False, f"HTTP {e.code}"
        except (urllib.error.URLError, OSError, ValueError) as e:
            if method == "GET":
                if any(h in url for h in SOFT_HOSTS):
                    return True, f"{e} (tolerated)"
                return False, str(e)
    return False, "unreachable"


def main() -> int:
    with open(README, encoding="utf-8") as f:
        text = f.read()

    anchors = {slugify(h) for h in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.M)}

    failures: list[str] = []
    for link in collect(text):
        if link.startswith("mailto:") or link.startswith("data:"):
            continue

        if link.startswith("#"):
            target = link[1:]
            ok = target in anchors
            status = "heading found" if ok else f"no heading matches (have: {sorted(anchors)})"
        elif link.startswith(("http://", "https://")):
            ok, status = check_external(link)
        else:
            path = os.path.join(ROOT, link.split("#")[0])
            ok = os.path.exists(path)
            status = "file exists" if ok else "file missing"

        print(f"  {'ok  ' if ok else 'FAIL'}  {link}  [{status}]")
        if not ok:
            failures.append(f"{link} -> {status}")

    print()
    if failures:
        print(f"{len(failures)} broken link(s):")
        for f_ in failures:
            print(f"  - {f_}")
        return 1
    print("all links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
