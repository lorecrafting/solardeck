# Standout Features & Engineering North Stars — SolarDeck

Written 2026-10-18 17:42 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## Executive Philosophy: The 14 Standout Feature Pillars (7 product pillars + 7 chapters)

SolarDeck is not an incremental iteration on an Android e-reader or a miniature Raspberry Pi toy. It is a sovereign, sunlight-readable mobile workstation designed to eliminate the fundamental compromises of modern computing: screen glare, battery anxiety, input latency, distraction loops, and hardware fragility.

The product is defined by **seven non-negotiable standout pillars** (summarised in `README.md` §2 and expanded below), followed by seven further chapters of emergent capability. If any of the seven core pillars feels sluggish, clumsy, or compromised, the product fails. If all seven are executed flawlessly, SolarDeck defines an entirely new category of personal computing.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE 7 SOLARDECK PILLARS TO HAMMER IN ON                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. THE DUAL-BRAIN INSTANT HANDOFF (<400ms Wake, 300-Day Zen / Infinite Desk)│
│ 2. THE TYPEWRITER-ON-PAPER LATENCY ENGINE (<20ms Keystroke & Inking)        │
│ 3. SUNLIGHT SOVEREIGNTY & PERPETUAL INDOOR HARVESTING (Zero-Glare, 0W Hold) │
│ 4. THE SNAPDECK FORM-MORPHOLOGY (Rigid Lapdeck ⟷ 620g Slate ⟷ Desk Easel)   │
│ 5. SOVEREIGN FIELD HARDENING (Hardware Airgap, Meshtastic LoRa, IP67 Rain)  │
│ 6. THE MODULAR UPGRADE BRIDGE (ARM-to-RISC-V Swappability, M.2 NVMe, & RAM) │
│ 7. THE SOVEREIGN VOICE AGENT (Barge-In & Touch-to-Talk, 80-Day Standby)     │
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
1. **Zero Bus Contention:** The **2× Texas Instruments TMUX1575** bus switch pair (4 channels each, 8 total) guarantees that when the RP2350 owns the display bus during Zen reading, all CM4 display pins are galvanically isolated with zero parasitic back-powering ($I_{\text{off}}$).
2. **Deterministic Wake Pins:** Keyboard keystroke IRQ (via USB-C or BLE), Wacom `PEN_PROX_INT`, BMA400 tap detection, and the 5-way navigation rocker are hardwired directly to RP2350 edge-triggered interrupt pins (GPIO 10–13), guaranteeing sub-microsecond interrupt capture.
3. **No Bootloader Delays:** In S2idle suspend, RAM remains refreshed at 15 mW. In cold hibernate, an immutable Linux kernel image with `initramfs` resides on high-speed eMMC with all non-essential systemd services disabled.

---

## Pillar 2: The "Typewriter-on-Paper" Latency Engine (<20ms Keystroke & Inking)

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
4. **Haptic Engine: Wideband LRA by Default, Spatial Piezo Array as an Option:**
   * *The Problem with Global Vibration:* Standard phones and tablets shake the entire aluminum body when you tap a virtual key, vibrating both palms and feeling artificial.
   * *Base build:* A single TI **DRV2605L** + 8 mm Z-axis LRA, chassis-mounted with its mass on the metal frame. `solardeck-hapticd` still shapes per-keystroke waveforms (<0.6 ms trigger), and the actuator is a replaceable part. The whole frame moves slightly; it feels like a good phone, not like a microswitch.
   * *Why:* The spatial array puts four adhesively bonded ceramics at the highest-strain location in a drop. It is the best tactile experience here and the worst 30-year bet here (ADR-020, `HARDWARE_SPEC.md` §7.6).
   * *Retained option (DNP footprint):* 4× **TDK PowerHap** at the glass corners + dual **Boréas BOS1901** CapDrive drivers with >80% energy recovery. `solardeck-hapticd` fires a sub-1.0 ms impulse into the nearest corner and phase-inverted damping pulses at the opposite corners, concentrating displacement under the fingertip for a genuine **localized mechanical click on flat glass**. Populate it for demos or for a buyer who accepts a 10-year glass-bond service life.

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

