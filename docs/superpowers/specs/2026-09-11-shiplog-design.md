# Ship Log — Design Spec

Date: 2026-09-11
Status: Approved (design phase complete, pending implementation plan)

## Overview

Ship Log is a build-in-public blog documenting every project worked on with Claude, published simultaneously to a public website and a Telegram channel. Each post follows a fixed template with a TL;DR and technical sections. Claude drafts posts from session context; the user approves; a git-push pipeline publishes everywhere.

## Goals

- Document every completed project/session: what was built, how, outcome.
- One source of truth (Markdown in git) → website + Telegram automatically.
- Claude drafts, human approves — no unreviewed publishing.
- Zero local tooling beyond `git`; near-zero maintenance.

## Non-Goals

- Comments, analytics, SEO campaigns, custom domain (optional later).
- Full detail on trading accounts — content is anonymized (see rules).
- Telegram discussion group — channel only.

## Key Decisions

| Decision | Choice |
|---|---|
| Audience | Public |
| Architecture | Single source (Markdown) → both website and Telegram |
| Drafting | Claude skill drafts, user approves, then push |
| Website | Hugo static site, Markdown posts, GitHub Pages |
| Telegram | Channel + Bot API (new bot, new channel — separate from MT4 bridge infra) |
| Post structure | Fixed template (below) |
| Content policy | Anonymized |
| Name | Ship Log; repo `shiplog`; channel "Ship Log" |
| URL | `https://<github-user>.github.io/shiplog/` — username resolved at implementation; custom domain optional later |

## Post Template

One Markdown file per post: `content/posts/YYYY-MM-DD-slug.md`.

```markdown
---
title: "Project X: one-line what it does"
date: 2026-09-11
tags: [python, automation]
project: project-x
draft: true
---
## TL;DR
- 2–4 bullets, plain language

<!--more-->

## Goal
## What I built
## How it works
## Outcome
```

- Text above `<!--more-->` (the TL;DR) renders on the homepage list and on the full post page.
- `draft: true` excludes post from build; flips to `false` on publish.

## Drafting Flow

Skill `shiplog-draft`. Trigger: end of a project session, or explicit request ("write a post about this").

1. Collect context: session summary, files touched, decisions made.
2. Write post from template to `content/posts/YYYY-MM-DD-slug.md` with `draft: true`.
3. Run anonymization check; show flagged items to user.
4. User edits/approves → skill sets `draft: false`, commits, pushes → pipeline takes over.

## Anonymization Rules

Banned in all posts:

- Broker names
- Account numbers and account sizes
- P&L figures
- Server names / hostnames
- IP addresses
- Tokens, keys, passwords
- Personal email addresses

Enforcement:

1. `shiplog-draft` checks before showing draft to user.
2. CI gate blocks publish on match; Action fails before deploy and names the offending line. Checks the built-in regex list plus extra terms listed in `anonymize-terms.txt` (repo root, one term/regex per line, one entry per project as needed).

## Pipeline

```
draft (skill) → user approves → commit + push to main → GitHub Action:
  1. validate frontmatter (required fields: title, date, tags, project, draft; date format YYYY-MM-DD)
  2. anonymization gate (fail = stop, no deploy)
  3. hugo build
  4. deploy to GitHub Pages
  5. Telegram post — one message per newly-added post file in that push
```

- Repo: `shiplog`, public (content is public anyway; drafts visible pre-publish is accepted). Private repo would require GitHub Pro for Pages.
- Hugo: minimal theme; builds happen in GitHub Actions. Local preview optional via `hugo server`.
- Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` stored in GitHub Secrets only. Bot created once via BotFather and added as channel admin.

## Telegram Message Format

One message per post, HTML parse mode:

```
<b>Project X: one-line what it does</b>
🧭 Ship Log · Sep 11

TL;DR bullets (plain text, ≤1024 chars total message limit, truncated cleanly)

<b>Read full post →</b> https://.../posts/project-x/
```

## Error Handling

| Failure | Behavior |
|---|---|
| Anonymization hit | Action fails before deploy; log names offending line |
| Frontmatter invalid | Action fails; names missing field |
| Hugo build error | No deploy; error in Action log |
| Telegram send fails | Site still deploys; rerun workflow manually to retry |
| Edit to existing post | No Telegram re-send — only newly-added files trigger messages |

## Testing / Verification

Implementation ends with an end-to-end hello-world post:

1. Push hello-world post (intro: who, why build-in-public, what Ship Log covers).
2. Verify site renders, TL;DR appears on list page.
3. Verify Telegram message arrives with correct format and link.
4. Plant a fake banned item (e.g., "account 123456") → verify gate blocks → remove → verify pass.
5. Hello-world stays as the first real post.

## Out of Scope (revisit later)

- Custom domain
- Per-post analytics / click tracking
- RSS feed (Hugo provides one by default; enable then)
- Automated post-creation triggers without user request
