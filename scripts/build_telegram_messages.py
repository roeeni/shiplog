#!/usr/bin/env python3
"""Build Telegram announcement message files for new posts.

Usage: build_telegram_messages.py <post1.md> [<post2.md> ...] --base-url <url>
Writes one HTML file per post into .messages/<filename>.html.
Message: bold title, ship log header, TL;DR (text before <!--more-->),
link to full post. Hard-capped at 4000 chars.
"""
import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / ".messages"
MAX_LEN = 4000
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_post(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        sys.exit(f"build_telegram_messages: no frontmatter in {path}")
    end = text.find("\n---\n", 4)
    if end == -1:
        sys.exit(f"build_telegram_messages: unterminated frontmatter in {path}")
    fm = {}
    for line in text[4:end].splitlines():
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    body = text[end + 5:]
    more = body.find("<!--more-->")
    tldr = body[:more] if more != -1 else body
    return fm, tldr


def tldr_to_plain(tldr: str) -> str:
    tldr = re.sub(r"##\s*TL;DR\s*", "", tldr)
    tldr = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", tldr)  # links -> text
    tldr = re.sub(r"[*_`#]+", "", tldr)  # md emphasis
    lines = [ln.strip().lstrip("- ").strip() for ln in tldr.splitlines()]
    return "\n".join(f"• {ln}" for ln in lines if ln)


def build_message(fm, tldr_plain, url):
    y, m, d = fm["date"].split("-")
    date_str = f"{MONTHS[int(m) - 1]} {int(d)}"
    title = html.escape(fm.get("title", path_title(fm)))
    parts = [f"<b>{title}</b>", f"🧭 Ship Log · {date_str}", ""]
    if tldr_plain:
        parts.append(html.escape(tldr_plain))
        parts.append("")
    parts.append(f"<b>Read full post →</b> {html.escape(url)}")
    msg = "\n".join(parts)
    if len(msg) > MAX_LEN:
        msg = msg[: MAX_LEN - 3].rstrip() + "…"
    return msg


def path_title(fm):
    return fm.get("title", "Ship Log post")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("posts", nargs="+")
    ap.add_argument("--base-url", required=True)
    args = ap.parse_args()
    base = args.base_url.rstrip("/")
    OUT_DIR.mkdir(exist_ok=True)
    for post in args.posts:
        path = Path(post)
        fm, tldr = parse_post(path)
        slug = path.stem
        url = f"{base}/posts/{slug}/"
        msg = build_message(fm, tldr_to_plain(tldr), url)
        out = OUT_DIR / f"{slug}.html"
        out.write_text(msg, encoding="utf-8")
        print(f"build_telegram_messages: wrote {out} ({len(msg)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
