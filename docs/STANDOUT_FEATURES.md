# Standout Features & Engineering North Stars — SolarDeck

Written 2026-10-18 17:42 UTC in the Pi harness by antigravity/gemini-3.8-flash
Revised 2026-10-21 15:59 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).
Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:22 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, ADR-044/045).

---

## Executive Philosophy: The 14 Standout Feature Pillars (7 product pillars + 7 chapters)

SolarDeck is not an incremental iteration on an Android e-reader or a miniature Raspberry Pi toy. It is a sovereign, sunlight-readable mobile workstation designed to eliminate the fundamental compromises of modern computing: screen glare, battery anxiety, input latency, distraction loops, and hardware fragility.

The product is defined by **seven non-negotiable standout pillars** (summarised in `README.md` and expanded below), followed by seven further chapters of emergent capability. If any of the seven core pillars feels sluggish, clumsy, or compromised, the product fails. If all seven are executed flawlessly, SolarDeck defines an entirely new category of personal computing.

The seven pillars, as named in `spec_values.features.product_pillars` (Pillar N below = PN):

| # | Pillar |
| :-- | :--- |
| P1 | Dual-brain handoff: instant ambient modes on the RP2350, Linux resume in seconds (ADR-036) |
| P2 | Typewriter-on-paper latency (1-bit DU keystroke, EMR ink, LRA haptics) |
| P3 | Sunlight-readable; solar tops up the idle co-processor outdoors (ADR-041) |
| P4 | Form-morphology: 620 g slate, desk easel, modular grips |
| P5 | Field hardening: airgap, GNSS, IP54 (V1) / IP67 (V2), rain-lock; LoRa in V2 |
| P6 | Modular upgrade bridge: ARM/RISC-V SOM, RAM, NVMe |
| P7 | Voice-first control: hold-to-talk button, opt-in hands-free wake word, barge-in (ADR-036) |

---

## Pillar 1: Dual-Brain Handoff — Instant Ambient Modes on the RP2350, Linux Resume in Seconds (ADR-036)

### The Vision
SolarDeck is **never truly "off", yet never dies**. Every conventional laptop or portable PC has a binary state: it is either an active computer burning watts, or a dead black mirror sleeping in a sleeve. Starting work requires the cognitive friction of opening a lid, waiting for wake, entering passwords, and waiting for radios to connect.

SolarDeck splits the work between two brains. When resting on a desk or shelf, the **RP2350 runs the ambient modes** (desk clock, weather barograph, Zen book reader) and they are instant, because the co-processor that runs them never powers off. The CM5 has no RAM-retaining low-power state, so when you need Linux, it **resumes from off/hibernate in seconds**, not milliseconds (`sleep_ladder` R2 is `null`, ADR-036). The hold-to-talk voice button (Pillar 7) starts recording on the RP2350 the moment it is pressed, so the boot time costs no words.

### Engineering Rules to Enforce:
1. **Zero Bus Contention:** The **2× Texas Instruments TMUX1575** bus switch pair (4 channels each, 8 total) guarantees that when the RP2350 owns the display bus during Zen reading, all CM5 display pins are galvanically isolated with zero parasitic back-powering ($I_{\text{off}}$).
2. **Deterministic Wake Pins:** Keyboard keystroke IRQ (via USB-C or BLE), Wacom `PEN_PROX_INT`, BMA400 tap detection, and the 5-way navigation rocker are hardwired directly to RP2350 edge-triggered interrupt pins (GPIO 10–13), guaranteeing sub-microsecond interrupt capture.
3. **Short Linux Resume:** There is no RAM-retaining suspend on the CM5 (ADR-036). Resume is from hibernate or a cold boot of an immutable kernel image with `initramfs` on eMMC/NVMe, with all non-essential systemd services disabled; the resume time is measured on the dev-kit bench (gate G1).

---

## Pillar 2: Typewriter-on-Paper Latency (1-Bit DU Keystroke, EMR Ink, LRA Haptics)

### The Vision
The single greatest reason developers abandon E-Ink displays for programming is **input lag and ghosting flashes**. If there is a 100ms–150ms delay between striking a key and seeing the character appear on screen, the human brain rejects the interface as sluggish and disconnected.

SolarDeck treats text entry like an **electric IBM Selectric typewriter striking crisp white bond paper**: instantaneous, binary, crisp, and tactile.

### The Typing & Waveform Pipeline

```
┌──────────────┐    2.5ms USB/BLE    ┌──────────────┐    1.5ms Wayland   ┌──────────────┐
│ Keyboard Key │ ──────────────────> │ Linux Kernel │ ─────────────────> │ Sway / Foot  │
│ Strike       │                     │ Input Subsys │                    │ Terminal     │
└──────────────┘                     └──────────────┘                    └──────────────┘
                                                                                │
                                                                   2.0ms Render │ Dirty Bounding Box
                                                                                ▼
┌──────────────┐     DU LUT (TBD)    ┌──────────────┐    < 2.5ms MIPI    ┌──────────────┐
│ 10.3" E-Ink  │ <────────────────── │ K4 controller│ <───────────────── │ GPU / tinydrm│
│ Microcapsule │     Particle Move   │ (TBD,ADR-032)│    Delta Transfer  │ Kernel Driver│
└──────────────┘                     └──────────────┘                    └──────────────┘
```

