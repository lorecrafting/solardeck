#!/usr/bin/env python3
"""
Capture 10 already-specced BOM line items into the schematic layer (20/62 -> 30/62).

Every part below is a REAL line item of docs/BOM_COST_ESTIMATE.md with a datasheet-anchored
footprint (package + size + pitch verified 2026-11-02). The change writes, in one step:
  1. a (symbol ...) block into the correct sheet of hardware/*.kicad_sch
  2. a (comp (ref ...)) block into hardware/solardeck-carrier.net
  3. a row into hardware/production/solardeck_bom.csv
  4. a row into hardware/production/solardeck_cpl.csv (centroid inside 222x160 board)
and asserts afterwards that netlist == bom == cpl designators, exactly the Phase 11 contract.
Run:  python3 scripts/capture_schematic_parts.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HW = os.path.join(ROOT, "hardware")
PROD = os.path.join(HW, "production")
NET = os.path.join(HW, "solardeck-carrier.net")

# (ref, sheet, value, footprint, manu, desc, datasheet, x_mm, y_mm)
PARTS = [
    # --- power sheet (Sheet 1: 67000001) ---
    ("U19", "power", "TPS22918DBVR", "Package_TO_SOT_SMD:SOT-23-6",
     "Texas Instruments", "Ultra-Low Leakage Load Switch (LTE/Wi-Fi/Audio/Exp rail gate, I_off<25mW S2idle)", 
     "https://www.ti.com/lit/ds/symlink/tps22918.pdf", 150.0, 135.0),
    ("U20", "power", "INA3221AIRGVR", "Package_DFN_QFN:VQFN-16-1EP_4x4mm_P0.65mm",
     "Texas Instruments", "3-Channel High-Side Current & Power Monitor (rail telemetry)",
     "https://www.ti.com/lit/ds/symlink/ina3221.pdf", 170.0, 135.0),
    ("U21", "power", "BQ27441-G1A", "Package_DFN_QFN:VSON-12_2.5x4mm_P0.5mm",
     "Texas Instruments", "Impedance Track Battery Fuel Gauge & Health (SOH/ESR)",
     "https://www.ti.com/lit/ds/symlink/bq27441-g1a.pdf", 150.0, 150.0),
    ("U22", "power", "TPS2051BDBVR", "Package_TO_SOT_SMD:SOT-23-5",
     "Texas Instruments", "1.5A Current-Limited USB Host Distribution Power Switch",
     "https://www.ti.com/lit/ds/symlink/tps2051.pdf", 170.0, 150.0),
    # --- compute / co-processor sensors (Sheet 2: 67000002) ---
    ("U23", "compute", "BMA400", "Package_LGA:LGA-12_2x2mm_P0.5mm",
     "Bosch Sensortec", "3-Axis Accelerometer, 3.5uA pick-up wake (BMA400)",
     "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/smart-motion/bst-bma400-ds000.pdf", 20.0, 60.0),
    ("U24", "compute", "BMP390", "Package_LGA:LGA-10_2x2mm_P0.5mm",
     "Bosch Sensortec", "Precision Barometric Pressure & Altimeter (BMP390)",
     "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp390-ds000.pdf", 35.0, 60.0),
    ("U25", "compute", "TMP112AIDRLR", "Package_TO_SOT_SMD:SOT-563",
     "Texas Instruments", "Precision Digital Temperature Sensor (battery + display backplane)",
     "https://www.ti.com/lit/ds/symlink/tmp112.pdf", 50.0, 60.0),
    # --- io sheet (Sheet 4: 67000004) ---
    ("U26", "io", "TUSB320RWBR", "Package_DFN_QFN:X2QFN-12_1.6x1.6mm_P0.4mm",
     "Texas Instruments", "USB-C Configuration Channel Dual-Role DRP Controller",
     "https://www.ti.com/lit/ds/symlink/tusb320.pdf", 140.0, 60.0),
    ("U27", "io", "TXU0104PWR", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
     "Texas Instruments", "Fail-Safe Cross-Domain Buffer with I_off Partial-Power-Down",
     "https://www.ti.com/lit/ds/symlink/txu0104.pdf", 155.0, 60.0),
    ("U28", "io", "MAX98357A", "Package_DFN_QFN:WQFN-16-1EP_3x3mm_P0.5mm",
     "Maxim Integrated", "I2S Class-D Speaker Amplifier, 1W (MAX98357A)",
     "https://www.analog.com/media/en/technical-datasheets/max98357a.pdf", 170.0, 60.0),
]

SHEET_UUID = {"power": "67000001", "compute": "67000002", "io": "67000004"}
SHEETPATH = {"power": ("/Power_PMIC/", "67000000-0001"), "compute": ("/Compute_DualBrain/", "67000000-0002"), "io": ("/IO_Peripherals/", "67000000-0004")}
SCH_FILE = {"power": os.path.join(HW, "power.kicad_sch"), "compute": os.path.join(HW, "compute.kicad_sch"), "io": os.path.join(HW, "io.kicad_sch")}

# next free comp-level tstamp counter per sheet (existing .net max: power 0007, compute 0006, io 0005)
TSTAMP_NEXT = {"power": 8, "compute": 7, "io": 6}


def symbol_block(ref, sheet, value, fp, desc, dsx, mm_x, mm_y, seq):
    """KiCad eeschema symbol: lib_id + Reference/Value/Footprint/Datasheet/Description props."""
    uuid = SHEET_UUID[sheet]
    lib = {"power": "SolarDeck_Power", "compute": "SolarDeck_Compute", "io": "SolarDeck_IO"}[sheet]
    u = f"{uuid}-{seq:04d}-0000-0000-000000000001"
    return (f"  ;; {ref}: {value} ({desc.split('(')[0].strip()})"
            f"\n  (symbol (lib_id \"{lib}:{value}\") (at {mm_x} {mm_y} 0) (unit 1)"
            f"\n    (in_bom yes) (on_board yes) (dnp no)"
            f"\n    (uuid \"{u}\")"
            f"\n    (property \"Reference\" \"{ref}\" (at {mm_x} {mm_y - 10} 0) (effects (font (size 1.27 1.27))))"
            f"\n    (property \"Value\" \"{value}\" (at {mm_x} {mm_y - 7.5} 0) (effects (font (size 1.27 1.27))))"
            f"\n    (property \"Footprint\" \"{fp}\" (at {mm_x} {mm_y} 0) (effects (font (size 1.27 1.27)) hide))"
            f"\n    (property \"Datasheet\" \"{dsx}\" (at {mm_x} {mm_y} 0) (effects (font (size 1.27 1.27)) hide))"
            f"\n    (property \"Description\" \"{desc}\" (at {mm_x} {mm_y} 0) (effects (font (size 1.27 1.27)) hide))"
            f"\n  )\n")


def comp_block(ref, value, fp, manu, desc, dsx, sheet, seq):
    spath, suid = SHEETPATH[sheet]
    return (f"    (comp (ref \"{ref}\")"
            f"\n      (value \"{value}\")"
            f"\n      (footprint \"{fp}\")"
            f"\n      (fields"
            f"\n        (field (name \"Manufacturer\") \"{manu}\")"
            f"\n        (field (name \"Description\") \"{desc}\"))"
            f"\n      (sheetpath (names \"{spath}\") (tstamps \"/{suid}-0000-0000-0000-000000000001/\"))"
            f"\n      (tstamps \"{SHEET_UUID[sheet]}-{seq:04d}-0000-0000-000000000001\"))\n")


def main():
    # --- 1. .kicad_sch symbol blocks: insert before the file's final closing paren ---
    for sheet, path in SCH_FILE.items():
        text = open(path).read()
        assert text.rstrip().endswith(")"), f"{path} does not end with ')'"
        blocks = []
        seq = 20  # keep symbol uuids well clear of existing 0001..0019 objects
        for ref, sh, value, fp, manu, desc, dsx, x, y in PARTS:
            if sh != sheet:
                continue
            blocks.append(symbol_block(ref, sh, value, fp, desc, dsx, x, y, seq))
            seq += 1
        insert_at = text.rstrip().rfind(")")
        text = text[:insert_at] + "".join(blocks) + text[insert_at:]
        open(path, "w").write(text)
        print(f"  symbol blocks -> {os.path.basename(path)} ({len(blocks)})")

    # --- 2. netlist comps: insert before '  )' that closes the (comp ...) section ---
    net = open(NET).read()
    comps_join = "".join(
        comp_block(ref, value, fp, manu, desc, dsx, sheet, TSTAMP_NEXT[sheet] + i)
        for i, (ref, sheet, value, fp, manu, desc, dsx, x, y) in enumerate(PARTS)
    )
    anchor = "  )\n  (nets"
    assert net.count(anchor) == 1, f"comps-section close anchor not unique/found (n={net.count(anchor)})"
    net = net.replace(anchor, comps_join + anchor, 1)
    open(NET, "w").write(net)
    print(f"  comp blocks -> solardeck-carrier.net")

    # --- 3&4. BOM + CPL CSV rows ---
    bom_path = os.path.join(PROD, "solardeck_bom.csv")
    cpl_path = os.path.join(PROD, "solardeck_cpl.csv")
    bom_lines = open(bom_path).read().rstrip("\n").splitlines()
    cpl_lines = open(cpl_path).read().rstrip("\n").splitlines()
    for ref, sheet, value, fp, manu, desc, dsx, x, y in PARTS:
        short_fp = fp.split(":")[-1]
        bom_lines.append(f"{value},{ref},{short_fp},TBD")
        cpl_lines.append(f"{ref},{value},{short_fp},{x},{y},0.0,top")
    open(bom_path, "w").write("\n".join(bom_lines) + "\n")
    open(cpl_path, "w").write("\n".join(cpl_lines) + "\n")
    print(f"  rows -> solardeck_bom.csv ({len(PARTS)}), solardeck_cpl.csv ({len(PARTS)})")

    # --- assert the Phase 11 contract, exactly as check_bom_coverage does ---
    net2 = open(NET).read()
    netlist = set(re.findall(r'\(comp \(ref "([A-Z][A-Z0-9_]*)', net2))
    def designators(path):
        import csv as _csv
        with open(path) as f:
            refs = set()
            for r in _csv.DictReader(f):
                for ref in re.split(r"[,\s]+", (r.get("Designator") or "").strip()):
                    if ref:
                        refs.add(ref)
        return refs
    bom = designators(bom_path)
    cpl = designators(cpl_path)
    assert netlist == bom == cpl, f"mismatch: net={sorted(netlist-bom)} bom={sorted(bom-netlist)} cpl={sorted(cpl-bom)}"
    assert len(netlist) == 30, f"expected 30 designators, got {len(netlist)}"
    print(f"  OK: netlist == BOM == CPL == {len(netlist)} designators (20 -> 30)")


if __name__ == "__main__":
    sys.exit(main())