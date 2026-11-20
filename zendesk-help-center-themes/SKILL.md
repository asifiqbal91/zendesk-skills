---
name: zendesk-help-center-themes
description: Build, customize, and ship Zendesk Guide Help Center themes — the templating, manifest, settings, and deploy workflow for a Zendesk knowledge base / support center. Use this whenever the user is working with Zendesk Guide themes, Curlybars/Handlebars templates (.hbs files like article_page, home_page, section_page, header, footer), a theme manifest.json with settings/variables, ZCLI theme commands, the Help Center Themes API, or wants to create a custom or Marketplace help center theme from scratch. Trigger even when the user just mentions "Zendesk theme", "help center theme", "Guide theme", "Copenhagen theme", "Curlybars", or a .hbs help-center template, even if they don't say "Zendesk" explicitly. Do NOT use for Zendesk Apps, Sell, or the ticketing/agent interface — this is specifically the customer-facing Help Center (Guide) theme layer.
---

# Zendesk Help Center Themes

A Zendesk Guide Help Center theme is a folder of page templates, styles, scripts, assets, and a manifest that Zendesk renders server-side into the customer-facing knowledge base / community / request pages. Templates are written in **Curlybars**, Zendesk's implementation of a large subset of Handlebars. This skill covers building a theme from scratch, customizing the standard Copenhagen theme, and the local-preview → import → publish workflow.

## Start here

1. **Read the right reference before writing code.** This SKILL.md is the map; the detail lives in `references/`. Don't write templates from memory of generic Handlebars — Curlybars has its own helpers, page objects, and rules (e.g. no partials, specific conditional helpers). Pull the relevant reference into context first.
2. **Never ship a theme that's missing required files or the `logo`/`favicon` settings** — Zendesk rejects the import outright. When scaffolding from nothing, copy `assets/starter-theme/`, then run `bash scripts/vendor_copenhagen_modules.sh <theme> [local-copenhagen-dir]` (v4 request form/list modules; the second argument works offline) and `python3 scripts/validate_theme.py <theme>`. Never create placeholder bundles — the validator rejects them.
3. **Confirm the templating version.** The current templating language is **v4** (set as `api_version` in the manifest). Helpers and behavior differ across v1–v4. If editing an existing theme, check its `manifest.json` `api_version` before assuming a helper exists.

## Need a different layout for *some* articles/sections/categories?

Don't fork the default template and branch inside it for one product line. On Enterprise plans you can add **alternate templates** for articles, sections, and categories and assign content to them — the clean way to ship more than one layout. See `references/templates-reference.md` (Multiple/alternate templates) before building "a custom article layout." For per-id tweaks within one template, use an `{{#is id ...}}` block (see `references/recipes.md`).

## Reference files — read by task

| Task | Read |
| --- | --- |
| Writing/editing `.hbs` templates: expressions, `if`/`unless`/`is`/`each`/`with`, subexpressions, comments | `references/curlybars-language.md` |
| Which helpers exist (`asset`, `t`, `dc`, `breadcrumbs`, `excerpt`, pagination, forms…) and what data each page exposes (`article`, `section`, `request`, `comments`…) | `references/helpers-and-objects.md` |
| Building/editing `manifest.json`, Settings-panel controls, the six setting types, limits (200 settings, 40/80-char labels), `style.css` `$setting` tokens, Copenhagen-compatible identifiers | `references/manifest-and-settings.md` |
| The full list of page templates (`.hbs` files), what each renders, multiple/alternate templates, custom pages | `references/templates-reference.md` |
| Local preview (ZCLI), import/update/publish/export via the Themes API, GitHub integration, Marketplace prep, plan + size limits | `references/dev-and-deploy.md` |
| Ready-made recipes: **v4 request form / request list / service catalog / approvals modules**, localizing theme-only copy, settings → tokens, articles in section, per-id customization, language selector, comments, generative search | `references/recipes.md` |
| Which `{{t 'key'}}` keys exist (custom keys do not resolve) | `references/t-keys.txt` |
| Accessibility, responsiveness, SEO, and Zendesk Marketplace submission readiness | `references/accessibility-and-marketplace.md` |

The `assets/starter-theme/` folder is a minimal v4 theme with the full template set: copy it, vendor the Copenhagen modules into its `assets/`, then extend.

## Validate before every import

Run the bundled validator on a theme folder before importing. It catches what Zendesk rejects on import and what imports but renders broken: missing files/settings, invalid setting types and Settings-panel limits, undeclared `settings.x`/`$x`, `{{t}}` keys that aren't platform keys, removed v4 helpers (`request_form`…) and non-existent properties (`page_title`, `error.title`…), partials, triple-stache, unbalanced blocks, missing `{{asset}}` files, and asset/theme size limits:

```bash
python3 scripts/validate_theme.py path/to/theme
```

It exits non-zero on errors and prints warnings for likely problems. This is faster and more reliable than eyeballing; run it after generating or editing a theme. For CI, pair it with `scripts/deploy_theme.py`, which zips, imports/updates, polls, and publishes via the Themes API (see `references/dev-and-deploy.md`).

