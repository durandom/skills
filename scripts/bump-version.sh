#!/usr/bin/env bash
# Atomically bump version across all three manifest files.
# Usage: scripts/bump-version.sh <new-version>
#   e.g. scripts/bump-version.sh 3.9.0
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 <new-version>" >&2
    exit 2
fi

NEW="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$ROOT/.claude-plugin/plugin.json"
MARKET="$ROOT/.claude-plugin/marketplace.json"
PYPROJ="$ROOT/pyproject.toml"

CURRENT="$(sed -n 's/^version = "\(.*\)"/\1/p' "$PYPROJ" | head -1)"
if [[ -z "$CURRENT" ]]; then
    echo "error: could not read current version from $PYPROJ" >&2
    exit 1
fi

echo "Bumping $CURRENT -> $NEW"

# pyproject.toml: only the [project] version line, not target-version
sed -i '' "s/^version = \"$CURRENT\"$/version = \"$NEW\"/" "$PYPROJ"

# plugin.json + marketplace.json: every "version": "$CURRENT" occurrence
sed -i '' "s/\"version\": \"$CURRENT\"/\"version\": \"$NEW\"/g" "$PLUGIN" "$MARKET"

echo "Updated:"
grep -H 'version' "$PLUGIN" "$MARKET" "$PYPROJ" | grep -v target-version
