# Mechanical Fit & Enclosure Verification Workflow

Written 2026-10-19 13:15 UTC in the Pi harness by antigravity/gemini-3.8-flash

Revised 2026-10-21 16:02 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).

Revised 2026-10-21 19:45 UTC in Claude Code by anthropic/claude-opus-5-5 (Li-ion smart pack, ADR-048).

---

## 1. Executive Summary & Purpose

This guide details the complete mechanical engineering pipeline to guarantee that the **10.3" E-Ink display, custom carrier PCB, Raspberry Pi CM5, Li-ion smart battery pack, and CNC enclosure** mate with sub-millimeter precision before spending capital on metal fabrication.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE MECHANICAL FIT PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. MANUFACTURER 3D STEP MODEL                                               │
│    Official 3D STEP/DXF from E Ink (Kaleido 4 drawing TBD, ADR-032)         │
│                                  │                                          │
│                                  ▼                                          │
│ 2. KICAD 3D BOARD EXPORT                                                    │
│    KiCad exports exact PCB outline, ZIF connector, and CM5 mating positions │
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

Never model display glass or flex cables using a hand caliper. Always obtain the official 2D DXF and 3D STEP files directly from E Ink Corporation.

### 10.3" E-Ink Panel Specification (mono Carta 1200, ADR-051):
* **Outer Glass Dimensions:** TBD — `spec_values.panel_module_outline_mm` stays `null` until the chosen module's drawing is on file. **Blocker:** AUDIT_6 §X5 records ED103TC2 at 216.7 × 174.4 mm against a 170 mm chassis depth, so the chassis or the glass moves before this section can be filled (ADR-051).
* **Active Display Area (AA) and resolution:** resolution is `spec_values.panel_sku.resolution_px` = 1872 × 1404; AA stays `null` until the drawing (`spec_values.display_active_mm`).
* **Border Offsets:** TBD — from the same drawing.
* **FPC (Ribbon Tail) Geometry** (width, tail length, pin count, pitch, exit coordinate): TBD — from the same drawing.
* **Panel thickness and stack:** TBD (`spec_values.display_stack_mm`). Design the cavity to the **colour variant's** envelope and shim for mono, or the V2 swap will not fit (ADR-051).

Every value above waits for E Ink's 10.3" Kaleido 4 datasheet and mechanical drawing.

---

## 3. Step 2: KiCad 3D Board Export

In KiCad 8 PCB Editor (`hardware/solardeck-carrier.kicad_pcb`):

1. **Lock Connector Positions:**
   * Align `J_EPDC` (the 0.5mm pitch ZIF connector) on the rear side of the PCB directly opposite the glass FPC exit coordinate.
   * Lock the CM5's dual Hirose DF40 100-pin receptacles (MOD1) at the CM5 datasheet center-to-center spacing (TBD — verify on CM5).
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

