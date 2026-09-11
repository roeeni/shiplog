#!/usr/bin/env python3
"""Anonymization gate: scan posts for banned content before publish.

Built-in patterns: emails, IPv4 addresses, account numbers, credential
assignments, Telegram bot tokens. Extra terms: one regex per line in
anonymize-terms.txt (repo root); lines starting with # and blanks ignored.

Non-draft posts: any hit fails (exit 1). Draft posts: hits are warnings only.
Exits 0 when clean.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "content" / "posts"
TERMS_FILE = ROOT / "anonymize-terms.txt"

BUILTIN = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("ipv4", re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")),
    ("account-number", re.compile(r"\baccount\D{0,5}\d{4,}\b", re.IGNORECASE)),
    ("credential", re.compile(r"\b(password|passwd|token|api[_-]?key|secret)[\s:=]+\S+", re.IGNORECASE)),
    ("telegram-bot-token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
]


def load_extra_terms():
    terms = []
    if not TERMS_FILE.exists():
        return terms
    for line in TERMS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            terms.append((f"terms:{line}", re.compile(line, re.IGNORECASE)))
        except re.error as e:
            print(f"check_anonymized: BAD RULE in anonymize-terms.txt: {line} ({e})")
            sys.exit(2)
    return terms


def is_draft(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False
    m = re.search(r"^draft:\s*(\S+)", text, re.MULTILINE)
    return bool(m and m.group(1) == "true")


def main():
    rules = BUILTIN + load_extra_terms()
    failures, warnings = [], []
    posts = sorted(POSTS_DIR.glob("*.md"))
    if not posts:
        print("check_anonymized: no posts found")
        return 0
    for path in posts:
        rel = path.relative_to(ROOT)
        draft = is_draft(path)
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for name, rx in rules:
                for hit in rx.findall(line):
                    hit = hit if isinstance(hit, str) else str(hit)
                    entry = f"{rel}:{i}: {name}: {hit!r} in: {line.strip()[:120]}"
                    (warnings if draft else failures).append(entry)
    for w in warnings:
        print(f"check_anonymized: WARN (draft) {w}")
    for f in failures:
        print(f"check_anonymized: FAIL {f}")
    if failures:
        print(f"check_anonymized: {len(failures)} violation(s) in published posts")
        return 1
    print("check_anonymized: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