## Pillar 4: Universal Form-Morphology (Handheld Grip ⟷ Pure Slate ⟷ Desk Easel)

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
│ 2. TACTICAL READING & INKING SLATE (The Pure 510g Tablet)                   │
│    • Detach from grip or stand in 0.5 seconds.                              │
│    • 510g lightweight, 9.8mm slim IP67 waterproof reading slate.            │
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
* The expensive components—the **10.3" Color E-Ink glass**, the **Wacom EMR digitizer**, the **custom 32 Wh LiFePO4 battery**, the **precision CNC/SLS enclosure**, and the **carrier motherboard**—are built to last a decade.
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

### 6. The "Cold Storage Vault" (Carry Up to 6+ Terabytes Off-Grid for $0 BOM)
To make SolarDeck the ultimate sovereign archive workstation without adding a single cent in electronics or compromising exterior unibody waterproofing:
* **Gasketed M.2 Service Hatch Cavity:** Molded directly into the inner face of the flush, IP67 silicone-gasketed M.2 SSD service hatch on the rear chassis unibody (secured by 2x stainless M2 captive screws).
* **Storage Capacity:**
  * **3x Uniform Friction-Fit MicroSD Card Pockets:** Holds three extra MicroSD cards (e.g. Card 1: 1TB offline Kiwix Wikipedia + MDN + Library of Genesis; Card 2: bootable Tails / Arch rescue OS; Card 3: encrypted personal git vault).
  * **Nano-SIM Compatibility via Adapter:** Standardizes on uniform MicroSD pocket dimensions (15.0mm × 11.0mm × 1.0mm). To store a spare Nano-SIM, users slide the SIM into a standard $0.05 plastic MicroSD carrier shell.
  * **1x Stainless Steel SIM Ejector Tool Retaining Clip:** Keeps a metal SIM ejector pin snapped into place.
* **Mechanical Retention & Weather Protection:** Molded 85A TPU micro-ribs prevent rattling or dislodging during severe drops, while the gasketed hatch keeps the cards 100% sealed inside the IP67 envelope, completely hidden and protected from rain, dust, and visual inspection.
* **Total Accessible Storage:** With 2TB on the active edge MicroSD slot, 3TB in the cold vault, and 2TB on the internal M.2 NVMe SSD, developers can carry **up to 7 Terabytes of uncompressed human knowledge and local AI weights** in a 510g tablet!

---

## Pillar 7: The Sovereign Voice Agent (Barge-In & Touch-to-Talk)

*Written 2026-10-20 19:37 UTC in the Pi harness by openrouter/deepseek/deepseek-v4-flash-0731*

The voice channel is a first-class pillar, not a bolt-on: SolarDeck can hear you for **80+ days on standby**, you can **speak over it mid-sentence**, and you can always fall back to a deterministic **touch-to-talk** path. It exists so the operator can command the machine hands-free in the field, the workshop, the cockpit — without cradling a keyboard.

### 1. The Cascaded 3-Tier Wake (Zero Standby Battery Penalty)
Instead of keeping the 1.8W CM4 awake, listening runs on a **cascaded 3-tier filter**:
  1. **Knowles MEMS hardware acoustic front-end** ($<0.05\text{ mW}$).
  2. **RP2350 co-processor** running INT8 `microWakeWord` (~14 mW, delivering **80+ days continuous standby**).
  3. **CM4 wakes in 250 ms** only when "Hey Deck" is spoken, evaluating **Resemblyzer speaker biometrics** (cosine similarity $\ge 0.78$) to reject bystanders before running `whisper.cpp`.

### 2. True Acoustic Barge-In (Interruption)
PipeWire loops back the MAX98357A speaker audio into SpeexDSP / WebRTC AEC3 Acoustic Echo Cancellation, subtracting SolarDeck's own voice from the microphones. The operator can speak over SolarDeck while it talks at full volume, and it **stops and retargets instantly** — no push-to-talk required for the barge-in path.