### The Three Hallmarks of the Typing Engine:
1. **1-Bit Direct Update (DU) Waveform (timing TBD, ADR-032):**
   * While actively typing in Claude Code, bash, or Neovim, the system locks into a high-speed 1-bit monochrome waveform. Particles transition between pure white and pure black; the Kaleido 4 DU timing is TBD (ADR-032).
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
4. **Haptic Engine (core, ADR-037): Frame-Mounted LRA, Spatial Piezo Array as a DNP Option:**
   * *Instant feedback:* Every keystroke — on the glass, the thumb-keyboard grip or an external keyboard — fires a haptic tap and an optional typewriter sound **at key-down**, independent of the panel refresh, so the feedback lands before the E-Ink draws and masks its latency.
   * *Base build:* A single TI **DRV2605L** + 8 mm Z-axis LRA, mounted on the frame (not on the glass). `solardeck-hapticd` still shapes per-keystroke waveforms (<0.6 ms trigger), and the actuator is a replaceable part. The whole frame moves slightly; it feels like a good phone, not like a microswitch.
   * *Why:* The spatial array puts four adhesively bonded ceramics at the highest-strain location in a drop. It is the best tactile experience here and the worst 30-year bet here (ADR-020, `HARDWARE_SPEC.md` §7.6).
   * *Retained option (DNP footprint):* 4× **TDK PowerHap** at the glass corners + dual **Boréas BOS1901** CapDrive drivers with >80% energy recovery. `solardeck-hapticd` fires a sub-1.0 ms impulse into the nearest corner and phase-inverted damping pulses at the opposite corners, concentrating displacement under the fingertip for a genuine **localized mechanical click on flat glass**. Populate it for demos or for a buyer who accepts a 10-year glass-bond service life.

---

## Pillar 3: Sunlight-Readable; Solar Tops Up the Idle Co-Processor Outdoors (ADR-041)

### The Vision
Modern laptops fail the instant they step outdoors. In direct sunlight, a 500-nit MacBook screen completely washes out. To compensate, users crank brightness to maximum, turning the laptop into a 50W furnace that burns their thighs and drains the battery in 90 minutes.

