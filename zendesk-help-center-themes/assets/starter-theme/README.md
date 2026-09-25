# Starter Theme

A minimal, valid Zendesk Guide Help Center theme scaffold (Templating API v4).
Copy this folder to your working directory and build on it.

## Why it imports cleanly
- Has the required `manifest.json`, `style.css`, `script.js`, and `templates/`.
- Declares the required `logo` and `favicon` settings (type `file`) with default
  files in `settings/`.
- Uses a small set of semantic token settings (colors, fonts, layout) mapped to
  CSS custom properties in `style.css`, so the whole theme re-skins from the
  Settings panel.
- Templates use only real, documented helpers.

## Validate, then develop
```bash
python3 ../../scripts/validate_theme.py .   # pre-import lint
zcli login -i            # subdomain, email, API token
zcli themes:preview .    # live-reload at localhost:4567, browse on your subdomain
zcli themes:import .     # add to a brand (test in a Sandbox first)
zcli themes:publish      # make it live
```

## Notes
- The platform auto-injects the compiled `style.css`/`script.js`; `document_head.hbs`
  only carries meta/title/favicon and any extra assets (via the `asset` helper).
- Comments/votes have no single helper: comments render via `{{#each comments}}`,
  the reply editor via `{{#form 'comment'}}{{wysiwyg 'body'}}{{input type='submit'}}{{/form}}`,
  and voting via `{{vote 'up'}}` / `{{vote 'sum'}}` / `{{vote 'down'}}`.
- `following_page` and `contributions_page` are left as documented stubs — build
  them against their page-object docs (links are in the template comments).
- Replace the placeholder SVG logo/favicon with real brand assets.
- Add community templates (`community_*.hbs`) only if the help center uses Gather.
- No partials are supported — share chrome via `header.hbs` / `footer.hbs`.
