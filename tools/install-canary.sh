#!/bin/bash
# Verify that skills CLI installs a complete copy for Codex and Claude Code.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${1:-${ROOT}/skills/fireworks-tech-graph}"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/fireworks-tech-graph-install.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT
mkdir -p "$TMP_ROOT/home" "$TMP_ROOT/npm-cache"

HOME="$TMP_ROOT/home" npm_config_cache="$TMP_ROOT/npm-cache" \
    npx -y skills@1.5.17 add "$SOURCE" \
    --agent codex claude-code -g -y --copy

for install_root in \
    "$TMP_ROOT/home/.agents/skills/fireworks-tech-graph" \
    "$TMP_ROOT/home/.claude/skills/fireworks-tech-graph"
do
    test -f "$install_root/SKILL.md"
    for directory in agents assets docs fixtures references schemas scripts templates tests; do
        test -d "$install_root/$directory"
    done
    cmp "$install_root/SKILL.md" "$ROOT/SKILL.md"
    cmp "$install_root/agents/openai.yaml" "$ROOT/agents/openai.yaml"
    cmp "$install_root/scripts/generate-from-template.py" "$ROOT/scripts/generate-from-template.py"
    cmp "$install_root/scripts/semantic_contracts.py" "$ROOT/scripts/semantic_contracts.py"
    test -f "$install_root/references/style-12-ops-pulse.md"
    test -f "$install_root/assets/icons/cloud/manifest-v1.json"
    test -f "$install_root/assets/samples/sample-style12-ops-pulse.png"
    test -x "$install_root/scripts/generate-diagram.sh"
    test -x "$install_root/scripts/fireworks.py"
done

python3 "$TMP_ROOT/home/.agents/skills/fireworks-tech-graph/scripts/fireworks.py" \
    render architecture \
    "$TMP_ROOT/home/.agents/skills/fireworks-tech-graph/fixtures/c4-review-canvas-style9.json" \
    "$TMP_ROOT/canary.svg" \
    --report "$TMP_ROOT/canary-layout.json"

python3 "$TMP_ROOT/home/.agents/skills/fireworks-tech-graph/scripts/fireworks.py" \
    check "$TMP_ROOT/canary.svg"

test -s "$TMP_ROOT/canary.svg"
test -s "$TMP_ROOT/canary-layout.json"
echo "install canary passed: $SOURCE"