SolarDeck inverts this entirely: **The brighter the sun, the crisper, higher-contrast, and more vibrant the screen becomes.** Outdoors, the bezel strip tops up the idle co-processor; indoors it does not keep the device charged (ADR-041).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SUNLIGHT SOVEREIGNTY MATRIX                          │
├──────────────────────────────┬──────────────────────────────┬───────────────┤
│ Operating Environment        │ Conventional Laptop (MacBook)│ SolarDeck     │
├──────────────────────────────┼──────────────────────────────┼───────────────┤
│ Direct Noon Sun (100,000 lux)│ Unreadable; heavy glare      │ Razor-sharp   │
│ Screen Backlight Power       │ 12W–18W (100% max brightness)│ 0.000 Watts   │
│ Thermal Behavior             │ Fans roar, CPU throttles     │ Silent, cool  │
│ Active Battery Runtime       │ 1.5 to 2.5 hours             │ TBD (ADR-040) │
│ Eye Strain Index             │ High (60Hz RGB blue light)   │ Zero (Reflect)│
└──────────────────────────────┴──────────────────────────────┴───────────────┘
```

### Outdoor Solar Top-Up
* The bezel strip feeds the **TI BQ25504** harvester and tops up the idle co-processor **outdoors only**. The indoor net-positive claim is withdrawn (ADR-041, gate G4).

---

## Pillar 4: Form-Morphology — 620 g Slate, Desk Easel, Modular Grips

### The Vision
The computing industry has struggled with 2-in-1 form factors:
* Fabric keyboard covers (iPad Pro, Surface Pro) flop around on your lap; their "lapability" is dreadful on a park bench, train, or airplane.
* Fixed cyberdecks (ClockworkPi DevTerm, uConsole) are thick, heavy bricks that you cannot hold in bed as an e-reader or write on with a stylus.

SolarDeck solves this by decoupling the core tablet from proprietary keyboards and providing a **Universal Mechanical Mounting Architecture**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       UNIVERSAL FORM MORPHOLOGY                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. HANDHELD THUMB-TYPING CYBERDECK (The Mobile Terminal)                    │
│    • Snaps onto an open-source 3D-printed handheld ergonomic grip.          │
│    • Accommodates an inexpensive $20 USB-C/BLE BlackBerry Q20 tactile       │
│      thumb keyboard beneath the 10.3" display.                              │
│    • Type bash commands and prompts with two thumbs while walking outdoors. │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. TACTICAL READING & INKING SLATE (The Pure Slate)                         │
│    • Detach from grip or stand in 0.5 seconds.                              │
│    • Lightweight slate (mass_g, chassis_mm), IP54 (V1 target).              │
│    • Full 10.3" portrait or landscape canvas for 100GB offline Kiwix docs,  │
│      technical schematics, and Wacom EMR handwritten annotations.           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. DESK EASEL / CODING DASHBOARD (The Ergonomic Terminal)                   │
│    • Mounts instantly to any MagSafe desk stand or camera tripod (1/4"-20). │
│    • View 80+ continuous lines of code in portrait orientation.             │
│    • Pairs with your favorite mechanical keyboard (Keychron, ThinkPad,      │
│      Apple Magic Keyboard, Corne, or glove80) over low-latency BLE or USB-C.│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Pillar 5: Field Hardening — Airgap, Mesh, GNSS, IP54 (V1) / IP67 (V2), Rain-Lock

### The Vision
In an era of cloud-locked, fragile, spy-by-design hardware, SolarDeck is an **indestructible, sovereign survival instrument**. It works when the cellular network is down, when the power grid fails, in torrential rain, and under zero-trust operational security requirements.

### The Three Hardening Anchors:
1. **Physical Hardware Airgap Switch (0.000 dBm / Zero Phantom Bleed):**
   * A recessed 2-position slide switch cuts the u-blox MAX-M10S GNSS rail to **0.000V** and pulls the CM5's `WL_nDisable` / `BT_nDisable` low, disabling the on-module Wi-Fi/BT (docs/PIN_BUDGET.md). (No cellular modem in V1, ADR-034; no on-board LoRa in V1, ADR-044.)
   * Digital lines are isolated via **TI TXU0104** buffers, eliminating parasitic back-powering through silicon clamping diodes.
   * 100% immune to software baseband exploits; completely invisible to RF spectrum analyzers.
2. **Off-Grid Mesh and GNSS:**
   * On-board LoRa radio: Deferred to V2 (ADR-044); the V1 board reserves the footprint and pins (ADR-045, docs/PIN_BUDGET.md). In V1 the CM5 talks to a paired external Meshtastic node over Bluetooth LE when Linux is up.
   * A **u-blox MAX-M10S** GNSS receiver on an RP2350 UART, behind a load switch, with a passive antenna at the top edge (ADR-038, amended by ADR-044): the RP2350 keeps time and logs position with Linux off, and the PPS line disciplines its RTC (tracking power `spec_values.gnss.tracking_mw`).
3. **IP54 (V1 target) / IP67 (V2 target) Enclosure & All-Weather "Water-Lock":**
   * SLS 3D-printed PA12 nylon prototypes and PC/ABS production enclosure (ADR-039) with continuous silicone perimeter gaskets and a GORE ePTFE hydrophobic pressure-equalization vent. IP67 waits for V2, once every aperture has a named sealing part.
   * **Torrential Rain "Water-Lock" Mode:** Capacitive touch screens go haywire when water droplets strike the surface. Flipping the water-lock switch cuts power to the Goodix capacitive touch overlay, while the **Wacom EMR digitizer and left-bezel 5-way tactical navigation rocker remain 100% immune to water**, enabling full terminal navigation in pouring rain.

---

## Pillar 6: Modular Upgrade Bridge — ARM/RISC-V SOM, RAM, NVMe

### The Vision: A Computer That Never Becomes E-Waste
Consumer electronics are designed for planned obsolescence: when Apple or Lenovo releases a faster chip, your $1,500 laptop must be thrown in the trash. The RAM is soldered, the SSD is soldered, and the CPU is locked.

SolarDeck is designed with **Generational Modular Longevity**:
* The expensive components—the **10.3" Color E-Ink glass**, the **Wacom EMR digitizer**, the **custom LiFePO4 battery** (capacity TBD until the cell is chosen, ADR-040), the **precision CNC/SLS enclosure**, and the **carrier motherboard**—are built to last a decade.
* The compute brain, RAM, and mass storage are **100% modular and field-upgradable in under 60 seconds with two screws**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 SOLARDECK MODULAR HARDWARE UPGRADE MATRIX                   │
├──────────────────────┬──────────────────────┬───────────────────────────────┤
│ Component            │ Modularity Mechanism │ Upgrade Path                  │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ **Main CPU & RAM**   │ Dual Hirose DF40     │ • CM5116064: 16GB / 64GB eMMC │
│                      │ Mezzanine Connectors │ • Swap ARM CM5 ⟷ RISC-V SOM   │
│                      │ (DF40 module family) │   (fit TBD — verify on CM5)   │
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
* **The Transition:** When RISC-V software reaches 100% parity with ARM, users can unclip the ARM CM5 and snap in a pure 64-bit RISC-V compute module. Zero chassis waste, zero motherboard redesign.

### 2. RAM (16GB, set by the compute module)
* In modern ultra-high-speed mobile systems, LPDDR4X memory operates at frequencies exceeding 4,000 MT/s, requiring sub-millimeter trace length matching directly adjacent to the silicon die.
* On SolarDeck, RAM is set by **the compute module**: V1 ships only the CM5116064 (16GB, ADR-031). A future module in the same socketed DF40 family swaps in the same way:
  * Step 1: Remove 2 mounting screws.
  * Step 2: Unseat the CM5 module.
  * Step 3: Snap in the replacement module.
  * Takes 30 seconds, zero soldering required.

### 3. Upgrading Mass Storage (From 64GB eMMC to 2TB NVMe SSD)
* SolarDeck provides a multi-tiered storage architecture:
  1. **Primary OS (64GB eMMC):** Soldered onto the SOM for ultra-fast, tamper-resistant system boots.
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
* **Autonomous Battery Protection:** The TI BQ25798 charger's programmable JEITA zones and a BQ29706-class protector with a back-to-back N-FET pair cut charging on cell thermals or over-voltage, independent of Linux; charging stays disabled until the RP2350 has written the LiFePO4 VREG (ADR-035).
* **Immutable Linux Rootfs with OverlayFS:** Base system is cryptographically locked with `dm-verity`; `solardeck-reset --safe` restores pristine factory OS in 3 seconds.

### 6. The "Cold Storage Vault" (Carry Up to 6+ Terabytes Off-Grid for $0 BOM)
To make SolarDeck the ultimate sovereign archive workstation without adding a single cent in electronics or compromising exterior unibody waterproofing:
* **Gasketed M.2 Service Hatch Cavity:** Molded directly into the inner face of the flush, silicone-gasketed M.2 SSD service hatch on the rear chassis unibody (secured by 2x stainless M2 captive screws).
* **Storage Capacity:**
  * **3x Uniform Friction-Fit MicroSD Card Pockets:** Holds three extra MicroSD cards (e.g. Card 1: 1TB offline Kiwix Wikipedia + MDN + Library of Genesis; Card 2: bootable Tails / Arch rescue OS; Card 3: encrypted personal git vault).
  * **Spare SIM storage and SIM ejector clip:** V2 (ADR-034).
* **Mechanical Retention & Weather Protection:** Molded 85A TPU micro-ribs prevent rattling or dislodging during severe drops, while the gasketed hatch keeps the cards inside the IP54 (V1 target) envelope, completely hidden and protected from rain, dust, and visual inspection.
* **Total Accessible Storage:** With 2TB on the active edge MicroSD slot, 3TB in the cold vault, and 2TB on the internal M.2 NVMe SSD, developers can carry **up to 7 Terabytes of uncompressed human knowledge and local AI weights** in one slate (`mass_g`).

---

## Pillar 7: Voice-First Control — Hold-to-Talk Button, Opt-In Hands-Free Wake Word, Barge-In (ADR-036)

*Written 2026-10-20 19:37 UTC in the Pi harness by openrouter/deepseek/deepseek-v4-flash-0731*

The voice channel is a first-class pillar, not a bolt-on: you can **hold a button and talk** at any time, **speak over it mid-sentence**, and opt in to hands-free "Hey Deck". Hardware: two MEMS mics, a speaker with an echo-cancel reference, and a hardware mute switch.

### 1. Hold-to-Talk Voice Button (Always Available, Zero Standby Cost)
Press and hold: the RP2350 starts capturing audio into PSRAM **at the press**, while the CM5 boots; Linux transcribes the buffer, so no words are lost to boot time. The mic is live only while the button is held, so the button costs nothing in standby.

### 1b. Hands-Free Wake Word (Opt-In)
"Hey Deck" is opt-in, and the device shows its measured battery cost before you enable it. It runs on the CM5 when Linux is up and on the RP2350 when Linux is off; the RP2350 wake-word power is TBD until measured on the bench. A verified speaker (**Resemblyzer biometrics**, cosine similarity $\ge 0.78$) is required before `whisper.cpp` acts on the command.

### 2. True Acoustic Barge-In (Interruption)
PipeWire loops back the MAX98357A speaker audio into SpeexDSP / WebRTC AEC3 Acoustic Echo Cancellation, subtracting SolarDeck's own voice from the microphones. The operator can speak over SolarDeck while it talks at full volume, and it **stops and retargets instantly** — no push-to-talk required for the barge-in path.

### 3. Touch-to-Talk (On-Screen Twin of the Button)
An on-screen **held-call PTT target** behaves like the voice button when Linux is up: the mic is hot only while it is held, giving deterministic operator control when acoustic conditions or bystanders defeat the wake word.

---

## Pillar 8: Zero-Cost Convenience Combinations ($0.00 Added BOM)

By orchestrating and cross-wiring the existing hardware components in innovative ways, SolarDeck delivers four extraordinary convenience features without adding a single cent to the Bill of Materials:

### 1. The Survival Powerbank (Reverse OTG, ADR-035)
* Utilizing the OTG boost mode of the **TI BQ25798** charger, SolarDeck sources USB power backwards through USB-C Port 1 or 2 to charge external smartphones, flashlights, or radios, capped at `power_bank.otg_max_a` (2 A).
* **Linux Stays 100% Asleep (0.000W):** The RP2350 co-processor manages power delivery and displays a live, crisp battery percentage and output wattage on the E-Ink screen. Never carry a separate powerbank again.

### 2. The Solar Micro-Strip as a Free Ambient Light Sensor ($0.00 Cost)
* Rather than adding a dedicated photodiode IC, the RP2350's internal 12-bit ADC directly samples the open-circuit voltage ($V_{OC}$) of the top-bezel IXYS solar strip.
* Stepping into direct sunlight instantly increases color saturation and engages high-contrast monochrome waveforms; stepping into a dim room or bedroom automatically dims the screen.

### 3. Driverless USB-C Secondary Monitor Sink (Instant Outdoor Laptop Screen)
* Connect a single USB-C cable from any MacBook, ThinkPad, or iPad into SolarDeck's Port 1.
* The CM5's USB device-mode port (TBD — verify on CM5) enumerates as a high-speed composite USB Gadget display sink (UVC / Weylus), giving you an instantaneous, 10.3" matte, zero-glare, eye-strain-free secondary monitor for terminal logs, documentation, or reading in bright sunlight while the laptop powers the tablet!

### 4. The Airgapped Hardware Crypto Vault & Document Notary (Zero-EMF Signing)
* V2 (ADR-034): QR camera scanning and NFC YubiKey/Tangem/Coldcard signing need the deferred rear camera and NFC.

### 5. Presence-Aware Power Scheduler (Attention-Gap Computing)
* Combining the **Wacom EMR digitizer**, the **voice button / opt-in wake word** (ADR-036), and the **per-rectangle refresh scheduler** on the Kaleido 4 display controller (TBD, ADR-032) into one cognitive budget.
* Hover-approaching stylus, grip-pressure, and keyboard events feed a *user-present* signal. The system runs refresh scrubbing, Meshtastic mailbox polling, telemetry bursts, and telemetryd relays **only in attention gaps** — never mid-stroke, never mid-paragraph.
* **Result:** the perceived smoothness target of Pillar 2 (the Typewriter-on-Paper latency engine) is reached on the *existing* 30 ms partial-rectangle scheduler, and the sleep tier extends further — the device does its housekeeping when you are thinking, not when you are typing.

### 6. RP2350-as-Secure-Element Voiceprint (Tamper-Resistant Identity)
* The **RP2350 co-processor** (which runs the opt-in wake word while Linux is off) becomes the trust boundary for the speaker-verification enrollment (ADR-026, `SOFTWARE_SPEC.md` §17.2).
* The 256-d voiceprint is flashed to co-processor non-volatile storage; the CM5 asks the RP2350 for an owner/not-owner verdict over the existing CM5↔RP2350 interface and never holds a reference copy.
* **Result:** a root-compromised Linux brain cannot swap the voiceprint or re-threshold cosine similarity — the identity anchor survives even a fully owned CM5. And because the verdict runs on the co-processor, stranger speech never wakes Linux at all.

### 7. Acoustic Home-Zone (Privacy-Clean Ambient Fingerprint)
* Requires the opt-in hands-free mode (ADR-036); with it enabled, the MEMS mics compute an **ambient-sound feature profile** (energy bands, cadence, occupancy rhythm) — features only, nothing recorded, nothing stored.
* SolarDeck learns to distinguish *its desk* from *the van* or *the workshop* purely acoustically.
* **Result:** theft alarm arms only outside the known home-zone; notification and brightness policy switch silently when the device knows where it is; zero camera, zero RF, zero GPS involved.

*(Further out: cooperative barometer mesh forecasting across the Meshtastic fleet, golden-hour chrono-locked crypto signing gated on verified presence, and the LoRa (V2, ADR-044) → LTE (V2, ADR-034) → placard comms escalation ladder. Adding any of them touches the same code surface as the three above.)*

---

## Pillar 9: Emergent Hardware + Software Synergies (The 6 Zero-Cost Force Multipliers)

When ultra-low-power microcontrollers (RP2350), bistable electrophoretic physics (E-Ink), specialized sensors, and 64-bit Linux are co-designed from the ground up, emergent system behaviors appear that are physically impossible on conventional laptops or smartphones:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   THE 6 EMERGENT ZERO-COST FORCE MULTIPLIERS                │
├─────────────────────┬───────────────────────┬───────────────────────────────┤
│ EMERGENT FEATURE    │ HARDWARE SYNERGY      │ OPERATIONAL RESULT            │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 1. Zero-Power Pager │ On-board LoRa         │ V2 (ADR-044)                  │
│    & Mailbox        │                       │                               │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 2. Shadow-Gesture   │ Bezel Solar Strip     │ Linux wake without buttons;   │
│    Wake             │ + 12-bit ADC          │ auto-flips Day/Night palette. │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 3. Airgapped Video  │ Rear camera           │ V2 (ADR-034)                  │
│    QR Bridge        │                       │                               │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 4. Whisper Voice-to-│ Two MEMS Mics         │ Transcribes speech in <600ms  │
│    Mesh PTT Memos   │ + ARM NEON + BLE node │ and sends encrypted text.     │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 5. Optical Celestial│ Rear camera           │ V2 (ADR-034)                  │
│    Dead-Reckoning   │                       │                               │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 6. Barometric Storm │ Bosch BMP390 Baro     │ Sounds piezo siren on sudden  │
│    & Flood Alarm    │ + RP2350 Low-IQ Loop  │ 2.5 hPa drop before rain.     │
└─────────────────────┴───────────────────────┴───────────────────────────────┘
```

