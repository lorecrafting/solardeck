# Standout Features & Engineering North Stars — SolarDeck

Written 2026-10-18 17:42 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## Executive Philosophy: The 5 Standout Pillars

SolarDeck is not an incremental iteration on an Android e-reader or a miniature Raspberry Pi toy. It is a sovereign, sunlight-readable mobile workstation designed to eliminate the fundamental compromises of modern computing: screen glare, battery anxiety, input latency, distraction loops, and hardware fragility.

To achieve legendary status, the engineering team must relentlessly zoom in on, refine, and protect **Five Non-Negotiable Standout Pillars**. If any of these five pillars feels sluggish, clumsy, or compromised, the product fails. If all five are executed flawlessly, SolarDeck defines an entirely new category of personal computing.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE 6 SOLARDECK PILLARS TO HAMMER IN ON                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. THE DUAL-BRAIN INSTANT HANDOFF (<400ms Wake, 300-Day Zen / Infinite Desk)│
│ 2. THE TYPEWRITER-ON-PAPER LATENCY ENGINE (<20ms Keystroke & Inking)        │
│ 3. SUNLIGHT SOVEREIGNTY & PERPETUAL INDOOR HARVESTING (Zero-Glare, 0W Hold) │
│ 4. THE SNAPDECK FORM-MORPHOLOGY (Rigid Lapdeck ⟷ 510g Slate ⟷ Desk Easel)   │
│ 5. SOVEREIGN FIELD HARDENING (Hardware Airgap, Meshtastic LoRa, IP67 Rain)  │
│ 6. THE MODULAR UPGRADE BRIDGE (ARM-to-RISC-V Swappability, M.2 NVMe, & RAM) │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Pillar 1: The "Dual-Brain" Instant Handoff (<400ms Glass-to-Glass)

### The Vision
SolarDeck is **never truly "off", yet never dies**. Every conventional laptop or portable PC has a binary state: it is either an active computer burning watts, or a dead black mirror sleeping in a sleeve. Starting work requires the cognitive friction of opening a lid, waiting for wake, entering passwords, and waiting for radios to connect.

SolarDeck destroys this friction. When resting on a desk or shelf, it operates as a **perpetual ambient instrument** (110 µW indoor desk clock, weather barograph, or Zen book reader). The instant you touch a key or the pen, the Linux brain activates in **under 300 milliseconds**, restoring your terminal, Neovim buffers, and Claude Code sessions in **under 400ms glass-to-glass**.

### The Latency & Power Budget

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               DUAL-BRAIN STATE TRANSITION TIMELINE (<400ms)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│   T = 0.0 ms  │ Keypress or Pen Proximity trips RP2350 GPIO Wake Interrupt  │
│   T + 2.0 ms  │ RP2350 asserts PMIC buck enable (TPS61088 5.0V Boost rail)  │
│   T + 8.0 ms  │ 5.0V system rail stabilizes; CM4 receives clean POWER_OK     │
│   T + 45.0 ms │ BCM2711 exits S2idle / LP state; DDR4 SDRAM self-refresh off│
│   T + 85.0 ms │ ARM Cortex-A72 cores ramp to 1.8GHz; Linux kernel resume irq│
│   T + 120 ms  │ Sway/Wayland compositor renders pending terminal dirty rect  │
│   T + 135 ms  │ TMUX1575 bus switch flips display ownership to CM4 MIPI/SPI │
│   T + 155 ms  │ IT8951 EPDC receives 1-bit Direct Update (DU) waveform command│
│   T + 175 ms  │ Pigment particles rotate into place on physical 10.3" glass │
├─────────────────────────────────────────────────────────────────────────────┤
│ TOTAL TIME:   │ < 180 ms (from S2idle) / < 380 ms (from cold power-gate)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Engineering Rules to Enforce:
1. **Zero Bus Contention:** The **Texas Instruments TMUX1575** 8-channel bus switch guarantees that when the RP2350 owns the display bus during Zen reading, all CM4 display pins are galvanically isolated with zero parasitic back-powering ($I_{\text{off}}$).
2. **Deterministic Wake Pins:** The SnapDeck pogo pin sense line (`ID_SENSE`), keyboard keystroke IRQ, Wacom `PEN_PROX_INT`, and 5-way navigation rocker are hardwired directly to RP2350 edge-triggered interrupt pins (GPIO 10–13), guaranteeing sub-microsecond interrupt capture.
3. **No Bootloader Delays:** In S2idle suspend, RAM remains refreshed at 15 mW. In cold hibernate, an immutable Linux kernel image with `initramfs` resides on high-speed eMMC with all non-essential systemd services disabled.