> Note on `document_head.hbs`: the platform injects `<title>`, the favicon, and the theme's `style.css` and `script.js`. Don't add them (there is no `page_title` property and no `css_link`/`javascripts` helper) — put only meta tags, the module import map, and *extra* assets (via the `asset` helper) in the head.

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
│   ├── community_*.hbs, new_community_post_page.hbs
│   └── service_*, approval_request_*, applications_page.hbs (feature pages)
├── assets/                # flat: fonts, images, JS/CSS, Copenhagen *-bundle.js modules (via the asset helper)
├── settings/              # default files for `file`-type settings (e.g. default logo/favicon)
└── translations/          # locale JSON for Settings-panel labels (optional; en-us.json typical)
```

Key facts that trip people up:
- **No template partials.** Help Center themes do not support Handlebars partials. Share markup via the global `header.hbs`/`footer.hbs`, JS, or by repeating template blocks — not `{{> partial}}`.
- **Assets are renamed/CDN-hosted on install.** Never hardcode `assets/foo.js`. Reference them with `{{asset 'foo.js'}}` in templates (`$assets-foo-js` style variables in the root `style.css`). `assets/` is flat; names ≤ 50 chars.
- **manifest.json is not editable in the in-browser code editor.** It's only changed by editing files locally and re-importing (or via GitHub). The Settings panel in Guide writes *values*; the manifest defines the *controls*.
- **Settings become a `settings` object** available as `{{settings.identifier}}` in templates and `$identifier` in the root `style.css` (Zendesk substitutes the value; also `url($file)`, `darken()`, `lighten()`). Put visual tokens in `style.css` — template output is HTML-escaped.
- **`{{t}}` only knows Zendesk's keys.** A made-up key renders broken text. Use `references/t-keys.txt`, a `text` setting, or a JS dictionary for JS-created strings.
- **v4 renders the request form client-side.** `{{request_form}}` is gone; mount Copenhagen's modules (`references/recipes.md`).

## Standard build workflow

1. **Scaffold or start from Copenhagen.** Either copy `assets/starter-theme/` (+ `bash scripts/vendor_copenhagen_modules.sh <theme>`), or fork the official `zendesk/copenhagen_theme`. Either way the request form, request list, service catalog and approvals come from Copenhagen's modules.
2. **Define design tokens as settings.** Colors, fonts, spacing knobs and toggles go in `manifest.json` (use Copenhagen identifiers like `brand_color`, `text_color`, `heading_font` for the shared ones so Zendesk-rendered UI follows the brand), mapped to CSS custom properties in the root `style.css` via `$identifier`. Required: `logo` and `favicon` (both `type: "file"`).
3. **Build templates.** Write each `.hbs` against the data objects that page exposes (see `references/templates-reference.md` and `helpers-and-objects.md`). Keep global chrome in `header.hbs`/`footer.hbs` and meta in `document_head.hbs`.
4. **Style with `style.css`** using setting variables; add interactivity in `script.js` or bundled modules in `assets/`.
5. **Preview locally with ZCLI** (`zcli themes:preview`) — live-reload against your real Zendesk instance, served from `localhost`. This is the only reliable way to test rendering with real data; the in-app Preview only shows look-and-feel.
6. **Import / update / publish.** Use `zcli themes:import` / `:update` / `:publish`, or the Themes API jobs. See `references/dev-and-deploy.md`.
7. **Validate against limits.** Max 10 themes per brand, a cap on total settings, and file/theme size ceilings — confirm before delivery (full list in the deploy reference).

## Common pitfalls (check these in any review)

- Using a generic Handlebars helper that Curlybars doesn't support, or a helper deprecated in the theme's `api_version`. Verify against `references/helpers-and-objects.md`.
- Referencing assets by raw path instead of the `asset` helper → broken links after install.
- Forgetting `logo`/`favicon` settings, or a `file`-type setting with no default file in `settings/` → import rejected.
- Triple-stache `{{{ }}}` — rejected on import; bodies already render as safe HTML. Font stacks/URLs belong in `style.css`.
- Custom `{{t 'key'}}` keys — render broken. Only keys in `references/t-keys.txt`; `translations/*.json` is for Settings-panel labels only.
- `{{request_form}}` / `{{request_list}}`, `page_title`, `error.title`, `user.created_at`, bare `articles` on `section_page` — removed or never existed in v4.
- Setting type `textarea`, labels > 40 / descriptions > 80 chars, lists with < 2 or > 20 options — import fails.
- Hardcoded demo content in a theme for others: status URLs, fake status badges, sample social links, your brand in fallbacks — make each a setting (empty = hidden).
- Assuming the in-browser editor can edit `manifest.json` — it can't.

## A note on accuracy

These docs describe Zendesk Guide as of the v4 templating API. Zendesk changes helpers, limits, and the Garden component set over time. When something is version-sensitive (a specific limit number, a new helper, Marketplace submission rules), verify against the live Zendesk developer docs rather than relying on this skill alone — links are in each reference file.
