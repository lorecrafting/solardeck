/**
 * Written 2026-10-19 08:35 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * SolarDeck V1 10.3" Open-Hardware Workstation Chassis
 * Parametric OpenSCAD Mechanical Envelope (IP67 / CNC 6061 / PA12 SLS)
 */

$fn = 60;

// Core Chassis Dimensions (Locked V1 Spec)
CHASSIS_WIDTH  = 227.0; // mm (X)
CHASSIS_HEIGHT = 165.0; // mm (Y)
CHASSIS_DEPTH  = 9.8;   // mm (Z)
WALL_THICKNESS = 2.0;   // mm
CORNER_RADIUS  = 6.0;   // mm (85A TPU bumper contour)

// Display Window (10.3" E-Ink Kaleido 3 / Carta 1200)
DISPLAY_ACTIVE_W = 209.0;
DISPLAY_ACTIVE_H = 157.0;
DISPLAY_LIP_DEPTH = 1.5;

// Solar Bezel Strip Recess (IXYS SM141K06L)
SOLAR_STRIP_W = 45.0;
SOLAR_STRIP_H = 15.0;
SOLAR_STRIP_D = 1.2;

// M.2 NVMe Flush Service Hatch & Cold Storage Vault
HATCH_W = 56.0;
HATCH_H = 32.0;
HATCH_DEPTH = 2.5;

// MicroSD Card Dimensions (Cold Storage Vault: 3 Slots)
MICROSD_W = 15.0;
MICROSD_H = 11.0;
MICROSD_D = 1.0;

// Camera Window (IMX219 Optical Port)
CAMERA_DIAMETER = 12.0;
CAMERA_RECESS_D = 1.2;

// GORE ePTFE Vent
GORE_VENT_DIAMETER = 6.0;

// M2.5 Brass Heat-Set Insert Specs
INSERT_HOLE_DIA   = 3.6; // For M2.5 × 4.0mm heat-set inserts
INSERT_HOLE_DEPTH = 4.5;
VESA_SPACING      = 75.0; // Standard 75x75mm rear mounting grid

// Module: Rounded Box
module rounded_box(w, h, d, r) {
    hull() {
        translate([r, r, 0]) cylinder(h = d, r = r);
        translate([w - r, r, 0]) cylinder(h = d, r = r);
        translate([r, h - r, 0]) cylinder(h = d, r = r);
        translate([w - r, h - r, 0]) cylinder(h = d, r = r);
    }
}

// Module: Main Unibody Chassis Base
module solardeck_chassis_base() {
    difference() {
        // Outer Shell
        rounded_box(CHASSIS_WIDTH, CHASSIS_HEIGHT, CHASSIS_DEPTH, CORNER_RADIUS);

        // Internal Pocket (Hollow Cavity for Carrier Board + Battery)
        translate([WALL_THICKNESS, WALL_THICKNESS, WALL_THICKNESS])
            rounded_box(
                CHASSIS_WIDTH - (WALL_THICKNESS * 2),
                CHASSIS_HEIGHT - (WALL_THICKNESS * 2),
                CHASSIS_DEPTH,
                CORNER_RADIUS - 1.0
            );

        // Display Aperture (Front Face Z = CHASSIS_DEPTH - DISPLAY_LIP_DEPTH)
        translate([
            (CHASSIS_WIDTH - DISPLAY_ACTIVE_W) / 2,
            (CHASSIS_HEIGHT - DISPLAY_ACTIVE_H) / 2,
            CHASSIS_DEPTH - DISPLAY_LIP_DEPTH
        ])
            cube([DISPLAY_ACTIVE_W, DISPLAY_ACTIVE_H, DISPLAY_LIP_DEPTH + 1]);

        // Front Solar Micro-Cell Recess (Top Bezel)
        translate([
            (CHASSIS_WIDTH - SOLAR_STRIP_W) / 2,
            CHASSIS_HEIGHT - SOLAR_STRIP_H - 3.0,
            CHASSIS_DEPTH - SOLAR_STRIP_D
        ])
            cube([SOLAR_STRIP_W, SOLAR_STRIP_H, SOLAR_STRIP_D + 0.5]);

        // Rear M.2 Service Hatch Opening (Bottom Face Z = 0)
        translate([30.0, 30.0, -1])
            cube([HATCH_W, HATCH_H, WALL_THICKNESS + 2]);

        // Rear Camera Window Aperture
        translate([CHASSIS_WIDTH - 35.0, CHASSIS_HEIGHT - 35.0, -1])
            cylinder(d = CAMERA_DIAMETER, h = WALL_THICKNESS + 2);

        // Rear GORE ePTFE Pressure Vent Aperture
        translate([CHASSIS_WIDTH - 55.0, CHASSIS_HEIGHT - 35.0, -1])
            cylinder(d = GORE_VENT_DIAMETER, h = WALL_THICKNESS + 2);

        // Rear M2.5 Heat-Set Insert Grid (75x75mm Pattern)
        rear_insert_grid();

        // O-Ring Sealing Channel around Perimeter
        o_ring_groove();
    }

