# Ship Log — Implementation Plan

Spec: `docs/superpowers/specs/2026-09-11-shiplog-design.md`

## Steps

1. **Hugo scaffold** (repo root = `makemoney/`)
   - `hugo.toml`: title "Ship Log", baseURL placeholder, tags enabled, summary divider default
   - **PaperMod theme** via Hugo modules (no git submodules): dark mode, search, RSS, TOC built in; minimal `layouts/` overrides only where needed
   - `content/posts/` empty

2. **Scripts** (`scripts/`)
   - `validate_posts.py` — required frontmatter: title, date (YYYY-MM-DD), tags, project, draft; slug = filename date prefix matches `date`
   - `check_anonymized.py` — built-in regexes: emails, IPv4, `account <digits>`, `password`, `token`, `api[_-]?key`, plus `anonymize-terms.txt` entries (one per line, repo root). Fails with file:line + match

3. **GitHub Action** (`.github/workflows/shiplog.yml`, on push to `main`)
   - validate → anonymize gate → setup-hugo (latest) → `hugo --minify` → deploy Pages (official actions config)
   - Telegram step: new `.md` files under `content/posts/` added in push (git diff A) → build HTML message from TL;DR (text before `<!--more-->`), send via `appleboy/telegram-action@v1` (pinned) with `format: html`, `disable_web_page_preview: true`, secrets `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`; continue on send failure but mark step failed

4. **shiplog-draft skill** (`~/.claude/skills/shiplog-draft/SKILL.md`)
   - Trigger: "write post", "document this project", "shiplog draft"
   - Steps per spec: gather session context → template post `draft: true` → run `check_anonymized.py` → show draft → on approval set `draft: false`, commit, push

5. **Repo + secrets setup**
   - `gh repo create shiplog --public --source . --push`
   - Pages: enable via workflow (Actions-based deploy, `actions/deploy-pages`)
   - User actions (asked when needed): BotFather → new bot; create channel "Ship Log"; add bot as admin; get `chat_id` via getUpdates; set GitHub Secrets

6. **Hello-world post + end-to-end verify**
   - First post: intro (who, why build-in-public, what Ship Log covers)
   - Push → verify: site live at `https://<user>.github.io/shiplog/`, TL;DR on list, Telegram message correct
   - Plant "account 123456" → gate blocks → remove → passes
   - Commit hello-world as first real post

## Later (not now)

- `/projects` index page listing all projects (levels.io pattern)

## Verification

Step 6 is full end-to-end gate. Local: `hugo server` optional preview; `python scripts/validate_posts.py` + `check_anonymized.py` runnable anytime.

## User dependencies

- `gh` authenticated
- BotFather bot + channel + chat_id (5 min, guided)
- Hugo binary optional (local preview only)
