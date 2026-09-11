---
title: "Ship Log: hello world"
date: 2026-09-11
tags: [meta]
project: shiplog
draft: true
---
## TL;DR
- Ship Log is live: a build-in-public log of every project, with a TL;DR and the technical details.
- Posts are drafted by Claude from the session that built the thing, then reviewed and approved by me.
- One Markdown file is the single source — it builds the website and posts to the Telegram channel.

<!--more-->

## Goal
Lots of projects get built, few get documented. The interesting parts — what was built, how, what broke — live in chat logs and get lost. Ship Log fixes that: every project gets a permanent, public writeup the day it ships.

## What I built
- **Website**: Hugo static site with the PaperMod theme, deployed to GitHub Pages by GitHub Actions.
- **Telegram channel**: every new post is announced automatically with its TL;DR and a link.
- **Drafting skill**: a Claude skill that turns a finished session into a draft post using a fixed template.

## How it works
The pipeline is deliberately boring:

1. A Markdown file with fixed frontmatter (title, date, tags, project, draft flag) is the only content format.
2. Push to `main` triggers one GitHub Action: validate frontmatter, run the anonymization gate, build with Hugo, deploy to Pages, announce new posts to Telegram.
3. Drafts never deploy — the `draft` flag flips to `false` only after review.

The anonymization gate blocks publishing if a post contains account numbers, broker names, tokens, IPs, or other sensitive strings — trading projects get documented without exposing anything exploitable.

## Outcome
This post is the first entry and doubles as the end-to-end test: if you are reading it on the site or saw it on Telegram, the whole pipeline works.
