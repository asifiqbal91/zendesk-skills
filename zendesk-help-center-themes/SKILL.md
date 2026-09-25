---
name: zendesk-help-center-themes
description: Build, customize, and ship Zendesk Guide Help Center themes — the templating, manifest, settings, and deploy workflow for a Zendesk knowledge base / support center. Use this whenever the user is working with Zendesk Guide themes, Curlybars/Handlebars templates (.hbs files like article_page, home_page, section_page, header, footer), a theme manifest.json with settings/variables, ZCLI theme commands, the Help Center Themes API, or wants to create a custom or Marketplace help center theme from scratch. Trigger even when the user just mentions "Zendesk theme", "help center theme", "Guide theme", "Copenhagen theme", "Curlybars", or a .hbs help-center template, even if they don't say "Zendesk" explicitly. Do NOT use for Zendesk Apps, Sell, or the ticketing/agent interface — this is specifically the customer-facing Help Center (Guide) theme layer.
---

# Zendesk Help Center Themes

A Zendesk Guide Help Center theme is a folder of page templates, styles, scripts, assets, and a manifest that Zendesk renders server-side into the customer-facing knowledge base / community / request pages. Templates are written in **Curlybars**, Zendesk's implementation of a large subset of Handlebars. This skill covers building a theme from scratch, customizing the standard Copenhagen theme, and the local-preview → import → publish workflow.

## Start here

1. **Read the right reference before writing code.** This SKILL.md is the map; the detail lives in `references/`. Don't write templates from memory of generic Handlebars — Curlybars has its own helpers, page objects, and rules (e.g. no partials, specific conditional helpers). Pull the relevant reference into context first.
2. **Never ship a theme that's missing required files or the `logo`/`favicon` settings** — Zendesk rejects the import outright. When scaffolding from nothing, copy `assets/starter-theme/` as the baseline; it already satisfies the import requirements.
3. **Confirm the templating version.** The current templating language is **v4** (set as `api_version` in the manifest). Helpers and behavior differ across v1–v4. If editing an existing theme, check its `manifest.json` `api_version` before assuming a helper exists.

## Need a different layout for *some* articles/sections/categories?

Don't fork the default template and branch inside it for one product line. On Enterprise plans you can add **alternate templates** for articles, sections, and categories and assign content to them — the clean way to ship more than one layout. See `references/templates-reference.md` (Multiple/alternate templates) before building "a custom article layout." For per-id tweaks within one template, use an `{{#is id ...}}` block (see `references/recipes.md`).

## Reference files — read by task

| Task | Read |
| --- | --- |
| Writing/editing `.hbs` templates: expressions, `if`/`unless`/`is`/`each`/`with`, subexpressions, comments | `references/curlybars-language.md` |
| Which helpers exist (`asset`, `t`, `dc`, `breadcrumbs`, `excerpt`, pagination, forms…) and what data each page exposes (`article`, `section`, `request`, `comments`…) | `references/helpers-and-objects.md` |
| Building/editing `manifest.json`, defining Settings-panel controls, setting types, required variables, translations.yml, limits | `references/manifest-and-settings.md` |
| The full list of page templates (`.hbs` files), what each renders, multiple/alternate templates, custom pages | `references/templates-reference.md` |
| Local preview (ZCLI), import/update/publish/export via the Themes API, GitHub integration, Marketplace prep, plan + size limits | `references/dev-and-deploy.md` |
| Ready-made recipes: per-id template customization, language selector, comment sorting/voting, WYSIWYG editor, generative search, related articles | `references/recipes.md` |
| Accessibility, responsiveness, SEO, and Zendesk Marketplace submission readiness | `references/accessibility-and-marketplace.md` |

The `assets/starter-theme/` folder is a minimal valid theme: copy it to the working directory as a starting scaffold, then extend.

## Validate before every import

Run the bundled validator on a theme folder before importing — it catches the failures Zendesk rejects on import (missing required files/variables, partials, hardcoded asset paths, unbalanced Curlybars blocks, malformed manifest, hyphenated identifiers):

```bash
python3 scripts/validate_theme.py path/to/theme
```

It exits non-zero on errors and prints warnings for likely problems. This is faster and more reliable than eyeballing; run it after generating or editing a theme. For CI, pair it with `scripts/deploy_theme.py`, which zips, imports/updates, polls, and publishes via the Themes API (see `references/dev-and-deploy.md`).

> Note on `document_head.hbs`: the platform automatically injects the theme's compiled `style.css` and `script.js`. Don't try to link them manually (there is no `css_link`/`javascripts` helper) — only put meta tags, `{{page_title}}`, the favicon, and any *extra* assets (via the `asset` helper) in the head.

