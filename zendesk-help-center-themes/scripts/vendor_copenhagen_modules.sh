#!/usr/bin/env bash
# Copy Zendesk's prebuilt Copenhagen v4 ES modules into a theme's assets/ folder.
#
# Templating API v4 has no {{request_form}}: the request form, request list,
# service catalog, approvals and flash notifications are client-rendered by
# these modules (Apache-2.0). Templates load them through the import map in
# document_head.hbs (see references/recipes.md → "Request form and other v4 modules").
#
# Usage: bash vendor_copenhagen_modules.sh <theme-dir> [git-ref | local-copenhagen-dir]
#   git-ref               clone that branch/tag from GitHub (default: master; needs network)
#   local-copenhagen-dir  offline: an unpacked copenhagen_theme checkout/zip, or any theme
#                         that already has the bundles (anything with assets/*-bundle.js)
# Writes <theme-dir>/assets/*-bundle.js, es-module-shims.js and
# <theme-dir>/THIRD_PARTY_COPENHAGEN.txt (version + license for attribution).
set -euo pipefail

THEME="${1:?usage: vendor_copenhagen_modules.sh <theme-dir> [git-ref | local-copenhagen-dir]}"
SRC="${2:-master}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [ -d "$SRC" ]; then
  [ -n "$(ls "$SRC"/assets/*-bundle.js 2>/dev/null)" ] || { echo "No assets/*-bundle.js under $SRC" >&2; exit 1; }
  SRC_ABS="$(cd "$SRC" && pwd)"
  ln -s "$SRC_ABS" "$TMP/cph"
  # Only trust a commit if SRC is itself the root of a git checkout (not a folder inside another repo).
  if [ "$(git -C "$SRC_ABS" rev-parse --show-toplevel 2>/dev/null)" = "$SRC_ABS" ]; then
    COMMIT="$(git -C "$SRC_ABS" rev-parse HEAD)"
  else
    COMMIT="local copy"
  fi
else
  git clone --quiet --depth 1 --branch "$SRC" https://github.com/zendesk/copenhagen_theme.git "$TMP/cph"
  COMMIT="$(git -C "$TMP/cph" rev-parse HEAD)"
fi
VERSION="unknown"
if [ -f "$TMP/cph/manifest.json" ]; then
  VERSION="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$TMP/cph/manifest.json" | head -1)"
elif [ -f "$TMP/cph/VERSION" ]; then
  VERSION="$(sed -n 's/^version: *//p' "$TMP/cph/VERSION" | head -1)"
fi

mkdir -p "$THEME/assets"
cp "$TMP/cph/assets/"*-bundle.js "$THEME/assets/"
cp "$TMP/cph/assets/es-module-shims.js" "$THEME/assets/" 2>/dev/null || true
{
  echo "Zendesk Copenhagen theme modules $VERSION ($COMMIT)"
  echo "https://github.com/zendesk/copenhagen_theme — Apache License 2.0, unmodified."
  echo
  cat "$TMP/cph/LICENSE" 2>/dev/null || echo "Apache License 2.0 — https://www.apache.org/licenses/LICENSE-2.0"
} > "$THEME/THIRD_PARTY_COPENHAGEN.txt"

echo "Copied Copenhagen $VERSION modules into $THEME/assets:"
ls -1 "$TMP/cph/assets/"*-bundle.js | xargs -n1 basename
echo "Make sure document_head.hbs has an import-map entry for each *-bundle.js above."
