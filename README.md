# Zendesk Skills

A comprehensive toolkit, agent skills, templates, and automation workflows for developing, validating, and deploying custom Zendesk Guide Help Center themes.

## Quickstart

### Prerequisites
- Python 3.8+
- Node.js 18+ (for `@zendesk/zcli` previewing)

### Validation & Preview

1. **Validate a theme:**
   ```bash
   python3 zendesk-help-center-themes/scripts/validate_theme.py zendesk-help-center-themes/assets/starter-theme
   ```

2. **Preview locally with Zendesk CLI:**
   ```bash
   npx @zendesk/zcli themes:preview zendesk-help-center-themes/assets/starter-theme
   ```

3. **Deploy to Zendesk Guide:**
   ```bash
   python3 zendesk-help-center-themes/scripts/deploy_theme.py zendesk-help-center-themes/assets/starter-theme \
     --subdomain YOUR_SUBDOMAIN \
     --email YOUR_EMAIL \
     --token YOUR_API_TOKEN
   ```

## Stack

- **Automation:** Python 3 (standard library)
- **Themes & Templating:** Curlybars (Zendesk Handlebars dialect), HTML5, CSS3, JavaScript (ES6+)
- **Platform:** Zendesk Guide / Help Center (API v2)
- **CLI & Tooling:** `@zendesk/zcli`

## Project Structure

```
.
├── .editorconfig                          # Code style & formatting rules
├── .gitignore                             # Ignore rules
├── AGENTS.md                              # AI coding agent briefing packet
├── CHANGELOG.md                           # Release history (Keep a Changelog)
├── CLAUDE.md                              # Pointer to AGENTS.md
├── CODE_OF_CONDUCT.md                     # Community code of conduct
├── CONTRIBUTING.md                        # Contribution guide
├── GEMINI.md                              # Pointer to AGENTS.md
├── LICENSE                                # MIT License
├── README.md                              # Human-facing overview & quickstart
├── REPORTING.md                           # Issue reporting guidelines
├── SECURITY.md                            # Public security policy & disclosure
├── docs/                                  # Canonical project documentation
│   ├── ARCHITECTURE.md                    # System architecture & layers
│   ├── DECISIONS.md                       # Architecture decision log (ADR)
│   ├── PRODUCT.md                         # Product scope & goals
│   ├── SECURITY.md                        # Technical threat model & hard rules
│   └── TESTING.md                         # Testing & validation strategy
└── zendesk-help-center-themes/            # Zendesk Help Center Themes skill
    ├── SKILL.md                           # Skill definition & guidelines
    ├── assets/starter-theme/              # Production-ready starter theme
    ├── references/                        # Curlybars, manifest, and template docs
    └── scripts/                           # Validation and deployment scripts
```

## 📚 Documentation

For technical details, project guidelines, and development context:

- 🤖 **For AI Coding Agents:** Refer to [AGENTS.md](AGENTS.md) for development commands, project conventions, and agent instructions.
- 🏗️ **Architecture:** See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the system structure, major components, and workflows.
- ⚖️ **Decision Log:** See [docs/DECISIONS.md](docs/DECISIONS.md) for architectural decisions, rationale, and established conventions.
- 🎯 **Product Scope:** See [docs/PRODUCT.md](docs/PRODUCT.md) for product goals, supported features, and planned work.
- 🛡️ **Security Guidelines:** See [docs/SECURITY.md](docs/SECURITY.md) for security practices and configuration guidance.
- 🧪 **Testing Strategy:** See [docs/TESTING.md](docs/TESTING.md) for test coverage, commands, and verification procedures.

## 🐛 Issues & Troubleshooting

Found a bug or have a feature request?

- Read the [Issue Reporting Guide](REPORTING.md) before submitting an issue.
- Please report issues via the [GitHub Issue Tracker](https://github.com/asifiqbal91/zendesk-skills/issues).

## 🤝 Contributing

Contributions are welcome! Read the [Contribution Guide](CONTRIBUTING.md) for development setup, contribution conventions, and the pull request process.

## ⭐ Support Us

If Zendesk Skills is useful to you:

- ⭐ **Star this repository** to help others discover the project.
- 📣 **Spread the word** by sharing it with your network.
- ☕ **Support Our Work** — [Donate](https://asifiqbal.rocks/donation?utm_source=zendesk_skills&utm_medium=github_readme&utm_campaign=readme&ref=zendesk-skills-readme) to help us maintain and grow our open-source projects.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
