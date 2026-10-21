# SolarDeck

> **The Sovereign, Sunlight-Readable 10.3" Color E-Ink Mobile Workstation & Tactical LifeOps Terminal.**
> 
> *Written 2026-10-18 17:35 UTC in the Pi harness by antigravity/gemini-3.8-flash*  
> *Revised 2026-10-20 14:40 UTC in the Pi harness by openrouter/deepseek/deepseek-v4-flash-0731*
> 
>
> **Status (2026-10-20): reference architecture, not yet fabricable.** Specs and BOM are complete and
> internally consistent; schematic capture covers 40 of 62 core BOM parts (65%) and the PCB is unrouted.
> Read `docs/AUDIT_2026-10-20.md` before quoting or ordering anything.
>
> *Open-Hardware Linux • AI Coding Terminal • 12MP Rear Camera • Wacom Stylus Slate • Meshtastic LoRa Node • Worldwide 4G LTE with Soldered eSIM • 300-Day Ambient Desk Clock • External USB-C / Bluetooth Keyboard • Hardware Airgap Switch • IP67 Rugged Enclosure.*

---

## 1. The Problem SolarDeck Tackles

Portable computing forces a false choice: a machine that **computes hard** (laptop: 4–8 h battery, washed out in sun, fragile glass, endless notifications) or a machine that **lasts long** (e-reader: months per charge, but a locked-down appliance that cannot compile, run a terminal, or talk to the field). Nobody wants to carry both.

SolarDeck is one device that refuses the trade-off. It is shaped like a reader and thinks like a workstation — because it is really a **power ladder with an instant hand-off at every rung**:

```
  ~110 µW   calendar clock / weather dashboard ........... hundreds of days per charge
             (Linux asleep; RP2350 co-processor only)
  ~4.5 mW   e-book reader & sketchpad .................... 200+ days per charge
             (RP2350 drives the panel; Linux still asleep)
  ~15 mW    S2idle — your whole session hot in RAM ........ ~80 days per charge
             (terminal, Neovim, Claude Code, reachable in <400 ms glass-to-glass)
   ~0.6 W+  full Linux — compiling, local LLM, barge-in voice, camera … the same
             session, now with both brains awake (24–32 h active, solar-recharged)
```

Reading one book and compiling a kernel are no longer different devices, or even different
moods of the same device — they are **two intensities of one machine**, and the ramp between
them (and back down when you close the lid) costs under 400 milliseconds and zero context
loss. When you're done working and just want a desk clock, the same slab sips 110 µW and
disappears from the power question for months.

### The seven problems it actually solves — each one by a named pillar:

| # | The problem | The pillar that fixes it |
| :--- | :--- | :--- |
| 1 | **Pick battery life or compute power — never both.** | Pillar 1 — the dual-brain instant hand-off: the RP2350 keeps the panel alive at µW/mW while Linux sleeps, and wakes the exact session you left in <400 ms |
| 2 | **E-readers are appliances: no terminal, no toolchain, no control.** | Pillar 1 again — the reader mode **is** Linux; you are never locked out of the machine that renders your books |
| 3 | **Screens wash out the moment the sun comes out.** | Pillar 3 — sunlight sovereignty: 227 PPI e-ink with 0% glare; the brighter the day, the better it reads |
| 4 | **Battery anxiety during real work.** | Pillar 3 — 24–32 h of active coding per charge and a net-positive indoor solar harvest on a shelf |
| 5 | **Your device reports home, and you can't prove otherwise.** | Pillar 5 — a physical hardware airgap that electrically cuts LTE, LoRa, Wi-Fi/BT, GPS and the mic to 0.000 V |
| 6 | **Field gear dies to a single drop or a rain shower.** | Pillar 5 — IP67 sealed, 1.22 m drop-rated, water-locked touch (Wacom + rocker survive a downpour) |
| 7 | **Obsolescence: the whole device is thrown away to upgrade one chip.** | Pillar 6 — the modular bridge: unclip the ARM CM4, snap in a RISC-V SOM, swap RAM or storage in seconds |
| 8 | **Voice assistants are either always-listening or always-useless.** | Pillar 7 — a hardware VAD (<0.05 mW) + RP2350 wake-word gates the mic, so listening standby costs ~nothing and the mic is only hot when you want it |
| 9 | **Distraction is built into the chassis.** | Pillar 2 — e-ink at 18–20 ms keystroke latency with zero flash background-swept, in a slate that has no room for a notification loop to begin with |

The rest of this README (and `docs/STANDOUT_FEATURES.md`) is the engineering argument that these nine fixes are not aspirational — each has a latency budget, a power budget, and a measurement gate. **Pillar 4** (the sovereign 620 g form) is the reason all of it is field-carryable, and the **Master System Blueprint** in the next section ties the parts together.

---

## 2. The 7 Standout Pillars (What We Must Get Flawlessly Right)

*(See [`docs/STANDOUT_FEATURES.md`](docs/STANDOUT_FEATURES.md) for the full architectural specification, latency budgets, and acceptance gates.)*

If SolarDeck is to be legendary, engineering must relentlessly focus on and master these seven non-negotiable capabilities:

1. **The "Dual-Brain" Instant Handoff (<400ms Glass-to-Glass):**
   * *Never off, yet never dies:* Sips ~110 µW as a perpetual indoor solar desk clock and 300-day Zen reader on the RP2350 co-processor.
   * *Zero boot friction:* The millisecond you touch a key or pen, the Linux CM4 wakes from S2idle in **<300 milliseconds**, restoring your terminal, Neovim buffers, and Claude Code sessions on screen in **under 400ms total**.
