# REGULATORY.md — What Has to Be Certified Before This Ships

Written 2026-10-20 12:05 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017
Revised 2026-10-21 15:59 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).
Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:23 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, pin budget; ADR-044/045).

Audit 3 found that no regulatory dimension existed anywhere in the repo. This file is that dimension.
**Rule: no certificate row at `filed` or `granted` = no shipment.** A prototype may exist without these;
a product may not. Rows marked V2 gate only the V2 product (ADR-034); a receive-only row has nothing to file.

## 1. The matrix

Statuses: `not started` → `scoped` → `tested` → `filed` → `granted`.

| Domain | Requirement | Scope | Status | Owner | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Cellular (V2) | **PTCRB / GCF** carrier conformance | V2 modem (ADR-034) | not started | TBD | V2 only: no cellular radio in V1. Reuse the module's certs; cite the certificate numbers, don't re-test the radio |
| Cellular (V2) | Carrier approval (per operator) | V2 end product | not started | TBD | V2 only (ADR-034). Needs IMEI allocation + a carrier contact |
| Radio (V1) | **RF exposure (Wi-Fi/BT)** | V1 end product | not started | TBD | Run the FCC §1.1307(b)(3) exemption for the CM5 radio at its real separation behind the shell |
| Radio (V2) | **RF exposure (LoRa)** | V2 end product | not started | TBD | V2 only (ADR-044). LoRa at up to +22 dBm conducted near the body may need SAR, not just MPE (AUDIT 6 H18) |
| Cellular (V2) | **LTE SAR / MPE** | V2 end product | not started | TBD | V2 only (ADR-034). A modem antenna near the palm must be *assessed*, not assumed |
| Wi-Fi / BT | Module cert reuse (CM5) + antenna rules | CM5 | not started | TBD | The CM5's modular grant (TBD — verify on CM5) covers the module; the **antenna** and the enclosure change the RF environment |
| LoRa 915 MHz (V2) | **FCC Part 15.247** (DTS) or 15.231 | SX1262 + antenna (V2, ADR-044) | not started | TBD | 902–928 MHz, ≤ +30 dBm EIRP, 50 Ω matched, no external gain |
| LoRa 868 MHz (V2) | **EN 300 220** + ERC/REC 70-03 | SX1262 + antenna (V2, ADR-044) | not started | TBD | 1 % duty cycle in most sub-bands; firmware must enforce it per region |
| GNSS | None as an intentional radiator | u-blox MAX-M10S + passive antenna | not started | TBD | Receive-only (ADR-038): no intentional-radiator certification; covered by the end-product EMC rows |
| Sub-GHz (CC1101) (V2) | Same as above, per band | Hotpack 2 (V2, ADR-034) | not started | TBD | Hotpack carries its own antenna → its own filing |
| EMC | **FCC Part 15B**, **EN 55032** | End product | not started | TBD | Radiated + conducted; e-paper drive lines and the boost converter are the emitters |
| Safety | **EN 62368-1** / UL 62368-1 | End product | not started | TBD | Includes the battery and the PD path |
| Battery | **UN 38.3** transport test | Pack, shipped separately | not started | TBD | Required to ship a LiFePO4 pack at all, air or ground |
| Battery | **IEC 62133-2** | Pack | not started | TBD | The BQ29706-class protector is protection, not certification |
| Battery | **EU 2023/1542** battery passport + carbon label | Pack | not started | TBD | Applies from 2027; a 30-year product will live inside this regime |
| Materials | **RoHS / REACH** declarations | All V1 line items | not started | TBD | Collect supplier declarations now — 2046 sourcing is easier with them |
| Materials | **WEEE** registration + **Prop 65** | End product | not started | TBD | Per-country registration for sale |
| Export | **ECCN / EAR** classification | End product | not started | TBD | Crypto (LUKS, WireGuard) may trigger classification review; cellular adds to it in V2 |
| Radio (region) | **EIRP table per region** in firmware | Firmware | not started | TBD | Already a spec constraint (`HARDWARE_SPEC.md` §RF); the table itself does not exist |

## 2. What is cheap to do now and expensive later

1. **Collect supplier RoHS/REACH declarations as you order.** Every supplier gives them at purchase;
   reconstructing them years later is a research project.
2. **Reuse module certificates deliberately.** The CM5's modular grant is TBD — verify on CM5 (the V2 cellular modem will bring its own module certificates). The
   moment you add your own antenna or change the enclosure, you own the delta. Record which certificate
   covers which line item.
3. **Write the per-region EIRP table before firmware.** Retrofitting a duty-cycle limiter into a shipped
   radio stack is a recall.
4. **UN 38.3 before the first pack order**, not before the first shipment. A pack you cannot legally
   transport is a pack you cannot debug on a bench across the country.

## 3. The honest position

Nothing above is started. For a hobby build that is fine and this file simply says so. For a product,
this matrix is the critical path, and it is longer than the schematic work: EMC and SAR need a finished
enclosure, the battery needs a finished pack, and (in V2) the carrier approvals need an IMEI range. The
sequencing constraint that matters: **enclosure → EMC/RF exposure → filings**, so the mechanical design is on
the certification critical path, not beside it.

→ skipped: drafting the actual test plans. They depend on the finished enclosure and pack, and a plan
written before the artifact is a document that will be rewritten. Add when the enclosure is frozen.
