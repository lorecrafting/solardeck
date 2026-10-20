#!/usr/bin/env python3
"""
Generate docs/STATUS.md from docs/spec_values.json -> "features".

Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

The catalogue (names + status) lives in spec_values.json. This script renders it and refuses to
render a catalogue that disagrees with the rest of the repo:

  1. STATUSES  every status is one of measured/modelled/specified/aspirational/TBD.
  2. IDS       ids are unique.
  3. COUNTS    product pillars == standout_pillars, engineering pillars == engineering_pillars,
               hotpacks == hotpacks.
  4. DAEMONS   bidirectional: every catalogued daemon appears in SOFTWARE_SPEC.md, and every
               `solardeck-*` daemon named in a SOFTWARE_SPEC heading is catalogued. Adding a
               daemon without giving it a status is a build failure, not a missing row.
  5. EVIDENCE  a daemon's evidence is derived from what exists on disk, never asserted.

Usage:
  python3 scripts/gen_status.py            write docs/STATUS.md
  python3 scripts/gen_status.py --check     fail if docs/STATUS.md is stale (CI)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = json.load(open(os.path.join(ROOT, "docs", "spec_values.json")))
FEATURES = SPEC["features"]
OUT = os.path.join(ROOT, "docs", "STATUS.md")
SW = os.path.join(ROOT, "docs", "SOFTWARE_SPEC.md")

STATUSES = ("measured", "modelled", "specified", "aspirational", "TBD")
GROUPS = [
    ("product_pillars", "Product pillars", "What the product is judged on (`README.md` §2)."),
    ("engineering_pillars", "Engineering pillars", "The architectural bets that make the pillars possible (`README.md` §4)."),
    ("daemons", "Daemons", "Host software specified in `SOFTWARE_SPEC.md`. Evidence is derived from `src/daemons/`."),
    ("hotpacks", "USB-C Hotpacks", "Field expansion modules (`OFFGRID_TACTICAL_SENSORS.md` §8)."),
    ("accessories", "Accessories", "Sold separately; not required for the core tablet."),
    ("acceptance_gates", "Acceptance gates", "The numbers that decide whether a build is field-ready (`STANDOUT_FEATURES.md`)."),
]


def fail(msg):
    print(f"gen_status: FAIL -- {msg}")
    sys.exit(1)


def check():
    ids = set()
    for key, _, _ in GROUPS:
        if key not in FEATURES:
            fail(f"spec_values.features.{key} missing")
        for e in FEATURES[key]:
            for f in ("id", "name", "status"):
                if f not in e:
                    fail(f"{key} entry missing '{f}': {e}")
            if e["status"] not in STATUSES:
                fail(f"{key}/{e['id']} status '{e['status']}' not in {STATUSES}")
            if e["id"] in ids:
                fail(f"duplicate feature id {e['id']}")
            ids.add(e["id"])

    expected = {
        "product_pillars": SPEC["standout_pillars"],
        "engineering_pillars": SPEC["engineering_pillars"],
        "hotpacks": SPEC["hotpacks"],
    }
    for key, n in expected.items():
        if len(FEATURES[key]) != n:
            fail(f"{key} has {len(FEATURES[key])} entries, spec_values says {n}")

    spec_text = open(SW, encoding="utf-8").read()
    catalogued = {e["name"] for e in FEATURES["daemons"]}
    in_headings = set()
    for m in re.finditer(r"^## \d+\. .*$", spec_text, re.M):
        in_headings |= {n for n in re.findall(r"`([a-z0-9-]+)`", m.group(0))
                        if n.startswith(("solardeck-", "eink-"))}
    errs = coverage_errors(catalogued, in_headings)
    if errs:
        fail(errs[0])
    return True


def coverage_errors(catalogued, headings):
    """Bidirectional: a daemon needs a status, a status needs a daemon. Pure, so it is testable."""
    errs = [f"catalogued without a SOFTWARE_SPEC heading: {n}" for n in sorted(catalogued - headings)]
    errs += [f"SOFTWARE_SPEC heading without a status: {n}" for n in sorted(headings - catalogued)]
    return errs


def selftest():
    """The one check for this script's non-trivial logic: coverage must fail in both directions."""
    h = {"solardeck-a", "eink-b"}
    assert coverage_errors({"solardeck-a", "eink-b"}, h) == []
    assert coverage_errors({"solardeck-a"}, h) == ["SOFTWARE_SPEC heading without a status: eink-b"]
    assert coverage_errors(h, {"solardeck-a"}) == ["catalogued without a SOFTWARE_SPEC heading: eink-b"]
    assert render().startswith("# STATUS.md")
    assert "| **total** |" in render()