* **The Physics:** Electrophoretic display glass is thin and brittle (Kaleido 4 glass thickness TBD, ADR-032). Direct contact with aluminum walls during drop impacts or chassis flex will crack the glass substrate.
* **The Constraint:** The panel module outline (glass plus its bonded driver border) and the active area are TBD (ADR-032).
* **The Enclosure:** the pocket is the panel outline $+0.40\,\text{mm}$ per side (TBD, ADR-032), inside a **$232.0 \times 170.0\,\text{mm}$** chassis; wall per side is TBD until the Kaleido 4 drawing exists. The $180^\circ$ FPC tail exits through a filleted midframe slot rather than adding to the outline.
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
│ 3. 10.3" Kaleido 4 Panel + Wacom EMR Sensor Foil         │    TBD    │
│ 4. Die-Cut Poron Foam Shock Gasket                       │  0.30 mm  │
│ 5. CNC Aluminum Internal Midframe (Structural/Heatsink)  │  1.00 mm  │
│ 6. Hirose DF40 Standoff Mating Gap                       │  1.50 mm  │
│ 7. Raspberry Pi Compute Module 5 (CM5116064)             │    TBD    │
│    Branch A total (compute side, above the PCB)          │    TBD    │
├─────────────────────────────────────────────────────────┼───────────┤
│ BRANCH B — DISPLAY + BATTERY (the binding constraint)   │ THICKNESS │
├─────────────────────────────────────────────────────────┼───────────┤
│ 1-4. Display glass stack (as above)                      │    TBD    │
│ 5. Main Carrier PCB (6-layer ENIG)                       │  1.20 mm  │
│ 6. Li-ion smart pack, 1S2P cells `battery_cell_mm`        │ cell T    │
│    Branch B total (cavity requirement)                   │    TBD    │
├─────────────────────────────────────────────────────────┼───────────┤
│ 7. Rear Unibody Enclosure Wall (CNC 6061-T6 / PA12)      │  1.50 mm  │
├─────────────────────────────────────────────────────────┼───────────┤
│ TOTAL OVERALL THICKNESS (stack TBD + PCB + cell + wall)   │ 14.00 mm  │
└─────────────────────────────────────────────────────────┴───────────┘
```

The CM5 sits *beside* the cell, not on top of it: the 1S2P cell pair (`battery_cell_mm`) occupies the lower-left of the cavity and the CM5 + DF40 stack occupies the upper-right, sharing the same display stack above them. The cavity is 12.5 mm; whether the battery branch clears it is TBD until the Kaleido 4 stack thickness is known (ADR-032), and the CM5 module height is TBD — verify on CM5.

**Why not thinner:** the cells are chosen (ADR-049, `battery_cell_mm`, `battery_wh.li_ion`). The pair is wider than the old 90 mm bay and the pack board's length is TBD from EEMB's pack drawing, so the bay outline is re-cut when that drawing arrives. The envelope must also hold the pack board (protector, gauge), the keyed pack connector and a pull tab, with screw access for user replacement and no adhesive (ADR-048). `docs/90-history/decisions.md` ADR-009 records the thickness trade; its capacity figures are re-derived from the chosen cell's datasheet, and a thinner variant stays a deferred SKU, not a free change.

### 4.3 FPC Ribbon Bend Radius & Relief Slot
* The ribbon cable must bend $180^\circ$ around the internal midframe to reach the carrier PCB ZIF connector on the reverse side.
* **Rule:** Minimum dynamic bend radius $R \ge 6 \times \text{FPC thickness}$ ($R \ge 1.2\,\text{mm}$).
* **Machined Feature:** The aluminum midframe must feature a **through-slot ($25.0\,\text{mm} \times 3.0\,\text{mm}$) with CNC-filleted edges ($R \ge 1.5\,\text{mm}$)**. Sharp $90^\circ$ machined metal edges will shear the copper traces inside the polyimide flex tail over thermal vibration cycles.

### 4.4 Automated Interference & Collision Detection
* In Fusion 360: Run **`Inspect → Interference`** across all components.
* Verify:
  * Zero intersections between PCB components (inductors, tall capacitors) and the aluminum midframe.
  * CM5 SoC thermal pad ($1.0\,\text{mm}$ silicone) compresses to $0.7\,\text{mm}$ against the rear chassis heatsink boss.
  * USB-C port shells align with chassis edge cutouts with $\pm 0.2\,\text{mm}$ radial clearance for waterproof O-rings.

---

## 5. Step 4: The Two-Tier Sanity Check (Before Metal Machining)

Never commit $150–$300 to CNC aluminum tooling on an unverified revision.

### Tier 1: The 1:1 Scale Paper Sanity Check ($0)
1. Export a 2D DXF of the carrier PCB silkscreen and enclosure outline.
2. Open in vector software or CAD and print to a standard office laser printer at **100% scale** (ensure "Fit to Page" is unchecked).
3. Measure the printed calibration box with calipers to confirm 100.0% print scaling.
4. Place the physical 10.3" Kaleido 4 panel, CM5 module, and USB-C cables directly on the paper:
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