    // Interior Structural PCB Mounting Bosses
    pcb_mounting_bosses();
}

// Module: M2.5 Insert Grid Holes
module rear_insert_grid() {
    cx = CHASSIS_WIDTH / 2;
    cy = CHASSIS_HEIGHT / 2;

    for (dx = [-VESA_SPACING / 2, VESA_SPACING / 2]) {
        for (dy = [-VESA_SPACING / 2, VESA_SPACING / 2]) {
            translate([cx + dx, cy + dy, -0.5])
                cylinder(d = INSERT_HOLE_DIA, h = INSERT_HOLE_DEPTH);
        }
    }
}

// Module: IP67 O-Ring Perimeter Groove
module o_ring_groove() {
    difference() {
        translate([WALL_THICKNESS - 0.6, WALL_THICKNESS - 0.6, CHASSIS_DEPTH - 1.0])
            rounded_box(
                CHASSIS_WIDTH - ((WALL_THICKNESS - 0.6) * 2),
                CHASSIS_HEIGHT - ((WALL_THICKNESS - 0.6) * 2),
                1.2,
                CORNER_RADIUS
            );
        translate([WALL_THICKNESS + 0.6, WALL_THICKNESS + 0.6, CHASSIS_DEPTH - 1.5])
            rounded_box(
                CHASSIS_WIDTH - ((WALL_THICKNESS + 0.6) * 2),
                CHASSIS_HEIGHT - ((WALL_THICKNESS + 0.6) * 2),
                2.0,
                CORNER_RADIUS - 0.5
            );
    }
}

// Module: PCB Mounting Bosses
module pcb_mounting_bosses() {
    boss_positions = [
        [15, 15],
        [CHASSIS_WIDTH - 15, 15],
        [15, CHASSIS_HEIGHT - 15],
        [CHASSIS_WIDTH - 15, CHASSIS_HEIGHT - 15]
    ];

    for (pos = boss_positions) {
        translate([pos[0], pos[1], WALL_THICKNESS])
            difference() {
                cylinder(d = 6.0, h = 3.5);
                cylinder(d = INSERT_HOLE_DIA, h = 4.0);
            }
    }
}

// Module: Flush M.2 Service Hatch with Cold Storage Vault (3x MicroSD Pockets)
module m2_service_hatch_with_vault() {
    difference() {
        // Outer Hatch Plate
        cube([HATCH_W - 0.4, HATCH_H - 0.4, HATCH_DEPTH]);

        // Cold Storage Vault: 3x MicroSD Pockets carved into inner face
        for (i = [0:2]) {
            translate([
                5.0 + (i * (MICROSD_W + 3.0)),
                (HATCH_H - MICROSD_H) / 2,
                HATCH_DEPTH - MICROSD_D
            ])
                cube([MICROSD_W, MICROSD_H, MICROSD_D + 0.2]);
        }

        // 4x M2.5 Counterbore Screw Holes
        hatch_screws = [
            [3.5, 3.5],
            [HATCH_W - 3.9, 3.5],
            [3.5, HATCH_H - 3.9],
            [HATCH_W - 3.9, HATCH_H - 3.9]
        ];
        for (hs = hatch_screws) {
            translate([hs[0], hs[1], -0.5]) {
                cylinder(d = 2.7, h = HATCH_DEPTH + 1); // Through-hole for M2.5
                translate([0, 0, 1.2]) cylinder(d = 4.5, h = HATCH_DEPTH); // Counterbore
            }
        }
    }
}

// Render Default Assembly View
solardeck_chassis_base();

// Render Service Hatch Exploded Offset
translate([0, -45.0, 0])
    m2_service_hatch_with_vault();