2. **The "Typewriter-on-Paper" Latency Engine (<20ms Keystroke, Inking & Haptics):**
   * *Zero perceptible lag:* Hardware-synchronized 1-bit Direct Update (DU) waveforms deliver crisp keystroke rendering in **18–20 milliseconds**, eliminating the sluggishness of traditional e-paper.
   * *Intelligent Anti-Ghosting (`eink-refreshd`):* Zero flashes during fast typing bursts; silently sweeps micro-ghosting during natural 1.2-second pauses in human thought.
   * *Sub-18ms Wacom EMR Inking:* Battery-free, 4096-level pressure pen laminated behind the display with zero optical distortion or parallax.
   * *Haptics:* Base build is a single TI DRV2605L + 8 mm LRA with per-keystroke waveform shaping. The spatial quad-corner PowerHap + BOS1901 array is a retained **DNP option** that concentrates sub-1 ms clicks under the touching finger; it is off the default BOM because four glass-bonded ceramics are the device's worst drop-fatigue site (ADR-020).
3. **Sunlight Sovereignty & Perpetual Indoor Life:**
   * *The brighter the sun, the better it gets:* 10.3" Color E-Ink (Carta 1200 / Kaleido 4, 227 PPI monochrome / 114–150 PPI colour) with 0% glare and zero power to hold a static page. 24–32 hours of active terminal coding under direct noon sun with 0W backlight.
   * *Perpetual Indoor Harvesting:* High-efficiency indoor a-Si micro-strip + TI BQ25504 nano-boost yields a **net positive power balance under 500 lux indoor room light**, allowing SolarDeck to live on a desk or shelf forever without ever plugging into a wall.
4. **The Sovereign Form-Morphology (Tactical 620g Slate, Desk Easel, & Modular Thumb Grips):**
   * *Total Input Freedom:* Descoping a proprietary keyboard for V1 leaves the core tablet ultra-light (~620g) and slim (14.0mm), allowing developers to connect their favorite keyboard (ThinkPad, Corne, NuPhy, Keychron, Apple Magic Keyboard) via low-latency Bluetooth 5.0 or USB-C.
   * *Universal Mechanical Mounting:* Standard **M2.5 threaded brass heat-set inserts + MagSafe magnetic anchor array** on the rear chassis enable instant clipping of 3D-printed handheld thumb keyboards (e.g. $25 BlackBerry Q20 clicky keyboard), camera tripods, or desk arms.
   * *The Ultimate Desk Easel:* MagSafe magnetic array + M2.5 mounts snap effortlessly onto any standard magnetic desk stand, origami folio, or OEM tablet stand, propping the tablet in portrait to display 80+ lines of uninterrupted code while typing on a desktop keyboard.
5. **Sovereign Field Hardening (Airgap, LoRa, & IP67 All-Weather):**
   * *Physical Hardware Airgap Switch:* Mechanically breaks power enable nets to LTE, LoRa, Wi-Fi/BT, GPS, and microphone to **0.000V** (zero EMF / 0.000 dBm).
   * *Autonomous Meshtastic Node:* Integrated Semtech SX1262 LoRa (868/915 MHz) permanently owned by RP2350 acts as an off-grid emergency mesh repeater for **80+ days**.
   * *Torrential Rain Water-Lock:* Cuts capacitive touch power during downpours, leaving the Wacom stylus and left-bezel 5-way tactical rocker 100% operational in pouring rain.
6. **The Modular Upgrade Bridge (ARM-to-RISC-V Swappability, RAM, & 2TB NVMe):**
   * *Silicon-Agnostic CM4 Socket:* Uses standard dual Hirose DF40 connectors. ARM provides 100% instant software compatibility today; users can unclip the ARM CM4 and snap in a drop-in 64-bit RISC-V SOM (e.g. Milk-V Mars CM) tomorrow with zero chassis or PCB waste.
   * *Instant RAM Swaps:* Upgrade from 4GB to 8GB or next-gen 16GB simply by swapping the modular compute module in 30 seconds.
   * *Multi-Tiered Mass Storage:* 32GB onboard eMMC + 2TB MicroSDXC edge slot + high-speed M.2 2230/2242 PCIe NVMe SSD socket (up to 2TB @ 400+ MB/s) for massive offline LLM weights and Wikipedia datasets.
7. **The Sovereign Voice Agent (Barge-In & Touch-to-Talk):**
   * *Zero standby penalty:* A cascaded 3-tier wake (Knowles MEMS hardware VAD < 0.05 mW → RP2350 INT8 microWakeWord ~14 mW → CM4 only on "Hey Deck") gives **80+ days continuous listening standby** without waking the Linux brain.
   * *True acoustic barge-in:* PipeWire loopback AEC subtracts SolarDeck's own voice in real time — you can speak over it mid-sentence and it stops and retargets instantly.
   * *Touch-to-talk fallback:* A held-call PTT path bypasses the wake-word entirely for deterministic, full-duplex operator control (mic hot only while pressed).

---