def evidence(key, e):
    if key != "daemons":
        return "—"
    d = os.path.join(ROOT, "src", "daemons", e["name"])
    if not os.path.isdir(d):
        return f"spec only (§{e.get('spec_section', '?')})"
    has_test = any(f.startswith("test_") for f in os.listdir(d))
    return f"code + test (§{e.get('spec_section', '?')})" if has_test else f"code only (§{e.get('spec_section', '?')})"


def render():
    lines = [
        "# STATUS.md — What This Project Actually Delivers, and How Sure We Are",
        "",
        "Written 2026-10-20 05:40 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017",
        "",
        "**Generated file — do not edit.** Source: `docs/spec_values.json` → `features`.",
        "Regenerate: `python3 scripts/gen_status.py`. CI Phase 12 fails if this page is stale.",
        "",
        "## Status vocabulary",
        "",
        "| Status | Means |",
        "| :--- | :--- |",
        "| `measured` | A bench value from this build or an equivalent dev kit, with an instrument and a date. Nothing here yet. |",
        "| `modelled` | Arithmetic, CAD, or simulation closes. Believable, not proven. |",
        "| `specified` | Designed and documented in a spec section. **No artifact proves it.** |",
        "| `aspirational` | A design goal. Do not quote it as a capability. |",
        "| `TBD` | Unknown, and we refuse to guess. |",
        "",
        f"`specified` is the honest default for this repo: {SPEC['core_bom_line_items']} BOM lines, "
        f"{SPEC['schematic_coverage_baseline']} captured in schematics, 0 board nets.",
        "Read `docs/AUDIT_2026-10-20.md` before treating any row here as a purchase decision.",
        "",
    ]
    total = sum(len(FEATURES[k]) for k, _, _ in GROUPS)
    lines += [
        "## Totals",
        "",
        "| Status | Count |",
        "| :--- | ---: |",
    ]
    for s in STATUSES:
        n = sum(1 for k, _, _ in GROUPS for e in FEATURES[k] if e["status"] == s)
        lines.append(f"| `{s}` | {n} |")
    lines.append(f"| **total** | **{total}** |")
    lines.append("")

    for key, title, blurb in GROUPS:
        lines += [f"## {title}", "", blurb, ""]
        if key == "daemons":
            lines += ["| ID | Daemon | Status | Spec | Evidence |", "| :--- | :--- | :--- | :--- | :--- |"]
            for e in FEATURES[key]:
                lines.append(f"| {e['id']} | `{e['name']}` | `{e['status']}` | §{e.get('spec_section', '?')} | {evidence(key, e)} |")
        else:
            lines += ["| ID | Feature | Status |", "| :--- | :--- | :--- |"]
            for e in FEATURES[key]:
                lines.append(f"| {e['id']} | {e['name']} | `{e['status']}` |")
        lines.append("")

    lines += [
        "## How this page stays true",
        "",
        "1. A new daemon with a `SOFTWARE_SPEC` heading but no status fails Phase 12 — you cannot add",
        "   a feature without declaring how sure you are about it.",
        "2. Daemon counts, pillar counts and hotpack counts are checked against `spec_values.json`.",
        "3. Evidence is derived from `src/daemons/`, not written by hand. When code lands, the column",
        "   changes by itself; nobody can claim code exists that isn't there.",
        "4. Promotion out of `specified` requires the evidence named in `docs/WORKFLOW.md` §1.",
        "",
    ]
    return "\n".join(lines)


def main():
    selftest()
    check()
    text = render()
    if "--check" in sys.argv:
        current = open(OUT, encoding="utf-8").read() if os.path.isfile(OUT) else ""
        if current != text:
            fail("docs/STATUS.md is stale -- run: python3 scripts/gen_status.py")
        n = sum(len(FEATURES[k]) for k, _, _ in GROUPS)
        print(f"STATUS.md up to date ({n} catalogued features).")
        return
    open(OUT, "w", encoding="utf-8").write(text)
    print(f"wrote docs/STATUS.md ({sum(len(FEATURES[k]) for k, _, _ in GROUPS)} features)")


if __name__ == "__main__":
    main()
