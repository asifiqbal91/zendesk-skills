# PRODUCT.md

> What we're building, for whom, and what is explicitly NOT in scope.
> This is the canonical scope document. Agents must check here before adding features.

## Product

A comprehensive agent skill, reference system, and starter kit for developing, linting, validating, and deploying custom Zendesk Guide Help Center themes.

## Target user

- Developers and technical support engineers building or maintaining custom Zendesk Help Center themes.
- AI coding agents orchestrating theme generation, audits, and deployments.

## Anti-persona

- General end-users seeking basic Help Center article content creation.
- Developers looking for Zendesk Support Apps (ZAF apps) — this skill is strictly focused on Guide / Help Center themes.

## Core value

Provides automated heuristic validation, comprehensive Curlybars helper references, and production-ready starter assets that prevent broken Zendesk theme imports and deployment failures.

## In scope (current phase)

- Zendesk Guide API v2 theme development and structure.
- Pre-import validation script (`validate_theme.py`) checking manifest, settings, and templates.
- Automated zip-and-deploy script (`deploy_theme.py`) for the Zendesk Guide Themes API.
- Modular starter theme implementing standard templates, settings schema, and accessible patterns.
- Deep documentation covering Curlybars helpers, template hierarchies, and marketplace guidelines.

## Explicitly out of scope

- Zendesk Support App Framework (ZAF v2) sidebar / ticket apps — reason: separate architectural domain.
- Live theme editing without API/CLI integration.
- Proprietary Zendesk server-side validator replacement (heuristic pre-linter only).

## Non-goals

- Not a visual WYSIWYG editor for Zendesk themes.
- Not an automated migration tool from legacy v1 Help Center themes.

## Success criteria

- `validate_theme.py` passes 100% on valid starter themes without false positives.
- `deploy_theme.py` successfully uploads and publishes themes to target Zendesk instances.
- Zero broken imports caused by missing required manifest fields or invalid template names.