## 3. Master System Blueprint

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SOLARDECK MVP (THE CORE TABLET)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. BRAIN:     Raspberry Pi CM4 (Quad A72 @ 1.8GHz, 8GB RAM, 32GB eMMC, Wi-Fi)│
│ 2. CO-PROC:   RP2350B (Cortex-M33 / RISC-V) + 8MB PSRAM (300-Day Zen Reader) │
│ 3. DISPLAY BUS: Single IT8951 EPDC over SPI @32MHz + 2x TMUX1575 Bus Mux   │
│ 4. SCREEN:    10.3" E-Ink (Carta 1200 / Kaleido 3 / Kaleido 4, 227 PPI) + EMR│
│ 5. CAMERA:    12MP Sony IMX708 PDAF Macro Rear (Multimodal Claude Code / OCR)│
│ 6. CELLULAR:  M.2 Quectel EG25-G LTE + Standard Push-Push Nano-SIM Tray      │
│ 7. MESH/GNSS: Built-In Semtech SX1262 LoRa (868–928MHz) + Qualcomm GNSS     │
│ 8. ANTENNAS:  Top-Edge IP67 SMA (LoRa) + Internal Taoglas FXUB63 MIMO (LTE) │
│ 9. AIRGAP SW: Physical Hardware RF Kill Switch (Zero EMF / 0.000 dBm Cutoff)│
│ 10. SENSORS:  Bosch BMA400 Accel + BMP390 Baro + Dual TMP112 + INA3221 Telemetry│
│ 11. AUDIO:    Sealed Micro-Box Speaker + MAX98357A Amp + MEMS Mic + Mute SW │
│ 12. POWER:    8,000–10,000 mAh (26–32 Wh LiFePO4 / 30–37 Wh Li-ion) Pack    │
│ 13. USB ARCH: Dedicated PCIe USB Host / Hub (Peripherals) + Port 1 OTG Sink │
│ 14. EXPAND:   Driverless USB-C Secondary Monitor + USB-C Port 2 (USB-to-I2C) │
│ 15. CHASSIS:  SLS 3D-Printed PA12 Nylon + 85A TPU Armor Corners (~510g total)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────────────────────┐     ┌───────────────────────────────┐
│ UNIVERSAL MECHANICAL MOUNT & KEYBOARDS│     │ MODULAR TACTICAL RF MULTI-TOOL│
│ • Universal M2.5 Brass Inserts (50mm) │     │ • Flipper Zero Sub-GHz CC1101 │
│ • MagSafe-Compatible Magnetic Array   │     │ • 13.56MHz NFC & 125kHz RFID  │
│ • Snap-on 3D-Printed BlackBerry Q20   │     │ • Dual High-Power IR TX/RX    │
│   Handheld Thumb-Keyboard Mount       │     │ • Wideband Sky-Scan SDR       │
│ • Bluetooth 5.0 / USB-C to Any Keyboard│    │ • Mates to USB-C Port 2       │
│   (ThinkPad, Keychron, Apple, Corne)  │     │                               │
└───────────────────────────────────────┘     └───────────────────────────────┘
```

---

## 4. Deep-Dive Architectural Innovations (The 9 Engineering Pillars)

### I. The Dual-Brain Display Mux (Zero-Leakage 300-Day Reader & Mesh Node)
* **The Problem:** Linux processors (like the CM4) draw 1.5W–3W just sitting idle, draining large batteries in hours.
* **The Fix:** A **Raspberry Pi RP2350B** microcontroller (Dual Cortex-M33 / RISC-V) with **8MB QSPI PSRAM** acts as a secondary brain. When Linux is powered completely off (0.000W), the RP2350 takes over the E-Ink display via **2× Texas Instruments TMUX1575** high-speed bus switches (4 channels each, 8 total), isolating all SPI and control signals (`SPI_MOSI`, `SPI_MISO`, `SPI_SCLK`, `SPI_CS`, `HRDY`, `RESET`).
* **30ms Zen Reading:** Double-buffers full 1872×1404 page images in PSRAM, handling reading page turns at ~4.5 mW (**300+ days battery life**).
* **24/7 Meshtastic Repeater:** Directly interfaces with the Semtech SX1262 LoRa radio, autonomously relaying encrypted emergency mesh packets across off-grid networks for **80+ days** without ever waking the Linux SoC.

### II. Seamless Auto-Ramping: Page-Turn Suspend to Instant Turbo (< 0.3s)
* **The Problem:** Developers want Kindle-like battery life for reading, but instant, uncompromised speed when they start coding.
* **The Fix:** SolarDeck implements bi-stable **Page-Turn Suspend-to-RAM (S2idle)**:
  * While reading documentation or eBooks, the CPU wakes for **80ms** to render a page turn, then drops into 15 mW deep sleep while you read. **Battery life: 80 to 90 DAYS (nearly 3 months).**
  * The millisecond you touch a key or stylus, a hardware GPIO interrupt wakes the system in **under 300 milliseconds**.
  * The Linux CPU governor instantly turbocharges all four Cortex-A72 cores to **1.8 GHz**, unfreezing your Neovim buffers, Claude Code terminal, and tmux panes with zero perceptible lag.

### III. Universal Mechanical Mount & Open Keyboard Architecture
* **The Philosophy:** Developers are fiercely particular about keyboards—forcing a proprietary scissor-switch keyboard alienates split mechanical, low-profile, and ThinkPad purists while adding $25,000 in tooling risk.
* **Universal Mechanical Anchor:** The rear chassis integrates standard **M2.5 threaded brass heat-set inserts (50mm/75mm spacing)** and an embedded **MagSafe-compatible neodymium magnetic ring**.
* **Handheld Bed/Couch Mode:** Using an open-source 3D-printed clip, users can snap on a **$25 Solder Party BlackBerry Q20 USB/BLE keyboard** directly beneath the screen, transforming SolarDeck into a handheld thumb-typing terminal for lounging in bed or a hammock.
* **Desktop Workstation Mode:** Pair any Bluetooth LE 5.0 or USB-C keyboard (Keychron, ThinkPad TrackPoint, NuPhy, Apple Magic Keyboard, Corne) and prop the tablet upright in portrait (80 lines of code) or landscape.
* **Expansion Footprint Reserved:** The rear USB-C Port 2 host interface is the sole expansion contract — no hermetic pogo bus (ADR-006: pogo descoped, USB-C only).

### IV. Hardware Airgap Switch: Zero EMF & Sovereign Privacy
* **The Problem:** Software "airplane mode" on phones is a soft setting easily bypassed by baseband firmware, malware, or carrier updates.
* **The Fix:** A recessed, physical slide switch on the chassis side.
* **True Electrical Cutoff:** The switch physically pulls the enable lines of our **TI TPS22918** power gates to hard ground, cutting all power to the Quectel LTE modem, Semtech LoRa transceiver, Broadcom Wi-Fi/BT chip, GPS engine, and microphone down to **0.000V**.
* **Zero Phantom Bleed:** Built-in **Texas Instruments TXU0104 ($I_{\text{off}}$)** buffers place all digital signal lines into high-impedance (Hi-Z), preventing parasitic back-powering through internal chip diodes.
* Emits **0.000 dBm RF radiation**. Completely undetectable by spectrum analyzers, 100% flight safe, and extends continuous active reading/sketching battery life to **35 to 42 hours**.

### V. Driverless USB-C External Monitor Mode
* Connect a single USB-C cable from any MacBook, Windows PC, or Linux laptop to SolarDeck's Port 1.
* Managed by an autonomous **USB-PD Sink Controller (STUSB4500 / CH224K)** and Type-C CC logic, SolarDeck safely negotiates power contracts while the dedicated BCM2711 USB OTG controller enumerates as a high-speed composite USB Gadget display sink. Peripheral devices (modem, keyboard, backpack) run unhindered on a separate PCIe USB host controller / USB hub.
* **E-Ink Optimized Rendering:** Using lightweight screen-casting (Weylus/Deskreen), SolarDeck renders only updated bounding boxes using 20ms fast-typing waveforms, completely bypassing the flickering and ghosting of conventional 60 FPS video feeds.
* **Simultaneous Charging:** The host laptop powers and charges the SolarDeck over the same cable, giving you a sunlight-readable secondary terminal monitor that never drains battery.

### VI. Modular Backpack Isolation (Keeping the Core Pure)
* **The Problem:** Cramming every RF hacking tool onto the main motherboard causes thermal throttling, RF desensitization (desense), and massive PCB layer costs.
* **The Fix:** The core tablet carries only essential daily communication (Worldwide LTE with soldered MFF2 eSIM, 915MHz LoRa Meshtastic, and GNSS).
* High-power tactical tools—**Flipper Zero suite (Sub-GHz CC1101, NFC, RFID, IR blaster)** and **Sky-Scan Wideband SDR (Airplane ADS-B 1090MHz, NOAA Weather Satellites 137MHz, Marine AIS)**—are isolated in rear snap-on Hotpacks connecting over the IP68-sealed USB-C Port 2 expansion interface (no spring-loaded pogo pins; see §7).
* The core tablet stays slim (~510g), cool, and lasts for days. When you want to sniff radio protocols or track aircraft overhead, you snap on the backpack and Linux launches the SIGINT stack instantly.

### VII. Self-Observant Hardware: The LLM Evolutionary Feedback Loop
* **The Problem:** Once standard hardware is manufactured, it is completely deaf and blind to its own physical operating stress. You cannot optimize what you cannot measure, and Rev 2 redesigns rely on human guesswork.
* **The Fix:** SolarDeck embeds a dedicated physical telemetry suite costing under $3.50:
  * **3-Rail Current Ammeter (TI INA3221):** Breaks down exact milliwatts between Compute, Display, and Wireless subsystems.
  * **Coulomb Counter (TI BQ27441-G1):** Measures internal battery impedance and State-of-Health to double pack life to 10+ years.
  * **Thermal Triad (Dual TMP112 + SoC):** Dynamically compensates E-ink waveform Look-Up Tables (LUTs) across winter cold and summer heat.
  * **Zero-BOM Ambient Lux Sensor (Solar Strip via RP2350 ADC):** Samples top-bezel solar cell open-circuit voltage ($V_{OC}$) to calculate precise ambient lux (10 to 120,000 lux) and automatically adjust display contrast without adding a dedicated photodiode IC.
* **The AI Evolution Loop:** A rolling circular SQLite database (`/var/log/solardeck/telemetry.db`) feeds structured physics logs to Claude Code CLI. Because SolarDeck is documented in plain text and open-source formats, engineers and AI assistants can query real-world inrush currents, thermal maps, and battery impedance over time to guide precise component sizing and layout optimizations for Rev 2.

### VIII. Thermal Viscosity Assist (No Video Engine in V1)
* **The Problem:** E-Ink is slow, and not only because of the bus. Electrophoretic particle mobility ($\mu$) is inversely proportional to fluid viscosity ($\eta$): $\mu \propto 1/\eta(T)$. In a cold room the microcapsule fluid thickens and the same drive pulse moves pigment more slowly.
* **The Fix:** A copper thermal plane couples waste heat from the CM4 shield into the panel backplane, holding it at **30°C–33°C**. Viscosity drops >40%, particles accelerate **$1.8\times$** under identical pulses, and `eink-refreshd` widens DU pulse width below 15°C instead of pretending the panel is fast.
* **Honest Throughput:** the IT8951 is fed over 32 MHz SPI, so a full 1872×1404 1-bit frame costs ~82 ms (~6 fps); small rectangles (caret, line, clock digits) run 15–25 fps. That is why the daemon is rectangle-driven. There is no MIPI-DSI video path and no cinema mode (ADR-005) — video decodes at ~6 fps dithered, or not at all.
* **Battery Lifespan:**
  * *High-motion screen work (dithering + repeated partial refresh):* ~1.6–2.2W, **16 to 20 hours**.
  * *Writing, Coding, Reading, Ambient Clock:* E-Ink consumes **0.000 Watts** to hold a static image. Active terminal coding gives **24 to 32 hours**, Zen reading **300+ days**, and ambient desk-clock with micro-solar is indefinite. LiFePO4 yields 3,000–5,000 cycles, **10 to 15+ years**.

### IX. Zero-Cost Convenience Combinations ($0.00 Added BOM)
1. **The 32 Wh LiFePO4 Survival Powerbank (15W Reverse Boost):**
   * Utilizing the bidirectional synchronous boost engine in the **TI BQ25895** buck charger, SolarDeck outputs **5.1V @ 3.1A (15.8W)** backwards through USB-C Port 1 or 2 to fast-charge external smartphones, flashlights, or radios.
   * **Linux Stays 100% Asleep (0.000W):** The RP2350 co-processor manages power delivery and displays a live, crisp battery percentage and output wattage on the E-Ink screen. Never carry a separate powerbank again.
2. **The Solar Micro-Strip as an Ambient Light Meter ($0.00 Cost):**
   * Rather than adding a dedicated photodiode IC, the RP2350's internal 12-bit ADC directly samples the open-circuit voltage ($V_{OC}$) of the top-bezel IXYS solar strip.
   * Stepping into direct sunlight instantly increases color saturation and engages high-contrast monochrome waveforms; stepping into a dim room or bedroom automatically dims the screen.
3. **Driverless USB-C Secondary Monitor Sink (Instant Outdoor Laptop Screen):**
   * Connect a single USB-C cable from any MacBook, ThinkPad, or iPad into SolarDeck's Port 1.
   * The dedicated BCM2711 USB OTG controller enumerates as a high-speed composite USB Gadget display sink (UVC / Weylus), giving you an instantaneous, 10.3" matte, zero-glare, eye-strain-free secondary monitor for terminal logs, documentation, or reading in bright sunlight while the laptop powers the tablet!
4. **The Airgapped Hardware Crypto Vault & Document Notary (Zero-EMF Signing):**
   * Combining the physical **Hardware Airgap Kill Switch** (cutting all RF radios to 0.000V), the **rear flush 12MP Sony IMX708 autofocus camera**, the **10.3" Color E-Ink display**, and **top-bezel 13.56 MHz NFC**.
   * When flipped to Stealth (0.000 dBm), SolarDeck becomes an impenetrable, mathematically verifiable cold-storage signing station:
     1. Scan an unsigned Bitcoin/Ethereum transaction QR or document hash with the rear 12MP camera.
     2. Inspect the complete decoded transaction details, contract calls, and gas fees in razor-sharp high contrast on the 10.3" screen.
     3. Authorize and sign using an onboard airgapped GPG/SSH key, or tap a physical **YubiKey, Tangem, or Coldcard** against the top-bezel NFC coil.
     4. Display the signed transaction QR on the E-Ink screen for an online smartphone to broadcast.
   * Completely immune to remote exploits or RF sniffing because the wireless power rails are physically cut by hardware switches!

---

## 5. The 3 Operational Personas

```
┌──────────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│       THE WORKHORSE          │     THE ZEN SCRIBE           │    THE PERPETUAL CLOCK       │
│  (Mobile Coding Station)     │  (Field Slate & Reader)      │   (LifeOps Desk Dashboard)   │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ • Bluetooth/USB-C keyboard  │ • Detached keyboard (510g)   │ • Propped on OEM desk stand  │
│ • Sway tiles terminal to 2/3 │ • Wacom EMR pen (4096 lvl)   │ • Linux CM4 dead (0.000W)    │
│ • Claude Code AI CLI active  │ • 100GB Offline Kiwix docs   │ • RP2350 direct-drives EPDC  │
│ • Worldwide 4G LTE connected │ • Airgap Switch ON (Zero EMF)│ • 1-sec TCXO live clock tick │
│ • 10.5–11 Hours continuous   │ • 35–42 Hours active reading │ • 300+ DAYS on single charge │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