### 1. The Zero-Power Dead-Drop LoRa Pager & Mailbox
* V2 (ADR-044): needs the deferred on-board LoRa radio, which receives while Linux is off. In V1, messages from a paired Meshtastic node reach the CM5 over Bluetooth LE when Linux is up.

### 2. Shadow-Gesture Wake & Solar Auto-Inversion
* **The Synergy:** The front-bezel monocrystalline solar panel generates open-circuit voltage ($V_{OC}$) continuously sampled by the RP2350 ADC every 100ms ($<5\,\mu\text{A}$ budget).
* **Hover Wake:** Waving a hand or notebook 2–3 inches above the top bezel drops incident light by >75% for 200 milliseconds. The RP2350 recognizes this distinct "shadow-dip signature" as an intentional user gesture and asserts the CM5 wake line (`PIN_GPIO17_WAKE`), starting the Linux resume (seconds, ADR-036) without touching a physical button or keyboard.
* **Sunlight Auto-Inversion:** Moving from direct noon sunlight (100,000 lux, 6.0V on solar cell) into a dark tent (<5 lux, 0.2V on solar cell) automatically signals Sway/Wayland to flip color palettes: from high-contrast black-on-white paper text to an inverted white-on-black terminal with the amber/red frontlight engaged at minimum lux.

