# TESTING.md

> Testing and verification strategy for Zendesk Help Center Themes and automation scripts.

## Test Strategy Overview

The testing strategy encompasses static validation of theme assets, Python script verification, and local theme previewing.

## Testing Layers

### 1. Static Theme Validation

Run the built-in heuristic validator against the theme folder to verify manifest integrity, settings types, and template file conventions before deployment:

```bash
python3 zendesk-help-center-themes/scripts/validate_theme.py zendesk-help-center-themes/assets/starter-theme
```

**Verification checks:**
- `manifest.json` exists and parses valid JSON.
- Required root keys (`name`, `author`, `version`, `api_version`) are present.
- `api_version` is equal to `2`.
- `settings` group and variable identifiers match lowercase alphanumeric regex `^[a-z0-9_]+$`.
- Required setting file variables (`logo`, `favicon`) are present.
- `templates/` folder contains recognizable Zendesk Guide templates.

### 2. Local Theme Previewing

Use the official Zendesk CLI tool (`@zendesk/zcli`) to preview theme templates and asset rendering in a local browser environment:

```bash
npx @zendesk/zcli themes:preview zendesk-help-center-themes/assets/starter-theme
```

### 3. Deployment Script Verification

Verify that deployment scripts handle missing credentials gracefully and validate theme directories before network execution:

```bash
# Verify argument parsing and validation failure handling
python3 zendesk-help-center-themes/scripts/deploy_theme.py non_existent_dir
```

## Continuous Quality Standards

- All Python scripts must execute cleanly with Python 3.8+ without external package requirements.
- Theme templates must conform to HTML5 and accessibility (a11y) standards, maintaining WCAG AA contrast and keyboard navigability.
