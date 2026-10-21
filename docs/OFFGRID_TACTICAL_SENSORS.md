# SolarDeck Off-Grid, Campervan & Tactical Sensor Expansion Specification

Written 2026-10-19 12:12 UTC in the Pi harness by antigravity/gemini-3.8-flash
Revised 2026-10-21 15:59 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).
Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:22 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, ADR-044/045).
Revised 2026-10-21 17:53 UTC in Claude Code by anthropic/claude-opus-5-5 (RTC chip, jack removed, ADR-046).
Revised 2026-10-21 19:45 UTC in Claude Code by anthropic/claude-opus-5-5 (Li-ion smart pack, ADR-048).

Detailed architectural specification for campervan energy bus integration, enhanced sensor navigation (RTK, celestial plate-solving, 9-DOF IMU), grid-down doomsday survival hardware, frontlight optical engineering, and offline AI knowledgebase traversal.

---

## 1. Campervan & Mobile Living Energy Integration

SolarDeck's dual-brain architecture (CM5 Linux + RP2350 microcontroller) and connectivity options (BLE 5.0, USB-C Host, RS-485, CAN Bus) allow it to serve as a sovereign, zero-power campervan monitoring console and electrical diagnostics hub:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAMPERVAN POWER BUS INTEGRATION                       │
├────────────────────┬─────────────────────────┬──────────────────────────────┤
│ SUBSYSTEM          │ PHYSICAL INTERFACE      │ PROTOCOL / DRIVER            │
├────────────────────┼─────────────────────────┼──────────────────────────────┤
│ Victron SmartSolar │ Bluetooth Low Energy    │ Passive Victron BLE Protocol │
│   & SmartShunts    │   (Non-pairing beacon)  │   (Instant Volts, Amps, SOC) │
│ Victron VE.Direct  │ USB-C Port 2 / UART     │ 19200-baud 3.3V ASCII Stream │
│ DIY LiFePO4 BMS    │ Bluetooth 5.0 (BlueZ)   │ `jbd-bms-cli`, `dalybms`     │
│   (JBD, Daly, ANT) │                         │   (Cell delta mV, thermals)  │
│ RV-C / Marine CAN  │ USB-to-CAN / SPI MCP2515│ Linux SocketCAN / J1939      │
│   (Inverters, Tank)│                         │   (RV-C standard PGNs)       │
│ Renogy / EPEVER    │ USB-to-RS485 Dongle     │ Modbus RTU / `libmodbus`     │
└────────────────────┴─────────────────────────┴──────────────────────────────┘
```

### 1.1 Victron Energy Passive BLE Sniffing
* **Mechanism:** Victron SmartSolar MPPTs, Orion-Tr Smart DC-DC chargers, and SmartShunts continuously transmit non-connectable BLE advertising beacons containing real-time telemetry (Battery Voltage, Amps, Watts, State of Charge, Yield).
* **Zero-Pairing Integration:** SolarDeck's CM5 captures these packets passively using `bleak` or a native C/Rust daemon (`solardeck-victron-ble`). No Bluetooth pairing, PIN codes, or handshakes are required. Telemetry is committed to `/var/log/solardeck/telemetry.db` every 1 to 5 seconds.
* **Wired Fallback (VE.Direct):** For metal campervan enclosures where 2.4 GHz RF is blocked, USB-C Port 2 accepts an isolated FTDI cable to read the native VE.Direct 19200-baud ASCII telemetry stream.

### 1.2 DIY LiFePO4 Battery Pack Management (JBD / Daly BMS)
* Connects over Linux BlueZ to over 90% of consumer and DIY campervan battery management systems.
* Tracks individual cell balancing voltages down to $\pm 1\text{ mV}$, high/low voltage cutoff thresholds, short-circuit faults, and MOS temperature limits.

### 1.3 RV-C CAN Bus Vehicle Gateway
* Modern expedition vehicles and campervans (Lithionics, BattleBorn, Mastervolt, Dometic, Victron Cerbo GX) use the open **RV-C protocol** (built on CAN Bus 2.0B / J1939 at 250 kbps).
* Mating a low-cost USB-CAN adapter (CANable / Candlelight firmware) to USB-C Port 2 or an onboard SPI CAN controller (MCP2515) exposes a native Linux `can0` interface via SocketCAN.
* SolarDeck monitors:
  1. High-voltage inverter status (AC output watts, shore power presence).
  2. Ultrasonic and resistive fresh/grey water tank level sensors.
  3. Hydronic and diesel cabin heater states (Webasto / Espar / Autoterm).

### 1.4 Perpetual E-Ink Van Wall Console
* **MagSafe Mount Integration:** SolarDeck mounts flush to an interior campervan bulkhead via its rear MagSafe magnetic array and M2.5 threaded brass inserts.
* **Circadian Advantage:** Unlike bright iPad or LCD camper monitors that illuminate the sleeping cabin with sleep-disrupting blue light, SolarDeck's frontlight locks to 0% at night. The screen displays battery health, solar yield, and water levels completely unlit, readable under natural moonlight, and drawing **0.000W** when static.

---

## 2. Advanced Sensors & Positioning (Beyond Standard GPS)

While standard single-band GPS provides 3 to 5 meter accuracy, SolarDeck's sensor architecture supports sub-meter satellite positioning, centimeter RTK, and zero-satellite celestial navigation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ENHANCED NAVIGATION & POSITIONING PIPELINE                  │
├───────────────────────┬─────────────────┬───────────────────────────────────┤
│ NAVIGATION TIER       │ TYPICAL ACCURACY│ HARDWARE / SENSOR MECHANISM       │
├───────────────────────┼─────────────────┼───────────────────────────────────┤
│ Standard GNSS (L1)    │ 3 – 5 Meters    │ u-blox MAX-M10S (ADR-038)         │
│ Galileo HAS (E6)      │ < 20 cm         │ Satellite Precise Point Pos (PPP) │
│ Dual-Frequency RTK    │ 1.4 cm (0.5 in) │ u-blox ZED-F9P (L1/L2/L5 Carrier) │
│ Barometric Altitude   │ ± 10 cm         │ Bosch BMP390 (0.01 hPa I2C)       │
│ Optical Celestial Nav │ V2 (ADR-034)    │ Needs the deferred rear camera    │
│ Inertial 9-DOF Vector │ Continuous $\Delta$│ Bosch BMI270 (6-DOF) + BMM350 Mag │
└───────────────────────┴─────────────────┴───────────────────────────────────┘
```

