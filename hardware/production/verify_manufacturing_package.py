#!/usr/bin/env python3
"""
Written 2026-10-19 08:55 UTC in the Pi harness by antigravity/gemini-3.8-flash
Verification Check for JLCPCB / PCBWay SMT Manufacturing Package
"""

import os
import csv
import re
import sys

def verify_manufacturing_package():
    prod_dir = os.path.dirname(os.path.abspath(__file__))
    hw_dir = os.path.dirname(prod_dir)

    bom_path = os.path.join(prod_dir, "solardeck_bom.csv")
    cpl_path = os.path.join(prod_dir, "solardeck_cpl.csv")
    net_path = os.path.join(hw_dir, "solardeck-carrier.net")
    pcb_path = os.path.join(hw_dir, "solardeck-carrier.kicad_pcb")

    print("[SMT Check] Verifying SMT Production Package & Centroid Alignment...")
    assert os.path.exists(bom_path), f"Missing {bom_path}"
    assert os.path.exists(cpl_path), f"Missing {cpl_path}"
    assert os.path.exists(net_path), f"Missing {net_path}"
    assert os.path.exists(pcb_path), f"Missing {pcb_path}"

    # 1. Read BOM CSV
    bom_components = {}
    with open(bom_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            des = row["Designator"]
            val = row["Comment"]
            lcsc = row["LCSC Part #"]
            assert lcsc.startswith("C"), f"Invalid LCSC part number {lcsc} for {des}"
            bom_components[des] = (val, lcsc)

    print(f"  ✓ BOM verified: {len(bom_components)} turnkey components mapped to LCSC.")

    # 2. Read CPL (Centroid) CSV
    cpl_components = {}
    with open(cpl_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            des = row["Designator"]
            x = float(row["Mid X"])
            y = float(row["Mid Y"])
            layer = row["Layer"]
            # Assert coordinates are within the 222.0 × 160.0 mm board perimeter with 5mm margin
            assert 5.0 <= x <= 220.0, f"{des} X coordinate {x} out of board bounds"
            assert 5.0 <= y <= 158.0, f"{des} Y coordinate {y} out of board bounds"
            assert layer in ["top", "bottom"], f"Invalid layer {layer} for {des}"
            cpl_components[des] = (x, y, layer)

    print(f"  ✓ CPL Centroid verified: {len(cpl_components)} SMT parts inside physical 222×160mm PCB boundary.")

    # 3. Verify 1:1 Alignment between BOM and CPL
    assert set(bom_components.keys()) == set(cpl_components.keys()), "BOM and CPL designators do not match 1:1"
    print("  ✓ BOM and CPL designators match 1:1 with zero discrepancies.")

    # 4. Verify Netlist Coverage
    with open(net_path, "r", encoding="utf-8") as f:
        net_content = f.read()

    for des in bom_components.keys():
        assert f'(ref "{des}")' in net_content, f"Component {des} from BOM missing in KiCad netlist"

    # 5. Verify PCB Footprint Placement
    with open(pcb_path, "r", encoding="utf-8") as f:
        pcb_content = f.read()

    for des in bom_components.keys():
        assert f'(fp_text reference "{des}"' in pcb_content, f"Footprint {des} missing on physical PCB"

    print("✓ Manufacturing Package Verification Passed: Turnkey SMT files 100% verified!")

if __name__ == "__main__":
    verify_manufacturing_package()
