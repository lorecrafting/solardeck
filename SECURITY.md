# Security Policy & Threat Model

Written 2026-10-20 04:13 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Revised 2026-10-21 16:03 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).

Revised 2026-10-21 17:23 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, pin budget; ADR-044/045).

Revised 2026-10-21 19:45 UTC in Claude Code by anthropic/claude-opus-5-5 (Li-ion smart pack, ADR-048).

SolarDeck is sold as a *sovereign* device, so its security claims are product claims, not
boilerplate. This document states what is actually enforced in hardware, what is enforced in
software, and what a buyer should not assume.

## Hardware-enforced (cannot be overridden by a compromised OS)

| Control | Mechanism | Limits |
| :--- | :--- | :--- |
| Radio cutoff | FULL BLACKOUT on the single 3-position privacy switch (HARDWARE_SPEC §2.25) holds the TPS22918 GNSS gate off. A pole-B contact that fails open leaves the radios on and reads as MIC MUTE (§2.25) | The GNSS rail is cut; the CM5's on-module Wi-Fi/BT is held off by tying its `WL_nDisable`/`BT_nDisable` pins low (CM5 datasheet §2.1.1–2.1.2), not by a rail cut. Residual emissions are what gate G5 measures |
| Microphone cutoff | MIC MUTE gates off the mics' I²S bit clock (`MIC_BCLK`, `docs/PIN_BUDGET.md`) through a hardware gate driven by the switch, and pulls the mic side to GND; FULL BLACKOUT also cuts the mic supply. An open switch reads as MIC MUTE | In MIC MUTE the mic supply is not cut. Firmware cannot drive the gate, but the switch position is only as trustworthy as its contacts — "hard to defeat", not "impossible" |
| Display bus isolation | Two TMUX1575 devices (fail-safe, $I_{\text{off}}$) present giga-ohm impedance when the CM5 rail is at 0 V | Isolation is per-line and switch-state dependent |
| Airgap | Series disconnect of peripheral power gates, not an RF shield | Near-field coupling, thermal and acoustic side channels are outside the model |
| Battery pack interlock (ADR-048) | The user-replaceable pack is input from outside the device. The RP2350, not Linux, reads the pack gauge's design charge voltage and keeps the charger's CE off unless it matches `battery.charge_limit_v`. Status: the gate logic is in firmware and host-tested (test 7); the I²C reads that feed it are not written yet (software frozen, ADR-046) | A firmware interlock, not authentication: a counterfeit or faulty pack can report any value, and a compromised OS that pushes RP2350 firmware (A/B update, `SOFTWARE_SPEC.md`) can skip the check. The backstops that need no firmware are the pack-side protector and fuse and the harvester's hardware temperature gate |

**Not claimed:** no tamper-evident mesh, no secure element for disk encryption keys, no measured
power side-channel resistance, no anti-evil-maid guarantee. Cellular and the eSIM are V2 (ADR-034); the V2 eSIM requirement is a consumer SGP.22 eUICC
(ADR-033).

## Software posture

* Full-disk encryption (LUKS2) with the passphrase entered at boot — the key lives in RAM, and an
  unlocked device left unattended while Linux is running stays unlocked.
* Network default-deny: `nftables` ruleset drops inbound; radios are down unless a profile enables
  them. `solardeck-airgapd` tears down interfaces and flushes keys before reporting blackout.
* No telemetry leaves the device. `solardeck-telemetryd` writes to `/var/log/solardeck/telemetry.db`
  locally; the AI evolution loop reads that file and nothing else.
* The AI features send prompts off-device when a hosted model is selected. That is a user decision,
  not a silent one: `solardeck-ai --offline` pins to local models only.

## Known weak points (documented, not hidden)

1. **The `.pi/`, `~/.ssh` and API-key stores are ordinary files** — a root compromise reads them.
2. **Local LLM prompt injection:** documents and images fed to a vision model can carry instructions
   that reach the agent's shell. Run agentic work in a bubblewrap sandbox with no radio access.
3. **Radios can locate you:** GNSS is receive-only, but Wi-Fi/BT and a paired Meshtastic node (ADR-044)
   transmit. The privacy switch cuts GNSS and the CM5 radios; nothing prevents RF fingerprinting while
   they are on, and an external node is outside the switch.
4. **The BIST engine (`solardeck-diag`) reads device state but does not attest it** — a rooted OS can
   lie to it. Hardware attestation is out of scope for V1.

## Reporting a vulnerability

Do not open a public issue for a security defect. Email the maintainer listed in `git log`, or open a
private security advisory on the repository host. Include the affected path, a reproduction, and
whether the issue is hardware, firmware, or userspace. Expect an acknowledgement within 7 days and a
coordinated disclosure date within 90 days.

## Scope exclusions

Bugs in vendor silicon or vendor firmware (Quectel, TI, ITE, u-blox, Raspberry Pi) should be reported
to the vendor; we will track them publicly once a workaround exists. Physical attacks requiring
sustained possession of the device are in scope for documentation, not for fixes.