### 3. Air-Gapped High-Density Animated QR Bridge (Zero-EMF Ingestion)
* V2 (ADR-034): needs the deferred rear camera.

### 4. Whisper Voice-to-LoRa PTT Tactical Dictaphone
* **The Synergy:** Two MEMS microphones + CM5 ARM NEON SIMD vector processing + a paired external Meshtastic node over Bluetooth LE (on-board LoRa is V2, ADR-044).
* **The Workflow:** Typing lengthy tactical sitreps on an e-ink screen while wearing heavy gloves or walking is cumbersome. The operator presses and holds the voice button (Push-to-Talk, ADR-036). Spoken audio is recorded at 16 kHz. As soon as the button is released, a quantized `whisper.cpp` engine runs across the 4x Cortex-A76 cores, transcribing speech to plain text in **<600 milliseconds**. The text is instantly encrypted (AES-256) and handed over Bluetooth LE to the paired Meshtastic node, which sends it across the mesh as a compact 60-byte packet. Field operators communicate silently and digitally with voice ergonomics.

### 5. Optical Celestial Dead-Reckoning (Zero-Satellite Navigation)
* V2 (ADR-034): needs the deferred rear camera.

### 6. Autonomous Barometric Sudden Storm & Flash-Flood Alarm
* **The Synergy:** Bosch BMP390 ultra-low-noise barometer connected to the RP2350 Always-On I2C bus.
* **The Workflow:** The RP2350 records barometric pressure once every 60 seconds (drawing <3 µA). If barometric pressure drops at a rate exceeding **$2.5\,\text{hPa}$ over 2 hours** (the universal physical signature of an approaching squall line, tornado, or mountain flash flood), the RP2350 triggers an audible piezo siren and stamps an emergency warning banner onto the E-Ink display, alerting outdoor operators to seek shelter before clouds or rain appear.

---

## Pillar 10: EDC Phone Symbiosis & Dual-Screen Hybrid Cyberdeck

Carrying a giant 6.7" glass smartphone alongside a 10.3" sovereign e-ink terminal creates unnecessary pocket bulk and battery anxiety. SolarDeck establishes a symbiotic two-device architecture: pairing the tablet with a compact, tactile pocket communicator (such as the **Clicks Communicator**, **Unihertz Jelly Star**, or **Sony Xperia 10 VI**).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE TWO-DEVICE EVERYDAY CARRY (EDC) RIG                     │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ 1. POCKET COMMUNICATOR (~170g)       │ 2. SOLARDECK WORKSTATION (mass_g)    │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • 50MP OIS Camera (Travel memories)  │ • 10.3" Colour E-Ink Kaleido 4       │
│ • Global 5G/4G + eSIM (Airalo ready) │ • Quad A76 CM5 + RP2350 Dual-Brain   │
│ • Turn-by-Turn Google Maps Navigation│ • Neovim, Claude Code CLI, Kiwix     │
│ • Tactile QWERTY Thumbboard & Calls  │ • LiFePO4 battery (Wh TBD, ADR-040)  │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