---

## Pillar 2: The "Typewriter-on-Paper" Latency Engine (<20ms Keystroke & Inking)

### The Vision
The single greatest reason developers abandon E-Ink displays for programming is **input lag and ghosting flashes**. If there is a 100ms–150ms delay between striking a key and seeing the character appear on screen, the human brain rejects the interface as sluggish and disconnected.

SolarDeck treats text entry like an **electric IBM Selectric typewriter striking crisp white bond paper**: instantaneous, binary, crisp, and tactile.

### The Typing & Waveform Pipeline

```
┌──────────────┐    2.5ms USB/BLE    ┌──────────────┐    1.5ms Wayland   ┌──────────────┐
│ Kailh X-Key  │ ──────────────────> │ Linux Kernel │ ─────────────────> │ Sway / Foot  │
│ Strike       │                     │ Input Subsys │                    │ Terminal     │
└──────────────┘                     └──────────────┘                    └──────────────┘
                                                                                │
                                                                   2.0ms Render │ Dirty Bounding Box
                                                                                ▼
┌──────────────┐     18.0ms DU LUT   ┌──────────────┐    < 2.5ms MIPI    ┌──────────────┐
│ 10.3" E-Ink  │ <────────────────── │ IT8951 EPDC  │ <───────────────── │ GPU / tinydrm│
│ Microcapsule │     Particle Move   │ Memory Buff  │    Delta Transfer  │ Kernel Driver│
└──────────────┘                     └──────────────┘                    └──────────────┘
```

### The Three Hallmarks of the Typing Engine:
1. **1-Bit Direct Update (DU) Waveform (18–20ms):**
   * While actively typing in Claude Code, bash, or Neovim, the system locks into a high-speed 1-bit monochrome waveform. Particles transition between pure white and pure black in **18 milliseconds**.
   * Completely bypasses multi-level grayscale relaxation phases.
2. **Intelligent Anti-Ghosting Daemon (`eink-refreshd`):**
   * *The Problem:* Fast typing waveforms leave behind faint pigment trails (ghosting). Frequent full-screen flashes (e-ink flash) induce nausea.
   * *The Solution:* `eink-refreshd` monitors human typing cadence:
     * While keystroke intervals are $< 800\text{ ms}$, **zero global flashing is permitted**.
     * When the user pauses for $> 1.2\text{ seconds}$ to think, read, or review a line, the daemon silently fires a localized, sub-surface background scrub over the dirty region.
     * **Result:** LCD-like typing speed while typing, followed by paper-sharp clarity when thinking.
3. **Sub-18ms Wacom Inking:**
   * Wacom EMR digitizer sits laminated **behind the display backplane** (0% optical distortion, zero added surface reflection, zero parallax).
   * Passive, battery-free stylus with 4096 pressure levels and tilt detection.
   * `solardeck-inkd` renders pen strokes directly into EPDC hardware memory, providing zero-latency inking for sketching, mathematical derivations, and code margin notes.
4. **Coordinate-Targeted Piezoelectric Haptic Engine (Spatial Acoustic Array):**
   * *The Problem with Global Vibration:* Standard phones and tablets shake the entire aluminum body when you tap a virtual key, vibrating both palms and feeling artificial.
   * *The Solution:* 4× **TDK PowerHap** miniature piezoelectric actuators mounted at the four glass corners, driven by dual **Boréas BOS1901** CapDrive ICs (with 80% energy recovery).
   * *Spatial Acoustic Focusing:* When typing on bare glass, `solardeck-hapticd` fires a sub-1.0ms impulse into the nearest corner actuator and phase-inverted damping pulses at opposing corners. Kinetic displacement concentrates strictly under the touching fingertip, producing a **crisp, localized mechanical click directly under that individual thumb/key**, replicating the tactile feel of an authentic physical microswitch on flat glass.

---

## Pillar 3: "Sunlight Sovereignty" & Perpetual Indoor Life

### The Vision
Modern laptops fail the instant they step outdoors. In direct sunlight, a 500-nit MacBook screen completely washes out. To compensate, users crank brightness to maximum, turning the laptop into a 50W furnace that burns their thighs and drains the battery in 90 minutes.