### 3. Touch-to-Talk (Deterministic Fallback)
A **held-call PTT path bypasses the wake-word entirely**: the mic is hot only while the touch target is held, giving deterministic, full-duplex operator control. This is the fallback when acoustic conditions or bystanders defeat the wake-word, and it never depends on wake latency.

---

## Pillar 8: Genius-Level Convenience Combinations ($0.00 Added BOM)

By orchestrating and cross-wiring the existing hardware components in innovative ways, SolarDeck delivers four extraordinary convenience features without adding a single cent to the Bill of Materials:

### 1. The 32 Wh Survival Powerbank (15W Reverse Boost)
* Utilizing the bidirectional synchronous boost engine in the **TI BQ25895** buck charger, SolarDeck outputs **5.1V @ 3.1A (15.8W)** backwards through USB-C Port 1 or 2 to fast-charge external smartphones, flashlights, or radios.
* **Linux Stays 100% Asleep (0.000W):** The RP2350 co-processor manages power delivery and displays a live, crisp battery percentage and output wattage on the E-Ink screen. Never carry a separate powerbank again.

### 2. The Solar Micro-Strip as a Free Ambient Light Sensor ($0.00 Cost)
* Rather than adding a dedicated photodiode IC, the RP2350's internal 12-bit ADC directly samples the open-circuit voltage ($V_{OC}$) of the top-bezel IXYS solar strip.
* Stepping into direct sunlight instantly increases color saturation and engages high-contrast monochrome waveforms; stepping into a dim room or bedroom automatically dims the screen.

### 3. Driverless USB-C Secondary Monitor Sink (Instant Outdoor Laptop Screen)
* Connect a single USB-C cable from any MacBook, ThinkPad, or iPad into SolarDeck's Port 1.
* The dedicated BCM2711 USB OTG controller enumerates as a high-speed composite USB Gadget display sink (UVC / Weylus), giving you an instantaneous, 10.3" matte, zero-glare, eye-strain-free secondary monitor for terminal logs, documentation, or reading in bright sunlight while the laptop powers the tablet!

### 4. The Airgapped Hardware Crypto Vault & Document Notary (Zero-EMF Signing)
* Combining the physical **Hardware Airgap Kill Switch** (cutting all RF radios to 0.000V), the **rear flush 12MP Sony IMX708 autofocus camera**, the **10.3" Color E-Ink display**, and **top-bezel 13.56 MHz NFC**.
* When flipped to Stealth (0.000 dBm), SolarDeck becomes an impenetrable, mathematically verifiable cold-storage signing station:
  1. Scan an unsigned Bitcoin/Ethereum transaction QR or document hash with the rear 12MP camera.
  2. Inspect the complete decoded transaction details, contract calls, and gas fees in razor-sharp high contrast on the 10.3" screen.
  3. Authorize and sign using an onboard airgapped GPG/SSH key, or tap a physical **YubiKey, Tangem, or Coldcard** against the top-bezel NFC coil.
  4. Display the signed transaction QR on the E-Ink screen for an online smartphone to broadcast.
* Completely immune to remote exploits or RF sniffing because the wireless power rails are physically cut by hardware switches!

### 5. Presence-Aware Power Scheduler (Attention-Gap Computing)
* Combining the **Wacom EMR digitizer**, the **Knowles MEMS wake-word tier**, and the **IT8951 per-rectangle refresh scheduler** into one cognitive budget.
* Hover-approaching stylus, grip-pressure, and keyboard events feed a *user-present* signal. The system runs refresh scrubbing, LoRa mailbox polling, telemetry bursts, and telemetryd relays **only in attention gaps** — never mid-stroke, never mid-paragraph.
* **Result:** the perceived smoothness target of Pillar 2 is reached on the *existing* 30 ms partial-rectangle scheduler, and the sleep tier extends further — the device does its housekeeping when you are thinking, not when you are typing.

