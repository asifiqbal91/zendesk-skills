# Recipes

Practical, verified snippets distilled from the Zendesk Help Center templating cookbook (<https://support.zendesk.com/hc/en-us/articles/4408832681626>). Zendesk doesn't support custom code, and exact markup varies by theme/`api_version` — preview locally after applying.

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

Use the advanced helpers `{{related_articles}}` (article page) and `{{recent_articles}}` (home/landing) rather than hand-building these lists.

## Other cookbook recipes (look up when needed)

The cookbook also covers: instant/autocomplete search, federated search sidebar filters, the new request-list experience, sorting on the Following / My Activities pages, CC'ing users on requests, follow-up request links, CSAT on solved tickets, content tags on articles/posts, badges, user profiles, subsections, the spam filter, approvals, and the service catalog. Pull the specific section from the cookbook URL above when a task calls for one — each lists the applicable template, the expression/object involved, and a reference link.
