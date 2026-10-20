# Mechanical Fit & Enclosure Verification Workflow

Written 2026-10-19 13:15 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## 1. Executive Summary & Purpose

This guide details the complete mechanical engineering pipeline to guarantee that the **10.3" E-Ink display, custom carrier PCB, Raspberry Pi CM4, LiFePO4 battery, and CNC enclosure** mate with sub-millimeter precision before spending capital on metal fabrication.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE MECHANICAL FIT PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. MANUFACTURER 3D STEP MODEL                                               │
│    Download official 3D STEP/DXF from Good Display (exact glass + FPC tail) │
│                                  │                                          │
│                                  ▼                                          │
│ 2. KICAD 3D BOARD EXPORT                                                    │
│    KiCad exports exact PCB outline, ZIF connector, and CM4 mating positions │
│                                  │                                          │
│                                  ▼                                          │
│ 3. MASTER CAD ASSEMBLY (Fusion 360 / SolidWorks / Onshape)                  │
│    • Mate Screen + Midframe + PCB + Battery into one 3D assembly            │
│    • Run automated "Interference / Collision Detection"                     │
│    • Verify +0.4mm XY tolerance & FPC ribbon bend radius                    │
│                                  │                                          │
│                                  ▼                                          │
│ 4. THE TWO-TIER SANITY CHECK (Before Metal Machining)                       │
│    • Tier 1: 1:1 Scale Paper Printout ($0)                                  │
│    • Tier 2: 3D-Printed PLA/PETG "Skeleton" Test Fit ($12–$15)              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Step 1: Manufacturer Mechanical Reference Data

Never model display glass or flex cables using a hand caliper. Always obtain the official 2D DXF and 3D STEP files directly from Good Display / E Ink Corporation.

### 10.3" E-Ink Panel Specification (GDEQ103Z21 / ED103TC2 / Kaleido 4):
* **Outer Glass Dimensions:** $227.70 \pm 0.20\,\text{mm} \times 165.80 \pm 0.20\,\text{mm} \times 0.78\,\text{mm}$.
* **Active Display Area (AA):** $209.664\,\text{mm} \times 157.248\,\text{mm}$ ($1872 \times 1404$ pixels).
* **Asymmetrical Border Offsets:**
  * Top Margin: $8.50\,\text{mm}$
  * Bottom Margin: $9.50\,\text{mm}$ (where FPC exits glass edge)
  * Left / Right Margins: $9.00\,\text{mm}$
* **FPC (Ribbon Tail) Geometry:**
  * Width: $17.0\,\text{mm}$
  * Tail Length: $35.0\,\text{mm}$
  * Pin Count: 33-pin or 39-pin $0.5\,\text{mm}$ pitch bottom-contact ZIF.
  * Exit Coordinate: Centered at $X = 113.85\,\text{mm}$ along bottom glass edge.

---

## 3. Step 2: KiCad 3D Board Export

In KiCad 8 PCB Editor (`hardware/solardeck-carrier.kicad_pcb`):

1. **Lock Connector Positions:**
   * Align `J_EPDC` (the 0.5mm pitch ZIF connector) on the rear side of the PCB directly opposite the glass FPC exit coordinate.
   * Lock `J_CM4_1` and `J_CM4_2` (dual Hirose DF40 100-pin receptacles) at exact $40.0\,\text{mm} \times 55.0\,\text{mm}$ center-to-center spacing.
   * Place mounting holes: 4x M2.5 non-plated holes with $5.0\,\text{mm}$ annular keep-out zones.
2. **Export Board STEP:**
   * In KiCad PCB Editor: Navigate to **`File → Export → STEP...`**
   * Settings:
     * Tolerance: `0.01 mm`
     * Include 3D models: `All components`
     * Output file: `hardware/solardeck_carrier_board.step`

---

## 4. Step 3: Master CAD Assembly & Tolerance Budget

Import all solid bodies into your mechanical CAD suite (Fusion 360, SolidWorks, or Onshape).

### 4.1 XY Perimeter Clearance (+0.4mm)

* **The Physics:** Electrophoretic display glass is $0.78\,\text{mm}$ thin and brittle. Direct contact with aluminum walls during drop impacts or chassis flex will crack the glass substrate.
* **The Constraint:** The panel module outline (glass plus its bonded driver border) is $227.7 \times 165.8\,\text{mm}$; the active area is $209.664 \times 157.248\,\text{mm}$.
* **The Enclosure:** the pocket is $228.5 \times 166.6\,\text{mm}$ ($+0.40\,\text{mm}$ per side over the glass), inside a **$232.0 \times 170.0\,\text{mm}$** chassis, giving **2.15 mm** of wall per side. The $180^\circ$ FPC tail exits through a filleted midframe slot rather than adding to the outline.
* **Superseded:** the earlier $227.0 \times 165.0\,\text{mm}$ chassis was *smaller than the glass it has to contain* by 0.7 mm (ADR-008).
* **Shock Gasket:** a die-cut **$0.30\,\text{mm}$ Poron foam gasket** sits between the glass perimeter and the chassis wall to absorb shock and thermal expansion.

### 4.2 Z-Stackup Budget (14.0mm Chassis, 12.5mm Cavity)

Two vertical branches share the cavity. The limit is the **battery branch**, not the compute branch:

