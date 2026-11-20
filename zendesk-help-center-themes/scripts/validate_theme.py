#!/usr/bin/env python3
"""
validate_theme.py — pre-import check for a Zendesk Guide Help Center theme
(Templating API v4).

Catches what makes an import job fail (InvalidManifest, InvalidSetting,
InvalidTemplates, FileNotFound, FileTooBig, TooManySettings…) and what imports
but renders broken (custom {{t}} keys, removed helpers, wrong property paths).

Usage:
    python3 validate_theme.py path/to/theme

Exit code 0 = no errors (warnings allowed); 1 = errors found; 2 = bad invocation.

Checks
  - Required files; standard templates present (warning).
  - manifest.json: root keys, api_version 4, setting types, identifier format and
    length, label/description length (resolved via translations/<locale>.json),
    list options, range integers, checkbox booleans, color hex, file settings
    with no `value` and a default in settings/, logo + favicon, 200-setting cap.
  - templates: partials, triple-stache, `~` on comments, removed v4 helpers,
    property paths that do not exist in v4, block balance, {{t}} keys against
    references/t-keys.txt, settings.X declared, {{asset}} targets exist,
    hardcoded assets/ paths.
  - style.css: every $X declared.
  - Module bundles in assets/ are real ES modules, not placeholder stubs.
  - Limits: asset name ≤ 50 chars, asset ≤ 5 MB, assets ≤ 50 MB, theme ≤ 55 MB,
    template/style.css/script.js ≤ 800 KB.

It is a linter, not Zendesk's validator. Always also run `zcli themes:preview`.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
T_KEYS_FILE = HERE.parent / "references" / "t-keys.txt"

REQUIRED_ROOT_KEYS = ["name", "author", "version", "api_version"]
REQUIRED_FILE_VARS = {"logo", "favicon"}
IDENTIFIER_RE = re.compile(r"^[a-z0-9_]+$")
VALID_SETTING_TYPES = {"text", "checkbox", "range", "list", "color", "file"}
STANDARD_TEMPLATES = [
    "document_head", "header", "footer", "home_page", "category_page", "section_page",
    "article_page", "search_results", "error_page", "new_request_page", "request_page",
    "requests_page", "subscriptions_page", "contributions_page", "user_profile_page",
    "community_topic_list_page", "community_topic_page", "community_post_list_page",
    "community_post_page", "new_community_post_page",
]
LIMITS = {
    "settings": 200, "identifier": 30, "label": 40, "description": 80, "list_options": 20,
    "text_value": 1000, "asset_name": 50, "asset_bytes": 5 * 1024 ** 2,
    "assets_total": 50 * 1024 ** 2, "theme_total": 55 * 1024 ** 2, "file_bytes": 800 * 1024,
}
# Helpers removed in Templating API v4: import fails with "'X' does not exist".
REMOVED_HELPERS = {
    "request_form": "render new_request_form with Copenhagen's new-request-form module (see references/recipes.md)",
    "comment_form": "use {{#form 'comment'}} … {{/form}}",
    "filter_form": "use Copenhagen's request-list module",
    "user_info": "use {{user_name}} / {{user_avatar}}",
}
DEPRECATED_HELPERS = {"request_list": "use Copenhagen's request-list module"}
# Property paths that do not exist in v4 (seen as import errors or blank output).
BAD_PATHS = {
    r"\{\{\s*page_title\s*\}\}": "page_title is not a v4 property; Zendesk injects <title> itself",
    r"\berror\.(title|message|status)\b": "error_page exposes top-level `error` (string) and `status_code`",
    r"\buser\.created_at\b": "user_profile_page uses top-level `member_since`",
    r"\barticle\.attachments\b": "attachments is top-level on article_page",
    r"\bhelp_center\.url\b": "use {{page_path 'help_center'}}",
}

errors, warnings = [], []
err, warn = errors.append, warnings.append


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"{path.name} is not valid JSON: {e}")
        return None


def check_structure(root: Path):
    for name in ["manifest.json", "style.css", "script.js"]:
        if not (root / name).is_file():
            err(f"{name} is missing (required at theme root).")
        elif name != "manifest.json" and (root / name).stat().st_size > LIMITS["file_bytes"]:
            err(f"{name} exceeds 800 KB.")
    tdir = root / "templates"
    if not tdir.is_dir():
        err("templates/ directory is missing (required).")
        return
    for t in STANDARD_TEMPLATES:
        if not (tdir / f"{t}.hbs").is_file():
            warn(f"templates/{t}.hbs missing — Zendesk falls back to defaults; ship the full set for a portable theme.")


def check_manifest(root: Path):
    mpath = root / "manifest.json"
    manifest = load_json(mpath) if mpath.is_file() else None
    if not manifest:
        return {}
    locale = manifest.get("default_locale", "en-us")
    tpath = root / "translations" / f"{locale}.json"
    tr = (load_json(tpath) or {}) if tpath.is_file() else {}
    res = lambda s: tr.get(s, s) if isinstance(s, str) else ""

    for key in REQUIRED_ROOT_KEYS:
        if key not in manifest:
            err(f"manifest.json is missing required root key '{key}'.")
    if manifest.get("api_version") != 4:
        err(f"api_version is {manifest.get('api_version')}; v1–v3 are being retired — use 4.")
    if "version" in manifest and not re.match(r"^\d+\.\d+\.\d+$", str(manifest["version"])):
        err("manifest version must be MAJOR.MINOR.PATCH.")

    settings = manifest.get("settings", [])
    if not isinstance(settings, list):
        err("manifest.json 'settings' must be an array of setting groups.")
        return {}

    declared = {}
    settings_files = {p.stem for p in (root / "settings").glob("*")} if (root / "settings").is_dir() else set()
    for group in settings:
        if not isinstance(group, dict):
            err("Each settings entry must be a group object with 'label' and 'variables'.")
            continue
        if len(res(group.get("label"))) > LIMITS["label"]:
            err(f"Setting group label too long (> {LIMITS['label']}): {group.get('label')}")
        for var in group.get("variables", []):
            ident = var.get("identifier")
            if not ident:
                err("A setting variable is missing an 'identifier'.")
                continue
            if not IDENTIFIER_RE.match(ident):
                err(f"Setting '{ident}': identifier must match [a-z0-9_] (hyphens break $var and settings.x).")
            if len(ident) > LIMITS["identifier"]:
                err(f"Setting '{ident}': identifier longer than {LIMITS['identifier']} chars.")
            if ident in declared:
                err(f"Setting '{ident}': duplicate identifier.")
            declared[ident] = var
            vtype = var.get("type")
            if vtype not in VALID_SETTING_TYPES:
                err(f"Setting '{ident}': invalid type '{vtype}'. Valid: {', '.join(sorted(VALID_SETTING_TYPES))} (no textarea).")
            if not var.get("label"):
                err(f"Setting '{ident}': missing 'label'.")
            elif len(res(var["label"])) > LIMITS["label"]:
                err(f"Setting '{ident}': label longer than {LIMITS['label']} chars.")
            if len(res(var.get("description", ""))) > LIMITS["description"]:
                err(f"Setting '{ident}': description longer than {LIMITS['description']} chars.")
            value = var.get("value")
            if vtype == "file":
                if "value" in var:
                    err(f"Setting '{ident}': file settings must not have a 'value'.")
                if ident not in settings_files:
                    err(f"Setting '{ident}': no default file settings/{ident}.<ext>.")
            elif vtype == "checkbox" and not isinstance(value, bool):
                err(f"Setting '{ident}': checkbox value must be true/false.")
            elif vtype == "range":
                nums = [var.get("min"), var.get("max"), value]
                if not all(isinstance(n, int) and not isinstance(n, bool) for n in nums):
                    err(f"Setting '{ident}': range min/max/value must be integers.")
                elif not var["min"] <= value <= var["max"]:
                    err(f"Setting '{ident}': value outside min/max.")
                if "step" in var:
                    warn(f"Setting '{ident}': 'step' is not a documented range attribute.")
            elif vtype == "list":
                opts = var.get("options", [])
                if not 2 <= len(opts) <= LIMITS["list_options"]:
                    err(f"Setting '{ident}': list needs 2–{LIMITS['list_options']} options.")
                if any(len(res(o.get("label", ""))) > LIMITS["label"] for o in opts):
                    err(f"Setting '{ident}': an option label is longer than {LIMITS['label']} chars.")
                if value not in [o.get("value") for o in opts]:
                    err(f"Setting '{ident}': default value is not one of the options.")
            elif vtype == "text":
                if not isinstance(value, str):
                    err(f"Setting '{ident}': text value must be a string.")
                elif len(value) > LIMITS["text_value"]:
                    err(f"Setting '{ident}': text value longer than {LIMITS['text_value']} chars.")
            elif vtype == "color" and not re.match(r"^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?$", str(value)):
                err(f"Setting '{ident}': color value must be hex (#RRGGBB).")

    for req in REQUIRED_FILE_VARS:
        if declared.get(req, {}).get("type") != "file":
            err(f"Required file setting '{req}' is missing (identifier '{req}', type 'file').")
    if len(declared) > LIMITS["settings"]:
        err(f"{len(declared)} settings exceeds the {LIMITS['settings']}-setting limit.")
    return declared


def strip_comments(text: str) -> str:
    return re.sub(r"\{\{!--.*?--\}\}|\{\{!.*?\}\}", "", text, flags=re.S)


def check_templates(root: Path, declared: dict):
    tdir = root / "templates"
    if not tdir.is_dir():
        return
    valid_keys = set()
    if T_KEYS_FILE.is_file():
        valid_keys = {l.strip() for l in T_KEYS_FILE.read_text().splitlines() if l.strip() and not l.startswith("#")}
    else:
        warn(f"{T_KEYS_FILE} not found — skipping {{{{t}}}} key check.")
    assets = {p.name for p in (root / "assets").glob("*")} if (root / "assets").is_dir() else set()

    for tpl in sorted(tdir.rglob("*.hbs")):
        rel = tpl.relative_to(root).as_posix()
        raw = tpl.read_text(encoding="utf-8")
        if len(raw.encode()) > LIMITS["file_bytes"]:
            err(f"{rel}: template exceeds 800 KB.")
        if re.search(r"\{\{~\s*!", raw):
            err(f"{rel}: '~' is not allowed on comments ({{{{~! … }}}}).")
        code = strip_comments(raw)

        if re.search(r"\{\{>", code):
            err(f"{rel}: uses a partial ({{{{> …}}}}). Help Center themes do NOT support partials.")
        if "{{{" in code:
            err(f"{rel}: triple-stache {{{{{{ }}}}}} — use {{{{ }}}}; bodies are already safe HTML. Put font stacks in style.css ($var).")
        if re.search(r'(?:src|href)\s*=\s*["\']/?assets/', code):
            err(f"{rel}: hardcoded assets/ path. Use {{{{asset 'file'}}}}.")
        for helper, fix in REMOVED_HELPERS.items():
            if re.search(r"\{\{#?\s*" + helper + r"\b", code):
                err(f"{rel}: '{helper}' was removed in Templating API v4 — {fix}.")
        for helper, fix in DEPRECATED_HELPERS.items():
            if re.search(r"\{\{#?\s*" + helper + r"\b", code):
                warn(f"{rel}: '{helper}' is deprecated — {fix}.")
        for pattern, why in BAD_PATHS.items():
            if re.search(pattern, code):
                err(f"{rel}: {why}.")
        if tpl.name == "section_page.hbs" and re.search(r"\{\{#each\s+articles\b", code):
            err(f"{rel}: use section.articles (bare `articles` does not exist on section_page).")

        stack = []
        for m in re.finditer(r"\{\{~?\s*([#/])\s*([\w.]+)", code):
            kind, name = m.groups()
            if kind == "#":
                stack.append(name)
            elif not stack:
                err(f"{rel}: closing {{{{/{name}}}}} with no matching opener.")
            elif stack[-1] != name:
                err(f"{rel}: block mismatch — {{{{#{stack[-1]}}}}} closed by {{{{/{name}}}}}.")
                stack.pop()
            else:
                stack.pop()
        for leftover in stack:
            err(f"{rel}: unclosed block {{{{#{leftover}}}}}.")

        for m in re.finditer(r"settings\.([a-z0-9_]+)", code):
            if declared and m.group(1) not in declared:
                err(f"{rel}: settings.{m.group(1)} is not declared in manifest.json.")
        if valid_keys:
            for m in re.finditer(r"[{(]t\s+(['\"])([a-z0-9_]+)\1", code):
                if m.group(2) not in valid_keys:
                    err(f"{rel}: {{{{t '{m.group(2)}'}}}} is not a Help Center translation key "
                        f"(custom keys render broken — use a platform key or a text setting).")
        for m in re.finditer(r"\basset\s+(['\"])([^'\"]+)\1", code):
            if m.group(2) not in assets:
                err(f"{rel}: {{{{asset '{m.group(2)}'}}}} not found in assets/.")


def check_style(root: Path, declared: dict):
    path = root / "style.css"
    if not path.is_file() or not declared:
        return
    css = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
    for m in re.finditer(r"\$([a-z0-9_]+)", css):
        if m.group(1) not in declared:
            err(f"style.css: ${m.group(1)} is not declared in manifest.json.")
    if re.search(r"#\{\$", css):
        warn("style.css: #{$var} interpolation is not documented by Zendesk; prefer calc($var * 1px).")


def check_sizes(root: Path):
    adir = root / "assets"
    total_assets = 0
    if adir.is_dir():
        for p in adir.iterdir():
            if not p.is_file():
                err(f"assets/{p.name}: subfolders are not supported in assets/.")
                continue
            size = p.stat().st_size
            total_assets += size
            if len(p.name) > LIMITS["asset_name"]:
                err(f"assets/{p.name}: name longer than {LIMITS['asset_name']} chars.")
            if size > LIMITS["asset_bytes"]:
                err(f"assets/{p.name}: larger than 5 MB.")
            if p.suffix == ".map":
                err(f"assets/{p.name}: source maps should not ship.")
            if p.name.endswith("-bundle.js") or p.name == "es-module-shims.js":
                head = p.read_text(encoding="utf-8", errors="ignore")
                if "PLACEHOLDER" in head[:500] or "export" not in head:
                    err(f"assets/{p.name}: placeholder, not a real ES module bundle — the request form/list will not render. "
                        f"Run scripts/vendor_copenhagen_modules.sh (or copy the real file from a Copenhagen checkout).")
    if total_assets > LIMITS["assets_total"]:
        err(f"assets/ total {total_assets / 1e6:.1f} MB exceeds 50 MB.")
    total = sum(p.stat().st_size for p in root.rglob("*") if p.is_file() and p.suffix != ".zip")
    if total > LIMITS["theme_total"]:
        err(f"Theme total {total / 1e6:.1f} MB exceeds 55 MB.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_theme.py path/to/theme", file=sys.stderr)
        sys.exit(2)
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        sys.exit(2)

    check_structure(root)
    declared = check_manifest(root)
    check_templates(root, declared)
    check_style(root, declared)
    check_sizes(root)

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ! {w}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  x {e}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s). Theme will likely FAIL import or render broken.")
        sys.exit(1)
    print(f"\nOK — no errors ({len(warnings)} warning(s)). Still preview with `zcli themes:preview`.")
    sys.exit(0)


if __name__ == "__main__":
    main()