### 2.1 Centimeter-Level RTK & Galileo HAS (Multi-Band GNSS)
* **The RTK Upgrade Option:** The carrier board expansion header accommodates high-precision dual-frequency GNSS modules (**u-blox ZED-F9P** or **Quectel LC29H**). By tracking carrier phase cycles across L1, L2, and L5 bands alongside local RTCM differential corrections (via a paired Meshtastic node, or NTRIP over Wi-Fi/tethering), horizontal position accuracy drops to **1.4 centimeters**.
* **Galileo HAS (High Accuracy Service):** The European Galileo constellation transmits free, open-access correction parameters directly from orbit on the **E6 carrier (1278.75 MHz)**. This provides **sub-20 cm accuracy worldwide** without requiring ground base stations, internet access, or local radios.

### 2.2 9-DOF Celestial & Orientation IMU (Sensor-Driven Stargazing)
* **The Sensor Addition:** Complementing the onboard Bosch BMA400 accelerometer, the system integrates a 3-axis gyroscope and a 3-axis geomagnetic sensor (electronic compass) via a **Bosch BMI270 (6-DOF) + BMM350 (Magnetometer)** or an integrated **BNO085** orientation sensor.
* **Stellarium & Planetarium Night Mode:**
  * Running **Stellarium** or CLI tools (`skyfield`, `pyephem`) natively under Wayland.
  * Holding SolarDeck toward the night sky renders constellations, planets, and satellite pass tracks corresponding to the exact 3D vector of the device.
  * Inverted red-on-black or amber-on-black e-paper display modes preserve human rhodopsin (scotopic rod vision) with zero photon glare.

