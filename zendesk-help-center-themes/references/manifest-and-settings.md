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
        "identifier": "color_brand",
        "type": "color",
        "label": "color_brand_label",
        "description": "color_brand_description",
        "value": "#0072EF"
      }
    ]
  }
]
```

Each variable object:
- `identifier` — the variable name; how you reference it (`settings.color_brand`, `$color_brand`). **Naming rule: use only lowercase letters, digits, and underscores** (`^[a-z0-9_]+$`). No hyphens, spaces, or uppercase — a hyphen breaks both the CSS variable and the Curlybars dot-path (`settings.brand-color` parses as subtraction, not a property). Use `brand_color`, never `brand-color`.
- `type` — the UI control (see below).
- `label`, `description` — shown in the panel. These can be literal strings or translation keys resolved from `translations.yml` / `translations/`.
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
| `text` | Single-line text input | ~1000-char limit per field |
| `textarea` | Multi-line text | longer free text |
| `checkbox` | Boolean toggle | value is `true`/`false` |
| `range` | Slider | numeric value within a min/max/step you define |
| `list` | Dropdown | provide selectable options |
| `color` | Color picker | hex value, e.g. `#0072EF` |
| `file` | File upload | needs a default file in `settings/`; required for `logo`/`favicon` |

Confirm the exact attributes each type accepts (e.g. `min`/`max`/`step` for `range`, option entries for `list`) against the Settings-panel reference, since these are occasionally extended.

## File-type settings and the settings/ folder

For any `file` variable, drop a default file in `settings/` so the panel has something to show before a merchant uploads their own. The Copenhagen convention is to name the default after the identifier (e.g. a default `background_image`).

## Translations for setting labels

`label`/`description` values can be keys resolved from translation files:
- The top-level `translations.yml` is reserved for **Settings-panel strings only** (labels, descriptions, list options).
- Do **not** put template/UI copy here — template strings use the `{{t}}` helper and Help Center's exposed keys.
- Locale JSON under `translations/` (e.g. `en-us.json`) carries translated versions. For custom themes, manage these manually.

## Using settings in code

CSS:
```css
.button { background: $color_brand; }
.search { max-width: #{$search_width}px; }
```

Curlybars (templates):
```hbs
<body style="--brand: {{settings.color_brand}};">
<h1 style="font-family: {{{settings.heading_font}}};">{{help_center.name}}</h1>
{{#is settings.show_hero}} <section class="hero">…</section> {{/is}}
```

## Limits to respect

- Total number of settings in `manifest.json` is capped (see Guide product limits). Don't expose hundreds of knobs.
- Theme/file size and file-count ceilings exist; oversized themes fail import.
- Full limits: <https://support.zendesk.com/hc/en-us/articles/4408831783962> (Guide theming limits) — verify current numbers there.

## Token-driven design tip

For a maintainable system, define a compact set of *semantic* settings (e.g. `color_action_primary`, `type_heading_1`) rather than one knob per element. Map those to CSS custom properties in `style.css`, and have component styles consume the custom properties. This keeps the Settings panel small while letting the whole theme re-skin from a few values — and lets you reuse the same token vocabulary across multiple themes built on a shared codebase.
