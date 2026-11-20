# Recipes

Practical, verified snippets distilled from the Zendesk Help Center templating cookbook (<https://support.zendesk.com/hc/en-us/articles/4408832681626>). Zendesk doesn't support custom code, and exact markup varies by theme/`api_version` — preview locally after applying.

## Request form and other v4 modules (replaces `{{request_form}}`)

v4 has no `{{request_form}}`; `new_request_page` exposes `new_request_form` as data and Zendesk's Garden-based module
renders it client-side (conditional fields, attachments, CCs, suggested articles, AI deflection). The same pattern
covers the request list, service catalog, approvals and flash notifications. Use Copenhagen's prebuilt bundles
(Apache-2.0, distribute unmodified with attribution):

```bash
bash scripts/vendor_copenhagen_modules.sh path/to/theme                    # clone from GitHub (network)
bash scripts/vendor_copenhagen_modules.sh path/to/theme ~/copenhagen_theme # offline: local checkout/zip, or any theme with the bundles
```

Never commit placeholder bundles to satisfy `{{asset}}` checks — `validate_theme.py` rejects files that aren't real
ES modules. If you can't fetch the bundles, leave them missing and say so; the validator will keep reporting it.

`document_head.hbs` — import map (one entry per bundle) and flash notifications:

```hbs
<script>
  if (!(HTMLScriptElement.supports && HTMLScriptElement.supports('importmap'))) {
    document.write('<script async src="{{asset 'es-module-shims.js'}}"><\/script>');
  }
</script>
<script type="importmap">
{ "imports": {
    "new-request-form": "{{asset 'new-request-form-bundle.js'}}",
    "new-request-form-translations": "{{asset 'new-request-form-translations-bundle.js'}}",
    "request-list": "{{asset 'request-list-bundle.js'}}",
    "request-list-translations": "{{asset 'request-list-translations-bundle.js'}}",
    "service-catalog": "{{asset 'service-catalog-bundle.js'}}",
    "service-catalog-translations": "{{asset 'service-catalog-translations-bundle.js'}}",
    "approval-requests": "{{asset 'approval-requests-bundle.js'}}",
    "approval-requests-translations": "{{asset 'approval-requests-translations-bundle.js'}}",
    "flash-notifications": "{{asset 'flash-notifications-bundle.js'}}",
    "shared": "{{asset 'shared-bundle.js'}}",
    "ticket-fields": "{{asset 'ticket-fields-bundle.js'}}",
    "wysiwyg": "{{asset 'wysiwyg-bundle.js'}}"
} }
</script>
<script type="module">
  import { renderFlashNotifications } from "flash-notifications";
  renderFlashNotifications({{json settings}}, {{json help_center.base_locale}}, {{json help_center.locale}});
</script>
```

`new_request_page.hbs` — wrap the mount point in your own layout (intro, tips sidebar, cards):

```hbs
<h1>{{t 'submit_a_request'}}</h1>
<div id="new-request-form"></div>
<script type="module">
  import { renderNewRequestForm } from "new-request-form";
  const settings = {{json settings}};
  renderNewRequestForm(settings, {
    requestForm: {{json new_request_form}},
    newRequestPath: {{json (page_path 'new_request')}},
    parentId: {{json parent.id}},
    parentIdPath: {{json parent.url}},
    locale: {{json help_center.locale}},
    baseLocale: {{json help_center.base_locale}},
    hasAtMentions: {{json help_center.at_mentions_enabled}},
    userRole: {{json user.role}},
    userId: {{json user.id}},
    brandId: {{json brand.id}},
    organizations: {{json user.organizations}},
    wysiwyg: true,
    showSuggestedArticles: settings.show_suggested_articles ?? true,
    answerBotModal: {
      answerBot: {{#if answer_bot}}{{json answer_bot}}{{else}}null{{/if}},
      answerBotGenerativeExperience: {{#if answer_bot_generative_experience}}{{json answer_bot_generative_experience}}{{else}}null{{/if}},
      hasRequestManagement: {{json help_center.request_management_enabled}},
      isSignedIn: {{json signed_in}},
      helpCenterPath: {{json (page_path 'help_center')}},
      requestsPath: {{json (page_path 'requests')}},
      requestPath: {{json (page_path 'request' id=request_id)}}
    }
  }, document.getElementById("new-request-form"));
</script>
```

Other pages follow Copenhagen's templates for the same file name (copy the prop shapes exactly):
`requests_page` → `renderRequestList(settings, props, el)`; `service_list_page` → `renderServiceCatalogPage(el, settings,
baseLocale, helpCenterPath, locale)`; `service_page` → `renderServiceCatalogItem(el, settings, props)`;
`approval_request_list_page` / `approval_request_page` → `renderApprovalRequestList` / `renderApprovalRequest`.

The modules theme themselves from `settings.brand_color`, `brand_text_color`, `text_color`, `link_color`,
`hover_link_color`, `visited_link_color`, `background_color` — name your settings that way. Re-test these flows in
`zcli themes:preview` after every Copenhagen update.

## Localizing theme-only copy

`{{t}}` resolves only Help Center's keys (`references/t-keys.txt`). For anything else:

1. Prefer an existing key — `submit_a_request`, `promoted_articles`, `articles_in_section`, `was_this_article_helpful`,
   `return_to_top`, `back_to_homepage`, `no_results_unified_start_new_search`, `skip_navigation`, `toggle_navigation`…
2. Merchant-facing copy (hero title, "still need help" block, tips) → a `text` setting.
3. Strings your JavaScript creates (TOC title, "Copy link", reading time) → a small dictionary in the JS keyed by
   `document.documentElement.lang`, falling back to English. Pass server-translated strings to JS via
   `<template id="strings"><span data-key="search_clear">{{t 'search_clear'}}</span></template>` and `textContent`.
4. Merchant copy that must differ **per language**, or needs **line breaks** → Zendesk Dynamic Content. `text`
   settings hold one value for every locale and the Settings panel input is single-line. Ship a `text` setting as the
   default and a checkbox that switches to a Dynamic Content item the merchant creates (Admin Center → Workspaces →
   Agent tools → Dynamic content, one variant per language):

   ```hbs
   {{#if settings.use_dc_support_note}}
     <div class="support-note">{{dc 'theme_support_note'}}</div>
   {{else}}
     {{#if settings.support_note}}<p class="support-note">{{settings.support_note}}</p>{{/if}}
   {{/if}}
   ```

   Document the identifier (`theme_support_note`) in the theme's setup guide. Keep the `dc` identifier a string literal;
   an unknown identifier renders a default placeholder message instead of your text, which is why it sits behind a checkbox.

Pick the closest platform key before adding a setting: e.g. "Browse topics" → `categories` or `knowledge_base`,
"Contact us" → `submit_a_request`, "Still need help?" has no key → setting.

## Settings → design tokens

Expose a compact set of settings and map them to CSS custom properties in the root `style.css`; style everything else
against the properties. Light/dark: set `data-theme` on `<html>` from a `list` setting in an inline script in
`document_head.hbs` (before paint), and override tokens under `html[data-theme="dark"]` with `$dark_*` settings.

## Customize a template for specific categories/sections/articles

Branch on an entity id with an `is` block. Works in `category_page`, `section_page`, `article_page`.

```hbs
{{#is section.id 200646205}}
  <p><strong>Important security information.</strong></p>
{{/is}}
{{#is section.id 203133596}}
  <p>Videos available at <a href="https://example.com">Learning to fly</a></p>
{{/is}}
```
For a fundamentally different layout (not just a tweak), prefer Enterprise **alternate templates** instead — see `templates-reference.md`.

## Customize / hide languages in the language selector (header.hbs)

Rename a variant:
```hbs
{{#is current_locale.name 'English (US)'}}English{{else}}{{current_locale.name}}{{/is}}
```
Inside `{{#each alternative_locales}}`, rename each:
```hbs
{{#is name 'English (US)'}}English{{else}}{{name}}{{/is}}
```
Hide a language by skipping it:
```hbs
{{#each alternative_locales}}
  {{#is name 'Français'}}
    {{! do nothing }}
  {{else}}
    <a href="{{url}}" dir="{{direction}}" rel="nofollow" role="menuitem">{{name}}</a>
  {{/is}}
{{/each}}
```

## Let users sort article comments (article_page.hbs)

Iterate `comment_sorters` (a property on the article page):
```hbs
{{#if comments}}
  <div class="comment-sorter">
    {{t 'sort_by'}}
    {{#each comment_sorters}}
      <a aria-selected="{{selected}}" href="{{url}}">{{name}}</a>
    {{/each}}
  </div>
{{/if}}
```

## Rich-text comment editor (article_page.hbs)

Swap a plain textarea for the WYSIWYG editor inside the comment form:
```hbs
{{#form 'comment' class='comment-form'}}
  <div class="comment-avatar">{{user_avatar class='user-avatar'}}</div>
  <div class="comment-container">
    {{wysiwyg 'body'}}
    <div class="comment-form-controls">{{input type='submit'}}</div>
  </div>
{{/form}}
```

## Vote on comments (article_page.hbs)

Reuse the `vote` helper inside the comment loop:
```hbs
{{#each comments}}
  <li id="{{anchor}}" class="comment">
    <div class="comment-vote vote">
      {{vote 'up' class="vote-up" selected_class="vote-voted"}}
      {{vote 'sum' class="vote-sum"}}
      {{vote 'down' class="vote-down" selected_class="vote-voted"}}
    </div>
    ...
  </li>
{{/each}}
```

## Generative (AI) search answers (search_results.hbs)

Add the helper where the answer should appear:
```hbs
<section id="main-content" class="search-results-column">
  {{generative_answers}}
  <h1 class="search-results-subheading">{{t 'search_results'}}</h1>
  ...
</section>
```
Style it to match by ensuring your theme defines the expected color/font settings (`text_color`, `link_color`, `hover_link_color`, `visited_link_color`, `heading_font`, `text_font`) rather than hardcoding look-and-feel in CSS.

## Related / recent articles

Use `{{related_articles}}` and `{{recent_articles}}` (both on the article page; `recent_articles` = recently viewed) rather than hand-building these lists. On the home page, `promoted_articles` is a property you can iterate (`{{#each promoted_articles}}`), and `{{recent_activity}}` lists new articles/posts.

## Articles in this section (article page)

`section.articles` holds the first 10 articles; link to the section when `section.more_articles` is true:

```hbs
<ul>
  {{#each section.articles}}
    <li><a href="{{url}}" {{#is id ../article.id}}aria-current="page"{{/is}}>{{title}}</a></li>
  {{/each}}
</ul>
{{#if section.more_articles}}<a href="{{section.url}}">{{t 'see_more'}}</a>{{/if}}
```

## Other cookbook recipes (look up when needed)

The cookbook also covers: instant/autocomplete search, federated search sidebar filters, the new request-list experience, sorting on the Following / My Activities pages, CC'ing users on requests, follow-up request links, CSAT on solved tickets, content tags on articles/posts, badges, user profiles, subsections, the spam filter, approvals, and the service catalog. Pull the specific section from the cookbook URL above when a task calls for one — each lists the applicable template, the expression/object involved, and a reference link.
