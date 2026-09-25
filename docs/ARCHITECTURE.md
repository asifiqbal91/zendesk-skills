# ARCHITECTURE.md

> Technical structure. How the pieces fit together. Not how to use the project (see AGENTS.md).

## High-level diagram

```
  ┌─────────────────────────────────────────────────────────────┐
  │                       zendesk-skills                        │
  │                                                             │
  │   ┌─────────────────────┐       ┌───────────────────────┐   │
  │   │     SKILL.md        │  ───  │ References & Guides   │   │
  │   │  (Agent Workflow)   │       │ (Curlybars, API v2)   │   │
  │   └──────────┬──────────┘       └───────────────────────┘   │
  │              │                                              │
  │              ▼                                              │
  │   ┌─────────────────────┐       ┌───────────────────────┐   │
  │   │   Starter Theme     │  ───  │   Python Scripts      │   │
  │   │ (Templates, Styles) │       │ (validate & deploy)   │   │
  │   └─────────────────────┘       └───────────┬───────────┘   │
  └─────────────────────────────────────────────┼───────────────┘
                                                │
                                                ▼ (HTTP REST API)
                                    ┌───────────────────────┐
                                    │  Zendesk Guide Cloud  │
                                    │ (Help Center Themes)  │
                                    └───────────────────────┘
```

## Layers

### 1. Agent Skill Layer (`zendesk-help-center-themes/SKILL.md`)
Orchestrates agent behavior for theme creation, modification, validation, and deployment.

### 2. Assets & Starter Theme (`zendesk-help-center-themes/assets/starter-theme/`)
Contains production-ready standard templates (`templates/*.hbs`), stylesheet (`style.css`), client-side scripts (`script.js`), settings (`settings/`), and configuration manifest (`manifest.json`).

### 3. Tooling & Automation (`zendesk-help-center-themes/scripts/`)
- `validate_theme.py`: Static analysis linter checking manifest validity, required files, Curlybars template names, and identifier formats.
- `deploy_theme.py`: Archives the theme directory into a zip bundle and interacts with the Zendesk Guide Themes API (`/api/v2/guide/theming/jobs/themes/imports`).

### 4. Reference Library (`zendesk-help-center-themes/references/`)
Comprehensive documentation of Curlybars syntax, Zendesk objects, manifest settings schemas, and deployment instructions.

## Request & Deployment Lifecycle

```
1. Developer / Agent builds theme templates in assets/ or project folder
2. validate_theme.py checks:
   ├── manifest.json structure & required keys (name, author, version, api_version: 2)
   ├── settings schema & identifier regex
   └── template names against Zendesk Guide standard templates
3. deploy_theme.py packages theme into in-memory zip archive
4. API request sent to Zendesk Guide Theme Import endpoint
5. Job polling verifies successful theme creation
```

## Patterns We Use

- **Self-contained automation:** Python scripts rely exclusively on Python standard libraries without requiring heavy external dependencies.
- **Strict static validation:** Heuristic linting before initiating network requests to minimize Zendesk API errors.
- **Fail-safe packaging:** Clean zip archive creation omitting local VCS or temporary files.

## Patterns We Avoid

- Hardcoding credentials or tokens inside repository files.
- Modifying Zendesk Guide theme files without pre-validation.