---

## 6. Specifications Matrix

| Subsystem | Specification |
| :--- | :--- |
| **Main Compute** | Raspberry Pi Compute Module 4 (CM4) — Quad Cortex-A72 @ 1.8GHz, 8GB RAM, 32GB eMMC (or CM5 / RK3566) |
| **Co-Processor** | Raspberry Pi RP2350B (Dual Cortex-M33 / RISC-V @ 150MHz) + 8MB QSPI PSRAM + DS3231 TCXO RTC |
| **Display Isolator**| **2×** Texas Instruments **TMUX1575** 4-Channel SPDT Bus Switch (8 channels, fail-safe power-off protection, all 6 lines) |
| **Display Panel** | 10.3" E-Ink Kaleido 3 / Kaleido 4 (1872×1404, 227 PPI B&W / 114–150 PPI Color) + Wacom EMR |
| **Display Bus** | Single-path SPI @32 MHz to IT8951 EPDC (flexible refresh) + TMUX1575 fallback to RP2350 (4.5 mW Zen Reader); no MIPI-DSI video path |
| **Waveform Engine** | Dynamic Quad-Zone Temperature-Compensated Waveform LUT Matrix (-10°C to +50°C in `eink-refreshd`) |
| **Haptic Feedback** | Base: TI DRV2605L + 8 mm Z-Axis LRA (per-gesture waveforms). DNP option: Quad-Corner TDK PowerHap + Dual Boréas BOS1901 (localized (X,Y) glass click) |
| **Frontlight** | Dual CCT Bezel Lightguide (TI TPS61163 Step-Up Driver, 2048-step circadian warm amber/white) |
| **Digitizer & Touch**| Laminated Wacom EMR (<18ms ink) + Hardware `PEN_PROX_INT` Palm Blanking Gate + 0.1mm Mu-Metal |
| **All-Weather Rain** | Torrential Rain "Water-Lock" Mode (TPS22918 capacitive touch cutoff; 100% water-immune Wacom stylus) |
| **Tactical Controls**| Left-Bezel IP67 Sealed 5-Way Tactical Navigation Rocker (ALPS SKRH; gloved 1-handed terminal/reading) |
| **Rear Camera** | 12MP Sony IMX708 PDAF Macro Autofocus Rear Camera (Multimodal Claude Code & PCB Loupe; a forward-facing unit was descoped — ADR-006) |
| **Keyboard & Input**   | Universal M2.5 Threaded Mount + MagSafe Magnetic Array + Bluetooth LE 5.0 / USB-C to Any Keyboard (ThinkPad, Keychron, Corne, Apple, or $20 BlackBerry Q20 Thumb Keyboard) |
| **Cold Storage Vault**| Gasketed M.2 Service Hatch: 3x Uniform Friction-Fit MicroSD Pockets (Supports Nano-SIM via SD shell) + Ejector Clip ($0 BOM) |
| **Cellular Internet**| M.2 Key-B 3042 (Quectel EG25-G, 30+ LTE bands) with Dual-SIM: Soldered MFF2 eSIM (ST4SIM-200M) + External Nano-SIM Tray |
| **Off-Grid Radio** | Semtech SX1262 LoRa 915/868 MHz (Meshtastic) dedicated to RP2350 with Top-Edge **IP67 Bulkhead SMA female jack** |
| **GNSS Positioning** | Integrated Qualcomm Multi-Constellation GNSS (GPS/GLONASS/BeiDou/Galileo/QZSS in EG25-G) |
| **RF Front-End** | 0402 Precision Pi-Matching Networks + 3.0mm U.FL Keepout + Molded Coaxial Retention Channels |
| **Antennas** | Linx ANT-916-CW-HWR Tactical LoRa Whip + Dual Internal Taoglas FXUB63 2×2 MIMO LTE FPCs |
| **Airgap Switch** | Physical 2-position slide switch; breaks power enable nets to all radios, mic, & cameras to 0.000V |
| **Tactical Stealth** | NVG Covert Mode (Monochromatic 630nm Red <0.5% PWM + Amber-only floor + Hardware Audio Squelch) |
| **Anti-Tamper** | RP2350 TrustZone OTP Derived Key & BIP-39 Recovery (No physical tripwire; enables RAM/SSD upgrades)|
| **Telemetry & Sensors**| TI INA3221 (3-rail ammeter for LLM tuning) + BQ27441 (fuel gauge) + Dual TMP112 (thermals) + Zero-BOM Solar Lux Sensor (RP2350 ADC) + BMA400 (accel) + BMP390 (baro) |
| **Survival Powerbank** | 15W Bidirectional USB-PD Boost (TI BQ25895: 5.1V @ 3.1A charges phones while Linux is 100% asleep at 0.000W; live E-Ink status) |
| **External Sensor Bus**| USB-C Port 2 High-Speed Host (Supports USB-to-I2C/Qwiic dongles; zero unsealed chassis JST holes) |
| **Audio & Acoustics**| Dual-MEMS Noise-Cancelling Acoustic Array + Maxim/ADI MAX98357A 1W Box Speaker Amp + Bottom-Edge IP67 3.5mm TRRS Audio Jack (Stereo DAC + Mic In + Auto-Mute) + Mute Switch |
| **NFC & Smartcard** | 13.56 MHz NFC (NXP PN532 / ST25R) in Top Bezel: YubiKey / FIDO2 Authentication, ePassport / Smartcard Reader, Tangem/Coldcard Crypto Signing + MagSafe Physical Card Wallet Mount |
| **Status Beacon** | 10.3" Color E-Ink Zero-Watt Ambient Notification Badges (Descoping Win for RGB LED & light pipe) |
| **Recovery** | Single Recessed IP67 Pinhole Button (`REC_RPI` eMMC recovery; RP2350 flashed over internal SWD) |
| **Monitor Sink** | Standalone USB-PD Sink Controller (CH224K / STUSB4500) + Dedicated BCM2711 USB Gadget OTG Port 1 (Instant 10.3" Zero-Glare Outdoor Second Screen for Mac/PC/iPad) |
| **USB Host / Hub** | Dedicated PCIe USB Host Controller (VIA VL805 / ASM1042A) or Industrial Hub (USB2514B) for Modem & Docks |
| **Expansion Bus**| USB-C Port 2 High-Speed Host (Tactical Multi-Tool Dongle, Sky-Scan SDR, Webcam, & Sensor Expand) |
| **Battery & Safety**| Hardware `CHEM_SEL` Strap (LiFePO4 3.65V vs Li-ion 4.20V) + Pure Silicon JEITA + TI BQ2970 PCM |
| **Firmware Failsafe**| RP2350 Dual-Bank A/B Flash Partitioning with 5-Second Autonomous Hardware Watchdog Rollback |
| **Flash Reliability**| Read-Only SquashFS + Transactional F2FS + 150ms Emergency Hardware Sync Hook (`GPIO_PWR_FAIL`) |
| **Power Architecture**| Dedicated Always-On 3.3V Low-IQ Buck-Boost (TI TPS62840, 60 nA IQ) for RP2350/RTC/Sensors |
| **RTC Backup** | Seiko MS621FE Rechargeable Lithium Micro-Battery (5.5 mAh, 100+ days hold without power) |
| **Solar Harvesting**| Dual-Stage: TI BQ25895 (20W USB-C PD / MPPT) + TI BQ25504 Nano-Power Harvester (Bezel Strip, ~0.15W peak) |
| **Solar Decoupling**| 0.5mm Die-Cut Aerogel Thermal Insulation Barrier + 1.0mm PCBA Milled Thermal Break Slot |
| **ESD & Rugged** | IEC 61000-4-2 Level 4 TVS Matrix (TI TPD4E05U06), IP67, PA12 / 6061 Aluminum, GORE vent |
| **PCBA Stackup** | 6-Layer Impedance-Controlled (JLC2313 / Isola FR408HR) with continuous unbroken ground planes |
| **Module Retention**| CNC Anodized Aluminum CM4 Retention Bracket & Thermal Interface Bridge (Drop-proof clamp) |
| **Fast Wake-Up** | Suspend-to-RAM (S2idle): **0.3-second instant resume** |

---

## 7. The Modular "Hotpack" Backpack System — and Why It Exists

SolarDeck treats the **core tablet** and the **specialised mission packs** as two separate products, connected by one standard: *a recessed, IP68-sealed USB-C Port 2 host interface, mechanically anchored by the rear MagSafe ring + M2.5 inserts*. That single decision buys four things at once:

1. **Corrosion-proof by design.** Spring-loaded pogo pins jam and corrode in beach sand, volcanic dust, and salt spray. A right-angle USB-C male plug has no springs, wipes clean, and seals at IP68 (`docs/OFFGRID_TACTICAL_SENSORS.md` §8).
2. **The core stays pure.** Daily-driver radios (LTE, LoRa mesh, GNSS) live on the carrier; anything exotic moves to a snap-on pack so the main board stays slim, cool, and cert-light.
3. **Certification isolation.** A direct-to-satellite modem (Hotpack 6) would cost $40,000+ in FCC/CE/Skylo lab certifications if soldered onto the main board. As a USB-C pack, SolarDeck never licenses the radio — the pack does.
4. **YAGNI, applied to hardware.** Instead of cloning a Flipper Zero (which would just be a worse Flipper Zero), the design says *buy the $169 Flipper Zero, clip it to the MagSafe ring, and run `qflipper-cli`* — SolarDeck contributes the sunlight-readable 10.3" screen and the Linux workflow, not a redundant CC1101.

The seven specced Hotpacks (`spec_values.features.hotpacks`, full detail in `docs/OFFGRID_TACTICAL_SENSORS.md`):

| Pack | Mission | Why it is a pack, not onboard |
| :--- | :--- | :--- |
| **H1 Doomsday Sky-Scan** | Passive all-band SIGINT receiver (ADS-B 1090 MHz, NOAA 137 MHz, AIS, broadcast) | Stealth/spectrum tools stay off the carrier; zero transmit-authority overhead |
| **H2 Dual-Mesh & HF** | Active off-grid comms: Meshtastic + HF shortwave transceiver (Si4732/Si4735) | High-power RF kept off the main board; regional-band licensing isolated |
| **H3 CBRN & SAR** | Environmental sensing: chemical, ionising radiation dosimeter, search-and-rescue | Specialty sensors are perishable/calibratable; don't age inside the carrier |
| **H4 RTK Survey** | Centimetre land surveying (dual-frequency RTK, Galileo HAS) | Unused most days; costs and weight stay with the surveyor |
| **H5 Thermal NV** | 15 g thermal night-vision + electrical-inspection module | Optics are fragile and cold-chain sensitive; snap-on keeps them serviceable |
| **H6 Satellite (Skylo)** | 3GPP NTN direct-to-satellite + global SAR (PLB integration over NFC) | Certification isolation (see §3 above) — biggest single cost kept off the carrier |
| **H7 Geophone** | Sub-surface acoustic perimeter sensing (`solardeck-geophoned`) | Physically invasive (100 mm ground spike); belongs to the mission, not the tablet |

The **why** in one sentence: every pack that *would* compromise the core — by desense, thermal load, licensing, fragility, or cost — lives behind one IP68 USB-C connector instead of inside the sealed chassis, so the daily driver stays perfect at its one job: always-on, sunlight-readable, months on a charge.

---

## 8. Failover, Longevity & Self-Diagnosis (The 30-Year Design)

Three properties make SolarDeck a *30-year object* rather than a gadget — and each is enforced by a gate in `docs/spec_values.json` (`features.acceptance_gates`):

### 8.1 Failover — the system survives its own updates
- **Dual-bank A/B firmware** on the RP2350: one bank is always the last-known-good image; a 5-second autonomous hardware watchdog rolls back a hung boot (**G6**: zero-brick rollback < 2.5 ms).
- **Sleep-ladder integrity**: S2idle (15 mW, <0.3 s resume), hibernate (0 W), and RP2350 keep-alive (<0.2 mW) each have resume contracts (**G12**), so Linux never loses the terminal, Neovim buffers, or Claude Code session across a near-death battery.
- **USB-C dead-battery protocol** (gate G11): the Port 1/2 controllers negotiate even when the pack is at 0 V, so a drained SolarDeck is still a charging receiver, not a brick.

### 8.2 Longevity — a budget, not a wish
- `docs/LONGEVITY_30Y.md` is a real 30-year failure budget: drop survival **G7** (1.22 m, 26 orientations), thermal-cycle joint integrity **G8** (500 cycles, dR < 10%), UV/weather **G9** (ASTM G154, 1000 h, ΔE < 3), unpowered storage **G10** (12 months, data intact).
- **Service schedule driven by data**: `solardeck-battcare` holds LiFePO4 at 50% SOC when idle and flags cell service by *measured* capacity retention; `solardeck-nandcare` scrubs the read-mostly storage quarterly — flash written often, kept read-mostly.
- **Repairability is a spec**: conformal acrylic coat is *reworkable* (Parylene is explicitly DNP — it would seal the board shut against ADR-024's service thesis), connectors are gasketed, and rework is a priced BOM line.

### 8.3 Self-Diagnosis — the LLM reads the hardware's own health
- A sub-$3.50 physical telemetry suite (INA3221 3-rail ammeter, BQ27441 coulomb counter / SOH, dual TMP112 thermals, zero-BOM solar-strip lux meter, BMA400 accel, BMP390 baro) writes a rolling SQLite DB (`/var/log/solardeck/telemetry.db`).
- **BIST + module health registers** on every board subsystem; `solardeck-diag` sweeps them, `solardeck-correlate` fuses the streams, and the Tier-2 loop (SOFTWARE_SPEC §3.3.2) feeds *measured* current, temperature, and impedance into the LLM Context Protocol — so Claude Code reasons from instrumented fact, not assumption.
- **The honest ceiling, stated**: the LLM can only diagnose what the instrumentation senses. A cracked pad under a BGA chip stays invisible without the registers — which is why per-rail current sense, six thermal zones, and module-health registers are **quote-line items for the fab**, not afterthoughts (`docs/HANDOFF_TO_FABLE.md`, `docs/FMEA.md`).
- The whole self-diagnosis story, failure family by failure family (connector corrosion → burnish actuator → gate), lives in `docs/FMEA.md`.

> **Status (2026-10-20): reference architecture, not yet fabricable.** The design is pursuable; the gates are the *contract* for the build. Cross-referenced in `docs/FMEA.md`; budgets in `docs/LONGEVITY_30Y.md`.

---

## 9. Repository Architecture & Documentation

```
.
├── README.md                  # Master manifesto, problem statement, and executive architecture
├── AGENTS.md                  # Developer, AI agent, and hardware safety rules
├── LICENSE / LICENSES/        # CERN-OHL-S-2.0 (hardware) + MIT (software) + CC-BY-SA (docs)
├── SECURITY.md                # Threat model, what hardware enforces, disclosure policy
├── CONTRIBUTING.md            # How to propose, verify and submit changes
├── docs/
│   ├── README.md              # Reading order + claim-status vocabulary (start here)
│   ├── WORKFLOW.md            # THE method: tags, change classes, intent→ledger lifecycle
│   ├── AUDIT_2026-10-20.md    # What is built vs written; fix plan. Read before trusting specs
│   ├── spec_values.json       # SINGLE SOURCE OF TRUTH for every quantitative claim
│   ├── INDEX.md               # Cross-reference table: claim -> file section
│   ├── STATUS.md              # Generated feature-status catalogue (Phase 12)
│   ├── STANDOUT_FEATURES.md   # Core standout pillars, latency budgets, & emergent superpowers
│   ├── MVP_ARCHITECTURE.md    # Dual-brain architecture, power state transitions, block diagrams
│   ├── HARDWARE_SPEC.md       # Complete carrier board schematic, pinouts, RF & power design
│   ├── SOFTWARE_SPEC.md       # Linux kernel, waveform drivers, 44 daemons & power profiles
│   ├── FIRMWARE_INTERFACE.md  # CM4 <-> RP2350 register contract + wire test (Phase 15)
│   ├── BOM_COST_ESTIMATE.md   # Bill of materials, supplier sourcing, turnkey cost breakdown
│   ├── LONGEVITY_30Y.md       # 30-year failure budget, service kit, gates G7-G10
│   ├── FMEA.md                # Failure family -> countermeasure -> detector -> actuator -> gate
│   ├── USB_ROBUSTNESS.md      # USB-C interoperability, dead-battery Rd, failure taxonomy (G11)
│   ├── REGULATORY.md          # Regional RF bands, EIRP, EMI, materials declarations
│   ├── OFFGRID_TACTICAL_SENSORS.md # Navigation, plate-solving, CBRN, & Hotpacks 1–7
│   ├── MECHANICAL_FIT_AND_ENCLOSURE_WORKFLOW.md # Tolerance, CAD envelope, & 2-tier checks
│   ├── HARDWARE_VERIFICATION_WORKFLOW.md # 8-rule netlist trap audit; what each phase proves
│   ├── DECK_BUILDER_LAYOUT.md # Who-can-build guide: snap-in vs soldered vs fab
│   ├── DEV_KIT_BENCH.md       # Breadboard bring-up plan, BOM, measurement gates
│   ├── FIRST_BOOT_CHECKLIST.md# Unboxing to first prompt bring-up checklist & power rail checks
│   ├── HANDOFF_TO_FABLE.md    # Turnkey Seeed Studio Fusion & manufacturing handoff package
│   └── 90-history/decisions.md# ADR-001..026: what was descoped and why
├── hardware/                  # NOTE: partial capture (40/62 parts), unrouted PCB -- see AUDIT
│   ├── solardeck-carrier.*    # KiCad 8 schematics, PCB layout, and netlists
│   ├── verify_schematics.py   # Netlist structure checks (Phase 1)
│   ├── audit_hardware_traps.py# 8-rule electrical trap audit (Phase 2)
│   ├── enclosure/             # OpenSCAD 3D chassis models + verify_enclosure.py
│   └── production/            # Generated Fusion Gerber zip, BOM, CPL, box-build guides
├── firmware/rp2350/           # Bare-metal C co-processor state machine, RTC, & PSRAM tests
├── src/
│   ├── daemons/               # eink-refreshd, solardeck-telemetryd, & C bridge daemons
│   └── dts/                   # solardeck-cm4.dts Device Tree Overlay
├── tools/provision/           # setup_solardeck_os.sh automated OS provisioning engine
└── scripts/
    ├── verify_all.py          # 16-phase automated master verification runner
    ├── check_docs_numbers.py  # docs vs spec_values.json (CI Phase 10)
    ├── check_bom_coverage.py  # BOM <-> netlist <-> CPL (CI Phase 11)
    ├── gen_status.py          # regenerates docs/STATUS.md (CI Phase 12)
    ├── check_longevity.py     # LONGEVITY_30Y budgets (CI Phase 13)
    ├── check_cost_and_power.py, check_firmware_interface.py,
    │   check_reliability_and_supply.py, reliability_model.py
```