```
┌─────────────────────────────────────────────────────────┬───────────┐
│ BRANCH A — DISPLAY + COMPUTE                            │ THICKNESS │
├─────────────────────────────────────────────────────────┼───────────┤
│ 1. Front Bezel Lip & Anti-Glare PMMA / Glass             │  1.10 mm  │
│ 2. Optically Clear Adhesive (OCA)                        │  0.15 mm  │
│ 3. 10.3" E-Ink Panel + Wacom EMR Sensor Foil             │  1.10 mm  │
│ 4. Die-Cut Poron Foam Shock Gasket                       │  0.30 mm  │
│ 5. CNC Aluminum Internal Midframe (Structural/Heatsink)  │  1.00 mm  │
│ 6. Hirose DF40 Standoff Mating Gap                       │  1.50 mm  │
│ 7. Raspberry Pi Compute Module 4 (CM4 with RF Shield)    │  4.70 mm  │
│    Branch A total (compute side, above the PCB)          │  9.85 mm  │
├─────────────────────────────────────────────────────────┼───────────┤
│ BRANCH B — DISPLAY + BATTERY (the binding constraint)   │ THICKNESS │
├─────────────────────────────────────────────────────────┼───────────┤
│ 1-4. Display glass stack (as above)                      │  2.65 mm  │
│ 5. Main Carrier PCB (6-layer ENIG)                       │  1.20 mm  │
│ 6. LiFePO4 flat pouch cell (142 x 90 x 8.5mm, 32 Wh)     │  8.50 mm  │
│    Branch B total (cavity requirement)                   │ 12.35 mm  │
├─────────────────────────────────────────────────────────┼───────────┤
│ 7. Rear Unibody Enclosure Wall (CNC 6061-T6 / PA12)      │  1.50 mm  │
├─────────────────────────────────────────────────────────┼───────────┤
│ TOTAL OVERALL THICKNESS (2.65+1.20+8.50+1.50 + 0.15 tol) │ 14.00 mm  │
└─────────────────────────────────────────────────────────┴───────────┘
```

The CM4 sits *beside* the cell, not on top of it: a 142 x 90 mm pouch occupies the lower-left of the cavity and the CM4 + DF40 stack occupies the upper-right, sharing the same 2.65 mm display stack above them. The cavity is 12.5 mm so the 12.35 mm battery branch clears with a 0.15 mm tolerance.

**Why not thinner:** 32 Wh of LiFePO4 needs ~8.5 mm of cell. A 5.0 mm cell caps the pack at roughly 18 Wh. `docs/90-history/decisions.md` ADR-009 records the trade: V1 keeps 32 Wh at 14.0 mm and 620 g; a 10.5 mm / 18 Wh "thin" variant is a deferred SKU, not a free change.

### 4.3 FPC Ribbon Bend Radius & Relief Slot
* The ribbon cable must bend $180^\circ$ around the internal midframe to reach the carrier PCB ZIF connector on the reverse side.
* **Rule:** Minimum dynamic bend radius $R \ge 6 \times \text{FPC thickness}$ ($R \ge 1.2\,\text{mm}$).
* **Machined Feature:** The aluminum midframe must feature a **through-slot ($25.0\,\text{mm} \times 3.0\,\text{mm}$) with CNC-filleted edges ($R \ge 1.5\,\text{mm}$)**. Sharp $90^\circ$ machined metal edges will shear the copper traces inside the polyimide flex tail over thermal vibration cycles.

### 4.4 Automated Interference & Collision Detection
* In Fusion 360: Run **`Inspect → Interference`** across all components.
* Verify:
  * Zero intersections between PCB components (inductors, tall capacitors) and the aluminum midframe.
  * CM4 SoC thermal pad ($1.0\,\text{mm}$ silicone) compresses to $0.7\,\text{mm}$ against the rear chassis heatsink boss.
  * USB-C port shells align with chassis edge cutouts with $\pm 0.2\,\text{mm}$ radial clearance for waterproof O-rings.

---

## 5. Step 4: The Two-Tier Sanity Check (Before Metal Machining)

Never commit $150–$300 to CNC aluminum tooling on an unverified revision.

### Tier 1: The 1:1 Scale Paper Sanity Check ($0)
1. Export a 2D DXF of the carrier PCB silkscreen and enclosure outline.
2. Open in vector software or CAD and print to a standard office laser printer at **100% scale** (ensure "Fit to Page" is unchecked).
3. Measure the printed calibration box with calipers to confirm 100.0% print scaling.
4. Place the physical Good Display 10.3" panel, CM4 module, and USB-C cables directly on the paper:
   * Verify screen active area aligns with the bezel cutout.
   * Verify ribbon cable lands directly over the ZIF footprint.
   * Verify USB-C plugs insert fully without hitting adjacent components.

### Tier 2: The $15 3D-Printed "Skeleton" Test Fit
1. Export `hardware/enclosure/solardeck_chassis.stl`.
2. 3D-print the bezel and rear chassis in standard PLA or PETG (0.2mm layer height) using a local printer (Bambu Lab) or rapid service (JLCPCB 3D / Seeed 3D for ~$12).
3. Perform physical dry-fit assembly:
   * Drop the real 10.3" screen into the pocket. Confirm it drops in freely without binding or forcing.
   * Insert the Poron foam gasket.
   * Route the FPC ribbon through the midframe slot and clamp into the ZIF connector.
   * Test physical USB-C cable retention and MagSafe magnetic attachment.

Once the 3D-printed chassis passes this physical verification, you can confidently authorize Seeed Fusion CNC to cut the 6061-T6 aluminum unibody.

---

*Skipped direct CNC aluminum machining on initial revision; add CNC milling after 3D-printed physical fit is confirmed.*
