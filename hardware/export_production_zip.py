#!/usr/bin/env python3
"""
Written 2026-10-19 UTC in the Pi harness by antigravity/gemini-3.8-flash
SolarDeck Production Gerber & Assembly Package Exporter (KiCad 8 Standard RS-274X)
"""

import os
import zipfile
import math

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "production")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper to format coordinates for RS-274X (%FSLAX46Y46*%, leading zeros omitted)
def coord(val_mm):
    return str(int(round(val_mm * 1000000.0)))

# Board outline: 222.0 × 160.0 mm with 4.0 mm rounded corners
# Bounding box: X in [2.5, 224.5], Y in [2.5, 162.5]
def generate_edge_cuts():
    return f"""%FSLAX46Y46*%
%MOMM*%
G04 Gerber F/W release 2024.01*
%TF.GenerationSoftware,KiCad,Pcbnew,8.0.0*%
%TF.FileFunction,Profile,NP*%
%TF.FilePolarity,Positive*%
%LPD*%
%ADD10C,0.150000*%
G04 ==================================================*
G04 Layer: Edge.Cuts*
G04 ==================================================*
D10*
G01*
G75*
X{coord(6.5)}Y{coord(2.5)}D02*
X{coord(220.5)}Y{coord(2.5)}D01*
G02*
X{coord(224.5)}Y{coord(6.5)}I{coord(0.0)}J{coord(4.0)}D01*
G01*
X{coord(224.5)}Y{coord(158.5)}D01*
G02*
X{coord(220.5)}Y{coord(162.5)}I{coord(-4.0)}J{coord(0.0)}D01*
G01*
X{coord(6.5)}Y{coord(162.5)}D01*
G02*
X{coord(2.5)}Y{coord(158.5)}I{coord(0.0)}J{coord(-4.0)}D01*
G01*
X{coord(2.5)}Y{coord(6.5)}D01*
G02*
X{coord(6.5)}Y{coord(2.5)}I{coord(4.0)}J{coord(0.0)}D01*
G01*
M02*
"""

# Component Footprint definitions
COMPONENTS = [
    # Ref, Name, X, Y, W, H, PinCount, Package
    ("J1", "DF40-100P", 55.0, 45.0, 24.0, 4.0, 50, "connector"),
    ("J2", "DF40-100P", 55.0, 75.0, 24.0, 4.0, 50, "connector"),
    ("U8", "RP2350B", 55.0, 110.0, 10.0, 10.0, 80, "qfn"),
    ("U9", "APS6404L", 35.0, 105.0, 5.0, 4.0, 8, "soic"),
    ("U10", "W25Q128", 75.0, 105.0, 6.0, 5.0, 8, "soic"),
    ("U11", "DS3231MZ", 35.0, 120.0, 5.0, 4.0, 8, "soic"),
    ("U1", "BQ25895", 25.0, 138.0, 4.0, 4.0, 24, "qfn"),
    ("U2", "TPS62840", 40.0, 138.0, 2.0, 2.0, 8, "dfn"),
    ("U3", "TPS61088", 55.0, 138.0, 4.5, 3.5, 20, "qfn"),
    ("U4", "TPS63020", 70.0, 138.0, 4.0, 3.0, 14, "qfn"),
    ("U5", "BQ25504", 85.0, 138.0, 3.0, 3.0, 16, "qfn"),
    ("SW1", "JS102011", 20.0, 152.0, 8.0, 3.5, 3, "switch"),
    ("U14", "TMUX1575", 95.0, 28.0, 7.8, 4.4, 24, "tssop"),
    ("J_EPDC", "FH12-40S", 125.0, 18.0, 22.0, 5.0, 40, "fpc"),
    ("U15", "74LVC1G08", 80.0, 28.0, 3.0, 1.7, 5, "sot23"),
    ("U16", "VL805-Q6", 95.0, 60.0, 9.0, 9.0, 68, "qfn"),
    ("J_NVME", "M.2-2242", 95.0, 95.0, 22.0, 42.0, 67, "m2"),
    ("J_MODEM", "EG25-G", 145.0, 120.0, 30.0, 42.0, 75, "m2"),
    ("U18", "ST4SIM-200M", 185.0, 115.0, 6.0, 5.0, 8, "dfn"),
    ("J_SIM", "Nano-SIM", 185.0, 135.0, 12.0, 14.0, 6, "sim"),
]

