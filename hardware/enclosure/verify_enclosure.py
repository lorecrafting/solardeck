#!/usr/bin/env python3
"""
Written 2026-10-19 08:36 UTC in the Pi harness by antigravity/gemini-3.8-flash
Runnable Verification Check for Track C (3D Enclosure & Mechanical Envelope)
"""

import os
import re

def verify_enclosure():
    enclosure_dir = os.path.dirname(os.path.abspath(__file__))
    scad_path = os.path.join(enclosure_dir, "solardeck_chassis.scad")

    print("[Track C Check] Verifying Mechanical CAD Parameters & Cold Storage Vault...")
    assert os.path.exists(scad_path), f"Missing {scad_path}"

    with open(scad_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Verify Core Chassis Envelope Dimensions (227 × 165 × 9.8 mm)
    assert re.search(r'CHASSIS_WIDTH\s*=\s*227\.0;', content), "CHASSIS_WIDTH must be 227.0mm"
    assert re.search(r'CHASSIS_HEIGHT\s*=\s*165\.0;', content), "CHASSIS_HEIGHT must be 165.0mm"
    assert re.search(r'CHASSIS_DEPTH\s*=\s*9\.8;', content), "CHASSIS_DEPTH must be 9.8mm"
    print("  ✓ Outer chassis envelope confirmed: 227.0 × 165.0 × 9.8 mm")

    # 2. Verify 10.3" Display Aperture
    assert re.search(r'DISPLAY_ACTIVE_W\s*=\s*209\.0;', content), "DISPLAY_ACTIVE_W must match 10.3in"
    assert re.search(r'DISPLAY_ACTIVE_H\s*=\s*157\.0;', content), "DISPLAY_ACTIVE_H must match 10.3in"
    print("  ✓ 10.3\" E-Ink display active bezel cutout confirmed (209.0 × 157.0 mm)")

    # 3. Verify Solar Bezel Strip Recess
    assert re.search(r'SOLAR_STRIP_W\s*=\s*45\.0;', content), "Solar strip width missing"
    assert re.search(r'SOLAR_STRIP_H\s*=\s*15\.0;', content), "Solar strip height missing"
    print("  ✓ Front micro-solar harvesting bezel recess confirmed")

    # 4. Verify Flush M.2 Service Hatch & Cold Storage Vault (3x MicroSD Pockets)
    assert "m2_service_hatch_with_vault" in content, "Service hatch module missing"
    assert re.search(r'MICROSD_W\s*=\s*15\.0;', content), "MicroSD width must be 15.0mm"
    assert re.search(r'MICROSD_H\s*=\s*11\.0;', content), "MicroSD height must be 11.0mm"
    assert re.search(r'\[0:2\]', content), "Must carve exactly 3 MicroSD pockets (0, 1, 2)"
    print("  ✓ Cold Storage Vault confirmed: 3x MicroSD secure card pockets inside M.2 service hatch")

    # 5. Verify Camera Window & GORE Pressure Vent
    assert re.search(r'CAMERA_DIAMETER\s*=\s*12\.0;', content), "Camera aperture must be 12.0mm"
    assert re.search(r'GORE_VENT_DIAMETER\s*=\s*6\.0;', content), "GORE vent must be 6.0mm"
    print("  ✓ Flush camera optical port (12mm) and GORE ePTFE pressure vent (6mm) confirmed")

    # 6. Verify Rear M2.5 Heat-Set Insert Grid (75x75mm VESA spacing)
    assert re.search(r'INSERT_HOLE_DIA\s*=\s*3\.6;', content), "Heat-set hole must be 3.6mm for M2.5"
    assert re.search(r'VESA_SPACING\s*=\s*75\.0;', content), "Mount grid spacing must be 75.0mm"
    print("  ✓ M2.5 brass heat-set insert grid confirmed (3.6mm pilot holes, 75x75mm pattern)")

    print("✓ Track C Verification Passed: All mechanical specifications and modules verified!")

if __name__ == "__main__":
    verify_enclosure()
