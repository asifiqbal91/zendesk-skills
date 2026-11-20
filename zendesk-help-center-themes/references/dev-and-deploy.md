# Development and deployment

How to preview a theme locally, get it into Guide, publish it, and ship it (including Marketplace). Two paths: **ZCLI** (recommended for humans) and the **Themes API** (for automated/CI workflows).

Sources:
- Previewing locally: <https://support.zendesk.com/hc/en-us/articles/4408822095642-Previewing-theme-changes-locally>
- ZCLI themes commands: <https://github.com/zendesk/zcli/blob/master/docs/themes.md>
- Importing/downloading: <https://support.zendesk.com/hc/en-us/articles/4408828976538>
- Themes API: <https://developer.zendesk.com/api-reference/help_center/help-center-api/theming/>
- Theming limits: <https://support.zendesk.com/hc/en-us/articles/4408831783962>

## Prerequisites

- Plan: code editing / custom themes require Suite Growth+ / Professional+ (Guide Professional or Enterprise). Local preview requires Suite Professional or above.
- Enable API access: Admin Center → Apps and integrations → APIs → Zendesk API.
- Install ZCLI (Zendesk Command Line Interface). ZCLI replaces the older ZAT for themes.

## Local preview with ZCLI

```bash
# one-time auth (subdomain, email, API token — don't append /token, ZCLI does it)
zcli login -i

# from the theme folder (where manifest.json lives)
zcli themes:preview .
```
- Serves theme assets from `localhost:4567` by default while you browse your real instance at `https://<subdomain>.zendesk.com`. Live-reloads on save.
- Useful flags: `--port=9999`, `--bind=<host>`, `--no-livereload`, `--logs`, `--https-cert`/`--https-key` (for HTTPS).
- The in-app **Preview** in Guide only shows look-and-feel and won't exercise interactive features end-to-end — use ZCLI (and a Sandbox) for real testing.

## ZCLI theme commands

| Command | Purpose |
| --- | --- |
| `zcli themes:preview [dir]` | Local live-reload preview. |
| `zcli themes:import [dir]` | Import the theme into a brand as a new theme. |
| `zcli themes:update [dir]` | Update an existing (api-managed) theme in place. |
| `zcli themes:publish` | Make a theme the live theme for its brand. |
| `zcli themes:list` | List themes. |
| `zcli themes:delete` | Delete a theme (cannot delete a brand's live theme). |

All theme commands require `zcli login` first.

## Themes API (automation / CI)

Base: `/api/v2/guide/theming`. With multiple brands, call the **account** domain, not a brand domain. OAuth scopes: `themes:read` or `themes:write`.

Resources: **themes** (the theme) and **jobs** (async import/update/export).

Theme endpoints:
- `GET /themes` (optionally `?brand_id=`) — list
- `GET /themes/{id}` — show
- `POST /themes/{id}/publish` — make live
- `DELETE /themes/{id}` — delete (not the live one)

Job endpoints (all async — poll the job):
- `POST /jobs/themes/imports` — body `{"job":{"attributes":{"brand_id":"…","format":"zip"}}}`. Returns a one-time `upload.url` + `parameters`.
- `POST /jobs/themes/updates` — body includes `theme_id`, `replace_settings` (bool), `format:"zip"`.
- `POST /jobs/themes/exports` — body `theme_id`, `format:"zip"`. Returns a `download.url` when complete.
- `GET /jobs/{id}` — poll status (`pending` → `completed`/`failed`).

### Import/update upload flow
The create-job endpoint does **not** receive the ZIP. Instead:
1. Create the job → get `data.upload.url` and `data.upload.parameters`.
2. `POST` the ZIP to that storage URL with **no auth headers**, `Content-Type: multipart/form-data`, every key in `parameters` as a form field, plus a `file` field with the ZIP. Treat `parameters` as opaque — send as-is.
3. Poll `GET /jobs/{id}` (~every 5s; don't hammer it) until `completed`. For imports, the new `theme_id` is in the job data.

### Export flow
Create export job → poll → download from `data.download.url`. Exporting is the only way to retrieve `manifest.json` and assets for a theme created/edited in Guide.

## GitHub integration

You can connect a theme to a GitHub repo so updates deploy from Git. Caution: if you click **Edit code** in Guide on a GitHub-managed theme and proceed past the warning, the theme is **disconnected** from GitHub. Keep `manifest.json` and `assets/` in the repo and in sync to avoid losing settings when updating. See Zendesk's "Setting up the GitHub integration with your help center theme."

## Limits

| Limit | Value |
| --- | --- |
| Themes per brand | 10 |
| Theme size | 55 MB |
| All assets / one asset | 50 MB / 5 MB |
| Asset file name | 50 chars (assets/ is flat — no subfolders) |
| Template, `style.css`, `script.js` | 800 KB each |
| Settings in `manifest.json` | 200 (identifier ≤ 30, label ≤ 40, description ≤ 80, list ≤ 20 options) |
| Elements per page | 30 (use `{{pagination}}`) |
| Custom pages / alternate templates per type | 100 / 100 |

No template partials. `scripts/validate_theme.py` enforces the size and settings limits. Source:
<https://support.zendesk.com/hc/en-us/articles/4408831783962> (re-check before a release).

## Import job error codes (for debugging failed jobs)

A failed job returns `errors[]` with a `code`. Common ones: `InvalidManifest`, `InvalidTemplates` (template syntax errors), `InvalidSetting`, `TooManySettings`, `FileNotSupported`, `FileTooBig`, `ThemeTooBig`, `FileNotFound` (a required file missing), `UnsupportedLocale`, `InvalidTranslationFile`, `InvalidThemeVersion`, `NonUpdatableTheme` (trying to update a non-api theme), `NameTooLong`. Map the code to the offending file/field and fix locally, then re-import.

## Shipping to the Zendesk Marketplace

Marketplace themes have additional review/branding/quality requirements beyond a clean import (responsive, accessible, documented settings, support contact). Treat a clean local preview + clean import as the baseline, then follow the current Marketplace/partner submission guidelines, which change over time — check Zendesk's partner/Marketplace docs for the latest checklist.

## CI pipeline (validate → deploy)

Bundle two scripts make this repeatable. Validate locally first so a broken theme never reaches upload, then deploy via the Themes API:

```bash
python3 scripts/validate_theme.py ./my-theme        # fails the build on import-breaking issues
ZD_SUBDOMAIN=acme ZD_EMAIL=a@b.com ZD_API_TOKEN=xxx \
  python3 scripts/deploy_theme.py ./my-theme --brand-id 360001234567 --publish
```
`deploy_theme.py` zips the theme, creates the import (or update, with `--theme-id`) job, uploads, polls, and optionally publishes. Use the **account** subdomain for multi-brand accounts.

**Upload gotcha:** the one-time storage URL is an S3-style presigned POST. Send the returned `parameters` as form fields with the `file` field **last**, and **no auth headers** on that request. (`deploy_theme.py` relies on `requests` ordering `data` before `files`; preserve that if you reimplement it.)

## Recommended loop

1. `zcli themes:preview .` and build against real data.
2. Validate import constraints (required files, `logo`/`favicon`, limits).
3. `zcli themes:import .` into a Sandbox brand; test interactive flows end-to-end: submit a request (attachment + conditional field), request list filters, reply + mark as solved, search filters, article vote/comment, community post.
4. `zcli themes:update .` as you iterate; `zcli themes:publish` when ready.
5. For CI, mirror this with the Themes API import/update/publish jobs.
