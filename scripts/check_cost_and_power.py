#!/usr/bin/env python3
"""
Phase 14: derive the numbers nobody was deriving.

Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Phase 10 checks prose against docs/spec_values.json. That catches drift between two places that both
hold a value -- but it silently certifies any value that is absent from spec_values, and it cannot
catch a stale total, because a total is not written down anywhere else. This phase derives from the
artifacts instead:

  BOM    sum the line-item rows; assert spec_values, the total row, and the ASCII summary agree.
  POWER  recompute the solar-vs-idle claim from primitives (radio idle power is null until measured, ADR-055).
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
    # ADR-055: the radio MCU's station-mode draw joins the idle load once measured; until then the claim covers the RP2350 only.
    radio_mw = SPEC["radio"]["station_mode_idle_mw"]
    idle_wh = (P["rp2350_idle_mw"] + (radio_mw or 0)) / 1000 * 24
    ratio = gen_wh / idle_wh
    if ratio < 1.0:
        err(f"bezel strip harvests {gen_wh:.2f} Wh/day but always-on idle needs {idle_wh:.3f} Wh/day "
            f"-> the 'infinite desk life' claim is FALSE at ratio {ratio:.2f}")
    elif ratio < 1.25:
        err(f"strip/idle margin is only {ratio:.2f}x; claim 'infinite' is not defensible")

    return gen_wh, idle_wh, ratio


def check_charger(err):
    """ADR-035 / AUDIT 6 X1: the charger must be able to regulate at the battery's charge limit.
    The BQ25895 (VREG floor 3.84 V) on a 3.6 V LiFePO4 cell was the failure this exists to catch."""
    c, b = SPEC["charger"], SPEC["battery"]
    limit_mv = round(b["charge_limit_v"] * 1000)
    if not (c["vreg_min_v"] <= b["charge_limit_v"] <= c["vreg_max_v"]):
        err(f"charger {c['part']} regulates {c['vreg_min_v']}-{c['vreg_max_v']} V; it cannot terminate at "
            f"the {b['chemistry']} limit {b['charge_limit_v']} V")
    elif (limit_mv - round(c["vreg_min_v"] * 1000)) % c["vreg_step_mv"]:
        err(f"charge limit {limit_mv} mV is not on the charger's {c['vreg_step_mv']} mV VREG grid")
    # AGENTS §4.1: one chemistry per hardware revision, each with a hard charge-voltage ceiling (mV).
    ceiling = {"li-ion": 4200, "lifepo4": 3650}.get(b["chemistry"].lower().replace("₄", "4"))
    if ceiling is None:
        err(f"battery.chemistry is {b['chemistry']!r}; AGENTS §4.1 has no ceiling for it")
    elif limit_mv > ceiling:
        err(f"charge limit {limit_mv} mV exceeds the AGENTS §4.1 {b['chemistry']} ceiling of {ceiling} mV")
    # The firmware gate that releases the charger's CE pin must use the same limit.
    hdr = read(os.path.join(ROOT, "firmware", "rp2350", "include", "solardeck_state.h"))
    m = re.search(r"#define\s+SD_CHARGE_LIMIT_MV\s+(\d+)", hdr)
    if not m or int(m.group(1)) != limit_mv:
        err(f"firmware SD_CHARGE_LIMIT_MV ({m.group(1) if m else 'missing'}) != battery.charge_limit_v ({limit_mv} mV)")
    # EVT-0 (docs/EVT0_POWER_BOARD.md §3.2): the VREG register code the RP2350 writes must follow the limit.
    m = re.search(r"VREG_10:0 = 0x([0-9A-Fa-f]+)", read(os.path.join(ROOT, "docs", "EVT0_POWER_BOARD.md")))
    if not m or int(m.group(1), 16) * c["vreg_step_mv"] != limit_mv:
        err(f"EVT0_POWER_BOARD VREG code ({m.group(0) if m else 'missing'}) != {limit_mv} mV / {c['vreg_step_mv']} mV")
    # The BQ25504 charges the cell without the CE gate: its OV threshold (Eq. 3) at worst-case accuracy
    # must stay at or below the charge limit.
    h = SPEC["harvester"]
    ov = 1.5 * h["vbias_v"] * (1 + h["rov2_mohm"] / h["rov1_mohm"])
    if abs(ov - h["vbat_ov_v"]) > 0.01:
        err(f"harvester.vbat_ov_v {h['vbat_ov_v']} V != {ov:.3f} V from rov1/rov2 (BQ25504 Eq. 3)")
    # Worst case: the threshold's own accuracy plus both divider resistors at tolerance.
    worst = ov * (1 + h["threshold_accuracy_pct"] / 100) * (1 + 2 * h["resistor_tol_pct"] / 100)
    if worst > b["charge_limit_v"]:
        err(f"harvester VBAT_OV worst case {worst:.3f} V exceeds the {b['charge_limit_v']} V charge limit")
    alarm_mv = round(b["low_alarm_v"] * 1000)
    m = re.search(r"#define\s+SD_LOW_BATT_ALARM_MV\s+(\d+)", hdr)
    if not m or int(m.group(1)) != alarm_mv:
        err(f"firmware SD_LOW_BATT_ALARM_MV ({m.group(1) if m else 'missing'}) != battery.low_alarm_v ({alarm_mv} mV)")
    return c["part"], c["vreg_min_v"], c["vreg_max_v"], b["chemistry"], b["charge_limit_v"]


def check_pack(err):
    """ADR-049: the chosen cell, protector and connector must cover the modelled pack load."""
    b, k, c = SPEC["battery"], SPEC["pack"], SPEC["charger"]
    wh = round(b["cells_parallel"] * b["cell_capacity_mah"] * b["cell_nominal_v"] / 1000, 1)
    if SPEC["battery_wh"]["li_ion"] != wh:
        err(f"battery_wh.li_ion {SPEC['battery_wh']['li_ion']} != {wh} Wh from battery.cell_*")
    rail = SPEC["cm5"]["supply_design_a"] + SPEC["usb"]["port2_current_limit_a"]
    if abs(k["rail_5v_a"] - rail) > 0.01:
        err(f"pack.rail_5v_a {k['rail_5v_a']} != CM5 {SPEC['cm5']['supply_design_a']} A + port 2 limit")
    peak = k["rail_5v_a"] * 5.0 / (k["boost_efficiency"] * b["low_alarm_v"])
    if abs(k["peak_a"] - peak) > 0.01:
        err(f"pack.peak_a {k['peak_a']} != {peak:.2f} A modelled from the 5 V rail at battery.low_alarm_v")
    cells_a = b["cells_parallel"] * b["cell_max_discharge_a"]
    if cells_a < k["discharge_margin"] * peak:
        err(f"cells give {cells_a} A continuous, below {k['discharge_margin']} x the {peak:.2f} A pack peak")
    if k["connector_contact_a"] < peak:
        err(f"pack connector {k['connector_contact_a']} A per contact < {peak:.2f} A pack peak")
    # The protector must never trip in normal charging: its minimum OVP clears the charger's worst VREG.
    ovp_min = k["protector_ovp_v"] - k["protector_ovp_acc_mv"] / 1000
    vreg_max = b["charge_limit_v"] * (1 + c["vreg_acc_max_pct"] / 100)
    if ovp_min <= vreg_max:
        err(f"protector {k['protector']} OVP min {ovp_min:.3f} V <= charger VREG max {vreg_max:.3f} V")
    return wh, peak, cells_a, ovp_min, vreg_max


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
    pack = check_pack(errors.append)
    check_stated_assumptions(errors.append)
    if errors:
        for e in errors:
            print(f"   • {e}")
        print(f"   {len(errors)} derived-number failure(s)")
        return 1
    print(f"  BOM: {n} rows derived to ${lo:.2f}-${hi:.2f}, prose agrees.")
    print(f"  Power: strip {gen:.2f} Wh/day vs idle {idle:.3f} Wh/day = {ratio:.1f}x"
          f"{'' if SPEC['radio']['station_mode_idle_mw'] is not None else ' (radio MCU excluded: not measured, ADR-055)'}.")
    print("  Charger: {} VREG {}-{} V covers {} {} V; firmware gate agrees.".format(*chg))
    print("  Pack: {:.1f} Wh; peak {:.2f} A vs cells {:.0f} A; protector OVP min {:.3f} V > VREG max {:.3f} V.".format(*pack))
    return 0


if __name__ == "__main__":
    sys.exit(main())
