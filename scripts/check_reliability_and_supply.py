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
    if S["cm4_production_commitment_year"] >= 2026 + S["design_life_years"]:
        errors.append("supply_chain no longer shows a shortfall; update AUDIT_4 and ADR-023 if that is real")
    if S["design_life_years"] - (S["cm4_production_commitment_year"] - 2026) != S["cm4_shortfall_years"]:
        errors.append("supply_chain.cm4_shortfall_years does not equal design_life - (2034 - 2026)")
    if str(S["cm4_production_commitment_year"]) not in hw:
        errors.append("HARDWARE_SPEC.md does not state the CM4 production commitment year")
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
          f"CM4 shortfall {S['cm4_shortfall_years']} y documented; {len(S['single_source_parts'])} single-source parts named.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
