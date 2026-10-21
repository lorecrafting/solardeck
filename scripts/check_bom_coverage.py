#!/usr/bin/env python3
"""
BOM <-> netlist <-> CPL coverage gate.
Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Three files must describe the same board:
  hardware/solardeck-carrier.net            (schematic, authoritative)
  hardware/production/solardeck_bom.csv     (SMT BOM)
  hardware/production/solardeck_cpl.csv     (placement centroids)

They must agree exactly. And the schematic must be catching up with the 61-line core BOM in
docs/BOM_COST_ESTIMATE.md: coverage may not regress, and is reported openly until it is complete.
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROD = os.path.join(ROOT, "hardware", "production")


def live_docs():
    """README + docs/*.md, excluding point-in-time records (AUDIT_*, 90-history)."""
    out = [os.path.join(ROOT, "README.md")]
    for base, _, files in os.walk(os.path.join(ROOT, "docs")):
        for f in files:
            if f.endswith(".md") and not f.startswith("AUDIT_"):
                p = os.path.join(base, f)
                if "/90-history/" not in p:
                    out.append(p)
    return out


def coverage_prose_mismatches(coverage, total):
    """Live prose restating the schematic coverage must agree with the netlist.
    AUDIT 5 finding: '20 of 61' vs '24 of 61' drifted twice because nothing checked."""
    out = []
    for path in live_docs():
        text = open(path, encoding="utf-8").read()
        for m in re.finditer(r"(\d+)\s*/\s*(\d+)\s+parts?\)", text):
            if (int(m.group(1)), int(m.group(2))) != (coverage, total):
                out.append(f"{os.path.relpath(path, ROOT)}: '{m.group(0).strip()}' != {coverage}/{total}")
        for m in re.finditer(r"(\d+)\s+of\s+(\d+)\s+core BOM", text):
            if (int(m.group(1)), int(m.group(2))) != (coverage, total):
                out.append(f"{os.path.relpath(path, ROOT)}: '{m.group(0).strip()}' != {coverage}/{total}")
        for m in re.finditer(r"reports\s+(\d+)\s*/\s*(\d+)", text):
            if (int(m.group(1)), int(m.group(2))) != (coverage, total):
                out.append(f"{os.path.relpath(path, ROOT)}: '{m.group(0).strip()}' != {coverage}/{total}")
    return out


def designators(path):
    with open(path) as f:
        rows = csv.DictReader(f)
        refs = set()
        for r in rows:
            for ref in re.split(r"[,\s]+", (r.get("Designator") or "").strip()):
                if ref:
                    refs.add(ref)
    return refs


def main():
    spec = json.load(open(os.path.join(ROOT, "docs", "spec_values.json")))
    net = open(os.path.join(ROOT, "hardware", "solardeck-carrier.net")).read()
    netlist = set(re.findall(r'\(comp \(ref "([A-Z][A-Z0-9_]*)', net))
    bom = designators(os.path.join(PROD, "solardeck_bom.csv"))
    cpl = designators(os.path.join(PROD, "solardeck_cpl.csv"))

    errors = []
    if netlist != bom:
        errors.append(f"netlist/solardeck_bom.csv disagree: only-netlist={sorted(netlist - bom)} "
                      f"only-bom={sorted(bom - netlist)}")
    if bom != cpl:
        errors.append(f"solardeck_bom.csv/solardeck_cpl.csv disagree: "
                      f"missing-in-cpl={sorted(bom - cpl)} missing-in-bom={sorted(cpl - bom)}")

    coverage = len(netlist)
    baseline = spec["schematic_coverage_baseline"]
    total = spec["core_bom_line_items"]
    if coverage < baseline:
        errors.append(f"schematic coverage regressed: {coverage} < baseline {baseline}")
    errors.extend(prose_mismatch for prose_mismatch in coverage_prose_mismatches(coverage, total))

    if errors:
        for e in errors:
            print(f"   • {e}")
        return 1

    pct = 100.0 * coverage / total
    print(f"  BOM = netlist = CPL ({coverage} designators).")
    if coverage < total:
        print(f"  WIP: schematic capture {coverage}/{total} core BOM line items ({pct:.0f}%). "
              f"Raise schematic_coverage_baseline in docs/spec_values.json as parts land.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
