# Starter Theme

A minimal Zendesk Guide Help Center theme scaffold for **Templating API v4**. Copy this folder to your working
directory and build on it.

## Set up

```bash
cp -r <skill>/assets/starter-theme ./my-theme
bash <skill>/scripts/vendor_copenhagen_modules.sh ./my-theme   # request form, list, catalog, approvals (add a local
                                                               # copenhagen_theme path as 2nd arg to work offline)
python3 <skill>/scripts/validate_theme.py ./my-theme           # must report 0 errors
zcli login -i
zcli themes:preview ./my-theme
```

The validator reports missing `assets/*-bundle.js` until you run the vendoring step: v4 has no `{{request_form}}`
helper, so `new_request_page.hbs` and `requests_page.hbs` render Zendesk's own modules through the import map in
`document_head.hbs`. Keep `THIRD_PARTY_COPENHAGEN.txt` (Apache-2.0 attribution) in your repo.

## What's here

- Required `manifest.json`, `style.css`, `script.js`, `templates/`, plus `logo`/`favicon` file settings with defaults in `settings/`.
- Token settings mapped to CSS custom properties in `style.css` via Zendesk's `$setting` substitution.
- The full standard template set, using only platform `{{t}}` keys (see `references/t-keys.txt`) and verified v4 properties
  (`section.articles`, top-level `attachments`, `error` + `status_code`, `member_since`, `promoted_articles`).

## Notes

- Zendesk injects `<title>`, the favicon, `style.css` and `script.js`; `document_head.hbs` holds only meta, the import
  map and extra assets via the `asset` helper.
- Need copy that has no platform translation key? Add a `text` setting; don't invent `{{t}}` keys.
- Replace the placeholder logo/favicon. No partials — share chrome through `header.hbs` / `footer.hbs`.
