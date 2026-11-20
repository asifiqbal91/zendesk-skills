# Helpers and page objects

Two things drive every template: the **helpers** you can call, and the **data objects** each page type exposes.
The per-page table below is verified against the v4 docs and the official Copenhagen theme; for anything not listed,
read the page's developer-docs entry before iterating (guessed property names are the most common cause of blank output).

- Helpers: <https://developer.zendesk.com/api-reference/help_center/help-center-templates/helpers/>
- Advanced helpers: <https://developer.zendesk.com/api-reference/help_center/help-center-templates/advanced_helpers/>
- Shared objects: <https://developer.zendesk.com/api-reference/help_center/help-center-templates/objects/>
- Per-page properties: the page links under <https://developer.zendesk.com/api-reference/help_center/help-center-templates/>
- Reference implementation: <https://github.com/zendesk/copenhagen_theme> (`templates/`)

## The helper set (v4)

If a helper isn't here (and isn't a page property), it does not exist — do not invent one.

**Built-in block helpers:** `if`, `unless`, `each`, `with`.

**Global custom helpers:** `asset`, `calc`, `compare`, `concat`, `contains`, `date`, `dc`, `excerpt`, `filter`, `is`, `isnt`,
`json`, `link`, `not`, `page_path`, `page_url`, `slice`, `search`, `t`, `user_avatar`, `user_name`.

**Shared helpers (certain pages):** `breadcrumbs`, `form`, `pagination`, `share`, `subscribe`, `vote`, `change_password`,
`my_profile`, `contact_details`, `actions`. Inside forms: `input`, `label`, `select`, `multiselect`, `checkbox`,
`required`, `validate`, `error`, `suggestion_list`.

**Advanced helpers:** `recent_activity`, `recent_articles`, `related_articles`, `comment_callout`, `request_callout`,
`follow_up`, `satisfaction`, `token_field`, `upload`, `wysiwyg`, `edit`, `generative_answers`, `application_catalog`.

**Removed in v4 — import fails with `'X' does not exist`:**

| Removed | v4 replacement |
| --- | --- |
| `request_form` | `new_request_form` object rendered by Copenhagen's `new-request-form` module (`recipes.md`) |
| `comment_form` | `{{#form 'comment'}} … {{/form}}` |
| `filter_form` | Copenhagen's `request-list` module |
| `user_info` | `{{user_name}}`, `{{user_avatar}}` |
| `page_title` (property) | nothing — Zendesk injects `<title>` |

**Deprecated:** `request_list` ("will not receive updates") — use Copenhagen's `request-list` module.

## Frequently used, with notes

| Helper | Note |
| --- | --- |
| `asset` | `{{asset 'app.js'}}` → installed CDN URL. Assets are flat (no subfolders), names ≤ 50 chars. |
| `t` | `{{t 'comments'}}`. **Only platform keys resolve** — the full list is `references/t-keys.txt`. Some take params: `{{t 'comments_count' count=n}}`, `{{t 'show_all_articles' count=article_count}}`, `{{t 'results' query=query count=results_count}}`, `{{t 'home_page' name=help_center.name}}`, `{{t 'team_member' name=author.name}}`. Dynamic: `{{t current_filter.identifier}}`. |
| `dc` | `{{dc 'identifier'}}` — merchant-created Dynamic Content; unknown identifiers show a default message. |
| `link` | Inline `{{link 'new_request'}}` renders a localized link; block form `{{#link 'sign_in'}}…{{/link}}`. Feature links (`community`, `service_catalog`, `applications`, `approval_requests`, `chat` = Ask AI, `new_request`) render **nothing** when the feature is off, so include them unconditionally. Accepts attributes: `class=`, `role=`, `aria-current='page'`, and params such as `id=`, `topic_id=`, `content_tag_id=`. |
| `page_path` / `page_url` | `{{page_path 'help_center'}}`, `{{page_path 'request' id=request_id}}` — use instead of hardcoded `/hc/...` paths. |
| `json` | Serializes for JavaScript: `const settings = {{json settings}};`, `{{json (page_path 'new_request')}}`. No block helpers or collection subexpressions inside. |
| `search` | `{{search submit=false instant=settings.instant_search scoped=settings.scoped_kb_search class='search'}}` — native instant search keeps Guide search analytics. |
| `vote` | `{{vote 'up'}}`, `{{vote 'down'}}`, `{{vote 'sum'}}`, `{{vote 'label'}}`; block form `{{#vote 'up' class=… selected_class=…}}<svg/>{{/vote}}`. Article votes go inside `{{#with article}}`, post votes inside `{{#with post}}`; comment votes work directly in `{{#each comments}}`. |
| `pagination` | `{{pagination}}`, or name the collection: `{{pagination 'section.articles'}}`. Max 30 elements per page. |
| `form` | `{{#form 'comment' class='…'}}{{wysiwyg 'body'}}{{input type='submit'}}{{/form}}`; also `'post'`, `'organization'`. |
| `contains` | Block helper for substring/collection membership: `{{#contains settings.heading_font "Inter"}}…{{/contains}}`. |

