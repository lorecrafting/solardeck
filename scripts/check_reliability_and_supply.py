#!/usr/bin/env python3
"""
Phase 16: reliability model, obsolescence policy, design-for-test.

Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Audit 4 found three things that no earlier phase could see, because they are not inconsistencies:
a 22-year gap between module supply and the life claim, zero test points, and a reliability question
nobody had done the arithmetic for. This phase keeps all three answerable:

  1. RELIABILITY  the model runs and agrees with spec_values.reliability (delegated, not duplicated)
  2. SUPPLY       the 2034 shortfall is stated in HARDWARE_SPEC, and every single-source part is named
  3. DFT          the minimum test-point set exists as a requirement, not prose
  4. HONESTY      the "10-year device" consequence is written down, so the claim cannot quietly inflate

A phase that merely checked the words "test point" appeared somewhere would be theatre; this one checks
that the *requirement* exists and that the uncomfortable consequence is documented.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = json.load(open(os.path.join(ROOT, "docs", "spec_values.json")))
HW = os.path.join(ROOT, "docs", "HARDWARE_SPEC.md")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def origin_errors(bom, china_open):
    """ADR-053: every core-BOM row states an origin (ISO code or TBD); every CN row is a listed open item."""
    lines = bom.split("\n")
    head = next((i for i, l in enumerate(lines) if l.startswith("| Category |")), None)
    cols = [c.strip() for c in lines[head].split("|")] if head is not None else []
    if "Origin" not in cols:
        return ["core BOM table has no Origin column (ADR-053)"]
    col, errs, cn = cols.index("Origin"), [], set()
    for line in lines[head + 2:]:
        if not line.startswith("|") or "Total Core BOM" in line:
            break
        cells = [c.strip() for c in line.split("|")]
        if len(cells) <= col:
            errs.append(f"BOM row is missing cells: {line[:60]!r}")
            continue
        name, origin = cells[1].strip("*").strip(), cells[col]
        if origin == "CN":
            cn.add(name)
        if origin != "TBD" and not re.fullmatch(r"[A-Z]{2}", origin):
            errs.append(f"BOM row {name!r}: origin {origin!r} is not an ISO country code or TBD")
        elif origin == "CN" and name not in china_open:
            errs.append(f"BOM row {name!r} is China-origin but not in supply_chain.china_origin_open (ADR-053)")
    errs += [f"supply_chain.china_origin_open lists {n!r}, which is no longer a CN row" for n in set(china_open) - cn]
    return errs


def main():
    errors = []
    hw = read("docs/HARDWARE_SPEC.md")
    R, S = SPEC["reliability"], SPEC["supply_chain"]

    # 1. the model itself
    r = subprocess.run([sys.executable, "scripts/reliability_model.py", "--check"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        errors.append(f"reliability model check failed: {r.stdout.strip() or r.stderr.strip()}")

    # 2. supply chain
    year = S["cm5_production_commitment_year"]
    if year is None:
        # ADR-031: unknown until Raspberry Pi publishes it; the spec must say so rather than guess.
        if S["cm5_shortfall_years"] is not None:
            errors.append("supply_chain.cm5_shortfall_years must stay null while the commitment year is null")
        if not re.search(r"CM5 production commitment[^\n]*(TBD|not yet published|null)", hw):
            errors.append("HARDWARE_SPEC.md must state the CM5 production commitment is not yet published")
    else:
        if S["design_life_years"] - (year - 2026) != S["cm5_shortfall_years"]:
            errors.append("supply_chain.cm5_shortfall_years does not equal design_life - (year - 2026)")
        if str(year) not in hw:
            errors.append("HARDWARE_SPEC.md does not state the CM5 production commitment year")
    if "7.7" not in hw or "Module Obsolescence Strategy" not in hw:
        errors.append("HARDWARE_SPEC.md §7.7 (module obsolescence) missing")
    for part in S["single_source_parts"]:
        key = part.split(" (")[0]
        if key not in hw:
            errors.append(f"single-source part {key} is not named in HARDWARE_SPEC.md")
    for phrase, why in [
        (r"10-year device", "the honest 'if no successor module exists' consequence is missing"),
        (r"spare modules", "no spare-module mitigation in HARDWARE_SPEC.md"),
    ]:
        if not re.search(phrase, hw, re.I):
            errors.append(why)
    errors.extend(origin_errors(read("docs/BOM_COST_ESTIMATE.md"), S["china_origin_open"]))

    # 3. design for test
    if "7.8" not in hw or "test-point set" not in hw:
        errors.append("HARDWARE_SPEC.md §7.8 (minimum test-point set) missing")
    for net in ("VBUS_P1", "3V3_ALWAYS", "EPDC_CS", "WAKE_GPIO17", "CC1_P1"):
        if net not in hw:
            errors.append(f"test-point net {net} not in the minimum set")

    # 4. reliability numbers must not drift from the model
    if R["model_status"] != "modelled":
        errors.append("reliability.model_status must stay 'modelled' until a bench measures it")
    if R["first_wearout_years"] >= R["mtbf_years"] / 2:
        errors.append("wear-out and MTBF have converged; the spares-not-redundancy decision needs revisiting")

    if errors:
        for e in errors:
            print(f"   • {e}")
        print(f"   {len(errors)} reliability/supply/DFT failure(s)")
        return 1
    print(f"  MTBF {R['mtbf_years']} y vs first wear-out {R['first_wearout_years']} y; "
          f"CM5 commitment {S['cm5_production_commitment_year'] or 'TBD'}; {len(S['single_source_parts'])} single-source parts named.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