### 6. RP2350-as-Secure-Element Voiceprint (Tamper-Resistant Identity)
* The **RP2350 co-processor** (already the wake-word tier) becomes the trust boundary for the speaker-verification enrollment (ADR-026, `SOFTWARE_SPEC.md` §17.2).
* The 256-d voiceprint is flashed to co-processor non-volatile storage; the CM4 asks the RP2350 for an owner/not-owner verdict over the existing CM4↔RP2350 interface and never holds a reference copy.
* **Result:** a root-compromised Linux brain cannot swap the voiceprint or re-threshold cosine similarity — the identity anchor survives even a fully owned CM4. And because the verdict runs in the 14 mW tier, stranger speech never wakes Linux at all.

### 7. Acoustic Home-Zone (Privacy-Clean Ambient Fingerprint)
* The already-always-on Knowles array computes an **ambient-sound feature profile** (energy bands, cadence, occupancy rhythm) — features only, nothing recorded, nothing stored.
* SolarDeck learns to distinguish *its desk* from *the van* or *the workshop* purely acoustically.
* **Result:** theft alarm arms only outside the known home-zone; notification and brightness policy switch silently when the device knows where it is; zero camera, zero RF, zero GPS involved.

*(Further out: cooperative barometer mesh forecasting across the LoRa fleet, golden-hour chrono-locked crypto signing gated on verified presence, and the LoRa → LTE → placard comms escalation ladder. Adding any of them touches the same code surface as the three above.)*

---

## Pillar 9: Emergent Hardware + Software Synergies (The 6 Zero-Cost Force Multipliers)

