#!/usr/bin/env python3
"""
Phase 14: derive the numbers nobody was deriving.

Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Phase 10 checks prose against docs/spec_values.json. That catches drift between two places that both
hold a value -- but it silently certifies any value that is absent from spec_values, and it cannot
catch a stale total, because a total is not written down anywhere else. This phase derives from the
artifacts instead:

  BOM    sum the line-item rows; assert spec_values, the total row, and the ASCII summary agree.
  POWER  recompute the solar-vs-idle claim from primitives (LoRa endurance left with LoRa, ADR-044).
  ENERGY assert the insolation assumption is stated (so a reader can recheck it).

Derivation, not agreement. That distinction is the whole point.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = json.load(open(os.path.join(ROOT, "docs", "spec_values.json")))
BOM = os.path.join(ROOT, "docs", "BOM_COST_ESTIMATE.md")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def bom_rows():
    """(name, low, high, is_tbd) for every line item before the Total row."""
    rows = []
    for line in read(BOM).split("\n"):
        if "Total Core BOM" in line:
            break
        if not line.startswith("|") or "--" in line:
            continue
        prices = re.findall(r"\$([0-9]+\.[0-9]{2})", line)
        if not prices:
            # ADR-032: an unpriced part is still a line item; it adds 0 and makes the total a floor.
            if re.search(r"\|\s*TBD\s*\|\s*$", line):
                rows.append((line.split("|")[1].strip().strip("*"), 0.0, 0.0, True))
            continue
        lo = float(prices[0])
        hi = float(prices[-1])
        rows.append((line.split("|")[1].strip().strip("*"), lo, hi, False))
    return rows


def check_bom(err):
    rows = bom_rows()
    lo = round(sum(r[1] for r in rows), 2)
    hi = round(sum(r[2] for r in rows), 2)
    n = len(rows)

    if n != SPEC["core_bom_line_items"]:
        err(f"BOM has {n} priced rows, spec_values.core_bom_line_items says {SPEC['core_bom_line_items']}")
    if (lo, hi) != (SPEC["bom_total_low"], SPEC["bom_total_high"]):
        err(f"BOM rows sum to {lo}-{hi}, spec_values says "
            f"{SPEC['bom_total_low']}-{SPEC['bom_total_high']}")

    text = read(BOM)
    total_line = next((l for l in text.split("\n") if "Total Core BOM" in l), "")
    tbd = [r[0] for r in rows if r[3]]
    if tbd and "TBD" not in total_line:
        err(f"Total Core BOM row must say the total excludes TBD rows: {', '.join(tbd)}")
    for want in (f"${lo:.2f}", f"${hi:.2f}"):
        if want not in total_line:
            err(f"Total Core BOM row does not contain {want} (rows sum to {lo:.2f}-{hi:.2f})")
    if f"${lo:.0f} – ${hi:.0f}" not in text:
        err(f"ASCII summary block does not contain '${lo:.0f} - ${hi:.0f}'")

    readme = read(os.path.join(ROOT, "docs", "README.md"))
    if f"${lo:.2f}-${hi:.2f}" not in readme:
        err(f"docs/README.md does not quote the derived total ${lo:.2f}-${hi:.2f}")
    if f"across {n} line items" not in readme:
        err(f"docs/README.md does not quote the derived line-item count {n}")
    return lo, hi, n


def check_power(err):
    P = SPEC["power"]
    gen_wh = P["solar_strip_w"] * P["insolation_kwh_m2_day"] * P["derate"] * 1000 / 1000
    idle_wh = P["rp2350_idle_mw"] / 1000 * 24
    ratio = gen_wh / idle_wh
    if ratio < 1.0:
        err(f"bezel strip harvests {gen_wh:.2f} Wh/day but RP2350 idle needs {idle_wh:.3f} Wh/day "
            f"-> the 'infinite desk life' claim is FALSE at ratio {ratio:.2f}")
    elif ratio < 1.25:
        err(f"strip/idle margin is only {ratio:.2f}x; claim 'infinite' is not defensible")

    return gen_wh, idle_wh, ratio


def check_charger(err):
    """ADR-035 / AUDIT 6 X1: the charger must be able to regulate at the battery's charge limit.
    The BQ25895 (VREG floor 3.84 V) on a 3.6 V LiFePO4 cell is the failure this exists to catch."""
    c, b = SPEC["charger"], SPEC["battery"]
    limit_mv = round(b["charge_limit_v"] * 1000)
    if not (c["vreg_min_v"] <= b["charge_limit_v"] <= c["vreg_max_v"]):
        err(f"charger {c['part']} regulates {c['vreg_min_v']}-{c['vreg_max_v']} V; it cannot terminate at "
            f"the {b['chemistry']} limit {b['charge_limit_v']} V")
    elif (limit_mv - round(c["vreg_min_v"] * 1000)) % c["vreg_step_mv"]:
        err(f"charge limit {limit_mv} mV is not on the charger's {c['vreg_step_mv']} mV VREG grid")
    if b["chemistry"].lower().replace("₄", "4") != "lifepo4":
        err(f"battery.chemistry is {b['chemistry']!r}; AGENTS §4.1 allows LiFePO4 only")
    if limit_mv > 3650:
        err(f"charge limit {limit_mv} mV exceeds the AGENTS §4.1 LiFePO4 ceiling of 3650 mV")
    # The firmware gate that releases the charger's CE pin must use the same limit.
    hdr = read(os.path.join(ROOT, "firmware", "rp2350", "include", "solardeck_state.h"))
    m = re.search(r"#define\s+SD_CHARGE_LIMIT_MV\s+(\d+)", hdr)
    if not m or int(m.group(1)) != limit_mv:
        err(f"firmware SD_CHARGE_LIMIT_MV ({m.group(1) if m else 'missing'}) != battery.charge_limit_v ({limit_mv} mV)")
    return c["part"], c["vreg_min_v"], c["vreg_max_v"], b["chemistry"], b["charge_limit_v"]


def check_stated_assumptions(err):
    hw = read(os.path.join(ROOT, "docs", "HARDWARE_SPEC.md"))
    for pat, why in [
        (r"4[.]28\s*kWh", "insolation assumption (4.28 kWh/m2/day) is not stated anywhere"),
        (r"70\s*%", "combined panel/MPPT derate (70%) is not stated"),
    ]:
        if not re.search(pat, hw):
            err(why)


def main():
    errors = []
    lo, hi, n = check_bom(errors.append)
    gen, idle, ratio = check_power(errors.append)
    chg = check_charger(errors.append)
    check_stated_assumptions(errors.append)
    if errors:
        for e in errors:
            print(f"   • {e}")
        print(f"   {len(errors)} derived-number failure(s)")
        return 1
    print(f"  BOM: {n} rows derived to ${lo:.2f}-${hi:.2f}, prose agrees.")
    print(f"  Power: strip {gen:.2f} Wh/day vs idle {idle:.3f} Wh/day = {ratio:.1f}x.")
    print("  Charger: {} VREG {}-{} V covers {} {} V; firmware gate agrees.".format(*chg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
