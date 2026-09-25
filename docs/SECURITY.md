# SECURITY.md

> Technical security architecture, threat model, and engineering hard rules. For public vulnerability disclosure and supported versions, see root [SECURITY.md](../SECURITY.md).

## Hard Rules

These rules are **absolute**. Violating any of them requires a `DECISIONS.md` entry that explicitly supersedes the rule, with security review.

1. **Never** log Zendesk API tokens, credentials, or sensitive headers — even in verbose debug output.
2. **Never** hardcode Zendesk subdomains, API tokens, or user credentials in source files, scripts, or theme templates.
3. **Never** execute untrusted user input directly in shell commands or string-interpolated network requests.
4. **Always** sanitize and escape dynamic data rendered in Zendesk Curlybars templates to prevent Cross-Site Scripting (XSS).
5. **Always** transmit Zendesk API requests over TLS 1.3 / HTTPS.
6. **Never** commit `.env` files or API secrets into git.

## Authentication & API Access

- **Authentication Method:** Zendesk API Basic Auth using email/token combination (`{email}/token:{api_token}`) or OAuth Bearer tokens.
- **Credential Storage:** Passed at runtime via command-line arguments or environment variables (`ZENDESK_SUBDOMAIN`, `ZENDESK_EMAIL`, `ZENDESK_TOKEN`). Never stored in repository files.

## Threat Model — Top Concerns

1. **API Token Exposure:**
   - *Risk:* Leakage of Zendesk admin API tokens granting unauthorized access to Zendesk Guide and ticketing data.
   - *Mitigation:* Explicit `.gitignore` rules for environment files, parameterized script arguments, and strict exclusion of credentials from logs.

2. **Template Injection / Cross-Site Scripting (XSS):**
   - *Risk:* Unsanitized user inputs or custom script modifications in theme `.hbs` files executing malicious code in Help Center users' browsers.
   - *Mitigation:* Adherence to Zendesk Curlybars safe rendering defaults, avoiding unescaped triple-curly braces (`{{{...}}}`) with untrusted variables, and maintaining strict Content Security Policy (CSP).

3. **Theme Archive Manipulation:**
   - *Risk:* Inadvertent packaging of sensitive local files into theme `.zip` archives sent to Zendesk.
   - *Mitigation:* `deploy_theme.py` strictly whitelists expected theme directories and files (`templates/`, `settings/`, `assets/`, `manifest.json`, `style.css`, `script.js`).
