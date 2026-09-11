# AGENTS.md

Workspace for money-making projects. Each subdirectory is a separate project with its own spec; the repo root itself is the Ship Log site (see below). No build/test/lint tooling exists yet — only Markdown.

## Layout

- `bug-bounty/` — HackerOne hunting project. Design only (`docs/superpowers/specs/`), no code yet. Planned: Osmedeus recon in WSL2 (install/verify scripts in `setup/`), targets/findings/reports trees per spec.
- `docs/superpowers/` — Ship Log project docs. Ship Log (build-in-public blog: Hugo + GitHub Pages + Telegram) is implemented at this repo root, not a subdir: `hugo.toml`, `layouts/`, `content/posts/`, `scripts/` per the plan.

## Conventions

- Specs live in `docs/superpowers/specs/` (or `<project>/docs/superpowers/specs/`), plans in `docs/superpowers/plans/`, filenames `YYYY-MM-DD-<name>-{design,plan}.md`. Follow this for new project docs.
- Git branch is `master` (not `main`). Commit style: lowercase conventional prefixes, e.g. `docs: Ship Log design spec`.
- Ship Log deployment pipeline triggers on push to `main` — keep that in mind if the branch is ever renamed.

## Ship Log rules (repo-root content)

- Publishing flow: posts are drafted with `draft: true`, user approves, then `draft: false` + commit + push. Never publish (set `draft: false` and push) without explicit user approval.
- Anonymization is hard rule for all posts — banned: broker names, account numbers/sizes, P&L, server names/hostnames, IPs, tokens/keys/passwords, personal emails. Enforced by `scripts/check_anonymized.py` plus `anonymize-terms.txt` (repo root, one term/regex per line) before deploy.
- Post template and required frontmatter (title, date YYYY-MM-DD, tags, project, draft) defined in `docs/superpowers/specs/2026-09-11-shiplog-design.md`; validation via `scripts/validate_posts.py`.
- Telegram secrets (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) live in GitHub Secrets only — never in files.
- Only newly added post files trigger Telegram messages; edits to existing posts must not re-send.

## bug-bounty specifics

- Osmedeus and recon tooling run in WSL2, not Windows shell.
- Dupe gate before drafting any report: search disclosed HackerOne reports + public writeups; doubtful findings marked "risk dupe" for user decision.
- Minimal-touch PII: verify with 1-2 records, redact PII in reports. Scope re-check before any probing.
- 3 consecutive empty sessions on a target → rotate (2-week cooldown in `targets/cooldown.md`).
