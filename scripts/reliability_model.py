#!/usr/bin/env python3
"""
Reliability model (CI Phase 16): FIT -> MTBF, and the wear-out comparison.

Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Purpose: answer "is a 30-year life limited by random failure or by wear-out?" with arithmetic instead of
intuition, so money goes to the right mitigation. The answer decides whether to add redundancy (never
worth it here) or spares (the actual answer).

The model is `modelled`, not measured: category FIT rates are Telcordia-SR-332-class estimates at 40 degC
for commercial parts, and placement counts are design estimates from HARDWARE_SPEC.md, not a parsed
netlist (the netlist has 24 of 61 line items). Every assumption is printed, so a reviewer can attack
one number instead of the whole result.

  python3 scripts/reliability_model.py           print the model
  python3 scripts/reliability_model.py --check    fail if docs disagree with spec_values.reliability
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = json.load(open(os.path.join(ROOT, "docs", "spec_values.json")))

# (category, placements, FIT each, why)
MODEL = [
    ("CM5 module (SoC + DRAM + eMMC)", 1, 120, "2.4 GHz SoC at 55 degC junction"),
    ("Display module (EPDC + panel + frontlight)", 1, 60, "Kaleido 4 + controller (TBD) + LED string"),
    ("NVMe SSD", 1, 50, "controller + NAND"),
    ("Analog / power ICs", 14, 15, "chargers, bucks, load switches, e-fuses"),
    ("Sensors", 6, 12, "IMU, ALS, SHT40, RTC, fuel gauge, ADC"),
    ("Discrete semiconductors", 22, 6, "MOSFETs, ideal diodes, ESD arrays"),
    ("Crystals / oscillators", 3, 5, "32.768 kHz, 26 MHz"),
    ("Inductors", 8, 2, "power magnetics"),
    ("Ceramic capacitors", 180, 0.5, "X7R/C0G, 2x voltage margin"),
    ("Resistors", 140, 0.2, "0402/0603"),
    ("Connectors", 8, 10, "USB-C, FPC ZIF, pogo, SMA"),
    ("Solder joints", 3000, 0.02, "corner-bonded BGAs"),
    ("PCB + assembly", 1, 2, "6-layer, IPC-6012 class 2"),
]

# (name, years, note, consumable?)  -- consumables are serviced, not limiters
WEAROUT = [
    ("LiFePO4 cell (capacity to 70 %)", 8, "10-year service interval", False),
    ("Silicone gasket (compression set)", 8, "wear part, in the service kit", False),
    ("RTC backup cell (CR2032/MS621FE)", 10, "socketed, service interval", False),
    ("Frontlight LED string (L70)", 15, "3 h/day at 40 % brightness", False),
    ("Display capsules (charge trapping)", 20, "ghosting budget, not failure", False),
    ("Desiccant", 2, "annual swap", True),
]


def model():
    rows, total_fit = [], 0.0
    for name, n, fit, why in MODEL:
        sub = n * fit
        total_fit += sub
        rows.append((name, n, fit, sub, why))
    mtbf_h = 1e9 / total_fit
    return rows, total_fit, mtbf_h


def main():
    rows, total_fit, mtbf_h = model()
    mtbf_y = mtbf_h / 8760.0
    worst = min((w for w in WEAROUT if not w[3]), key=lambda w: w[1])
    R = SPEC["reliability"]
    if "--check" in sys.argv:
        bad = []
        if abs(R["fit_total"] - round(total_fit)) > 25:
            bad.append(f"spec_values.reliability.fit_total={R['fit_total']} vs model {round(total_fit)}")
        if abs(R["mtbf_years"] - round(mtbf_y)) > 5:
            bad.append(f"spec_values.reliability.mtbf_years={R['mtbf_years']} vs model {round(mtbf_y)}")
        if R["first_wearout_years"] != worst[1]:
            bad.append(f"spec_values.reliability.first_wearout_years={R['first_wearout_years']} vs {worst[1]}")
        doc = open(os.path.join(ROOT, "docs", "LONGEVITY_30Y.md"), encoding="utf-8").read()
        if f"{R['mtbf_years']}" not in doc:
            bad.append("LONGEVITY_30Y.md does not quote the modelled MTBF")
        for b in bad:
            print(f"   • {b}")
        if bad:
            return 1
        print(f"  reliability model agrees: {R['fit_total']} FIT, MTBF {R['mtbf_years']} y, first wear-out {R['first_wearout_years']} y.")
        return 0

    print(f"{'category':45s} {'qty':>5s} {'FIT':>6s} {'subtotal':>9s}")
    for name, n, fit, sub, _ in rows:
        print(f"{name:45s} {n:5d} {fit:6.2f} {sub:9.1f}")
    print(f"\n  total {total_fit:.0f} FIT  ->  MTBF {mtbf_h:,.0f} h = {mtbf_y:.0f} years at 40 degC")
    print("\n  wear-out limiters (years to 70-80 % of spec):")
    for name, y, note, cons in sorted(WEAROUT, key=lambda w: w[1]):
        tag = "consumable" if cons else "hard part"
        print(f"    {y:3d} y  {name:38s} {note} ({tag})")
    print(f"\n  CONCLUSION: random failure ({mtbf_y:.0f} y) is not the limiter; {worst[0]} at {worst[1]} y is the first hard wear-out.")
    print("  Therefore: spares and service intervals, never redundancy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
