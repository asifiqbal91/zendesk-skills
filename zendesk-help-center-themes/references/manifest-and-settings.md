# manifest.json and the Settings panel

The `manifest.json` defines theme metadata and the **Settings panel** merchants see in Guide. Each setting becomes a *variable* usable as `{{settings.identifier}}` in templates and `$identifier` in CSS. This is how you expose colors/fonts/toggles/images for no-code editing.

Sources:
- Settings panel: <https://support.zendesk.com/hc/en-us/articles/4408846524954-Customizing-the-Settings-panel-of-the-theme>
- Customizing the theme / variables: <https://support.zendesk.com/hc/en-us/articles/4408839332250>
- Templating versions: <https://support.zendesk.com/hc/en-us/articles/4408820214554>

> `manifest.json` is **not** editable in the in-browser code editor. Change it by editing files locally and re-importing, or via the GitHub integration. The Settings panel writes *values*; the manifest defines the *controls*.

## Document root

```json
{
  "name": "My Theme",
  "author": "Jane Doe",
  "version": "1.0.1",
  "api_version": 4,
  "settings": [ ]
}
```

- `name`, `author`, `version` surface in the Themes API and Guide.
- `api_version` selects the templating language version (use `4` for new themes). Changing it later and previewing locally surfaces deprecation warnings.
- `settings` is an array of **setting groups**.

## Setting groups → variables

Each group has a label and a `variables` array. Groups become headings (Colors, Fonts, Images, etc.) in the Settings panel.

```json
"settings": [
  {
    "label": "Colors",
    "variables": [
      {
        "identifier": "brand_color",
        "type": "color",
        "label": "brand_color_label",
        "description": "brand_color_description",
        "value": "#0072EF"
      }
    ]
  }
]
```

Each variable object:
- `identifier` — the variable name; how you reference it (`settings.brand_color`, `$brand_color`). **Naming rule: only lowercase letters, digits, and underscores** (`^[a-z0-9_]+$`), **30 characters max**. A hyphen breaks both the CSS variable and the Curlybars dot-path (`settings.brand-color` parses as subtraction). Use `brand_color`, never `brand-color`.
- `type` — the UI control (see below).
- `label`, `description` — shown in the panel. Literal strings or translation keys resolved from `translations/<locale>.json`. **Label ≤ 40 characters, description ≤ 80 characters** (after resolving the key).
- `value` — default value (for `file` types, supply a default file in `settings/` instead).

## Required variables

The manifest **must** include these two, or the import is rejected:

```json
{ "identifier": "logo",    "type": "file", "label": "logo_label",    "description": "logo_description" },
{ "identifier": "favicon", "type": "file", "label": "favicon_label", "description": "favicon_description" }
```

Both must use `identifier` exactly `"logo"` / `"favicon"` and `type: "file"`.

## Setting types

The `type` maps to a Settings-panel control. The standard set:

| type | Control | Notes |
| --- | --- | --- |
| `text` | Single-line text input | value ≤ 1000 characters |
| `checkbox` | Boolean toggle | value is `true`/`false` |
| `range` | Slider | `min`, `max`, `value` are **integers**; `step` is not documented |
| `list` | Dropdown | `options` array of `{label, value}`: **2–20 options**, option label ≤ 40 chars, `value` must be one of them |
| `color` | Color picker | hex value, e.g. `#0072EF` |
| `file` | File upload | **no `value` key**; default file `settings/<identifier>.<ext>`; required for `logo`/`favicon` |

These six are the only documented types. **There is no `textarea`** — use `text` for longer copy (1000 chars). The
panel input is single-line; for multi-line or per-language copy see `recipes.md` → "Localizing theme-only copy"
(Dynamic Content).

`list` example (fonts as a chooser — Copenhagen uses `list` for `heading_font` / `text_font`; values are CSS font stacks):

```json
{
  "identifier": "heading_font",
  "type": "list",
  "label": "heading_font_label",
  "description": "heading_font_description",
  "value": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
  "options": [
    { "label": "System", "value": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" },
    { "label": "Georgia", "value": "Georgia, 'Times New Roman', serif" }
  ]
}
```

Option labels may be literal text (as above) or translation keys.

## File-type settings and the settings/ folder

For any `file` variable, drop a default file in `settings/` so the panel has something to show before a merchant uploads their own. The Copenhagen convention is to name the default after the identifier (e.g. a default `background_image`).

## Translations for setting labels

`label`/`description` values can be keys resolved from translation files:
- `translations/<locale>.json` (e.g. `en-us.json`) is a **flat JSON object** mapping each key used in `label`,
  `description` or an option `label` to its text: `{ "brand_color_label": "Brand color", "brand_color_description": "Buttons and links." }`.
  Add one file per locale to translate the Settings panel. Literal labels (no file) also work; keys are the
  Marketplace-friendly choice. These files are for **Settings-panel strings only**.
- Do **not** put template copy there: `{{t}}` only resolves Help Center's own keys (`references/t-keys.txt`). Theme-only copy belongs in `text` settings.

## Using settings in code

### In the root `style.css` (preferred for anything visual)

Zendesk processes the root `style.css` and substitutes setting values before serving it. Supported, as used by
Copenhagen: `$identifier`, `url($file_setting)`, `darken($color, 10%)`, `lighten($color, 20%)`. For numbers that need a
unit, use plain CSS: `calc($content_width * 1px)` (`#{$var}px` interpolation is not documented).

Map settings to custom properties once, then style everything against the properties (including CSS in `assets/`):

```css
:root {
  --brand: $brand_color;
  --font-heading: $heading_font;            /* font stacks with quotes are safe here */
  --radius: calc($corner_radius * 1px);
  --hero-image: url($homepage_background_image);
}
html[data-theme="dark"] { --bg: $dark_background_color; }
```

### In templates

```hbs
{{#if settings.show_hero}} <section class="hero">…</section> {{/if}}
<a href="{{settings.status_page_url}}">{{settings.status_page_label}}</a>
<script>const settings = {{json settings}};</script>
```

Template output is HTML-escaped and triple-stache is rejected on import, so **don't inject font stacks or URLs into a
`<style>` block via `{{settings.x}}`** — quotes become `&#39;` and the CSS breaks. Use `style.css` instead. Inside
`{{#each}}`, reach settings with `../settings.x`.

### Copenhagen-compatible identifiers

Zendesk-rendered UI (the v4 request form and other Copenhagen modules, flash notifications, generative answers) reads
theme colors by Copenhagen's identifiers. Use these names for the matching settings so that UI follows the brand:
`brand_color`, `brand_text_color`, `text_color`, `link_color`, `hover_link_color`, `visited_link_color`,
`background_color`, `heading_font`, `text_font`. Name theme-specific settings however you like.

## Limits to respect

| Limit | Value |
| --- | --- |
| Settings in `manifest.json` | 200 |
| Identifier length | 30 chars, `^[a-z0-9_]+$` |
| Label / description | 40 / 80 chars |
| Options per `list` | 2–20 (option label ≤ 40) |
| `text` value | 1000 chars |

`scripts/validate_theme.py` enforces all of these. Source:
<https://support.zendesk.com/hc/en-us/articles/4408846524954> and <https://support.zendesk.com/hc/en-us/articles/4408831783962>.

## Token-driven design tip

For a maintainable system, define a compact set of *semantic* settings (e.g. `color_action_primary`, `type_heading_1`) rather than one knob per element. Map those to CSS custom properties in `style.css`, and have component styles consume the custom properties. This keeps the Settings panel small while letting the whole theme re-skin from a few values — and lets you reuse the same token vocabulary across multiple themes built on a shared codebase.
