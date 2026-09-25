# Accessibility, SEO, and Marketplace readiness

A theme that imports cleanly is the floor, not the bar — especially for a productized or Marketplace theme. This checklist covers quality gates beyond a successful import.

## Accessibility

The official Copenhagen theme is built to be responsive and accessible, and Zendesk runs automated accessibility audits against it; aim for the same baseline. Practical targets (WCAG 2.1 AA):

- **Semantic structure:** one `<h1>` per page (the article/section/category title), logical heading order, landmark elements (`<header>`, `<nav>`, `<main>`, `<footer>`), and a skip-to-content link in `header.hbs`.
- **Keyboard:** every interactive control reachable and operable by keyboard; visible focus styles (don't remove outlines without replacing them); dropdowns (e.g. the language selector) operable without a mouse.
- **Names and roles:** images have meaningful `alt` (empty `alt=""` for decorative); form fields have associated labels; menus use appropriate `role`/`aria-*` (see the cookbook language-selector markup which uses `role="menu"`/`menuitem` and `aria-haspopup`).
- **Contrast:** text/background combinations meet contrast ratios. Because colors come from settings, pick accessible defaults and document that merchants must keep contrast when they re-skin.
- **Don't fight the advanced helpers:** widgets like `request_form`, `wysiwyg`, `generative_answers` ship accessible markup; heavily overriding their internals with CSS/JS can break it.
- **Test:** run an automated audit (axe, Lighthouse) during local preview, then do a manual keyboard + screen-reader pass on article, search, and request-form flows.

## Responsiveness

- Mobile-first CSS; verify at narrow (~360px), tablet, and desktop widths.
- The scaffold exposes a `content_max_width` setting and collapses multi-column layouts at small breakpoints — keep that pattern.
- Tap targets large enough; no horizontal scroll; sticky sidebars (e.g. an article TOC) must fall back to static on mobile.

## SEO and metadata

- Set a real `<title>` (`{{page_title}}`) and a meta description in `document_head.hbs`; expose Open Graph/Twitter tags where useful.
- Use proper heading hierarchy and descriptive link text (`{{#link}}` block form), not "click here".
- Don't block crawlers on public content; keep canonical/locale handling intact via `alternative_locales`.
- Let the platform inject compiled CSS/JS — don't duplicate or block render with large head scripts.

## Performance

- Reference assets via the `asset` helper so they're CDN-served and cache-busted on install.
- Keep bundled JS lean; defer non-critical scripts. If using React/Garden components (as Copenhagen 4.x does), bundle them and import via the `asset` helper — don't ship unbundled modules.
- Optimize images and provide appropriately sized hero/background images.

## Localization

- Wrap all visible template copy in `{{t 'key'}}`; never hardcode UI strings.
- Reserve top-level `translations.yml` for Settings-panel labels only; manage `translations/<locale>.json` for the rest.
- Test at least one RTL locale if the theme targets multilingual help centers (`dir="{{direction}}"`).

## Marketplace submission readiness

Selling on the Zendesk Marketplace adds review requirements on top of a clean import. Expect to need:

- A theme that is responsive, accessible, and works across the standard page set (KB, search, requests, and community if claimed).
- Documented, sensibly-grouped settings with clear labels/descriptions and good defaults (including required `logo`/`favicon`).
- Versioning and a changelog; a support contact/path; clear install and customization docs.
- No reliance on unsupported files/helpers; passes within plan/size limits.
- Brand/quality conformance per Zendesk's current partner guidelines.

Marketplace and partner requirements change over time — verify the current submission checklist in Zendesk's partner/Marketplace documentation before submitting rather than relying on this list alone.

## Pre-delivery gate (run all)

1. `python3 scripts/validate_theme.py <theme>` passes with no errors.
2. `zcli themes:preview` shows no unknown-helper/deprecation warnings for the theme's `api_version`.
3. Automated a11y audit (axe/Lighthouse) clean on article, search, and new-request pages; manual keyboard pass done.
4. Responsive check at 360px / tablet / desktop.
5. All visible copy localized via `{{t}}`; `logo`/`favicon` present with defaults.
6. Within theme/file/settings limits (see `dev-and-deploy.md`).