There is no `article_comments` or `article_votes` helper — render comments with `{{#each comments}}` and votes with `vote`.

## Settings object

Every manifest variable is `settings.<identifier>`. In templates: `{{settings.hero_title}}`, `{{#if settings.show_hero}}`,
`{{json settings}}`. Visual tokens (colors, fonts, sizes, image URLs) belong in the root `style.css` via `$identifier`
substitution — see `manifest-and-settings.md`. Inside `{{#each}}` use `../settings.x`.

## Per-page data (v4, verified)

| Template | Properties | Helpers / notes |
| --- | --- | --- |
| all | `help_center` (`name`, `locale`, `base_locale`, `community_enabled`, `request_management_enabled`, `request_ccs_enabled`, `at_mentions_enabled`, `custom_statuses_enabled`), `settings`, `signed_in`, `user` (`name`, `role`, `id`, `organizations`), `brand` (`id`) | `header.hbs`/`footer.hbs` also get `alternative_locales` (`name`, `url`, `direction`) and `current_locale.name`. |
| `home_page` | `categories` (`id`, `name`, `description`, `url`, `sections` → `name`, `url`, `description`), `has_multiple_categories`, **`promoted_articles`** (`title`, `url`, `internal`), `featured_posts`, `ticket_forms` | `pagination`, `recent_activity`. If only one category, Copenhagen lists its sections instead. |
| `category_page` | `category` (`name`, `description`), `sections` (`id`, `name`, `url`, `articles`, `more_articles`, `article_count`) | `breadcrumbs`. |
| `section_page` | `section` (`name`, `description`, `articles` → `title`, `url`, `promoted`, `internal`; `sections` = subsections) | `subscribe`, `pagination 'section.articles'`. **Never bare `articles`.** |
| `article_page` | `article` (`id`, `title`, `body`, `author` → `id`, `name`, `avatar_url`, `agent`; `created_at`, `edited_at`, `internal`, `content_tags`, `comment_count`), **`section`** (`name`, `url`, **`articles`** = first 10, `more_articles`), top-level **`attachments`** (`name`, `url`, `size`), `comments` (`anchor`, `author`, `body`, `created_at`, `edited_at`, `editor`, `pending`, `ticket`), `comment_sorters` (`name`, `url`, `selected`) | `breadcrumbs`, `subscribe`, `share`, `vote`, `related_articles`, `recent_articles`, `request_callout`, `comment_callout`, `actions`, `{{#form 'comment'}}`. |
| `search_results` | `results` (`title`, `url`, **`text`** = snippet, `type`, `is_external`, `path_steps`, `author`, `created_at`, `vote_sum`, `comment_count`), `results_count`, `query`, `source_filters` / `type_filters` / `subfilters` / `content_tag_filters` (`name`, `url`, `count`, `selected`), `current_filter.identifier`, `current_subfilter` | `generative_answers`, `pagination`. |
| `error_page` | top-level `status_code` (int) and `error` (`not_found` / `forbidden` / `unauthorized`) | No `error.title`/`error.message`. |
| `new_request_page` | `new_request_form`, `parent` (`id`, `url`), `answer_bot`, `answer_bot_generative_experience`, `request_id` | Render with the `new-request-form` module (`recipes.md`). |
| `requests_page` | — | `request-list` module. |
| `request_page` | `request` (`id`, `subject`, `status`, `status_name`, `status_description`, `requester`, `created_at`, `updated_at`, `can_be_marked_as_solved`, `followup_source_id`, `type`, `type_title`, `type_name`, `priority`, `priority_title`, `priority_name`, `due_date`), `comments` (+ `attachments`), `attachments`, `collaborators`, `assignee`, `group`, `custom_fields` (`title`, `value`), `satisfaction_response` (`rating`, `editable`, `id`) | `{{#form 'comment'}}` with `token_field 'ccs'`, `wysiwyg 'body'`, `upload`, `checkbox 'mark_as_solved'`; `{{#form 'organization'}}{{select 'organization'}}{{/form}}`; `satisfaction`, `comment_callout`. |
| `subscriptions_page` | `subscriptions` (`title`, `url`, `name`, `type`, `following`, `avatar_url`), `filters`, `current_filter.label` | `subscribe`, `pagination`. Empty: `{{t 'not_following'}}`. |
| `contributions_page` | `contributions` (`title`, `url`, `type`, `vote_sum`, `last_activity_at`, `created_at`), `filters` | `pagination`. Empty: `{{t 'no_contributions'}}`. |
| `user_profile_page` | `user` (`name`, `avatar_url`, `url`, `agent`, `badges`), `description`, top-level **`member_since`**, `last_activity_at`, `total_activity`, `following_count`, `follower_count`, `vote_count`, `subscription_count`, `visible`, `private_profile`, `filters`, `current_filter`, `activities`, `contributions`, `sorters` | `actions`, `subscribe`. No `user.created_at`. |
| `community_topic_list_page` | `topics` (`name`, `url`, `description`, `post_count`, `follower_count`, `internal`), `featured_posts` | `recent_activity scope='community'`, `pagination`. |
| `community_topic_page` / `community_post_list_page` | `topic`, `posts` (`id`, `title`, `url`, `author`, `vote_sum`, `comment_count`, `status`, `status_name`, `status_dasherized`, `pinned`, `featured`), `filters`, `sorters`, `current_filter.label`, `current_sorter.label` | `subscribe`, `{{link 'new_post' topic_id=topic.id}}`. |
| `community_post_page` | `post` (`title`, `details` = body, `author`, `status_*`, `pinned`, `featured`, `pending`, `ticket`, `content_tags`, `comment_count`, `actions`), `comments` (+ `official`), `comment_sorters` | `vote` inside `{{#with post}}`; `{{#post.actions}}…{{/post.actions}}`; comment form has `{{checkbox 'official'}}`, no `upload`. |
| `new_community_post_page` | — | `{{#form 'post'}}` with `input 'title'`, `wysiwyg 'details'`, `select 'topic'`, `multiselect 'content_tags'` (not `token_field`). |
| `service_list_page`, `service_page`, `approval_request_list_page`, `approval_request_page` | — | Copenhagen `service-catalog` / `approval-requests` modules. |
| `applications_page` | — | `{{application_catalog}}`. |

## Patterns worth reusing

- **Empty-state guards:** `{{#if collection}} … {{else}} … {{/if}}` (empty collections are falsy).
- **Current item:** `{{#each section.articles}}<a href="{{url}}" {{#is id ../article.id}}aria-current="page"{{/is}}>{{title}}</a>{{/each}}`.
- **Badges:** `{{#each (slice (filter author.badges on="category_slug" equals="achievements") 0 4)}}`.
- **Asset references:** `<script type="module" src="{{asset 'app.js'}}"></script>` — never `assets/app.js`.