When ultra-low-power microcontrollers (RP2350), bistable electrophoretic physics (E-Ink), specialized sensors, and 64-bit Linux are co-designed from the ground up, emergent system behaviors appear that are physically impossible on conventional laptops or smartphones:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   THE 6 EMERGENT ZERO-COST FORCE MULTIPLIERS                │
├─────────────────────┬───────────────────────┬───────────────────────────────┤
│ EMERGENT FEATURE    │ HARDWARE SYNERGY      │ OPERATIONAL RESULT            │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 1. Zero-Power Pager │ RP2350 + SX1262 LoRa  │ 60–90 day autonomous terminal;│
│    & Mailbox        │ + E-Ink Bistability   │ updates e-paper while CM4 off.│
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 2. Shadow-Gesture   │ Bezel Solar Strip     │ <300ms wake without buttons;  │
│    S2idle Wake      │ + 12-bit ADC          │ auto-flips Day/Night palette. │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 3. Airgapped Video  │ 12MP IMX708 Autofocus │ Ingests multi-MB files visually│
│    QR Bridge        │ + VideoCore VI GPU    │ under 100% RF kill.           │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 4. Whisper Voice-to-│ Knowles MEMS Dual-Mic │ Transcribes speech in <600ms  │
│    LoRa PTT Memos   │ + ARM NEON + SX1262   │ and blasts encrypted text.    │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 5. Optical Celestial│ IMX708 + 9-DOF IMU +  │ Derives lat/long within 150m  │
│    Dead-Reckoning   │ DS3231 RTC + Plate-Sol│ with zero GPS/GNSS satellites.│
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 6. Barometric Storm │ Bosch BMP390 Baro     │ Sounds piezo siren on sudden  │
│    & Flood Alarm    │ + RP2350 Low-IQ Loop  │ 2.5 hPa drop before rain.     │
└─────────────────────┴───────────────────────┴───────────────────────────────┘
```

### 1. The 90-Day Zero-Power Dead-Drop LoRa Pager & Mailbox
* **The Synergy:** Electrophoretic pigment particles retain their physical orientation indefinitely with **zero holding current**. The RP2350 co-processor and SX1262 LoRa transceiver consume just **12 milliwatts** in continuous packet listen mode.
* **The Workflow:**
  1. The CM4 Linux processor is powered completely OFF (0.000W).
  2. The SX1262 receives an incoming encrypted Meshtastic / Reticulum packet over the top SMA antenna.
  3. The RP2350 decrypts the packet header in hardware and draws the message into its 8MB PSRAM framebuffer.
  4. The RP2350 asserts `PIN_TMUX_SEL_CM4_NRP` to claim the display SPI bus, sends a 1-bit partial refresh command to the bottom 2 inches of the 10.3" screen, pulses the onboard micro-piezo buzzer once, and returns to sleep.
  5. The message remains legibly stamped in physical ink on the display.
* **Result:** SolarDeck can sit on a vehicle dashboard, camp table, or tactical operations center for **over 2 months** as a live, self-updating electronic paper bulletin board that requires zero boot time to read.

### 2. Shadow-Gesture S2idle Wake & Solar Auto-Inversion
* **The Synergy:** The front-bezel monocrystalline solar panel generates open-circuit voltage ($V_{OC}$) continuously sampled by the RP2350 ADC every 100ms ($<5\,\mu\text{A}$ budget).
* **Hover Wake:** Waving a hand or notebook 2–3 inches above the top bezel drops incident light by >75% for 200 milliseconds. The RP2350 recognizes this distinct "shadow-dip signature" as an intentional user gesture and asserts `CM4_GPIO_WAKE`, waking the Linux terminal in **<300 milliseconds** without touching a physical button or keyboard.
* **Sunlight Auto-Inversion:** Moving from direct noon sunlight (100,000 lux, 6.0V on solar cell) into a dark tent (<5 lux, 0.2V on solar cell) automatically signals Sway/Wayland to flip color palettes: from high-contrast black-on-white paper text to an inverted white-on-black terminal with the amber/red frontlight engaged at minimum lux.

### 3. Air-Gapped High-Density Animated QR Bridge (Zero-EMF Ingestion)
* **The Synergy:** Combining the hardware RF Airgap Kill Switch (which cuts all wireless transmitters to 0.000V), the 12MP Sony IMX708 PDAF autofocus camera, and the Broadcom VideoCore VI GPU hardware video pipeline.
* **The Workflow:** When full radio silence is mandatory, software patches, encrypted documents, or cryptographic keys are transferred into SolarDeck visually. An external device displays a high-speed animated 2D barcode stream (UR / BBQr standard). The IMX708 captures 30 FPS video frames, hardware-decoded by the GPU in memory. Multi-megabyte files are sucked in across the airgap in seconds with **zero radio emissions (0.000 dBm)**.

### 4. Whisper Voice-to-LoRa PTT Tactical Dictaphone
* **The Synergy:** Dual Knowles SPH0645 MEMS microphones + CM4 ARM NEON SIMD vector processing + Semtech SX1262 LoRa mesh.
* **The Workflow:** Typing lengthy tactical sitreps on an e-ink screen while wearing heavy gloves or walking is cumbersome. The operator presses and holds the left-bezel tactical button (Push-to-Talk). Spoken audio is recorded at 16 kHz. As soon as the button is released, a quantized `whisper.cpp` engine runs across the 4x Cortex-A72 cores, transcribing speech to plain text in **<600 milliseconds**. The text is instantly encrypted (AES-256) and transmitted across the LoRa mesh as a compact 60-byte packet. Field operators communicate silently and digitally with voice ergonomics.

### 5. Optical Celestial Dead-Reckoning (Zero-Satellite Navigation)
* **The Synergy:** 12MP Sony IMX708 camera + DS3231 temperature-compensated RTC (<2 ppm drift) + Bosch 9-DOF IMU + offline `astrometry.net` solver.
* **The Workflow:** In severe electronic warfare or geomagnetic storms where GPS/GNSS signals are jammed or spoofed, the operator places SolarDeck flat facing the night sky. The camera captures a 2-second exposure. The onboard plate-solver matches stellar coordinates against the offline Tycho-2 star catalog, combines them with atomic UTC from the RTC and gravity tilt vectors from the IMU, and computes the observer's exact terrestrial latitude and longitude within **150 meters**—with **zero satellites, zero cell reception, and zero RF emissions**.

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
│ 1. POCKET COMMUNICATOR (~170g)       │ 2. SOLARDECK WORKSTATION (510g)      │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • 50MP OIS Camera (Travel memories)  │ • 10.3" Color E-Ink Carta 1200       │
│ • Global 5G/4G + eSIM (Airalo ready) │ • Quad A72 CM4 + RP2350 Dual-Brain   │
│ • Turn-by-Turn Google Maps Navigation│ • Neovim, Claude Code CLI, Kiwix     │
│ • Tactile QWERTY Thumbboard & Calls  │ • 26–32 Wh LiFePO4 All-Day Battery   │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

### 1. Bluetooth PAN Low-Power Internet Tethering (`bnep0`)
* **The Physics:** Standard Wi-Fi hotspots force the phone into high-power AP mode (~1.8W–2.3W total system overhead), heating the phone and draining its battery in 3–4 hours.
* **The Bluetooth PAN Alternative:** By routing data over Bluetooth Network Access Point (NAP) via Linux `bnep0`, link power drops to **~0.10W total system overhead (22× lower power)**.
* **The Result:** The pocket phone stays ice-cold in your pocket, lasts **2 to 3 days on a single charge**, and auto-reconnects to SolarDeck in **<2.0 seconds** upon waking from S2idle. The 1.5–2.5 Mbps bandwidth is more than enough for terminal sessions, SSH, Claude Code CLI, git operations, and documentation browsing.

### 2. Center-of-Gravity "Chin-Dock" Dual-Screen Handheld
* **The Cantilever Problem:** Cantilevering a phone below the bottom edge of a 510g tablet creates a 227mm lever arm that exhausts wrists within minutes of handheld thumb-typing.
* **The Screen-Overlap Solution:** The Clicks Communicator docks **on top of the lower bezel/screen face**, suspended 1.0mm above the E-Ink front glass with soft silicone bumpers.
* **Handheld Ergonomics:** Both hands grip the rigid bottom chassis of SolarDeck. The 510g tablet mass is cradled directly between your palms with **zero wrist torque**, matching the balanced feel of a Nintendo Switch or Steam Deck.
* **Dynamic Software Viewport Masking:** Sway/Wayland shifts the active workspace upwards (`swaymsg "gaps bottom 400"`), rendering a clean 1872×1004 desktop on the top visible E-Ink panel. The occluded bottom pixels are filled with static black/white, drawing **0.000 Watts**.
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
* **Local vs. Remote Tradeoff:** Small code tweaks (<15s) compile locally on CM4 using ~18 Joules. Heavy builds (Linux kernel, DRM tree, large Rust/C++ projects) are offloaded via `bld --remote`.
* **The Pipeline:** Computes a `git diff`, pushes across encrypted **Tailscale (WireGuard)** to a home Apple Silicon or Ryzen workstation, cross-compiles in 10 seconds inside Docker ARM64, and SCPs the stripped binary back to SolarDeck.
* **Energy Impact:** Burns **180 Joules** on SolarDeck vs **18,000 Joules** locally—a **100× power saving** that eliminates fanless thermal throttling in direct sunlight. Mosh ensures terminal connections survive spotty cell coverage indefinitely.

---

## Pillar 11: Campervan E-Ink Dual-Screen Dock, Blackout Beacon & Field Digitizer

*Written 2026-10-19 14:20 UTC in the Pi harness by antigravity/gemini-3.8-flash. Voice content moved to Pillar 7 (2026-10-20).*

### 1. Giant E-Ink Secondary Monitor & Campervan Docking
* **Native Micro-HDMI 4K Silicon Path:** CM4 routes `HDMI0` to a sealed Micro-HDMI port with TPD4E05U06 ESD protection.
* **The 25.3" / 13.3" E-Ink Advantage:** Unlike LCD/OLED monitors that burn 15W–25W continuous backlight power, external E-Ink monitors (Dasung Paperlike 253, Boox Mira Pro 25.3" 3200×1800) consume **0.000W holding power on static text**.
* **Wayland Multi-Head Orchestration:** `solardeck-dockd` automatically binds high-density workspaces 1–8 to the big monitor, pins van telemetry (Victron battery, water tanks, LoRa chat) to the 10.3" internal screen, and locks Wacom stylus input strictly to the internal display.

### 2. Blackout Supercapacitor Emergency SOS Beacon
* **The Zero-Battery Bootstrap:** When the main LiFePO4 battery is completely dead (0.000V) or missing, an onboard **1.0F 3.3V supercapacitor** fed by the front micro-solar strip charges in 12–15 minutes under direct sunlight.
* **150ms Cold Burst:** RP2350 cold-boots, grabs last-known GPS coordinates from RTC NVRAM, transmits a +22 dBm emergency LoRa SOS burst on 915 MHz, and burns an indelible distress placard onto the 10.3" screen. The distress message remains legible forever with **0.000W battery consumption**.

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
│ 3. IMSI Catchers &  │ AT Signaling Watchdog │ Detects forced 2G & cuts radio│
│    Stingray Towers  │ (`solardeck-stingray`)│ power via TPS22918 load gate. │
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 4. BadUSB / Kiosk   │ Physical Analog SPST  │ Mechanically severs D+/D- lines│
│    Juice-Jacking    │ Switch (TS3USB221A)   │ while negotiating 20W PD power│
├─────────────────────┼───────────────────────┼───────────────────────────────┤
│ 5. Evil-Maid Case   │ Optical & Contact Reed│ Triggers RP2350 NMI interrupt;│
│    Disassembly      │ Sensor (`TAMPER_NMI`) │ zeroizes RAM keys in <3 ms.   │
└─────────────────────┴───────────────────────┴───────────────────────────────┘
```

