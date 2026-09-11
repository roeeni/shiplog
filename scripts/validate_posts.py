#!/usr/bin/env python3
"""Validate frontmatter of all posts in content/posts/.

Required fields: title, date (YYYY-MM-DD), tags, project, draft.
Filename must be YYYY-MM-DD-<slug>.md with date matching the date field.
Exits 1 on any violation.
"""
import re
import sys
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent.parent / "content" / "posts"
REQUIRED = ["title", "date", "tags", "project", "draft"]
FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return None, "missing frontmatter block"
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, "unterminated frontmatter block"
    fm = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm, None


def main():
    errors = []
    posts = sorted(POSTS_DIR.glob("*.md"))
    if not posts:
        print("no posts found")
        return 0
    for path in posts:
        rel = path.relative_to(POSTS_DIR.parent.parent)
        m = FILENAME_RE.match(path.name)
        if not m:
            errors.append(f"{rel}: filename must be YYYY-MM-DD-<slug>.md")
            continue
        fm, err = parse_frontmatter(path.read_text(encoding="utf-8"))
        if err:
            errors.append(f"{rel}: {err}")
            continue
        for field in REQUIRED:
            if field not in fm or not fm[field]:
                errors.append(f"{rel}: missing required field '{field}'")
        if "date" in fm:
            if not DATE_RE.match(fm["date"]):
                errors.append(f"{rel}: date must be YYYY-MM-DD, got '{fm['date']}'")
            elif m.group(1) != fm["date"]:
                errors.append(f"{rel}: filename date {m.group(1)} != date field {fm['date']}")
        if "draft" in fm and fm["draft"] not in ("true", "false"):
            errors.append(f"{rel}: draft must be true/false, got '{fm['draft']}'")
        if "tags" in fm:
            v = fm["tags"].strip()
            if not (v.startswith("[") and v.endswith("]")) or not v[1:-1].strip():
                errors.append(f"{rel}: tags must be a non-empty list like [python, automation]")
    if errors:
        for e in errors:
            print(f"validate_posts: FAIL {e}")
        return 1
    for path in posts:
        print(f"validate_posts: OK {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
