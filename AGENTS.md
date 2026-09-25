# AGENTS.md

> Briefing packet for AI coding agents (Claude Code, Antigravity, Codex, Cursor, Gemini CLI, etc.).
> Humans should read README.md instead.

## Rules of engagement

These rules are the agent's first read every session. Keep this list short — absolute rules:

1. **Do** follow conventions documented in this file, `zendesk-help-center-themes/SKILL.md`, and the relevant `docs/` files. **Don't** invent new conventions silently.
2. **Do** check `docs/DECISIONS.md` before contradicting any documented pattern.
3. **Do** read `docs/SECURITY.md` Hard Rules before touching API credentials, Zendesk API tokens, or input-validation logic.
4. **Do** run `python3 zendesk-help-center-themes/scripts/validate_theme.py <theme-dir>` before declaring any Zendesk theme modifications complete.
5. **Don't** edit files in the do-not-touch zones below.
6. **Don't** hardcode raw Zendesk API tokens, subdomains, or credentials in any scripts or templates.
7. **Do** enforce and conform to `.editorconfig` formatting rules (indentation, line endings, charset, whitespace) across all code and documentation.
8. **Do** ensure Zendesk Guide themes maintain compatibility with Help Center API v2 and Curlybars requirements.

## Stack

- Language(s): Python 3 (automation scripts), HTML5/Curlybars (Handlebars dialect), CSS3, JavaScript (ES6+)
- Framework / Platform: Zendesk Guide / Help Center (API v2)
- Tooling: Zendesk CLI (`@zendesk/zcli`), Python 3 standard library
- Package/dependency manager: Python 3 (`pip`), Node.js/npm (for `@zendesk/zcli` when previewing)
- Language version: Python 3.8+, Node.js 18+

## Commands

```bash
# Validate a theme against Zendesk Help Center manifest & template requirements
python3 zendesk-help-center-themes/scripts/validate_theme.py zendesk-help-center-themes/assets/starter-theme

# Deploy / import a theme via Zendesk Guide API
python3 zendesk-help-center-themes/scripts/deploy_theme.py <theme-dir> --subdomain <subdomain> --email <email> --token <api_token>

# Local theme preview (requires Zendesk CLI)
zcli themes:preview <theme-dir>
```

## Conventions

- **Code Style & Formatting (.editorconfig):** Strict adherence to `.editorconfig` is required across all project files. All generated and modified files must preserve uniform line endings (`lf`), UTF-8 charset, 2-space indentation for templates/CSS/JS/JSON, 4-space indentation for Python, and trailing whitespace settings.
- **Curlybars Templates:** All Zendesk templates live in `templates/` and use `.hbs` extension. Use standard Zendesk Curlybars helpers (`{{#if ...}}`, `{{#each ...}}`, `{{dc "identifier"}}`, `{{asset "filename"}}`).
- **Manifest Requirements:** `manifest.json` must specify `api_version: 2`, `name`, `author`, `version`, and include valid setting types (`text`, `textarea`, `checkbox`, `range`, `list`, `color`, `file`). Required file settings include `logo` and `favicon`.
- **Scripts:** Python automation scripts must follow PEP 8 and avoid third-party dependencies where standard library (`urllib.request`, `json`, `pathlib`, `zipfile`) suffices.

## Do-not-touch zones

- `.git/` internal metadata
- Environment and credential files (`.env`, `.env.*`)
- Zendesk local cache directory (`.zat`)

## Where to look

- Architecture overview: `docs/ARCHITECTURE.md`
- Product scope: `docs/PRODUCT.md`
- Settled decisions: `docs/DECISIONS.md`
- Security rules: `docs/SECURITY.md`
- Theme skill instructions: `zendesk-help-center-themes/SKILL.md`
- Theme templates reference: `zendesk-help-center-themes/references/templates-reference.md`
- Curlybars helper reference: `zendesk-help-center-themes/references/curlybars-language.md`
- Manifest and settings reference: `zendesk-help-center-themes/references/manifest-and-settings.md`
