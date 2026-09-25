# Curlybars templating language

Curlybars is Zendesk's server-side templating language for Help Center themes. It implements a large subset of [Handlebars](https://handlebarsjs.com). Templates are plain text files (`.hbs`) mixing HTML with `{{ }}` expressions that are resolved at render time. **Current version: v4** (`api_version` in `manifest.json`).

Source: <https://developer.zendesk.com/api-reference/help_center/help-center-templates/introduction> and <https://support.zendesk.com/hc/en-us/articles/4408824571674>

## Table of contents
- Expressions and literals
- Escaping: `{{ }}` vs `{{{ }}}`
- Help Center properties (paths, dot notation, `length`)
- Conditional helpers: `if`, `unless`, `is`
- How conditions are evaluated (truthiness)
- Iteration: `each`
- Context: `with` and `../` escaping
- Subexpressions
- Comments
- Hard rules and gotchas

## Expressions and literals

An expression is delimited by double curly brackets: `{{author.name}}`. An expression can contain:
- **Literals** — a string (single or double quotes), a number (positive/negative integer), or a boolean (`true`/`false`).
- **Help Center properties** — data exposed to the page, e.g. `article.title`.
- **Helpers** — actions, e.g. `{{asset 'logo.png'}}`.
- **Comments** — notes that don't render.

Nesting brackets directly (`{{ {{ ... }} }}`) is an error. To compose, use subexpressions with parentheses (below).

Helper invocation syntax:
```hbs
{{helper [positional-param ...] [key=value ...]}}
```
Only the helper name is mandatory. Example: `{{excerpt article.title characters=50}}`.

## Escaping: double vs triple

- `{{value}}` — HTML-escaped output. Default for anything user-influenced.
- `{{{value}}}` — raw, unescaped output. Use only for trusted HTML or values like font stacks that must render literally (e.g. `{{{settings.heading_font}}}`).

## Help Center properties

Each page template has access to a set of objects. Use dot notation to read nested values; the full dotted name is the property's *path*.

```hbs
<h1>{{article.title}}</h1>
<p>Author: {{article.author.name}}</p>
{{article.body}}
```

A value may be a string, integer, boolean, object, or an array of objects. Arrays have an implicit `length`:
```hbs
<p>This article has {{comments.length}} comments.</p>
```

Which objects exist per page is documented in `helpers-and-objects.md` and the page-specific docs under <https://developer.zendesk.com/api-reference/help_center/help-center-templates/>.

## Conditional helpers

### if / if-else
```hbs
{{#if article.internal}}
  <p>This article is internal.</p>
{{else}}
  <p>Public article.</p>
{{/if}}
```

### unless
```hbs
{{#unless comments}}
  <p>No comments yet.</p>
{{/unless}}
```

### is / is-else (equality)
`is` is a Curlybars custom helper for value equality — plain Handlebars has no `is`.
```hbs
{{#is article.author.name 'John Venturini'}}
  <p>Authored by John.</p>
{{else}}
  <p>Someone else wrote this.</p>
{{/is}}
```

### How conditions are evaluated (truthiness)
When a condition isn't already boolean:
- number: `0` is false, any other number is true
- string: empty string is false, any other string is true
- collection: empty collection is false, any non-empty collection is true
- `null` is false

## Iteration: each

`each` iterates an array and sets the block context to each item. Inside the block, reference item properties directly — do **not** prefix with the array's singular name.

```hbs
{{#each comments}}
  <li>
    <img src="{{author.avatar_url}}" alt="Avatar" />
    {{author.name}} commented on {{created_at}}.
  </li>
{{/each}}
```
Here `author` resolves against the current comment, not a top-level object. To reach the outer context from inside, use `../` (see below).

## Context: with and ../ escaping

`with` sets a context so you can drop repeated path prefixes:
```hbs
{{#with article.author}}
  <p>Author: {{name}}</p>
  <img src="{{avatar_url}}">
{{/with}}
```
To read something outside the current context, climb with `../`:
```hbs
{{#with article.author}}
  {{../article.title}}
  <p>{{name}}</p>
{{/with}}
```
Each `../` climbs one level; stack them to climb further (`{{../../article.title}}`). `with` also accepts an `{{else}}` block for when the context is falsy.

Pass the current root context into a helper with `this`:
```hbs
{{#with article}}
  {{my_helper this}}
{{/with}}
```

## Subexpressions

Parentheses let you feed one helper's result into another, and let helpers appear inside conditionals/iterators.
```hbs
{{search placeholder=(dc "search_text")}}
{{search placeholder=(excerpt (dc "search_text"))}}

{{#if (compare collection.length "==" 0)}}
  <div>Empty collection.</div>
{{else}}
  <div>{{collection.length}} items</div>
{{/if}}

{{#each (slice (filter user.badges on="category_slug" equals="achievements") 0 4)}}
  <section><h3>{{name}}</h3><div>{{description}}</div></section>
{{/each}}
```

## Comments
```hbs
{{! short note }}
{{!-- block comment that can wrap other {{expressions}} while debugging --}}
```

## Hard rules and gotchas

- **No partials.** Help Center themes do not support Handlebars partials (`{{> name}}`). Reuse markup via `header.hbs`/`footer.hbs`, JS, or repetition.
- **No arbitrary helpers.** Only Curlybars built-ins + Help Center custom helpers work. A helper that works in vanilla Handlebars/Node may not exist here. Check `helpers-and-objects.md`.
- **Version sensitivity.** Helpers can be deprecated between templating versions; previewing locally surfaces deprecation warnings for the theme's `api_version`.
- **Settings as variables.** Manifest settings appear as `{{settings.identifier}}` in templates (and `$identifier` in CSS). They can be passed to helpers like any object: `{{#is settings.enabled}} ... {{/is}}`.
- **Escape control characters in HTML attributes** by preferring `{{ }}`; reserve `{{{ }}}` for known-safe values.