SolarDeck inverts this entirely: **The brighter the sun, the crisper, higher-contrast, and more vibrant the screen becomes.** And when sitting on a desk indoors, it sips micro-watts and stays charged indefinitely from ambient room light.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SUNLIGHT SOVEREIGNTY MATRIX                          │
├──────────────────────────────┬──────────────────────────────┬───────────────┤
│ Operating Environment        │ Conventional Laptop (MacBook)│ SolarDeck     │
├──────────────────────────────┼──────────────────────────────┼───────────────┤
│ Direct Noon Sun (100,000 lux)│ Unreadable; heavy glare      │ Razor-sharp   │
│ Screen Backlight Power       │ 12W–18W (100% max brightness)│ 0.000 Watts   │
│ Thermal Behavior             │ Fans roar, CPU throttles     │ Silent, cool  │
│ Active Battery Runtime       │ 1.5 to 2.5 hours             │ 24 to 32 hours│
│ Eye Strain Index             │ High (60Hz RGB blue light)   │ Zero (Reflect)│
└──────────────────────────────┴──────────────────────────────┴───────────────┘
```

### Perpetual Indoor Harvesting (The "Solar Calculator" Effect)
* **The Physics:** By utilizing an indoor-tuned **Amorphous Silicon (a-Si)** micro-strip (PowerFilm Indoor Light / Panasonic Amorton) coupled to the **TI BQ25504** nano-power boost harvester:
  * Indoor ambient office lighting (400–600 lux) generates **200 to 350 µW**.
  * SolarDeck ambient desk clock / dashboard consumes **110 µW** (RP2350 sleep + 1-minute 1-bit partial time flip).
  * **Net Energy Balance: POSITIVE (+100 to +240 µW surplus).**
  * It sits on your desk, bookshelf, or kitchen counter, displaying time, weather barographs, tasks, and off-grid LoRa emergency traffic **forever, without ever being plugged into a wall outlet.**

---

## Pillar 4: The SnapDeck Form-Morphology (Lapdeck ⟷ Slate ⟷ Easel)

### The Vision
The computing industry has struggled with 2-in-1 form factors:
* Fabric keyboard covers (iPad Pro, Surface Pro) flop around on your lap; their "lapability" is dreadful on a park bench, train, or airplane.
* Fixed cyberdecks (ClockworkPi DevTerm, uConsole) are thick, heavy bricks that you cannot hold in bed as an e-reader or write on with a stylus.

SolarDeck solves this through the **SnapDeck Parallel Form-Morphology**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SNAPDECK FORM MORPHOLOGY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. ON-SCREEN LAPDECK MODE (The Focused Workstation)                         │
│    • Snaps magnetically directly over the lower 1/3 of the landscape screen.│
│    • Rigid magnetic hinge creates a stiff, stable clamshell for your lap.   │
│    • Sway automatically tiles terminal into upper 2/3 (1872×950 px).        │
│    • Kailh X-Switches (3.5mm travel) + RIM 9900 optical trackpad.           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. TACTICAL READING & INKING SLATE (The Pure 510g Tablet)                   │
│    • Detach keyboard in 0.5 seconds.                                        │
│    • 510g lightweight, 9.8mm slim IP67 waterproof reading slate.            │
│    • Full 10.3" portrait or landscape canvas for 100GB offline Kiwix docs,  │
│      technical schematics, and Wacom EMR handwritten annotations.           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. DESK EASEL / CODING DASHBOARD (The Ergonomic Terminal)                   │
│    • Prop tablet vertically or horizontally on its integrated kickstand.    │
│    • View 80+ continuous lines of code in portrait orientation.             │
│    • SnapDeck keyboard sits freely on desk; communicates over low-latency   │
│      Nordic nRF52840 BLE 5.0 (<5ms) or wired pogo jumper.                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Pillar 5: Sovereign Field Hardening (Airgap, LoRa, & IP67 All-Weather)

### The Vision
In an era of cloud-locked, fragile, spy-by-design hardware, SolarDeck is an **indestructible, sovereign survival instrument**. It works when the cellular network is down, when the power grid fails, in torrential rain, and under zero-trust operational security requirements.

### The Three Hardening Anchors:
1. **Physical Hardware Airgap Switch (0.000 dBm / Zero Phantom Bleed):**
   * A recessed 2-position slide switch physically breaks the enable lines of all **TI TPS22918** power gates to ground.
   * Completely severs power to the Quectel LTE modem, Semtech LoRa transceiver, Broadcom Wi-Fi/BT module, GPS engine, and MEMS microphone to **0.000V**.
   * Digital lines are isolated via **TI TXU0104** buffers, eliminating parasitic back-powering through silicon clamping diodes.
   * 100% immune to software baseband exploits; completely invisible to RF spectrum analyzers.
2. **Autonomous Meshtastic Off-Grid Radio Node (80+ Days):**
   * Built-in **Semtech SX1262 LoRa (868/915 MHz)** transceiver connected to a top-edge **IP67 bulkhead SMA female jack**.
   * Permanently owned by the RP2350 co-processor over dedicated SPI.
   * Acts as a continuous, autonomous emergency repeater node across off-grid mesh networks for **80+ days** on battery without ever waking the Linux SoC.
3. **IP67 Enclosure & All-Weather "Water-Lock":**
   * SLS 3D-printed PA12 nylon or CNC 6061 aluminum enclosure with continuous silicone perimeter gaskets and a GORE ePTFE hydrophobic pressure-equalization vent.
   * **Torrential Rain "Water-Lock" Mode:** Capacitive touch screens go haywire when water droplets strike the surface. Flipping the water-lock switch cuts power to the Goodix capacitive touch overlay, while the **Wacom EMR digitizer and left-bezel 5-way tactical navigation rocker remain 100% immune to water**, enabling full terminal navigation in pouring rain.

---

## Pillar 6: The Modular Upgrade Bridge (ARM-to-RISC-V Swappability, RAM, & 2TB NVMe)

### The Vision: A Computer That Never Becomes E-Waste
Consumer electronics are designed for planned obsolescence: when Apple or Lenovo releases a faster chip, your $1,500 laptop must be thrown in the trash. The RAM is soldered, the SSD is soldered, and the CPU is locked.

SolarDeck is designed with **Generational Modular Longevity**:
* The expensive components—the **10.3" Color E-Ink glass**, the **Wacom EMR digitizer**, the **custom 35 Wh LiFePO4 battery**, the **precision CNC/SLS enclosure**, and the **carrier motherboard**—are built to last a decade.
* The compute brain, RAM, and mass storage are **100% modular and field-upgradable in under 60 seconds with two screws**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 SOLARDECK MODULAR HARDWARE UPGRADE MATRIX                   │
├──────────────────────┬──────────────────────┬───────────────────────────────┤
│ Component            │ Modularity Mechanism │ Upgrade Path                  │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ **Main CPU & RAM**   │ Dual Hirose DF40     │ • Swap CM4 4GB ⟷ CM4 8GB      │
│                      │ Mezzanine Connectors │ • Swap ARM CM4 ⟷ RISC-V SOM   │
│                      │ (Standard CM4 socket)│   (e.g. Milk-V Mars CM)       │
│                      │                      │ • Drop-in upgrade to CM5      │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ **Mass Storage**     │ Standard M.2 2230 /  │ • User-swappable NVMe SSD     │
│                      │ 2242 PCIe Gen2 NVMe  │   (256GB to 2TB high-speed)   │
│                      │ + MicroSDXC Slot     │ • 2TB offline Kiwix Wikipedia │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ **Co-Processor**     │ RP2350B Dual-Arch    │ • Live software flash over SWD│
│                      │ (Native RISC-V)      │ • No hardware swap needed:    │
│                      │                      │   Already has 2x RISC-V cores!│
└──────────────────────┴──────────────────────┴───────────────────────────────┘
```