### 1. Bluetooth PAN Low-Power Internet Tethering (`bnep0`)
* **The Physics:** Standard Wi-Fi hotspots force the phone into high-power AP mode (~1.8W–2.3W total system overhead), heating the phone and draining its battery in 3–4 hours.
* **The Bluetooth PAN Alternative:** By routing data over Bluetooth Network Access Point (NAP) via Linux `bnep0`, link power drops to **~0.10W total system overhead (22× lower power)**.
* **The Result:** The pocket phone stays ice-cold in your pocket, lasts **2 to 3 days on a single charge**, and auto-reconnects to SolarDeck in **<2.0 seconds** once Linux has resumed. Phone tethering (Bluetooth PAN or Wi-Fi) is V1's only wide-area link; cellular is V2 (ADR-034). The 1.5–2.5 Mbps bandwidth is more than enough for terminal sessions, SSH, Claude Code CLI, git operations, and documentation browsing.

### 2. Center-of-Gravity "Chin-Dock" Dual-Screen Handheld
* **The Cantilever Problem:** Cantilevering a phone below the bottom edge of the tablet creates a 227mm lever arm that exhausts wrists within minutes of handheld thumb-typing.
* **The Screen-Overlap Solution:** The Clicks Communicator docks **on top of the lower bezel/screen face**, suspended 1.0mm above the E-Ink front glass with soft silicone bumpers.
* **Handheld Ergonomics:** Both hands grip the rigid bottom chassis of SolarDeck. The tablet mass is cradled directly between your palms with **zero wrist torque**, matching the balanced feel of a Nintendo Switch or Steam Deck.
* **Dynamic Software Viewport Masking:** Sway/Wayland shifts the active workspace upwards (`swaymsg "gaps bottom 400"`), rendering a clean desktop (resolution TBD, ADR-032) on the top visible E-Ink panel. The occluded bottom pixels are filled with static black/white, drawing **0.000 Watts**.
* **Dual-Screen Symbiosis:**
  * **Top Canvas (10.3" E-Ink):** Deep focus, zero glare, sunlight-readable code, terminal, and documentation.
  * **Bottom Insert (4.03" AMOLED):** Live color Google Maps, audio controls, battery telemetry, and incoming Signal messages, flanked by physical clicky QWERTY thumb keys.

### 3. Tactile Thumbboard & Hardware Focus Flip
* **Thumbboard Input:** Android exposes the phone's physical keyboard as a standard Bluetooth HID or wired USB-C input (`/dev/input/eventX`) with sub-millisecond latency.
* **0-Millisecond Focus Flip:** Tapping the phone's programmable hardware side key instantly flips typing focus between SolarDeck's terminal and local phone SMS/Google Maps with zero re-pairing or menu diving.
* **Capacitive Touch Scrolling:** Swiping thumbs up and down across the physical keycaps acts as an invisible trackpad, scrolling terminal buffers and reading PDFs without lifting fingers from the keys.

### 4. MagSafe Ecosystem & Wacom Mu-Metal Flux Isolation
* **Universal Snap-On Magnetic Mount:** Embedded 54mm Neodymium N52 magnetic ring array on the rear shell supports off-the-shelf **MOFT folding origami kickstands** (25° writing, 45° typing, 60° reading), MagSafe wallets, vehicle mounts, and magnetic campervan bulkhead pucks.
* **Mu-Metal Shielding Layer:** A 0.1mm high-permeability Mu-Metal / Ferrite foil laminated behind the Wacom EMR digitizer redirects static magnetic flux away from the resonant 560 kHz coil, ensuring **zero stylus coordinate drift or jitter** even with powerful magnetic kickstands attached.

### 5. Hybrid Remote-Builder Loop (`bld --remote`)
* **Local vs. Remote Tradeoff:** Small code tweaks (<15s) compile locally on CM5 using ~18 Joules. Heavy builds (Linux kernel, DRM tree, large Rust/C++ projects) are offloaded via `bld --remote`.
* **The Pipeline:** Computes a `git diff`, pushes across encrypted **Tailscale (WireGuard)** to a home Apple Silicon or Ryzen workstation, cross-compiles in 10 seconds inside Docker ARM64, and SCPs the stripped binary back to SolarDeck.
* **Energy Impact:** Burns **180 Joules** on SolarDeck vs **18,000 Joules** locally—a **100× power saving** that eliminates fanless thermal throttling in direct sunlight. Mosh ensures terminal connections survive a spotty tethered link indefinitely.

---

## Pillar 11: Campervan E-Ink Dual-Screen Dock, Blackout Beacon & Field Digitizer

*Written 2026-10-19 14:20 UTC in the Pi harness by antigravity/gemini-3.8-flash. Voice content moved to Pillar 7 (2026-10-21).*

### 1. Giant E-Ink Secondary Monitor & Campervan Docking
* **Native Micro-HDMI 4K Silicon Path:** CM5 routes `HDMI0` (TBD — verify on CM5) to a sealed Micro-HDMI port with TPD4E05U06 ESD protection.
* **The 25.3" / 13.3" E-Ink Advantage:** Unlike LCD/OLED monitors that burn 15W–25W continuous backlight power, external E-Ink monitors (Dasung Paperlike 253, Boox Mira Pro 25.3" 3200×1800) consume **0.000W holding power on static text**.
* **Wayland Multi-Head Orchestration:** `solardeck-dockd` automatically binds high-density workspaces 1–8 to the big monitor, pins van telemetry (Victron battery, water tanks, Meshtastic chat) to the 10.3" internal screen, and locks Wacom stylus input strictly to the internal display.

### 2. Blackout Supercapacitor Emergency SOS Beacon
* **The Zero-Battery Bootstrap:** When the main LiFePO4 battery is completely dead (0.000V) or missing, an onboard **1.0F 3.3V supercapacitor** fed by the front micro-solar strip charges in 12–15 minutes under direct sunlight.
* **150ms Cold Burst:** RP2350 cold-boots, grabs last-known GNSS (MAX-M10S) coordinates from RTC NVRAM, burns an indelible distress placard onto the 10.3" screen. The distress message remains legible forever with **0.000W battery consumption**. The radio SOS burst is V2 (ADR-044).

### 3. Zero-Hardware Wacom Field Caliper & CAD Digitizer
* **10mm Hover Tracking:** The Wacom EMR digitizer senses the stylus tip up to 10 mm above the glass with **0.1 mm precision**, allowing contact-free measurement of delicate physical specimens without touching the screen.
* **Mutual-Capacitance Part Profiling:** Placing conductive metal bolts, drill bits, or washers directly on the capacitive glass detects contact centroid ellipses, extracting length and thread diameter automatically and exporting 1:1 DXF/SVG CAD files for 3D printing.

---

## Pillar 12: Hostile Border Defense & Anti-Forensic Evasion

*Written 2026-10-19 15:50 UTC in the Pi harness by antigravity/gemini-3.8-flash*

Engineered specifically to defeat forensic extraction kiosks (Cellebrite UFED, MSAB XRY, GrayKey), rogue cellular towers (Stingrays), and physical search duress:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 HOSTILE BORDER DEFENSE & ANTI-FORENSICS                     │
├─────────────────────┬───────────────────────┬───────────────────────────────┤
│ THREAT              │ HARDWARE / CRYPTO     │ COUNTER-MEASURE               │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 1. Forensic Kiosks  │ Detached LUKS Header  │ Master header stored on hidden│
│    (Cellebrite)     │ (`solardeck-stealth`) │ vault MicroSD; drive is noise.│
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 2. Physical Duress  │ Dual-PIN Decoy Boot   │ Decoy PIN boots tourist OS;   │
│    Screen Search    │ (Plausible Deniability│ panic PIN wipes volatile keys.│
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 3. IMSI Catchers &  │ AT Signaling Watchdog │ V2 (ADR-034): no cellular     │
│    Stingray Towers  │ (`solardeck-stingray`)│ radio in V1.                  │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 4. BadUSB / Kiosk   │ Physical Analog SPST  │ Mechanically severs D+/D- lines│
│    Juice-Jacking    │ Switch (TS3USB221A)   │ while negotiating 20W PD power│
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 5. Evil-Maid Case   │ Optical & Contact Reed│ Triggers RP2350 NMI interrupt;│
│    Disassembly      │ Sensor (`TAMPER_NMI`) │ zeroizes RAM keys in <3 ms.   │
└─────────────────────┴───────────────────────┴───────────────────────────────┘
```

1. **Detached LUKS Header:** Relocating the 16MB LUKS header to the cold storage vault renders the 2TB NVMe SSD mathematically indistinguishable from factory-unpartitioned random NAND flash.
2. **Dual-PIN Plausible Deniability:** Unlocks an authentic Debian tourist desktop (travel itineraries, photos, recipes) under inspection, keeping tactical volumes invisible.
3. **Hardware USB Isolation:** Physical SPST analog switch breaks high-speed USB data lines ($D+/D-$) to 0.000V during charging at untrusted public stations or border ports.
4. **Active IMSI Catcher Watchdog:** V2 (ADR-034).
5. **Chassis Zeroization Sensor:** Internal micro-phototransistor and leaf contact trigger instantaneous RAM key wiping within 3 ms if the unibody shell is opened.

---

## Pillar 13: Perpetual Solar Zen Ecosystem & Immortal Batteryless Mode

*Written 2026-10-19 15:50 UTC in the Pi harness by antigravity/gemini-3.8-flash*

Transforming SolarDeck from an active computer into an immortal, zero-battery ambient station and off-grid mind gym powered purely by ambient sunlight:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 PERPETUAL SOLAR ZEN DASHBOARD & ENTERTAINMENT               │
├─────────────────────┬───────────────────────┬───────────────────────────────┤
│ APPLICATION         │ HARDWARE SUBSYSTEM    │ OPERATIONAL ENERGY            │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 1. Living Wall Clock│ RP2350 + DS3231 RTC   │ 4.5 mW (Refreshes once/min;   │
│    & Barometer HUD  │ + Bosch BMP390 Baro   │ 0.000W static holding power). │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 2. Infinite Chess   │ Micro-Max / Toledo C  │ 0.000W between moves;         │
│    Engine           │ on Hazard3 RISC-V     │ 5 AI levels & pass-and-play.  │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 3. Infocom Z-Machine│ C Frotz Interpreter   │ 0.000W between keystrokes;    │
│    Interactive Fic  │ in 8MB QSPI PSRAM     │ Zork I-III, Planetfall, etc.  │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 4. Daily Procedural │ Algorithmic RTC Seed  │ Solvable via Wacom EMR stylus;│
│    Puzzle Engine    │ Generator             │ 50,000+ Sudoku/Nonograms.     │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 5. Daily Stoic &    │ 10,000 Text Curated   │ Auto-refreshes at solar dawn; │
│    Tao Te Ching     │ Offline Typography    │ zero battery drain all day.   │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 6. Immortal Solar   │ Dual-Bezel IBC Panel  │ Direct solar cold-boot via    │
│    "Zombie Mode"    │ (1.24W) + 1.0F Supercap│ 1.0F supercap (Zero battery). │
└─────────────────────┴───────────────────────┴───────────────────────────────┘
```

1. **Full-Width Dual-Bezel IBC Solar Array:** SunPower Maxeon Gen 7 back-contact monocrystalline strips ($51.6\text{ cm}^2$ total area across top and bottom bezels) generate **1.24W peak in direct sunlight** and **120 mW to 240 mW in indirect shade**—an **8× to 20× surplus** over the 4.5 mW to 15 mW required for RP2350 operation.
2. **Batteryless Direct Solar Cold-Boot ("Zombie Mode"):** Even with the LiFePO4 battery missing or drained to 0.000V, sunlight charges the onboard 1.0F supercapacitor in **under 25 seconds**, cold-booting the RP2350 into the Zen Solar Suite indefinitely.
3. **Mind Games & Intellectual Entertainment:** Infinite E-Ink chess, Infocom interactive fiction (*Zork*), procedural daily Sudoku/Wordle, and stoic philosophy oracles run completely offline with **zero battery drain** between user actions.
4. **Perpetual Solar Mesh Relay:** V2 (ADR-044): needs the deferred on-board LoRa radio.
5. **Snap-On MagSafe 7.1W "Solar Armor" Backplate & 2.5m Remote Shade Tether (`SOLAR-ARMOR-V1`):**
   * Snaps via the embedded MagSafe N52 magnetic ring with a 2.0mm convective chimney to dissipate heat, harvesting **7.13W Peak** in direct tropical sun—surpassing the 5.5W full turbo compilation load of the quad-core CM5.
   * **The Remote Shade Tether:** Features an integrated 2.5-meter Kevlar-reinforced flat ribbon cable that unspools from the backplate. The panel sits out on a sunlit boulder or vehicle roof generating 7.1W, while the operator sits comfortably in the cool shade using the tablet with **zero thermal stress on the LiFePO4 battery**. Doubles as an independent 7.1W USB-C solar charger for phones and flashlights.

---

## Pillar 14: Global Travel & Field Biology Sovereign Recon

*Written 2026-10-19 15:50 UTC in the Pi harness by antigravity/gemini-3.8-flash*

Equipping the sovereign traveler and wilderness naturalist with completely offline scientific instruments:

1. **Airgapped Sovereign e-Passport Inspector (`solardeck-epassport`):** V2 (ADR-034): needs the deferred NFC.
2. **Zero-Cloud Camera Sign Translation & Currency Arbitrage (`solardeck-lensworld`):** V2 (ADR-034): needs the deferred rear camera.
3. **Consular & Geopolitical Evacuation Navigator (`solardeck-evacd`):** Offline 195-nation database of embassies, Level-1 trauma centers, and paved airstrips, displaying high-contrast great-circle evacuation vectors during regional unrest or telecommunications collapse.
4. **Macro Parasite & Tick Morphology Triage (`solardeck-parasited`):** V2 (ADR-034): needs the deferred rear camera.
5. **Galvanic Soil pH & Agricultural Profiler (`solardeck-soild`):** Dual tent-stake probes measure soil galvanic potential and conductivity, calculating pH (3.5–9.0) and moisture for survival agriculture and heavy-metal contamination screening.
6. **Timber Fuel Energy & Bow-Drill Firecraft Oracle (`solardeck-timberd`):** Evaluates tree bark and leaf morphology to identify wood BTU density, wet-splitting characteristics, and friction fire spindle/hearth combinations.
7. **Microscopic Waterborne Pathogen Lens Guide (`solardeck-microbed`):** V2 (ADR-034): needs the deferred rear camera.

---

## Verification & Acceptance Gate (The North Star Metrics)

Before any prototype PCBA or firmware build is declared ready for field release, it must be benchmarked against these twelve non-negotiable gates:

| # | Metric | Target Threshold | Method of Verification |
| :--- | :--- | :--- | :--- |
| **G1** | Linux resume to first keystroke (ADR-036) | **Target set from the dev-kit bench** (no RAM-retaining suspend on CM5) | High-speed 240 FPS camera recording key strike to display glyph. |
| **G2** | 1-Bit Fast-Typing Latency | **< 20 milliseconds** | Oscilloscope measuring key switch closure to the Kaleido 4 display controller (TBD, ADR-032) pin toggle. |
| **G3** | Zen Reading Power Consumption | **< 5.0 milliwatts** | TI INA3221 telemetry / Keithley precision source meter at VBAT. |
| **G4** | Outdoor solar top-up of RP2350 idle (indoor claim withdrawn, ADR-041) | **Strip output exceeds RP2350 idle draw outdoors** | Outdoor insolation; verify net charge current into the cell with the CM5 off. |
| **G5** | Airgap RF Radiation | **0.000 dBm (Noise Floor)** | Rohde & Schwarz / HackRF sweep in anechoic chamber across 50MHz–6GHz. |
| **G6** | Zero-Brick Watchdog Auto-Rollback | **< 2.5 milliseconds** | Fault injected into Bank B; verify hardware WDT fallback to Golden Image. |
| **G7** | Transit Drop Survival | **1.22 m, 26 orientations, functional** | MIL-STD-810H 516.8 procedure IV; corner drops first (cell retention, corner bond). |
| **G8** | Thermal-Cycle Joint Integrity | **500 cycles −40…+85 °C, ΔR < 10%** | Per-package joint resistance sampled before/after; proves the DSBGA corner bond (§7.6). |
| **G9** | UV & Weather Durability | **ASTM G154 1000 h, ΔE < 3, no crazing** | Quartz-xenon chamber on PA12 + anodised samples; colour dye degrades faster by design. |
| **G10** | Unpowered Storage Survival | **12 months, boots, OS volumes intact** | Powered off at 50% SOC, 30 °C; validates the NAND scrub policy against real retention loss. |
| **G11** | USB-C interoperability: 10-row matrix incl. dead-battery Rd and charge-only-cable diagnostic | Every row passes on the dev kit | `USB_ROBUSTNESS.md` §3 |
| **G12** | Sleep-ladder energy & resume integrity: R2 is `null` (no RAM-retaining state on CM5, ADR-036); R3 disk-hibernate 0.000 W idle; R4 deep-off keep-alive <0.2 mW via Li-primary; resumed sessions pass a post-wake integrity check | All rungs measured on the dev kit; hibernation image survives 30-day cold storage (§54 scrub) | `SOFTWARE_SPEC.md` §3.3.3, `HARDWARE_SPEC.md` §2.30 |

---

*This document serves as the permanent architectural North Star for all SolarDeck hardware, firmware, and software development.*
