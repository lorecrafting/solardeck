# Security Policy & Threat Model

Written 2026-10-20 04:13 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

SolarDeck is sold as a *sovereign* device, so its security claims are product claims, not
boilerplate. This document states what is actually enforced in hardware, what is enforced in
software, and what a buyer should not assume.

## Hardware-enforced (cannot be overridden by a compromised OS)

| Control | Mechanism | Limits |
| :--- | :--- | :--- |
| Radio cutoff | 3-position slide switch cuts the series enable nets of the TPS22918 radio gates | The modem's own standby draw continues via the AON rail; only the switched rails are cut |
| Microphone cutoff | `MIC_MUTE` shunts the PDM clock to GND | The mic bias rail is not cut, so a hostile firmware could re-enable it if it can drive that GPIO — treat as "hard to do silently", not "impossible" |
| Display bus isolation | Two TMUX1575 devices (fail-safe, $I_{\text{off}}$) present giga-ohm impedance when the CM4 rail is at 0 V | Isolation is per-line and switch-state dependent |
| Airgap | Series disconnect of peripheral power gates, not an RF shield | Near-field coupling, thermal and acoustic side channels are outside the model |

**Not claimed:** no tamper-evident mesh, no secure element for disk encryption keys, no measured
power side-channel resistance, no anti-evil-maid guarantee. The EG25-G eSIM is soldered, but the
cellular *link* is not authenticated against a hostile carrier.

## Software posture

* Full-disk encryption (LUKS2) with the passphrase entered at boot — the key lives in RAM, and an
  unlockable device left unattended in suspend is unlocked.
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
3. **GNSS and LoRa are receive-transparent:** an observer can locate the device by its LoRa
   transmissions. The privacy switch cuts them; nothing prevents RF fingerprinting while they are on.
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
