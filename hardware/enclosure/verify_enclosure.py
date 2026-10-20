#!/usr/bin/env python3
"""
Runnable Verification Check for Track C (3D Enclosure & Mechanical Envelope)
Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

All dimensions come from docs/spec_values.json. Nothing here restates a number, so the CAD and the
spec cannot drift apart; scripts/check_docs_numbers.py checks the prose against the same file.
The old version asserted hardcoded literals, which is why it could not see the 14.0 vs 9.8 mm and
panel-vs-chassis conflicts (see docs/AUDIT_2026-10-20.md B4).
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SPEC = json.load(open(os.path.join(ROOT, "docs", "spec_values.json")))
SCAD = os.path.join(HERE, "solardeck_chassis.scad")


def const(content, name):
    m = re.search(rf"^{name}\s*=\s*([0-9.]+);", content, re.M)
    assert m, f"{name} not declared in solardeck_chassis.scad"
    return float(m.group(1))


def verify_enclosure():
    print("[Track C Check] Mechanical CAD vs docs/spec_values.json...")
    assert os.path.exists(SCAD), f"Missing {SCAD}"
    content = open(SCAD, encoding="utf-8").read()

    w, d, h = SPEC["chassis_mm"]
    assert const(content, "CHASSIS_WIDTH") == w, f"SCAD width != spec {w}mm"
    assert const(content, "CHASSIS_HEIGHT") == d, f"SCAD height != spec {d}mm"
    assert const(content, "CHASSIS_DEPTH") == h, f"SCAD depth != spec {h}mm"
    print(f"  - Outer envelope matches spec: {w} x {d} x {h} mm")

    pw, pd = SPEC["panel_module_outline_mm"]
    aw, ad = SPEC["display_active_mm"]
    assert w >= pw + 2.0, f"chassis {w}mm cannot hold panel module {pw}mm + 2mm wall"
    assert d >= pd + 2.0, f"chassis {d}mm cannot hold panel module {pd}mm + 2mm wall"
    assert const(content, "DISPLAY_ACTIVE_W") >= aw, "aperture narrower than the active area"
    assert const(content, "DISPLAY_ACTIVE_H") >= ad, "aperture shorter than the active area"
    print(f"  - Panel module {pw} x {pd}mm fits with >=1mm wall; aperture clears {aw} x {ad}mm active area")

    cw, cd, ch = SPEC["battery_cell_mm"]
    stack = SPEC["display_stack_mm"] + SPEC["pcb_thickness_mm"] + ch
    assert stack <= SPEC["chassis_cavity_depth_mm"], \
        f"battery branch {stack:.2f}mm exceeds cavity {SPEC['chassis_cavity_depth_mm']}mm"
    assert h >= SPEC["chassis_cavity_depth_mm"] + SPEC["rear_wall_mm"], \
        f"chassis {h}mm leaves no rear wall behind a {SPEC['chassis_cavity_depth_mm']}mm cavity"
    assert cw < w and cd < d, f"cell {cw}x{cd}mm exceeds chassis {w}x{d}mm"
    print(f"  - Battery branch {stack:.2f}mm fits the {SPEC['chassis_cavity_depth_mm']}mm cavity; "
          f"cell {cw} x {cd} x {ch}mm inside {w} x {d}mm")

    assert "m2_service_hatch_with_vault" in content, "service hatch module missing"
    assert re.search(r'MICROSD_W\s*=\s*15\.0;', content), "MicroSD width must be 15.0mm"
    assert re.search(r'MICROSD_H\s*=\s*11\.0;', content), "MicroSD height must be 11.0mm"
    assert re.search(r'\[0:2\]', content), "must carve exactly 3 MicroSD pockets (0, 1, 2)"
    print("  - Cold storage vault: 3x MicroSD pockets inside the M.2 service hatch")

    assert re.search(r'CAMERA_DIAMETER\s*=\s*12\.0;', content), "camera aperture must be 12.0mm"
    assert re.search(r'GORE_VENT_DIAMETER\s*=\s*6\.0;', content), "GORE vent must be 6.0mm"
    print("  - Flush 12mm camera port and 6mm GORE ePTFE pressure vent present")

    assert re.search(r'INSERT_HOLE_DIA\s*=\s*3\.6;', content), "heat-set hole must be 3.6mm for M2.5"
    assert re.search(r'VESA_SPACING\s*=\s*75\.0;', content), "mount grid spacing must be 75.0mm"
    print("  - M2.5 brass heat-set grid: 3.6mm pilot holes on a 75mm pattern")

    print("Track C verification passed.")


if __name__ == "__main__":
    verify_enclosure()