1. **Detached LUKS Header:** Relocating the 16MB LUKS header to the IP67 cold storage vault renders the 2TB NVMe SSD mathematically indistinguishable from factory-unpartitioned random NAND flash.
2. **Dual-PIN Plausible Deniability:** Unlocks an authentic Debian tourist desktop (travel itineraries, photos, recipes) under inspection, keeping tactical volumes invisible.
3. **Hardware USB Isolation:** Physical SPST analog switch breaks high-speed USB data lines ($D+/D-$) to 0.000V during charging at untrusted public stations or border ports.
4. **Active IMSI Catcher Watchdog:** Automatically halts cellular emissions before transmitting IMSI when rogue base stations attempt forced 2G downgrade attacks.
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
4. **Perpetual Solar Mesh Relay:** Operates as a permanent, immortal Meshtastic LoRa packet repeater atop a mountain or campervan roof, forwarding regional emergency communications without needing a battery.
5. **Snap-On MagSafe 7.1W "Solar Armor" Backplate & 2.5m Remote Shade Tether (`SOLAR-ARMOR-V1`):**
   * Snaps via the embedded MagSafe N52 magnetic ring with a 2.0mm convective chimney to dissipate heat, harvesting **7.13W Peak** in direct tropical sun—surpassing the 5.5W full turbo compilation load of the quad-core CM4.
   * **The Remote Shade Tether:** Features an integrated 2.5-meter Kevlar-reinforced flat ribbon cable that unspools from the backplate. The panel sits out on a sunlit boulder or vehicle roof generating 7.1W, while the operator sits comfortably in the cool shade using the 510g tablet with **zero thermal stress on the LiFePO4 battery**. Doubles as an independent 7.1W USB-C solar charger for phones and flashlights.

