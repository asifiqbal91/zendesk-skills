# Helpers and page objects

Two things drive every template: the **helpers** you can call, and the **data objects** each page type exposes. This file orients you; the authoritative, version-specific lists live in the Zendesk docs (links below) — read them when you need an exact signature or the complete property set for a page.

- Helpers: <https://developer.zendesk.com/api-reference/help_center/help-center-templates/helpers/>
- Advanced helpers: <https://developer.zendesk.com/api-reference/help_center/help-center-templates/advanced_helpers/>
- Shared objects: <https://developer.zendesk.com/api-reference/help_center/help-center-templates/objects/>
- Per-page properties: the page links under <https://developer.zendesk.com/api-reference/help_center/help-center-templates/> (Home, Category, Section, Article, Search Results, Request, New Request, Request List, Following, Contributions, User Profile, Error, Community pages, Custom page)

## The complete helper set (v4)

This is the authoritative list. If a helper isn't on it (and isn't a page property), it does not exist — do not invent one. Confirm exact parameters/attributes and version notes on the linked docs.

**Built-in (Handlebars block helpers, all pages):** `if`, `unless`, `each`, `with`.

**Global custom helpers (all pages):** `asset`, `calc`, `compare`, `concat`, `contains`, `date`, `dc`, `excerpt`, `filter`, `is`, `isnt`, `json`, `json_stringify`, `link`, `not`, `page_path`, `page_url`, `slice`, `search`, `t`, `user_avatar`, `user_name`.

**Shared custom helpers (only on certain pages):** `breadcrumbs`, `form`, `pagination`, `share`, `subscribe`, `vote`, `change_password`, `my_profile`.

**Advanced helpers (global + shared; richer widgets — avoid heavy CSS/JS overrides of their internals):** `recent_activity`, `recent_articles`, `actions`, `comment_callout`, `follow_up`, `token_field`, `related_articles`, `request_callout`, `request_form`, `request_list`, `satisfaction`, `upload`, `wysiwyg`, `edit`, `generative_answers`.

Frequently used, with notes:

| Helper | Purpose / note |
| --- | --- |
| `asset` | Resolve a file in `assets/` to its installed CDN URL: `{{asset 'app.js'}}`. Optional `prefix=`, `suffix=`. **Always** use instead of a raw path. |
| `t` | Translate a template string: `{{t 'comments'}}`. Only keys Help Center exposes to the theme resolve. |
| `dc` | Insert a dynamic-content placeholder: `{{dc 'search_text'}}`. |
| `link` | Build a link to a help center entity; block form: `{{#link 'requests'}}My requests{{/link}}`. |
| `is` / `isnt` | Equality / inequality block helpers (Curlybars-specific). |
| `compare` / `not` / `contains` | Conditions for use in `{{#if (...)}}` subexpressions. |
| `excerpt` | Truncate: `{{excerpt article.title characters=50}}`. |
| `date` | Format a timestamp: `{{date article.created_at}}`. |
| `filter` / `slice` / `concat` / `calc` | Transform collections/values inside subexpressions. |
| `search` | Render the search input/widget. |
| `breadcrumbs` | Breadcrumb navigation (KB pages). |
| `pagination` | Pagination controls for paginated lists. |
| `vote` | Vote control: `{{vote 'up'}}`, `{{vote 'sum'}}`, `{{vote 'down'}}` (articles and, optionally, comments). |
| `form` | Block helper wrapping a form, e.g. `{{#form 'comment'}}{{wysiwyg 'body'}}{{input type='submit'}}{{/form}}`. |
| `wysiwyg` | Rich-text editor field inside a form (replaces a plain textarea). |
| `request_form` | The full request/ticket submission form (new request page). |
| `request_list` | The user's request list (requests page). |
| `recent_articles` / `related_articles` | Article lists for home/article pages. |
| `generative_answers` | AI answer block on the search results page (version-permitting). |
| `subscribe` | Follow/unfollow button. |
| `my_profile` | Renders the user profile widget. |

Some helpers emit different HTML per `api_version` — check the per-helper docs and preview locally to catch deprecations.

## The settings object

Every manifest setting variable is exposed as a property of `settings`:
- In templates: `{{settings.color_brand}}`, `{{{settings.heading_font}}}` (triple-stache for font stacks), `{{settings.homepage_background_image}}` (resolves to a file path), `{{settings.my_range}}`.
- In CSS: `$color_brand`, and inside expressions `#{$search_width}px`.
- Can be passed to helpers: `{{#is settings.show_hero}} ... {{/is}}`.

See `manifest-and-settings.md` for defining these.

## Per-page data objects (orientation)

Each template type renders with a specific top-level object (plus shared objects like the current `user`, `help_center`, `settings`). Typical anchors:

| Template | Primary object(s) | Notable properties |
| --- | --- | --- |
| `home_page.hbs` | `categories` (and/or sections), `articles` collections | iterate categories → sections → articles |
| `category_page.hbs` | `category`, its `sections` | `category.name`, `category.description` |
| `section_page.hbs` | `section`, its `articles` | `section.name`, paginated `articles` |
| `article_page.hbs` | `article`, `comments`, `section` | `article.title`, `article.body`, `article.author`, `article.created_at`, `comments` (array), vote/follow controls |
| `search_results.hbs` | `results` (+ query) | iterate `results`; each has title/url/snippet |
| `new_request_page.hbs` | the request form | render ticket form fields |
| `request_page.hbs` | `request`, `comments` | individual ticket view |
| `requests_page.hbs` | `requests` | list of the user's requests |
| `subscriptions_page.hbs` | followed items | categories/sections/articles the user follows |
| `contributions_page.hbs` | user contributions | posts/comments by the user |
| `user_profile_page.hbs` | `user`, badges, activity | profile data |
| `error_page.hbs` | error context | message for missing pages |
| Community: `community_*` | `topics`, `posts`, `post`, `comments` | community lists and detail pages |

Always confirm the exact property names and nested shapes for a page from its developer-docs page before iterating — guessing property names is the most common source of blank output. Use `{{comments.length}}`-style checks and `{{#if}}` guards around optional data.

## Patterns worth reusing

- **Empty-state guards:** wrap collections in `{{#if collection}} ... {{else}} ...empty... {{/if}}` (empty collections are falsy).
- **Author block via context:** `{{#with article.author}}{{name}} · {{avatar_url}}{{/with}}` then `../` to reach article fields.
- **Localized labels everywhere:** `{{t 'key'}}` for any visible string so the theme works across locales.
- **Asset references:** `<script src="{{asset 'modules/app.js'}}"></script>` — never `assets/modules/app.js`.
- **Comments and votes have no single helper.** Render article/request comments with `{{#each comments}}` and the reply editor with `{{#form 'comment'}}{{wysiwyg 'body'}}{{input type='submit'}}{{/form}}`; render voting with `{{vote 'up'}}` / `{{vote 'sum'}}` / `{{vote 'down'}}`. There is no `article_comments` or `article_votes` helper — those are common hallucinations.
