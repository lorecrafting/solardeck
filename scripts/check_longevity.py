#!/usr/bin/env python3
"""
Longevity-constraint checker for SolarDeck (CI Phase 13).

Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

The 30-year constraints in docs/spec_values.json -> longevity are worthless as prose. This phase makes
each one either present in the artifact that implements it, or a build failure:

  1. SCHEMA   every required longevity key exists and is the right kind.
  2. DOCS     HARDWARE_SPEC.md must state the process-layer constraints: corner bond, 20k-cycle USB-C,
              0.45 N.m torque, threadlocker, gasket compression, mechanical cell retention.
  3. BOM      the gasket and the haptic engine must be BOM line items; the piezo array must NOT be
              (it is a DNP option, ADR-020) -- a descope that reappears in the BOM is a lost decision.
  4. DAEMONS  the two aging daemons must be specified and catalogued.
  5. GATES    G7-G10 must exist in STANDOUT_FEATURES.md and in features.acceptance_gates.
  6. PLAN     LONGEVITY_30Y.md must state the maintenance intervals from spec_values.

Deliberately asserts on *presence of the constraint*, not on a measurement: no bench has run yet, so a
checker that demanded numbers would just force someone to invent them.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = json.load(open(os.path.join(ROOT, "docs", "spec_values.json")))
L = SPEC["longevity"]

REQUIRED = {
    "design_life_years": int, "drop_height_m": float, "drop_peak_g": int,
    "drop_orientations": int, "thermal_cycles": int, "thermal_uv_hours": int,
    "unpowered_months": int, "battery_capacity_retained_year30_pct": int,
    "battery_service_interval_years": int, "gasket_compression_pct": int,
    "fastener_torque_nm": float, "screw_types_max": int, "usb_c_rated_cycles": int,
    "salt_fog_hours": int, "nand_scrub_interval_days": int, "storage_soc_pct": int,
    "battery_retention": str, "gasket_material": str, "rtc_backup": str,
    "capacitor_policy": str, "underfill": str, "conformal_coat": str,
    "service_kit_items": list,
}


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def check_schema(err):
    for key, kind in REQUIRED.items():
        if key not in L:
            err(f"longevity.{key} missing from docs/spec_values.json")
        elif not isinstance(L[key], kind):
            err(f"longevity.{key} is {type(L[key]).__name__}, expected {kind.__name__}")


def check_docs(err):
    hw = read("docs/HARDWARE_SPEC.md")
    want = [
        (r"[Cc]orner[- ]bond", "corner bond on DSBGA/QFN (§7.6.1)"),
        (r"20,?000\s*[- ]?(?:insertion\s+)?cycles?", "20,000-cycle USB-C requirement (§7.6.4)"),
        (rf"{str(L['fastener_torque_nm']).replace('.', '[.]')}\s*N", "fastener torque in §7.6.5"),
        (r"[Tt]hreadlocker", "low-strength threadlocker (§7.6.5)"),
        (rf"{L['gasket_compression_pct']}\s*%", "gasket compression from spec_values (§7.6.3)"),
        (r"[Mm]echanical(?:ly)?\s+clamp|stainless bracket", "mechanically clamped cell (§7.6.2)"),
    ]
    for pat, why in want:
        if not re.search(pat, hw):
            err(f"HARDWARE_SPEC.md does not state: {why}")


def check_bom(err):
    bom = read("docs/BOM_COST_ESTIMATE.md")
    must = [
        (r"Perimeter Gasket", "the gasket is not a BOM line item (it is a wear part)"),
        (r"DRV2605L|Haptic Engine", "the base-build haptic engine is not in the BOM"),
        (r"MS621FE|CR2032", "no RTC backup cell in the BOM"),
    ]
    for pat, why in must:
        if not re.search(pat, bom):
            err(why)
    for banned, why in [
        (r"PowerHap", "quad piezo array is a DNP option (ADR-020) and must not be a BOM line item"),
        (r"BOS1901", "BOS1901 is a DNP option (ADR-020) and must not be a BOM line item"),
        (r"[Aa]luminium [Ee]lectrolytic|Aluminum Electrolytic",
         "wet electrolytics are banned by longevity.capacitor_policy"),
    ]:
        if re.search(banned, bom):
            err(why)


def check_daemons(err):
    sw = read("docs/SOFTWARE_SPEC.md")
    catalogued = {e["name"] for e in SPEC["features"]["daemons"]}
    for name in ("solardeck-battcare", "solardeck-nandcare"):
        if name not in sw:
            err(f"{name} has status 'specified' but no SOFTWARE_SPEC section")
        if name not in catalogued:
            err(f"{name} missing from features.daemons")
    for name in list(catalogued):
        # catalogued daemons must still appear somewhere in the spec body
        if name.startswith(("solardeck-", "eink-")) and name not in sw:
            err(f"daemon {name} catalogued in STATUS.md but absent from SOFTWARE_SPEC.md")


def check_gates(err):
    standout = read("docs/STANDOUT_FEATURES.md")
    ids = {e["id"] for e in SPEC["features"]["acceptance_gates"]}
    for g in ("G7", "G8", "G9", "G10"):
        if g not in ids:
            err(f"gate {g} missing from features.acceptance_gates")
        if f"**{g}**" not in standout:
            err(f"gate {g} missing from STANDOUT_FEATURES.md")


def check_plan(err):
    plan = read("docs/LONGEVITY_30Y.md")
    for pat, why in [
        (r"Quarterly", "quarterly NAND scrub missing from the maintenance schedule"),
        (rf"{L['battery_service_interval_years']}\s*years", "battery service interval missing"),
        (rf"{L['storage_soc_pct']}\s*%", "storage parking SOC missing"),
        (rf"{L['drop_height_m']}\s*m|1[.]22", "drop height in the drop-physics section"),
    ]:
        if not re.search(pat, plan):
            err(why)


def main():
    errors = []
    err = errors.append
    check_schema(err)
    check_docs(err)
    check_bom(err)
    check_daemons(err)
    check_gates(err)
    check_plan(err)
    if errors:
        for e in errors:
            print(f"   • {e}")
        print(f"   {len(errors)} longevity constraint(s) unenforced")
        return 1
    print(f"  {len(REQUIRED)} longevity constraints present in schema, docs, BOM, daemons, gates, plan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
