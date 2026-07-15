#!/usr/bin/env python3
"""Fail CI when product, package, site, and installation claims drift."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL_SOURCE = "yizhiyanhua-ai/fireworks-tech-graph/skills/fireworks-tech-graph"
STYLE_CATALOG = {
    1: ("style-1-flat-icon.md", "mem0-style1.json", "sample-style1-flat.png"),
    2: ("style-2-dark-terminal.md", "tool-call-style2.json", "sample-style2-dark.png"),
    3: ("style-3-blueprint.md", "microservices-style3.json", "sample-style3-blueprint.png"),
    4: ("style-4-notion-clean.md", "agent-memory-types-style4.json", "sample-style4-notion.png"),
    5: ("style-5-glassmorphism.md", "multi-agent-style5.json", "sample-style5-glass.png"),
    6: ("style-6-claude-official.md", "system-architecture-style6.json", "sample-style6-claude.png"),
    7: ("style-7-openai.md", "api-flow-style7.json", "sample-style7-openai.png"),
    8: ("style-8-dark-luxury.md", "dark-luxury-style8.svg", "sample-style8-dark-luxury.png"),
    9: ("style-9-c4-review-canvas.md", "c4-review-canvas-style9.json", "sample-style9-c4-review-canvas.png"),
    10: ("style-10-cloud-fabric.md", "cloud-fabric-style10.json", "sample-style10-cloud-fabric.png"),
    11: ("style-11-event-transit.md", "event-transit-style11.json", "sample-style11-event-transit.png"),
    12: ("style-12-ops-pulse.md", "ops-pulse-style12.json", "sample-style12-ops-pulse.png"),
}
GENERATOR_STYLES = (1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12)


def main() -> int:
    problems: list[str] = []
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    version = str(package["version"])
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## {version} " not in changelog:
        problems.append(f"CHANGELOG.md has no {version} release heading")
    if any(str(entry).startswith("skills") for entry in package.get("files", [])):
        problems.append("package.json files must not include skills/")

    for relative in ("README.md", "README.zh.md", "index.html"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        if INSTALL_SOURCE not in text:
            problems.append(f"{relative} is missing the nested skills install source")
        if "Codex" not in text or "Claude Code" not in text:
            problems.append(f"{relative} must describe both Codex and Claude Code")
        if relative != "index.html" and "12" not in text:
            problems.append(f"{relative} is missing the twelve-style claim")

    showcase = Path("assets") / "samples" / "showcase-12-styles.png"
    if not (ROOT / showcase).is_file():
        problems.append(f"missing latest showcase overview: {showcase}")
    for relative in ("README.md", "README.zh.md"):
        if showcase.as_posix() not in (ROOT / relative).read_text(encoding="utf-8"):
            problems.append(f"{relative} is missing the latest showcase overview")

    index = (ROOT / "index.html").read_text(encoding="utf-8")
    for stale in (
        "npx skills add yizhiyanhua-ai/fireworks-tech-graph\n",
        "All eight styles are generator-backed",
        "See 8 styles",
        "One system, eight aesthetics",
        "8 visual styles",
        "across 8 distinct visual styles",
        "Adaptive Workflow Engine",
    ):
        if stale in index:
            problems.append(f"index.html contains stale claim: {stale.strip()}")
    if "Agent Runtime Architecture" not in index:
        problems.append("index.html Style 8 title does not match the fixture")

    for style_id, (reference, fixture, sample) in STYLE_CATALOG.items():
        for relative in (
            Path("references") / reference,
            Path("fixtures") / fixture,
            Path("assets") / "samples" / sample,
        ):
            if not (ROOT / relative).is_file():
                problems.append(f"Style {style_id} is missing catalog artifact: {relative}")
        if f"STYLE {style_id:02d}" not in index:
            problems.append(f"index.html is missing the Style {style_id:02d} gallery card")

    for style_id in GENERATOR_STYLES:
        baseline = ROOT / "fixtures" / "quality-baseline" / f"agent-runtime-style{style_id}.json"
        if not baseline.is_file():
            problems.append(f"Style {style_id} is missing its same-topology quality baseline")

    semantic_source = (ROOT / "scripts" / "semantic_contracts.py").read_text(encoding="utf-8")
    for style_id, name in ((9, "C4 Review Canvas"), (10, "Cloud Fabric"), (11, "Event Transit"), (12, "Ops Pulse")):
        if f'{style_id}: "{name}"' not in semantic_source:
            problems.append(f"semantic style catalog is missing Style {style_id}: {name}")

    for path in (
        "scripts/fireworks.py",
        "scripts/diagram_ir.py",
        "scripts/fireworks_geometry.py",
        "scripts/interactive_html.py",
        "scripts/semantic_contracts.py",
        "schemas/diagram-v1.schema.json",
        "docs/CAPABILITIES.md",
        "assets/icons/cloud/manifest-v1.json",
    ):
        if not (ROOT / path).is_file():
            problems.append(f"missing required capability file: {path}")

    markdown_link = re.compile(r"\[[^]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
    for relative in ("README.md", "README.zh.md", "CONTRIBUTING.md", "docs/CAPABILITIES.md"):
        source = ROOT / relative
        for raw_target in markdown_link.findall(source.read_text(encoding="utf-8")):
            target = raw_target.split("#", 1)[0].strip().strip("<>")
            if target and not (source.parent / target).resolve().exists():
                problems.append(f"broken local link in {relative}: {raw_target}")

    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        return 1
    print(f"project consistency passed for v{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