## Theme folder structure

A theme that imports cleanly into Guide has this shape. Anything outside these recognized files/folders is ignored on import.

```
my-theme/
├── manifest.json          # metadata + Settings-panel definition (REQUIRED)
├── style.css              # main stylesheet (REQUIRED)
├── script.js              # main script (REQUIRED)
├── templates/             # all .hbs page templates (REQUIRED)
│   ├── document_head.hbs
│   ├── header.hbs
│   ├── footer.hbs
│   ├── home_page.hbs
│   ├── category_page.hbs
│   ├── section_page.hbs
│   ├── article_page.hbs
│   ├── search_results.hbs
│   ├── new_request_page.hbs
│   ├── request_page.hbs
│   ├── requests_page.hbs
│   ├── subscriptions_page.hbs
│   ├── contributions_page.hbs
│   ├── user_profile_page.hbs
│   ├── error_page.hbs
│   └── ... (community + custom pages as needed)
├── assets/                # fonts, images, JS/CSS modules, etc. (referenced via the asset helper)
├── settings/              # default files for `file`-type settings (e.g. default logo/favicon)
└── translations/          # locale JSON for Settings-panel labels (optional; en-us.json typical)
```

Key facts that trip people up:
- **No template partials.** Help Center themes do not support Handlebars partials. Share markup via the global `header.hbs`/`footer.hbs`, JS, or by repeating template blocks — not `{{> partial}}`.
- **Assets are renamed/CDN-hosted on install.** Never hardcode `assets/foo.js`. Reference assets through the `asset` helper in templates (`{{asset 'foo.js'}}`) and `$assets-foo-js` / the documented syntax in CSS. See `references/helpers-and-objects.md`.
- **manifest.json is not editable in the in-browser code editor.** It's only changed by editing files locally and re-importing (or via GitHub). The Settings panel in Guide writes *values*; the manifest defines the *controls*.
- **Settings become a `settings` object** available as `{{settings.identifier}}` in templates and `$identifier` in CSS. This is the bridge between the merchant-facing Settings panel and the code.

## Standard build workflow

1. **Scaffold or start from Copenhagen.** Either copy `assets/starter-theme/`, or fork the official `zendesk/copenhagen_theme` (good when you want Zendesk Garden React components, accessibility baseline, and the full template set). For a clean token-driven custom build, the starter scaffold is lighter.
2. **Define design tokens as settings.** Put colors, fonts, spacing knobs, and toggles in `manifest.json` as setting variables so they're editable in Guide without code changes, then consume them as `$identifier` in CSS / `{{settings.identifier}}` in templates. Required: `logo` and `favicon` (both `type: "file"`).
3. **Build templates.** Write each `.hbs` against the data objects that page exposes (see `references/templates-reference.md` and `helpers-and-objects.md`). Keep global chrome in `header.hbs`/`footer.hbs` and meta in `document_head.hbs`.
4. **Style with `style.css`** using setting variables; add interactivity in `script.js` or bundled modules in `assets/`.
5. **Preview locally with ZCLI** (`zcli themes:preview`) — live-reload against your real Zendesk instance, served from `localhost`. This is the only reliable way to test rendering with real data; the in-app Preview only shows look-and-feel.
6. **Import / update / publish.** Use `zcli themes:import` / `:update` / `:publish`, or the Themes API jobs. See `references/dev-and-deploy.md`.
7. **Validate against limits.** Max 10 themes per brand, a cap on total settings, and file/theme size ceilings — confirm before delivery (full list in the deploy reference).

## Common pitfalls (check these in any review)

- Using a generic Handlebars helper that Curlybars doesn't support, or a helper deprecated in the theme's `api_version`. Verify against `references/helpers-and-objects.md`.
- Referencing assets by raw path instead of the `asset` helper → broken links after install.
- Forgetting `logo`/`favicon` settings, or a `file`-type setting with no default file in `settings/` → import rejected.
- Triple-stache vs double-stache: use `{{{ }}}` only for trusted HTML/font-stack values that must not be escaped; default to `{{ }}` for escaped output.
- Hardcoding text that should be localized — use the `{{t 'key'}}` translation helper for template strings, and `translations.yml` only for *Settings-panel* labels (not template copy).
- Assuming the in-browser editor can edit `manifest.json` — it can't.

## A note on accuracy

These docs describe Zendesk Guide as of the v4 templating API. Zendesk changes helpers, limits, and the Garden component set over time. When something is version-sensitive (a specific limit number, a new helper, Marketplace submission rules), verify against the live Zendesk developer docs rather than relying on this skill alone — links are in each reference file.