### 1. The ARM-to-RISC-V Bridge
* **The Strategy:** Today, ARM gives us 100% immediate software compatibility with Claude Code, Debian Linux, Neovim, and fast AI speech recognition.
* **The Future-Proof Socket:** Because SolarDeck uses the open industrial **Hirose DF40 100-pin standard**, third-party manufacturers already produce drop-in RISC-V System-on-Modules (such as the *Milk-V Mars CM* featuring the StarFive JH7110 64-bit RISC-V quad-core).
* **The Transition:** When RISC-V software reaches 100% parity with ARM, users can unclip the ARM CM4 and snap in a pure 64-bit RISC-V compute module. Zero chassis waste, zero motherboard redesign.

### 2. Upgrading RAM (From 4GB to 8GB / 16GB)
* In modern ultra-high-speed mobile systems, LPDDR4X memory operates at frequencies exceeding 4,000 MT/s, requiring sub-millimeter trace length matching directly adjacent to the silicon die.
* On SolarDeck, RAM is upgraded by **swapping the compute module**:
  * Step 1: Remove 2 mounting screws.
  * Step 2: Unseat the CM4 4GB module.
  * Step 3: Snap in a CM4 8GB module (or next-gen CM5 with 16GB RAM).
  * Takes 30 seconds, zero soldering required.