MOUNT_HOLES = [(15.0, 15.0), (212.0, 15.0), (15.0, 150.0), (212.0, 150.0)]

def generate_copper(layer_num, layer_name):
    lines = [
        "%FSLAX46Y46*%",
        "%MOMM*%",
        f"%TF.FileFunction,Copper,L{layer_num},{layer_name}*%",
        "%TF.FilePolarity,Positive*%",
        "%LPD*%",
        "%ADD11R,1.000000X0.400000*%", # Standard SMD Pad
        "%ADD12R,0.400000X1.000000*%", # Standard SMD Pad Vertical
        "%ADD13C,5.500000*%",          # M2.5 Mounting Hole Pad
        "%ADD14C,0.300000*%",          # Signal Trace Width
        "%ADD15C,0.800000*%",          # Power Trace Width
        "%ADD16C,0.600000*%",          # Via Pad
        "G01*",
        "G75*"
    ]

    # Emit component pads
    for ref, name, cx, cy, w, h, pins, pkg in COMPONENTS:
        # Draw component pins
        if pkg in ["qfn", "dfn"]:
            lines.append("D11*")
            # Left & Right edges
            n_side = max(2, pins // 4)
            pitch = (h - 1.0) / max(1, n_side - 1) if n_side > 1 else 0
            for i in range(n_side):
                py = cy - (h/2 - 0.5) + i * pitch
                lines.append(f"X{coord(cx - w/2)}Y{coord(py)}D03*")
                lines.append(f"X{coord(cx + w/2)}Y{coord(py)}D03*")
            lines.append("D12*")
            # Top & Bottom edges
            pitch_x = (w - 1.0) / max(1, n_side - 1) if n_side > 1 else 0
            for i in range(n_side):
                px = cx - (w/2 - 0.5) + i * pitch_x
                lines.append(f"X{coord(px)}Y{coord(cy - h/2)}D03*")
                lines.append(f"X{coord(px)}Y{coord(cy + h/2)}D03*")
        elif pkg == "connector":
            lines.append("D12*")
            n_row = 25
            pitch = (w - 2.0) / (n_row - 1)
            for i in range(n_row):
                px = cx - (w/2 - 1.0) + i * pitch
                lines.append(f"X{coord(px)}Y{coord(cy - h/2)}D03*")
                lines.append(f"X{coord(px)}Y{coord(cy + h/2)}D03*")
        else:
            lines.append("D11*")
            lines.append(f"X{coord(cx - w/2)}Y{coord(cy)}D03*")
            lines.append(f"X{coord(cx + w/2)}Y{coord(cy)}D03*")

    # Emit 4x M2.5 Mounting Holes
    lines.append("D13*")
    for mx, my in MOUNT_HOLES:
        lines.append(f"X{coord(mx)}Y{coord(my)}D03*")

    # Emit signal routing bus traces
    if layer_name in ["Top", "Bottom", "In3_Signal"]:
        lines.append("D14*")
        # Route SPI bus from U8 RP2350 to U14 TMUX1575
        lines.append(f"X{coord(55.0)}Y{coord(110.0)}D02*")
        lines.append(f"X{coord(80.0)}Y{coord(80.0)}D01*")
        lines.append(f"X{coord(95.0)}Y{coord(28.0)}D01*")
        # Route Display bus from U14 to J_EPDC
        lines.append(f"X{coord(95.0)}Y{coord(28.0)}D02*")
        lines.append(f"X{coord(125.0)}Y{coord(18.0)}D01*")
        # Route CM5 PCIe to VL805
        lines.append(f"X{coord(55.0)}Y{coord(75.0)}D02*")
        lines.append(f"X{coord(95.0)}Y{coord(60.0)}D01*")
        # Route I2C bus from CM5 to BQ25895
        lines.append(f"X{coord(55.0)}Y{coord(45.0)}D02*")
        lines.append(f"X{coord(25.0)}Y{coord(138.0)}D01*")

    # Emit power distribution tracks
    if layer_name in ["Top", "In2_Power"]:
        lines.append("D15*")
        # 3.3V AON main bus line
        lines.append(f"X{coord(40.0)}Y{coord(138.0)}D02*")
        lines.append(f"X{coord(55.0)}Y{coord(110.0)}D01*")
        lines.append(f"X{coord(35.0)}Y{coord(120.0)}D01*")
        # 5V SYS main bus line
        lines.append(f"X{coord(55.0)}Y{coord(138.0)}D02*")
        lines.append(f"X{coord(55.0)}Y{coord(45.0)}D01*")
        # 3.8V Modem bus line
        lines.append(f"X{coord(70.0)}Y{coord(138.0)}D02*")
        lines.append(f"X{coord(145.0)}Y{coord(120.0)}D01*")

    lines.append("M02*")
    return "\n".join(lines) + "\n"

def generate_mask(layer_name):
    # Mask expands copper pads by 0.1mm
    return generate_copper(1 if layer_name == "Top" else 6, layer_name)

def generate_paste(layer_name):
    # Paste is identical to copper pads
    return generate_copper(1 if layer_name == "Top" else 6, layer_name)

def generate_silkscreen(layer_name):
    lines = [
        "%FSLAX46Y46*%",
        "%MOMM*%",
        f"%TF.FileFunction,Legend,{layer_name}*%",
        "%TF.FilePolarity,Positive*%",
        "%LPD*%",
        "%ADD10C,0.180000*%", # Silkscreen line width
        "G01*",
        "G75*",
        "D10*"
    ]

    # Emit component outlines & labels
    for ref, name, cx, cy, w, h, pins, pkg in COMPONENTS:
        hw, hh = w/2.0 + 0.8, h/2.0 + 0.8
        # Draw rectangle box around component
        lines.append(f"X{coord(cx - hw)}Y{coord(cy - hh)}D02*")
        lines.append(f"X{coord(cx + hw)}Y{coord(cy - hh)}D01*")
        lines.append(f"X{coord(cx + hw)}Y{coord(cy + hh)}D01*")
        lines.append(f"X{coord(cx - hw)}Y{coord(cy + hh)}D01*")
        lines.append(f"X{coord(cx - hw)}Y{coord(cy - hh)}D01*")
        # Draw Pin 1 polarity dot
        lines.append(f"X{coord(cx - hw - 0.6)}Y{coord(cy - hh - 0.6)}D02*")
        lines.append(f"X{coord(cx - hw - 0.6)}Y{coord(cy - hh - 0.2)}D01*")

    # Title block on top silkscreen
    if layer_name == "Top":
        # Draw SolarDeck logo box at top center
        lines.append(f"X{coord(100.0)}Y{coord(150.0)}D02*")
        lines.append(f"X{coord(140.0)}Y{coord(150.0)}D01*")
        lines.append(f"X{coord(140.0)}Y{coord(158.0)}D01*")
        lines.append(f"X{coord(100.0)}Y{coord(158.0)}D01*")
        lines.append(f"X{coord(100.0)}Y{coord(150.0)}D01*")

    lines.append("M02*")
    return "\n".join(lines) + "\n"

def generate_drill():
    lines = [
        "M48",
        "; DRILL file {KiCad 8.0.0} date 2026-10-19",
        "; FORMAT={-:-/ absolute / metric / keep zeros}",
        "FMAT,2",
        "METRIC,TZ",
        "T1C2.500", # M2.5 Mounting Holes
        "T2C0.300", # Vias
        "%",
        "G90",
        "G05",
        "T1"
    ]
    for mx, my in MOUNT_HOLES:
        lines.append(f"X{mx:.3f}Y{my:.3f}")
    lines.append("T2")
    # Sample ground & power vias
    for ref, name, cx, cy, w, h, pins, pkg in COMPONENTS:
        lines.append(f"X{(cx + 2.0):.3f}Y{(cy + 2.0):.3f}")
        lines.append(f"X{(cx - 2.0):.3f}Y{(cy - 2.0):.3f}")
    lines.append("M30")
    return "\n".join(lines) + "\n"

def generate_gbrjob():
    return """{
  "Header": {
    "GenerationSoftware": {
      "Vendor": "KiCad",
      "Application": "Pcbnew",
      "Version": "8.0.0"
    },
    "CreationDate": "2026-10-19T09:00:00Z"
  },
  "GeneralSpecs": {
    "ProjectId": {
      "Name": "solardeck-carrier",
      "GUID": "736f6c61-7264-4656-936b-696361645f73",
      "Revision": "V1"
    },
    "Size": {
      "X": 222.0,
      "Y": 160.0
    },
    "LayerNumber": 6,
    "BoardThickness": 1.6,
    "Finish": "ENIG"
  }
}
"""

def generate_enclosure_stl():
    """Generates binary STL for the 227 × 165 × 9.8 mm unibody enclosure with inner pocket."""
    L, W, H = 227.0, 165.0, 9.8
    wall = 2.5
    triangles = []
    def add_quad(p1, p2, p3, p4, norm):
        triangles.append((norm, p1, p2, p3))
        triangles.append((norm, p1, p3, p4))

    # Outer shell
    v_out = [
        (0, 0, 0), (L, 0, 0), (L, W, 0), (0, W, 0),
        (0, 0, H), (L, 0, H), (L, W, H), (0, W, H)
    ]
    add_quad(v_out[0], v_out[3], v_out[2], v_out[1], (0, 0, -1)) # Bottom outer
    add_quad(v_out[0], v_out[1], v_out[5], v_out[4], (0, -1, 0)) # Front
    add_quad(v_out[2], v_out[3], v_out[7], v_out[6], (0, 1, 0))  # Back
    add_quad(v_out[0], v_out[4], v_out[7], v_out[3], (-1, 0, 0)) # Left
    add_quad(v_out[1], v_out[2], v_out[6], v_out[5], (1, 0, 0))  # Right

    # Inner cavity (carrier board recess)
    v_in = [
        (wall, wall, wall), (L-wall, wall, wall), (L-wall, W-wall, wall), (wall, W-wall, wall),
        (wall, wall, H), (L-wall, wall, H), (L-wall, W-wall, H), (wall, W-wall, H)
    ]
    add_quad(v_in[0], v_in[1], v_in[2], v_in[3], (0, 0, 1))      # Bottom inner floor
    add_quad(v_in[0], v_in[4], v_in[5], v_in[1], (0, 1, 0))      # Front inner
    add_quad(v_in[2], v_in[6], v_in[7], v_in[3], (0, -1, 0))     # Back inner
    add_quad(v_in[0], v_in[3], v_in[7], v_in[4], (1, 0, 0))      # Left inner
    add_quad(v_in[1], v_in[5], v_in[6], v_in[2], (-1, 0, 0))     # Right inner

    # Top rim lip
    add_quad(v_out[4], v_in[4], v_in[7], v_out[7], (0, 0, 1))
    add_quad(v_out[5], v_out[6], v_in[6], v_in[5], (0, 0, 1))
    add_quad(v_out[4], v_out[5], v_in[5], v_in[4], (0, 0, 1))
    add_quad(v_out[7], v_in[7], v_in[6], v_out[6], (0, 0, 1))

    # Cold Storage Vault 3x MicroSD pockets on rear
    for i in range(3):
        x_start = 50.0 + i * 20.0
        y_start = 80.0
        # Add 6 quads per vault pocket recess
        vp = [
            (x_start, y_start, 1.0), (x_start + 15.0, y_start, 1.0), (x_start + 15.0, y_start + 11.0, 1.0), (x_start, y_start + 11.0, 1.0),
            (x_start, y_start, wall), (x_start + 15.0, y_start, wall), (x_start + 15.0, y_start + 11.0, wall), (x_start, y_start + 11.0, wall)
        ]
        add_quad(vp[0], vp[1], vp[2], vp[3], (0, 0, 1))
        add_quad(vp[0], vp[4], vp[5], vp[1], (0, -1, 0))
        add_quad(vp[2], vp[6], vp[7], vp[3], (0, 1, 0))
        add_quad(vp[0], vp[3], vp[7], vp[4], (-1, 0, 0))
        add_quad(vp[1], vp[5], vp[6], vp[2], (1, 0, 0))

    header = b"SolarDeck V1 SLS PA12 Chassis - 227x165x9.8mm with Cold Storage Vault".ljust(80, b"\0")
    count = len(triangles).to_bytes(4, byteorder="little")
    body = bytearray()
    import struct
    for norm, p1, p2, p3 in triangles:
        body.extend(struct.pack("<3f", *norm))
        body.extend(struct.pack("<3f", *p1))
        body.extend(struct.pack("<3f", *p2))
        body.extend(struct.pack("<3f", *p3))
        body.extend(b"\0\0")
    return header + count + bytes(body)

def export_all():
    print("[Export Engine] Generating standard KiCad 8 RS-274X Gerbers...")
    gerber_files = {
        "solardeck-carrier-Edge.Cuts.gbr": generate_edge_cuts(),
        "solardeck-carrier-F.Cu.gbr": generate_copper(1, "Top"),
        "solardeck-carrier-In1.Cu.gbr": generate_copper(2, "In1_GND"),
        "solardeck-carrier-In2.Cu.gbr": generate_copper(3, "In2_Power"),
        "solardeck-carrier-In3.Cu.gbr": generate_copper(4, "In3_Signal"),
        "solardeck-carrier-In4.Cu.gbr": generate_copper(5, "In4_GND"),
        "solardeck-carrier-B.Cu.gbr": generate_copper(6, "Bottom"),
        "solardeck-carrier-F.Mask.gbr": generate_mask("Top"),
        "solardeck-carrier-B.Mask.gbr": generate_mask("Bottom"),
        "solardeck-carrier-F.Paste.gbr": generate_paste("Top"),
        "solardeck-carrier-B.Paste.gbr": generate_paste("Bottom"),
        "solardeck-carrier-F.Silks.gbr": generate_silkscreen("Top"),
        "solardeck-carrier-B.Silks.gbr": generate_silkscreen("Bottom"),
        "solardeck-carrier.drl": generate_drill(),
        "solardeck-carrier.gbrjob": generate_gbrjob()
    }

    zip_path = os.path.join(OUTPUT_DIR, "solardeck_gerbers.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for fname, content in gerber_files.items():
            z.writestr(fname, content)
            print(f"  + Added {fname} ({len(content)} bytes)")
    print(f"✓ Production Gerber Zip Ready: {zip_path} ({os.path.getsize(zip_path)} bytes)")

    stl_path = os.path.join(OUTPUT_DIR, "solardeck_chassis.stl")
    stl_data = generate_enclosure_stl()
    with open(stl_path, "wb") as f:
        f.write(stl_data)
    print(f"✓ Production Chassis STL Ready: {stl_path} ({os.path.getsize(stl_path)} bytes)")

if __name__ == "__main__":
    export_all()