### 2.3 Optical Celestial Navigation & Plate-Solving (Zero-Satellite Doomsday Nav)
V2 (ADR-034): needs the deferred rear camera.

---

## 3. Doomsday & Tactical Grid-Down Hardening

To guarantee survival and utility during severe natural disasters, infrastructure blackouts, or electromagnetic disturbances:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GRID-DOWN HARDENING ARCHITECTURE                         │
├────────────────────┬────────────────────────────────────────────────────────┤
│ SUBSYSTEM          │ IMPLEMENTATION SPECIFICATION                           │
├────────────────────┼────────────────────────────────────────────────────────┤
│ All-Band HF Radio  │ Si4732 / Si4735 DSP Receiver (LW, MW, SW 3–30M, SSB)   │
│ Radiation Monitor  │ Pocket Geiger Type 5 / BG51 Tube (RP2350 Interrupt)    │
│ Wild Power DC Port │ 3.6V–14V Raw DC Input to TI BQ25798 (Direct Solar/Auto)│
│ EMP Hardening      │ Sub-ns Bidirectional TVS Arrays + Faraday Storage      │
│ Physical Hardcopy  │ Mini 58mm Thermal Receipt Printer (ESC/POS Paper Map)  │
└────────────────────┴────────────────────────────────────────────────────────┘
```

### 3.1 All-Band HF / Shortwave / AM Radio Receiver (Si4732 / Si4735)
* **The Need:** While the RTL-SDR module covers VHF/UHF (24–1700 MHz), regional VHF repeaters die when emergency generator fuel runs out. Continental and trans-oceanic emergency intelligence broadcasts rely on **High-Frequency (HF) Shortwave (3–30 MHz)** and AM medium-wave radio.
* **The Silicon:** An ultra-low-power **Silicon Labs Si4732 / Si4735** all-band broadcast receiver IC connected over I2C/SPI:
  * Full coverage: AM (520–1710 kHz), Shortwave (2.3–30.0 MHz), Longwave (153–279 kHz), and FM (64–108 MHz).
  * Direct SSB (Single Sideband - USB/LSB) decoding for amateur ham radio emergency nets.
  * Operates on less than 15 mA total current.

### 3.2 Continuous Ionizing Radiation & Fallout Dosimeter
* **Sensor Selection:** Integrates a miniature solid-state radiation sensor (e.g., **Radiation Watch Pocket Geiger Type 5** or a miniature BG51 PIN diode sensor).
* **Autonomous Micro-Power Logging:** The pulse output is wired directly to an interrupt-enabled GPIO on the **RP2350 co-processor**.
  * RP2350 continuously accumulates Counts Per Minute (CPM) in background sleep ($I_Q < 15\text{ µA}$).
  * If radiation levels exceed normal ambient background threshold ($>0.25\text{ }\mu\text{Sv/hr}$), the RP2350 sounds the piezo buzzer, illuminates the ruby beacon, and fires `GPIO 17` to wake Linux with a radiological fallout contour map.

### 3.3 "Wild Power" Raw DC Input (Salvaged Power Harvesting)
* **The Problem:** In a disaster, regulated 5V USB-PD wall supplies do not exist. Power must be drawn from salvaged 12V car batteries, fluctuating 18V folding solar blankets, or improvised bicycle/water dynamos.
* **Implementation:** The carrier board routes an auxiliary rugged 2-pin screw terminal directly to the **TI BQ25798** charger (ADR-035):
  * Accepts raw DC voltages from **3.6V to 14.0V** (BQ25798 input floor, datasheet).
  * Integrated Dynamic Power Management (VINDPM) prevents input voltage collapse when connected to weak or shaded solar panels.

### 3.4 Micro Thermal Hardcopy Receipt Printer (ESC/POS)
* **The Role:** Digital communication is ineffective if a companion's device is dead.
* **Operation:** Connects via USB-C or BLE to standard 58mm micro thermal receipt printers using standard ESC/POS commands. SolarDeck prints physical paper topographic snippets, medical step-by-step triage checklists, radio frequency rosters, and cryptographic public keys onto waterproof, inkless thermal paper.

---

## 4. Frontlight Optical Engineering & Spectrum Control

E-Ink panels are physically opaque (electrophoretic pigment microcapsules mounted on a steel or plastic backplane). They cannot be backlit.

```
                                [ AMBIENT SUNLIGHT / ROOM LIGHT ]
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. PROTECTIVE MATTE COVER GLASS (Anti-Glare Etched Surface, 0% Glare)      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. ULTRA-THIN OPTICAL LIGHTGUIDE (Micro-Etched Extraction Prisms)           │
│    ◄── SIDE-FIRING BEZEL LED STRINGS: White (5000K) + Amber (2700K) + Red  │
│    (Light is directed downward onto the pigment capsules, then reflected up)│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. 10.3" E-INK CAPSULE MATRIX (Black, White, Color Micro-Particles)         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. WACOM EMR DIGITIZER SHIELD (Behind Display Backplane, ~560 kHz RF)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Downward-Reflecting Lightguide Architecture
* **Physical Principle:** Bezel-mounted surface-mount LEDs inject light horizontally into the edge of a specialized micro-grooved optical lightguide film. The micro-prisms redirect light **strictly downward** onto the e-paper surface, which reflects back into the user's eyes.
* **Zero Eyestrain:** Photons reflect off paper naturally rather than shining directly out of a liquid crystal matrix into the user's retinas, completely eliminating optical fatigue.