### 3. Upgrading Mass Storage (From 32GB to 2TB NVMe SSD)
* SolarDeck provides a multi-tiered storage architecture:
  1. **Primary OS (32GB eMMC):** Soldered onto the SOM for ultra-fast, tamper-resistant system boots.
  2. **MicroSDXC Edge Slot:** Accepts up to **2TB MicroSD** for instant off-grid distro swapping, field logs, or airgapped data transfer.
  3. **High-Speed M.2 NVMe SSD Socket (PCIe Gen 2 x1):**
     * Located on the underside of the carrier motherboard.
     * Accepts standard **M.2 2230 and 2242 NVMe SSDs** (the exact form factor used in the Steam Deck and Surface Pro).
     * Speeds exceeding **400 MB/s**, enabling instant storage expansion up to **2 Terabytes** for multi-gigabyte local LLMs, full offline Kiwix encyclopedias, and complete offline codebases.

### 4. What About the Co-Processor? (Why It's Already Future-Proof)
* You never need to replace the co-processor hardware because **the RP2350 ALREADY HAS NATIVE DUAL RISC-V CORES INSIDE IT**.
* It can be reconfigured in software at any time:
  * You can boot it as pure dual-core RISC-V.
  * You can reprogram its firmware from Linux in 1.2 seconds over the internal SWD bus.
  * Its 12 Programmable I/O (PIO) state machines can morph their hardware pin behavior on the fly.
* It is soldered directly as a QFN-80 chip to keep the tablet chassis at a razor-thin **9.8mm depth**.

### 5. The Zero-Brick Defense Matrix (Fearless AI & RISC-V Experimentation)
Giving developers and autonomous AI agents root access to flash co-processor silicon, switch CPU architectures, and mutate hardware state machines carries zero bricking risk:
* **Silicon Mask ROM:** Factory-etched into RP2350 silicon at TSMC; physically unbrickable.
* **Dual-Bank A/B Flash & Hardware Watchdog:** Experimental firmware boots with an 8-second countdown. If new code hangs or faults, the hardware watchdog auto-rolls back to Bank A (Golden Image) in $<2.5\text{ ms}$.
* **Current-Clamping Resistors:** All shared I/O lines incorporate 330Ω–1kΩ resistors, physically preventing pin burnout even during software logic contention.
* **Autonomous Analog Battery Protection:** TI BQ25895 analog comparator cuts charging if cell thermals exceed limits, bypassing all software.
* **Immutable Linux Rootfs with OverlayFS:** Base system is cryptographically locked with `dm-verity`; `solardeck-reset --safe` restores pristine factory OS in 3 seconds.

---

## Verification & Acceptance Gate (The North Star Metrics)

Before any prototype PCBA or firmware build is declared ready for field release, it must be benchmarked against these six non-negotiable gates:

| # | Metric | Target Threshold | Method of Verification |
| :--- | :--- | :--- | :--- |
| **G1** | S2idle to Active Keystroke Response | **< 350 milliseconds** | High-speed 240 FPS camera recording key strike to display glyph. |
| **G2** | 1-Bit Fast-Typing Latency | **< 20 milliseconds** | Oscilloscope measuring key switch closure to IT8951 pin toggle. |
| **G3** | Zen Reading Power Consumption | **< 5.0 milliwatts** | TI INA3221 telemetry / Keithley precision source meter at VBAT. |
| **G4** | Ambient Indoor Solar Sustainability | **Positive Net Energy** | Lux chamber @ 500 lux; verify battery charge current $> 0\text{ }\mu\text{A}$. |
| **G5** | Airgap RF Radiation | **0.000 dBm (Noise Floor)** | Rohde & Schwarz / HackRF sweep in anechoic chamber across 50MHz–6GHz. |
| **G6** | Zero-Brick Watchdog Auto-Rollback | **< 2.5 milliseconds** | Fault injected into Bank B; verify hardware WDT fallback to Golden Image. |

---

*This document serves as the permanent architectural North Star for all SolarDeck hardware, firmware, and software development.*