---

## Pillar 14: Global Travel & Field Biology Sovereign Recon

*Written 2026-10-19 15:50 UTC in the Pi harness by antigravity/gemini-3.8-flash*

Equipping the sovereign traveler and wilderness naturalist with completely offline scientific instruments:

1. **Airgapped Sovereign e-Passport Inspector (`solardeck-epassport`):** Reads ICAO 9303 RFID passport chips via the 13.56 MHz NFC coil, authenticates RSA/ECDSA digital signatures against the Machine Readable Zone, and archives verified sovereign digital identity clones in cold storage.
2. **Zero-Cloud Camera Sign Translation & Currency Arbitrage (`solardeck-lensworld`):** Offline OCR and neural translation for non-Latin scripts (Arabic, Cyrillic, Asian scripts) plus real-time currency conversion based on historical forex and purchasing-power parity tables.
3. **Consular & Geopolitical Evacuation Navigator (`solardeck-evacd`):** Offline 195-nation database of embassies, Level-1 trauma centers, and paved airstrips, displaying high-contrast great-circle evacuation vectors during regional unrest or telecommunications collapse.
4. **Macro Parasite & Tick Morphology Triage (`solardeck-parasited`):** 12MP macro camera analysis distinguishes Lyme-carrying blacklegged deer ticks from dog ticks and brown recluse from wolf spiders, providing immediate bite triage.
5. **Galvanic Soil pH & Agricultural Profiler (`solardeck-soild`):** Dual tent-stake probes measure soil galvanic potential and conductivity, calculating pH (3.5–9.0) and moisture for survival agriculture and heavy-metal contamination screening.
6. **Timber Fuel Energy & Bow-Drill Firecraft Oracle (`solardeck-timberd`):** Evaluates tree bark and leaf morphology to identify wood BTU density, wet-splitting characteristics, and friction fire spindle/hearth combinations.
7. **Microscopic Waterborne Pathogen Lens Guide (`solardeck-microbed`):** Magnetic $5 100x smartphone lens over the 12MP camera evaluates water droplets on-screen to identify *Giardia*, *Cryptosporidium*, and toxic cyanobacteria.