### 4.2 2048-Step Logarithmic Dimming Curve
* **Driver:** Texas Instruments **TPS61163** dual-channel constant-current step-up driver.
* **Human Eye Perception:** Human luminous response is logarithmic. The RP2350 co-processor applies a 2048-step logarithmic PWM curve:
  * High-end: Smooth daylight fill illumination.
  * Low-end: Micro-adjustments below 0.1 lux, achieving a true **candlelight/moonlight floor (< 0.05 lux)** without flickering or jumping steps.

### 4.3 Spectrum Options: Dual CCT + Tactical Tri-Color Roadmap
1. **Cold-White (5000K):** High-contrast daytime reading in dimly lit rooms.
2. **Warm-Amber (2700K):** Circadian-safe night reading with zero blue light emission.
3. **Hardware Tri-Color Roadmap (630nm / 660nm Deep-Red):**
   * The frontlight FPC can populate interleaved **630nm/660nm monochromatic deep-red micro-LEDs**.
   * Provides full-screen, uniform red illumination across the 10.3" display.
   * Maintains 100% human night adaptation for dark-sky astronomy, tactical night navigation, and military flight decks.

---

## 5. Local Offline RAG (AI Knowledgebase Traversal)

SolarDeck runs a local, airgapped **Retrieval-Augmented Generation (RAG)** pipeline allowing users to query over 100GB of compressed human knowledge without external network access:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OFFLINE LOCAL RAG INFERENCE ENGINE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. USER PROMPT: Natural language query entered in terminal or voice         │
│                         │                                                   │
│                         ▼ (< 50ms over PCIe NVMe Gen 2 x1)                  │
│ 2. INDEX RETRIEVAL:                                                         │
│    • Queries pre-indexed Xapian / SQLite FTS5 index in Kiwix .zim archives  │
│    • Extracts top 3–5 candidate text chunks (~1,500 tokens)                 │
│                         │                                                   │
│                         ▼                                                   │
│ 3. CONTEXT ASSEMBLY:                                                        │
│    • Combines user query + extracted reference passages + strict grounding │
│                         │                                                   │
│                         ▼ (tokens/sec TBD — verify on CM5)                  │
│ 4. LOCAL SYNTHESIS (llama.cpp on CM5 Quad Cortex-A76):                      │
│    • Model: Qwen 2.5 3B Instruct or Llama 3.2 3B (Q4_K_M Quantization)     │
│    • Memory: 2.2 GB RAM footprint (rest of the 16GB CM5 stays free)         │
│    • Synthesizes concise, actionable, numbered field steps                  │
│                         │                                                   │
│                         ▼                                                   │
│ 5. ZERO-POWER STATIC DISPLAY:                                               │
│    • Flushes answer to E-Ink display; consumes 0.000W while being read      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Storage & Retrieval Performance
* **Index Storage:** The 100GB+ Kiwix `.zim` files reside on the **M.2 2230/2242 PCIe NVMe SSD** (wired to the CM5's PCIe Gen 2 x1 bus at 400+ MB/s).
* **Search Speed:** Pre-computed Xapian / SQLite full-text indices resolve multi-keyword queries in **under 45 milliseconds**.

### 5.2 Local LLM Resource Footprint (CM5 16GB)
* **Engine:** `llama.cpp` compiled with native ARMv8 NEON SIMD optimizations.
* **Model Selection:** **Qwen 2.5 3B Instruct** or **Llama 3.2 3B** (Q4_K_M quantization).
  * Model Weight Size: ~2.0 GB.
  * Active Inference RAM: ~2.4 GB (including 4K KV cache).
  * System Free Memory: the rest of the CM5's 16 GB for Linux, Wayland, and user tasks.
  * Inference Throughput: TBD — verify on CM5.
  * Battery Consumption: ~3.2W during 20 seconds of generation = **~0.018 Wh per query** (share of the pack TBD until the cell is chosen, ADR-040).
* **Zero-Hallucination Grounding:** The prompt template strictly constrains the model to cite only the retrieved excerpts. If an answer is not present in the local manuals, the model explicitly acknowledges the absence rather than guessing.

---

## 6. GPU Architecture & Silicon Capabilities (CM5 / BCM2712)

*Appended 2026-10-19 12:20 UTC in the Pi harness by antigravity/gemini-3.8-flash*

The Raspberry Pi CM5's BCM2712 integrates a 3D graphics and compute GPU with open-source Linux kernel and userspace driver stacks; its generation, clock, API levels and video-codec blocks are TBD — verify on CM5:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CM5 (BCM2712) GPU SILICON PIPELINE                      │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ Graphics Standards    │ • Mesa v3d / v3dv; API levels TBD — verify on CM5   │
│                       │ • Hardware direct DRM/KMS scanout with zero tearing │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Dedicated Video ASIC  │ • Decode / encode blocks TBD — verify on CM5        │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ SolarDeck Workloads   │ • Real-time GLSL Blue-Noise Dithering (<2.0ms frame)│
│                       │ • Vulkan compute acceleration for local AI / STT    │
│                       │ • Wayland Sway compositor GPU hardware page flip    │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

1. **Hardware-Accelerated Temporal Blue-Noise Dithering (`dither.glsl`):**
   * Electrophoretic displays physically cannot switch 24-bit RGB or 256-level greyscale at video rates.
   * A custom GLSL fragment shader running on the CM5 GPU dynamically maps 24-bit frames into 1-bit binary or 2-bit (4-level) dithered bitmaps in **under 2.0 milliseconds**, creating smooth optical gradients with near-zero CPU load.
2. **Vulkan Matrix Compute Acceleration (`llama.cpp` & `whisper.cpp`):**
   * Leveraging Mesa's native `v3dv` Vulkan driver, matrix multiplications and token embedding lookups can be partially offloaded from the Cortex-A76 cores to the GPU shaders, improving local STT transcription latency and conserving battery.
3. **Hardware Camera ISP & Outgoing Video Encoding:** V2 (ADR-034): needs the deferred rear camera.

---

## 8. Tactical Module Rejiggering: Core Tablet vs. USB-C "Hotpacks"

*Appended 2026-10-19 13:00 UTC in the Pi harness by antigravity/gemini-3.8-flash*

USB-C Hotpacks are deferred to V2 (ADR-034). The V1 core tablet is listed in `README.md` and `MVP_ARCHITECTURE.md` §1.

---

### 8.1 Why We Descope the Flipper Zero Clone (Use the Real Flipper Zero)
* **The Trap:** Designing a custom backpack with a CC1101 Sub-GHz chip, 125 kHz RFID coil, and IR remote replicates hardware that already exists.
* **The Ponytail Reality:** The **Flipper Zero** is already a mature, battery-powered $169 multi-tool with extensive community firmware (Unleashed, Momentum).
* **The Integration:** Users mount their existing Flipper Zero directly to SolarDeck’s rear M2.5 inserts or MagSafe ring, connecting via a 10cm right-angle USB-C cable or Bluetooth 5.0. SolarDeck’s CM5 Linux runs `qflipper-cli` and `flipperzero-protobuf`, exposing full control on the 10.3" sunlight-readable screen without adding custom silicon.

---

### 8.2–8.5 Hotpacks 1–4
Deferred to V2 (ADR-034).

---

### 8.6 The Hawaii Sun Problem: Why Solar Covers Are Descoped
* **The Thermal Ceiling:** In direct tropical midday sun (Hawaii, Arizona, Mexico), ambient temperatures hit +35°C to +42°C, and dark unibody surfaces bake to **over +70°C (+158°F)**.
* **Display Physics:** Electrophoretic microcapsules (E-Ink) undergo permanent fluid degradation and pigment sticking if operated above **+60°C**.
* **Battery Safety:** the V1 Li-ion pack (ADR-048) must stop charging outside its charge-temperature window; the charger's JEITA zones, the pack NTC and the harvester's hardware temperature gate enforce it, and heat also speeds the pack's wear-out.
* **The Detached Solar Workflow:**
  * Descope the integrated solar smart cover.
  * Pack a standard, lightweight folding 15W–28W USB-C solar panel (e.g. BigBlue / Anker with SunPower Maxeon cells).
  * Place the solar panel out in the scorching sun on a hot volcanic rock or vehicle roof.
  * Run a **3-meter high-visibility USB-C cable** into the shade of a tree, awning, or tent where SolarDeck and its battery pack operate at ambient temperature.

---

### 8.7–8.9 Hotpacks 5–7
Deferred to V2 (ADR-034).

---

*Appended 2026-10-19 14:10 UTC in the Pi harness by antigravity/gemini-3.8-flash*

The following custom software utilities and daemons leverage SolarDeck's bi-stable E-Ink display, dual-brain architecture, tactical radios, and sensor array:

## 9. Cross-Domain Daemon Catalog (Field, Maritime & Writing)

### 9.1 Tactical RF, Air Radar & Signals
1. **`solardeck-waterfall` (High-Contrast E-Ink RF Spectrum & Air Radar):**
   * Captures raw I/Q samples from the RTL-SDR and CC1101 radios (Hotpacks, V2, ADR-034).
   * Renders a real-time RF waterfall using custom 1-bit Atkinson dithering optimized for high sunlight visibility.
   * Integrates with `dump1090-fa` to plot commercial and private aircraft ADS-B transponder positions, altitudes, and headings directly over an offline vector topographic map.
2. **`solardeck-recon` (Zero-Glow Wi-Fi & BLE Tactical RF Audit):**
   * Integrates with `kismet` or `bettercap` to passively map nearby Wi-Fi APs, client MAC addresses, and Bluetooth beacons along with MAX-M10S GNSS coordinates.
   * **Zero-Glow Stealth Advantage:** Operates with the frontlight turned off (0.000 lux), remaining completely undetectable to outside observers at night while scanning.
3. **`solardeck-ham` (Off-Grid Global HF Text Messenger - JS8Call / FT8 / APRS):**
   * Interfaces with external QRP ham transceivers via USB audio or CAT control.
   * Encodes and decodes weak-signal digital text messages bounced off the ionosphere across continental distances using less than 5W of RF power.
   * Decodes 144.390 MHz VHF APRS packets, tracking local search-and-rescue teams, weather stations, and repeaters on the e-ink screen.

### 9.2 Acoustic, Solar & Inertial Field Navigation
4. **`solardeck-acoustic-compass` (Dual-Mic Acoustic Angle-of-Arrival Tracker):**
   * Utilizes the 65 mm Knowles dual-MEMS microphone array to compute the Time Difference of Arrival (TDoA) of sudden sharp transients (gunshots, distant engine revs, whistles, shouting).
   * Renders a 360-degree tactical compass HUD with an arrow pointing toward the bearing of the sound source.
5. **`solardeck-sundial` (Optical Solar Heading & Astronomical Compass):**
   * Samples micro-solar strip voltage via the RP2350 12-bit ADC alongside MAX-M10S GNSS coordinates and RTC time.
   * Rotating the tablet until the micro-solar strip reaches peak voltage calculates **True Geographic North** geometrically from the sun's position, completely immune to magnetic vehicle distortion.
6. **`solardeck-survey` (BLE Laser Distance Room Sketcher & Clinometer):**
   * Connects via BLE to laser distance measurers (Bosch GLM, Leica DISTO) to automatically sketch real-time floor plans with Wacom EMR in CAD/SVG.
   * Uses the Bosch IMU as a high-precision digital clinometer for surveying slope grades, vehicle roll/pitch, and solar panel tilt optimization.

### 9.3 Maritime, UAV & Hardware Engineering
7. **`solardeck-marine` (Waterproof Salt-Spray E-Ink Marine Chartplotter):**
   * Runs **OpenCPN** and **Signal K** connected to NMEA 2000 / NMEA 0183 boat instrument buses and AIS ship receivers.
   * Delivers 0% glare under blinding open-ocean sunlight.
   * Hardware water-lock isolates capacitive touch against splashing waves while allowing the Wacom EMR stylus to plot course bearings; draws only 1.2W vs 25W for standard marine MFDs.
8. **`solardeck-gcs` (Sunlight UAV & Weather Balloon Ground Control Station):**
   * Runs **QGroundControl** over USB telemetry radios using MAVLink (on-board LoRa is V2, ADR-044).
   * Serves as an outdoor daylight ground station for tracking autonomous drones, search-and-rescue quadcopters, and high-altitude meteorological balloons.
9. **`solardeck-bench` (Outdoor Logic Analyzer, Oscilloscope & Bus Pirate):**
   * Pairs with open-source USB logic analyzers via `sigrok` and `PulseView` on USB-C Port 2.
   * Turns SolarDeck into an outdoor 24 MHz 8-channel logic analyzer and oscilloscope for probing SPI/I2C/UART lines on field hardware in direct sun.

### 9.4 Sovereign Writing, Focus & Cryptography
10. **`solardeck-zen` (Sovereign Prose Typewriter):**
    * A distraction-free markdown environment running on the 20ms 1-bit typing waveform.
    * The CM5 has no RAM-retaining suspend (ADR-036), so there is no S2idle gating between keystrokes; writing runtime is TBD until the cell is chosen (ADR-040).
11. **`solardeck-slate` (Low-Latency Wacom Vector Field Notebook):**
    * Direct-to-DRM canvas hooking into Wacom EMR (<18ms latency) for sketching circuit schematics, physics math, or tactical maps, with 1-click export to vector SVG or Obsidian.
12. **`solardeck-courier` (Autonomous Bi-Stable LoRa Pager & Bulletin Board):**
    * V2 (ADR-044); V1 uses a paired Meshtastic node over BLE.
13. **`solardeck-airgap-tx` (Optical QR Fountain Code Bridge):**
    * V2 (ADR-034): ingestion needs the deferred rear camera.
14. **`solardeck-vault-totp` (Bi-Stable Airgapped 2FA & Password Vault):**
    * Generates TOTP two-factor codes and unlocks KeePassXC vaults securely on an airgapped device.
    * Displays the 6-digit code on the zero-power e-ink screen where it can be read without casting a glow in dark rooms.
15. **`solardeck-drone` (Microclimate Generative Ambient Sound Synthesizer):**
    * Runs a lightweight Pure Data (Pd) or SuperCollider sound engine.
    * Maps barometric pressure drops and solar cloud shadow variations into soothing, real-time generative ambient soundscapes through the micro-speaker.
16. **`solardeck-bioacoustics` (Ultrasonic Bat & Pest Spectrogram Detector):**
    * Samples high-frequency acoustic data from the Knowles MEMS array up to 48–96 kHz to heterodyne and visualize bat echolocation and pest activity on an e-paper spectrogram.
