#!/usr/bin/env python3
"""
validate_theme.py — pre-import sanity check for a Zendesk Guide Help Center theme.

Catches the most common reasons an import job fails (InvalidManifest,
InvalidSetting, InvalidTemplates, FileNotFound) plus high-probability mistakes,
before you spend a round-trip on import.

Usage:
    python3 validate_theme.py path/to/theme

Exit code 0 = no errors (warnings allowed); 1 = errors found; 2 = bad invocation.

This is a heuristic linter, not the Zendesk validator. It is intentionally
conservative: it ERRORs only on things that reliably break import, and WARNs on
likely problems. Always also preview locally with `zcli themes:preview`.
"""

import json
import re
import sys
from pathlib import Path

REQUIRED_ROOT_KEYS = ["name", "author", "version", "api_version"]
REQUIRED_FILE_VARS = {"logo", "favicon"}
IDENTIFIER_RE = re.compile(r"^[a-z0-9_]+$")
VALID_SETTING_TYPES = {"text", "textarea", "checkbox", "range", "list", "color", "file"}

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def check_structure(root: Path):
    if not (root / "manifest.json").is_file():
        err("manifest.json is missing (required at theme root).")
    if not (root / "style.css").is_file():
        warn("style.css not found at theme root (expected main stylesheet).")
    if not (root / "script.js").is_file():
        warn("script.js not found at theme root (expected main script).")
    if not (root / "templates").is_dir():
        err("templates/ directory is missing (required).")


def check_manifest(root: Path):
    mpath = root / "manifest.json"
    if not mpath.is_file():
        return None
    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"manifest.json is not valid JSON: {e}")
        return None

    for key in REQUIRED_ROOT_KEYS:
        if key not in manifest:
            err(f"manifest.json is missing required root key: '{key}'.")

    if "api_version" in manifest and manifest["api_version"] != 4:
        warn(f"api_version is {manifest['api_version']}; current is 4. Helpers/behavior may differ.")

    settings = manifest.get("settings", [])
    if not isinstance(settings, list):
        err("manifest.json 'settings' must be an array of setting groups.")
        return manifest

    seen_file_vars = {}
    total_vars = 0
    for group in settings:
        for var in group.get("variables", []) if isinstance(group, dict) else []:
            total_vars += 1
            ident = var.get("identifier")
            if not ident:
                err("A setting variable is missing an 'identifier'.")
                continue
            if not IDENTIFIER_RE.match(ident):
                err(f"Setting identifier '{ident}' is invalid. Use only [a-z0-9_] "
                    f"(no hyphens/uppercase): breaks $var in CSS and settings.{ident} in Curlybars.")
            vtype = var.get("type")
            if vtype not in VALID_SETTING_TYPES:
                err(f"Setting '{ident}' has invalid type '{vtype}'. "
                    f"Valid: {', '.join(sorted(VALID_SETTING_TYPES))}.")
            if not var.get("label"):
                warn(f"Setting '{ident}' has no 'label' (Settings panel needs one).")
            if vtype == "file":
                seen_file_vars[ident] = var

    for req in REQUIRED_FILE_VARS:
        if req not in seen_file_vars:
            err(f"Required file variable '{req}' is missing (must exist with type 'file').")

    # file-type settings need a default file in settings/
    settings_dir = root / "settings"
    existing = {p.stem for p in settings_dir.glob("*")} if settings_dir.is_dir() else set()
    for ident in seen_file_vars:
        if ident not in existing:
            warn(f"File setting '{ident}' has no default file in settings/ "
                 f"(expected settings/{ident}.<ext>).")

    if total_vars > 100:
        warn(f"{total_vars} settings defined — check the Guide settings limit; keep the panel lean.")

    return manifest


def check_templates(root: Path):
    tdir = root / "templates"
    if not tdir.is_dir():
        return
    block_open = re.compile(r"{{#([a-zA-Z_][\w]*)")
    block_close = re.compile(r"{{/([a-zA-Z_][\w]*)")
    partial = re.compile(r"{{>\s*[\w./-]+\s*}}")
    hardcoded_asset = re.compile(r'(?:src|href)\s*=\s*["\']/?assets/')

    for tpl in sorted(tdir.glob("*.hbs")):
        text = tpl.read_text(encoding="utf-8")
        rel = f"templates/{tpl.name}"

        if partial.search(text):
            err(f"{rel}: uses a partial ({{> ...}}). Help Center themes do NOT support partials.")

        if hardcoded_asset.search(text):
            warn(f"{rel}: hardcoded assets/ path in src/href. Use the asset helper: {{{{asset 'file'}}}}.")

        # naive balance check for block helpers (ignores {{else}})
        opens = block_open.findall(text)
        closes = block_close.findall(text)
        # stack match
        stack = []
        for m in re.finditer(r"{{#([a-zA-Z_][\w]*)|{{/([a-zA-Z_][\w]*)", text):
            if m.group(1):
                stack.append(m.group(1))
            else:
                name = m.group(2)
                if not stack:
                    err(f"{rel}: closing {{{{/{name}}}}} with no matching opener.")
                elif stack[-1] != name:
                    err(f"{rel}: block mismatch — opened '{stack[-1]}' but closed '{name}'.")
                    stack.pop()
                else:
                    stack.pop()
        for leftover in stack:
            err(f"{rel}: unclosed block {{{{#{leftover}}}}}.")

        if len(opens) != len(closes):
            warn(f"{rel}: block open/close count differs ({len(opens)} vs {len(closes)}).")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_theme.py path/to/theme", file=sys.stderr)
        sys.exit(2)
    root = Path(sys.argv[1])
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        sys.exit(2)

    check_structure(root)
    check_manifest(root)
    check_templates(root)

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ! {w}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  x {e}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s). Theme will likely FAIL import.")
        sys.exit(1)

    print(f"\nOK — no errors ({len(warnings)} warning(s)). Still preview with `zcli themes:preview`.")
    sys.exit(0)


if __name__ == "__main__":
    main()
