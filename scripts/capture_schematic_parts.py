#!/usr/bin/env python3
"""
Capture 10 already-specced BOM line items into the schematic layer (30/62 -> 40/62).

Every part below is a REAL line item of docs/BOM_COST_ESTIMATE.md with a datasheet-anchored
footprint (package + size + pitch verified 2026-11-02) and a verified LCSC part number.
The change writes, in one step:
  1. a (symbol ...) block into the correct sheet of hardware/*.kicad_sch
  2. a (comp (ref ...)) block into hardware/solardeck-carrier.net
  3. a row into hardware/production/solardeck_bom.csv (real LCSC number, no TBD)
  4. a row into hardware/production/solardeck_cpl.csv (centroid inside 222x160 board)
and asserts afterwards that netlist == bom == cpl designators, exactly the Phase 11 contract.
Idempotent: parts already present in the netlist are skipped, so re-runs are safe.
Run:  python3 scripts/capture_schematic_parts.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HW = os.path.join(ROOT, "hardware")
PROD = os.path.join(HW, "production")
NET = os.path.join(HW, "solardeck-carrier.net")

# (ref, sheet, value, footprint, manu, desc, datasheet, x_mm, y_mm, lcsc)
PARTS = [
    # --- power sheet (Sheet 1: 67000001) ---
    ("U19", "power", "TPS22918DBVR", "Package_TO_SOT_SMD:SOT-23-6",
     "Texas Instruments", "Ultra-Low Leakage Load Switch (LTE/Wi-Fi/Audio/Exp rail gate, I_off<25mW S2idle)",
     "https://www.ti.com/lit/ds/symlink/tps22918.pdf", 150.0, 135.0, "C131941"),
    ("U20", "power", "INA3221AIRGVR", "Package_DFN_QFN:VQFN-16-1EP_4x4mm_P0.65mm",
     "Texas Instruments", "3-Channel High-Side Current & Power Monitor (rail telemetry)",
     "https://www.ti.com/lit/ds/symlink/ina3221.pdf", 170.0, 135.0, "C181255"),
    ("U21", "power", "BQ27441-G1A", "Package_DFN_QFN:VSON-12_2.5x4mm_P0.5mm",
     "Texas Instruments", "Impedance Track Battery Fuel Gauge & Health (SOH/ESR)",
     "https://www.ti.com/lit/ds/symlink/bq27441-g1a.pdf", 150.0, 150.0, "C473397"),
    ("U22", "power", "TPS2051BDBVR", "Package_TO_SOT_SMD:SOT-23-5",
     "Texas Instruments", "1.5A Current-Limited USB Host Distribution Power Switch",
     "https://www.ti.com/lit/ds/symlink/tps2051.pdf", 170.0, 150.0, "C24593"),
    # --- compute / co-processor sensors (Sheet 2: 67000002) ---
    ("U23", "compute", "BMA400", "Package_LGA:LGA-12_2x2mm_P0.5mm",
     "Bosch Sensortec", "3-Axis Accelerometer, 3.5uA pick-up wake (BMA400)",
     "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/smart-motion/bst-bma400-ds000.pdf", 20.0, 60.0, "C437655"),
    ("U24", "compute", "BMP390", "Package_LGA:LGA-10_2x2mm_P0.5mm",
     "Bosch Sensortec", "Precision Barometric Pressure & Altimeter (BMP390)",
     "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp390-ds000.pdf", 35.0, 60.0, "C5124834"),
    ("U25", "compute", "TMP112AIDRLR", "Package_TO_SOT_SMD:SOT-563",
     "Texas Instruments", "Precision Digital Temperature Sensor (battery + display backplane)",
     "https://www.ti.com/lit/ds/symlink/tmp112.pdf", 50.0, 60.0, "C28927"),
    # --- io sheet (Sheet 4: 67000004) ---
    ("U26", "io", "TUSB320RWBR", "Package_DFN_QFN:X2QFN-12_1.6x1.6mm_P0.4mm",
     "Texas Instruments", "USB-C Configuration Channel Dual-Role DRP Controller",
     "https://www.ti.com/lit/ds/symlink/tusb320.pdf", 140.0, 60.0, "C2674065"),
    ("U27", "io", "TXU0104PWR", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
     "Texas Instruments", "Fail-Safe Cross-Domain Buffer with I_off Partial-Power-Down",
     "https://www.ti.com/lit/ds/symlink/txu0104.pdf", 155.0, 60.0, "C2938871"),
    ("U28", "io", "MAX98357A", "Package_DFN_QFN:WQFN-16-1EP_3x3mm_P0.5mm",
     "Maxim Integrated", "I2S Class-D Speaker Amplifier, 1W (MAX98357A)",
     "https://www.analog.com/media/en/technical-datasheets/max98357a.pdf", 170.0, 60.0, "C910544"),
    # --- power sheet batch 2: PD sink, battery PCM, VBUS OR-ing ---
    ("U29", "power", "STUSB4500QTR", "Package_DFN_QFN:VQFN-24-1EP_4x4mm_P0.5mm",
     "STMicroelectronics", "Standalone USB-PD 20W Sink Controller (9V/12V contract, dead-battery mode)",
     "https://www.st.com/resource/en/datasheet/stusb4500.pdf", 190.0, 135.0, "C2678061"),
    ("U31", "power", "BQ29700DSET", "Package_DFN_QFN:WSON-6_1.5x1.5mm_P0.5mm",
     "Texas Instruments", "Battery Protection IC (PCM; li-ion OVP 4.275V - see ADR on LiFePO4 profile)",
     "https://www.ti.com/lit/ds/symlink/bq29700.pdf", 190.0, 150.0, "C2876282"),
    ("U32", "power", "LM66100DCKR", "Package_TO_SOT_SMD:SC-70-6",
     "Texas Instruments", "Low-IQ Ideal-Diode VBUS OR-ing Controller (dual, 2A)",
     "https://www.ti.com/lit/ds/symlink/lm66100.pdf", 190.0, 145.0, "C2869734"),
    # --- io sheet batch 2: NFC, ESD TVS, dual MEMS mics, LoRa module, DAC, haptic ---
    ("U30", "io", "PN5321A3HN", "Package_DFN_QFN:HVQFN-40_6x6mm_P0.5mm",
     "NXP Semiconductors", "13.56MHz NFC/Smartcard Controller + Crypto Signer (FeliCa/ISO14443)",
     "https://www.nxp.com/docs/en/data-sheet/PN5321A3-C10655.pdf", 20.0, 80.0, "C28925"),
    ("U33", "io", "TPD4E05U06", "Package_DFN_QFN:USON-10_2.5x1mm_P0.5mm",
     "Texas Instruments", "Low-Capacitance ESD/TVS Diode Array (USB-C pin protection)",
     "https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf", 50.0, 80.0, "C138714"),
    ("U34", "io", "SPH0645LM4H-B", "Package_LGA:MIC-SMD-6P_3.5x2.65mm_P0.9mm",
     "Knowles", "I2S Digital MEMS Microphone (left, 65mm from U35)",
     "https://www.knowles.com/docs/default-source/knowles-datasheets/SPH0645LM4H-B_datasheet.pdf", 110.0, 80.0, "C19190864"),
    ("U35", "io", "SPH0645LM4H-B", "Package_LGA:MIC-SMD-6P_3.5x2.65mm_P0.9mm",
     "Knowles", "I2S Digital MEMS Microphone (right, 65mm from U34)",
     "https://www.knowles.com/docs/default-source/knowles-datasheets/SPH0645LM4H-B_datasheet.pdf", 175.0, 80.0, "C19190864"),
    ("U36", "io", "E22-900M22S", "Module_EByte:E22-900M22S_20x14mm",
     "Ebyte", "915/868MHz LoRa Transceiver Module (Semtech SX1262, +22dBm)",
     "https://www.ebyte.com/en/product-view-news.html?id=1569", 20.0, 110.0, "C411293"),
    ("U37", "io", "PCM5102APWR", "Package_SO:TSSOP-20_6.5x4.4mm_P0.65mm",
     "Texas Instruments", "32-bit Stereo I2S Headphone DAC (384kHz)",
     "https://www.ti.com/lit/ds/symlink/pcm5102a.pdf", 155.0, 110.0, "C107671"),
    ("U38", "io", "DRV2605LDGST", "Package_TO_SOT_SMD:VSSOP-10_3x4.9mm_P0.5mm",
     "Texas Instruments", "Wideband Haptic Driver (LRA actuator controller)",
     "https://www.ti.com/lit/ds/symlink/drv2605l.pdf", 170.0, 110.0, "C425927"),
]

SHEET_UUID = {"power": "67000001", "compute": "67000002", "io": "67000004"}
SHEETPATH = {"power": ("/Power_PMIC/", "67000000-0001"), "compute": ("/Compute_DualBrain/", "67000000-0002"), "io": ("/IO_Peripherals/", "67000000-0004")}
SCH_FILE = {"power": os.path.join(HW, "power.kicad_sch"), "compute": os.path.join(HW, "compute.kicad_sch"), "io": os.path.join(HW, "io.kicad_sch")}

# next free comp-level tstamp counter per sheet (existing .net max: power 0008, compute 0006, io 0007)
TSTAMP_NEXT = {"power": 12, "compute": 7, "io": 12}


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


def pcb_block(ref, value, fp, mm_x, mm_y):
    """KiCad PCB footprint: reference label + value label + one reference-grade pad.
    Matches the U5/U14 convention in solardeck-carrier.kicad_pcb; full pad maps and
    routing remain the stated 'unrouted PCB' phase."""
    return (f"\n  (footprint \"{fp}\" (layer \"F.Cu\")"
            f"\n    (at {mm_x} {mm_y})"
            f"\n    (fp_text reference \"{ref}\" (at 0 -3.0) (layer \"F.SilkS\") (effects (font (size 1 1) (thickness 0.15))))"
            f"\n    (fp_text value \"{value}\" (at 0 3.0) (layer \"F.Fab\") (effects (font (size 1 1) (thickness 0.15))))"
            f"\n    (pad \"1\" smd rect (at 0 0) (size 1.0 1.0) (layers \"F.Cu\" \"F.Paste\" \"F.Mask\"))"
            f"\n  )")


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
    net0 = open(NET).read()
    present = set(re.findall(r'\(comp \(ref "([A-Z][A-Z0-9_]*)', net0))

    def skip(ref):
        if ref in present:
            print(f"  skip {ref}: already captured")
            return True
        return False

    # --- 1. .kicad_sch symbol blocks: insert before the file's final closing paren ---
    new_parts = [(p, i) for i, p in enumerate(PARTS) if not skip(p[0])]
    for sheet, path in SCH_FILE.items():
        text = open(path).read()
        assert text.rstrip().endswith(")"), f"{path} does not end with ')'"
        blocks = []
        seq = 30  # keep symbol uuids well clear of existing 0001..0019 objects
        for (ref, sh, value, fp, manu, desc, dsx, x, y, lcsc), _ in new_parts:
            if sh != sheet:
                continue
            if f":{value}\") (at " in text:
                print(f"  skip {ref}: symbol already in {os.path.basename(path)}")
                continue
            blocks.append(symbol_block(ref, sh, value, fp, desc, dsx, x, y, seq))
            seq += 1
        insert_at = text.rstrip().rfind(")")
        text = text[:insert_at] + "".join(blocks) + text[insert_at:]
        open(path, "w").write(text)
        print(f"  symbol blocks -> {os.path.basename(path)} ({len(blocks)} new)")

    # --- 2. netlist comps: insert before '  )' that closes the (comp ...) section ---
    net = open(NET).read()
    comps_join = "".join(
        comp_block(ref, value, fp, manu, desc, dsx, sheet, TSTAMP_NEXT[sheet] + i)
        for (ref, sheet, value, fp, manu, desc, dsx, x, y, lcsc), i in new_parts
    )
    anchor = "  )\n  (nets"
    assert net.count(anchor) == 1, f"comps-section close anchor not unique/found (n={net.count(anchor)})"
    net = net.replace(anchor, comps_join + anchor, 1)
    open(NET, "w").write(net)
    print(f"  comp blocks -> solardeck-carrier.net ({len(new_parts)} new)")

    # --- 2b. kicad_pcb footprint blocks (reference-grade single pad per U5/U14) ---
    pcb_path = os.path.join(HW, "solardeck-carrier.kicad_pcb")
    pcb_text = open(pcb_path).read()
    pcb_blocks = []
    for (ref, sh, value, fp, manu, desc, dsx, x, y, lcsc), _ in new_parts:
        if f'(fp_text reference "{ref}"' in pcb_text:
            print(f"  skip {ref}: footprint already in solardeck-carrier.kicad_pcb")
            continue
        pcb_blocks.append(pcb_block(ref, value, fp, x, y))
    if pcb_blocks:
        pcb_insert = pcb_text.rstrip().rfind(")")
        pcb_text = pcb_text[:pcb_insert] + "".join(pcb_blocks) + pcb_text[pcb_insert:]
        open(pcb_path, "w").write(pcb_text)
    print(f"  footprint blocks -> solardeck-carrier.kicad_pcb ({len(pcb_blocks)} new)")

    # --- 3&4. BOM + CPL CSV rows (real LCSC number) ---
    bom_path = os.path.join(PROD, "solardeck_bom.csv")
    cpl_path = os.path.join(PROD, "solardeck_cpl.csv")
    bom_lines = open(bom_path).read().rstrip("\n").splitlines()
    cpl_lines = open(cpl_path).read().rstrip("\n").splitlines()
    added = 0
    for ref, sheet, value, fp, manu, desc, dsx, x, y, lcsc in PARTS:
        if skip(ref):
            continue
        short_fp = fp.split(":")[-1]
        bom_lines.append(f"{value},{ref},{short_fp},{lcsc}")
        cpl_lines.append(f"{ref},{value},{short_fp},{x},{y},0.0,top")
        added += 1
    open(bom_path, "w").write("\n".join(bom_lines) + "\n")
    open(cpl_path, "w").write("\n".join(cpl_lines) + "\n")
    print(f"  rows -> solardeck_bom.csv + cpl.csv ({added} new)")

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
    assert len(netlist) == 40, f"expected 40 designators, got {len(netlist)}"
    print(f"  OK: netlist == BOM == CPL == {len(netlist)} designators (30 -> 40)")


if __name__ == "__main__":
    sys.exit(main())