---

## Verification & Acceptance Gate (The North Star Metrics)

Before any prototype PCBA or firmware build is declared ready for field release, it must be benchmarked against these twelve non-negotiable gates:

| # | Metric | Target Threshold | Method of Verification |
| :--- | :--- | :--- | :--- |
| **G1** | S2idle to Active Keystroke Response | **< 350 milliseconds** | High-speed 240 FPS camera recording key strike to display glyph. |
| **G2** | 1-Bit Fast-Typing Latency | **< 20 milliseconds** | Oscilloscope measuring key switch closure to IT8951 pin toggle. |
| **G3** | Zen Reading Power Consumption | **< 5.0 milliwatts** | TI INA3221 telemetry / Keithley precision source meter at VBAT. |
| **G4** | Ambient Indoor Solar Sustainability | **Positive Net Energy** | Lux chamber @ 500 lux; verify battery charge current $> 0\text{ }\mu\text{A}$. |
| **G5** | Airgap RF Radiation | **0.000 dBm (Noise Floor)** | Rohde & Schwarz / HackRF sweep in anechoic chamber across 50MHz–6GHz. |
| **G6** | Zero-Brick Watchdog Auto-Rollback | **< 2.5 milliseconds** | Fault injected into Bank B; verify hardware WDT fallback to Golden Image. |
| **G7** | Transit Drop Survival | **1.22 m, 26 orientations, functional** | MIL-STD-810H 516.8 procedure IV; corner drops first (cell retention, corner bond). |
| **G8** | Thermal-Cycle Joint Integrity | **500 cycles −40…+85 °C, ΔR < 10%** | Per-package joint resistance sampled before/after; proves the DSBGA corner bond (§7.6). |
| **G9** | UV & Weather Durability | **ASTM G154 1000 h, ΔE < 3, no crazing** | Quartz-xenon chamber on PA12 + anodised samples; colour SKU degrades faster by design. |
| **G10** | Unpowered Storage Survival | **12 months, boots, OS volumes intact** | Powered off at 50% SOC, 30 °C; validates the NAND scrub policy against real retention loss. |
| **G11** | USB-C interoperability: 10-row matrix incl. dead-battery Rd and charge-only-cable diagnostic | Every row passes on the dev kit | `USB_ROBUSTNESS.md` §3 |
| **G12** | Sleep-ladder energy & resume integrity: R2 S2idle ≈15 mW floor / ≤0.3 s resume; R3 disk-hibernate 0.000 W idle; R4 deep-off keep-alive <0.2 mW via Li-primary; resumed sessions pass a post-wake integrity check | All rungs measured on the dev kit; hibernation image survives 30-day cold storage (§54 scrub) | `SOFTWARE_SPEC.md` §3.3.3, `HARDWARE_SPEC.md` §2.30 |

---

*This document serves as the permanent architectural North Star for all SolarDeck hardware, firmware, and software development.*
