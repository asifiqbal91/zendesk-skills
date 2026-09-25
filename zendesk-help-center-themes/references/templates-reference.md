# Templates reference

Every page type in a Help Center is rendered from an editable `.hbs` template in `templates/`. This is the full set of templates and global elements, what each renders, and the rules for multiple/custom templates.

Source: <https://support.zendesk.com/hc/en-us/articles/4408839332250-Customizing-your-help-center-theme> and the per-page docs under <https://developer.zendesk.com/api-reference/help_center/help-center-templates/>

## Global elements (chrome + meta)

| File | Renders |
| --- | --- |
| `document_head.hbs` | The document `<head>` — meta tags, title, favicon, CSS/JS includes. |
| `header.hbs` | The bars at the top of every page (logo, nav, search). Use this for shared top chrome — there are no partials. |
| `footer.hbs` | The bars at the bottom of every page. Shared bottom chrome. |

## Knowledge base pages

| File | Renders |
| --- | --- |
| `home_page.hbs` | Top-level help center landing page. |
| `category_page.hbs` | A category landing page (lists its sections). |
| `section_page.hbs` | A section landing page (lists its articles). |
| `article_page.hbs` | An individual knowledge base article + comments/votes. |
| `search_results.hbs` | Search results listing. |
| `error_page.hbs` | Message shown for non-existent pages. |

## Requests / tickets (customer self-service)

| File | Renders |
| --- | --- |
| `new_request_page.hbs` | The request/ticket submission form. |
| `request_page.hbs` | An individual request/ticket page. |
| `requests_page.hbs` | List of requests assigned to or CC'ing the user. |
| `subscriptions_page.hbs` | "Following" page — categories/sections/articles the user follows. |
| `contributions_page.hbs` | A user's posts, community comments, and article comments. |
| `user_profile_page.hbs` | A user's profile page. |

## Community (Gather) pages

| File | Renders |
| --- | --- |
| `community_topic_list_page.hbs` | List of community topics. |
| `community_topic_page.hbs` | A single community topic. |
| `community_post_list_page.hbs` | List of posts. |
| `community_post_page.hbs` | A single community post + comments. |
| `new_community_post_page.hbs` | New post form. |

## Custom pages

| File | Renders |
| --- | --- |
| `custom_page.hbs` (and named custom pages) | Pages you build from scratch and link from anywhere in the help center. Enterprise plans. |

There are also service catalog and approval request page templates for accounts using those features — see the developer docs sidebar if the theme needs them.

## Multiple / alternate templates (Enterprise)

On Enterprise plans you can add **additional templates** for articles, sections, and categories when you need more than one layout (e.g. a different article layout for a product line). You can also create custom pages. See <https://support.zendesk.com/hc/en-us/articles/4408828878106> (Adding multiple article, section, and category templates).

## What to include

- A theme needs the templates for the features it uses. If the help center has no community, you can omit/leave minimal community templates, but the standard set is safest for a portable/Marketplace theme.
- Keep all reusable top/bottom chrome in `header.hbs`/`footer.hbs`. Keep `<head>` concerns (CSS/JS links via the `asset` helper, meta, favicon) in `document_head.hbs`.
- Guard optional data with `{{#if}}` and use `{{t}}` for visible copy on every template.

## Editing in Guide vs locally

- In Guide: **Customize design → Customize → Edit code** lists templates, `style.css`, and `script.js` — but **not** `manifest.json`.
- Locally: download/export the theme to get the full folder including `manifest.json`, edit with your own tools, preview with ZCLI, then re-import. See `dev-and-deploy.md`.
