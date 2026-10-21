# WORKFLOW.md — How SolarDeck Changes Actually Happen

Written 2026-10-20 05:05 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

This is the operating procedure for humans and agents working in this repo. `AGENTS.md` is the short
version that points here. The rules below were written *after* the 2026-10-20 audit, and each one
exists because an audit finding proved it was needed (see `AUDIT_2026-10-20.md`).

---

## 0. The one principle

**A claim is a contract.** Every quantitative or capability statement in this repo is either
enforced by a test or tagged as unverified. There is no third state. A doc that says "24 fps" with no
tag and no test is a defect, not optimism.

Corollaries:
- Numbers live in `docs/spec_values.json`. Prose and tests reference them; nothing restates them.
- A measurement nobody can reproduce is a guess with a decimal point.
- A feature nobody specified is a rumour. A spec with no artifact is a wish.

---

## 1. Claim status tags

Every figure and capability claim carries exactly one tag. Untagged = untrustworthy.

| Tag | Means | Required evidence | May appear in README? |
| :--- | :--- | :--- | :--- |
| `measured <date>` | Bench value from *this* build or an equivalent dev kit | Instrument, setup, date, and a script or log committed | yes |
| `datasheet` | Vendor-published figure | Datasheet revision + page in the doc | yes |
| `modelled` | Arithmetic, simulation, or first-principles estimate | The calculation, in the doc | yes, with the tag |
| `aspirational` | A design goal, not a capability | Nothing — that is the point | **only** as a goal, never in the specs table |
| `null` / TBD | Unknown, and we refuse to guess | An ADR saying why it is unknown and what unlocks it | as "TBD" |

Rules:
1. **Promotion is one-way and requires evidence.** `aspirational → modelled` needs the calculation;
   `modelled → measured` needs a bench run; there is no path back to `aspirational` except an ADR.
2. **`null` is a legitimate, permanent value.** `spec_values.json` uses `null` where we do not know
   (e.g. `refresh_modes.kaleido4_fps`). Do not fill a `null` in to make a table look complete.
3. **Numbers in chat are not numbers in the repo.** If a figure is worth saying, it is worth a JSON key
   and a tag.
4. Deleting a superseded claim means deleting its *prose*, not annotating it. The reasoning goes to
   `docs/90-history/decisions.md` as an ADR.

---

## 2. Change classes

Classify the change before touching anything. The class determines required evidence.

| Class | Examples | Required evidence before merge |
| :--- | :--- | :--- |
| **C1 CLAIM** | New/edited figure, capability, cost, dimension | `spec_values.json` key + tag + Phase 10 green |
| **C2 DESIGN** | Schematic, pinout, bus, thermal, mechanical | Affected propagation artifacts regenerated + relevant Phase + a trap-audit run |
| **C3 FIRMWARE / SOFTWARE** | RP2350 C, daemons, provisioning | One runnable `assert`-based check (self-test or targeted test) in the same commit |
| **C4 HYGIENE** | CI, lint, links, licences, renames | Phase 9/10/11 green; no behavioural claim changed |
| **C5 RELEASE** | Bundle, version bump, CHANGELOG | All every phase green + bundle regenerated from source, never hand-edited |

A change that spans classes needs **all** of their evidence. When in doubt, treat it as the higher
class: C2 beats C1, C3 beats C4.

---

## 3. The lifecycle

```
INTENT ──► DECISION ──► CLAIM ──► ARTIFACT ──► VERIFICATION ──► LEDGER
   │           │           │          │              │             │
   └─ blocked ─┴─ ADR ─────┴─ JSON ───┴─ source ─────┴─ phase ─────┴─ INDEX/HANDOFF
```

### 3.1 INTENT — say what and why, in one paragraph
- Written into the issue/ADR stub, not into the spec.
- **Exit:** a stated user problem and the smallest solution that solves it. If the intent is
  "make X better", it is not ready — quantify the problem or drop it (YAGNI).
- **Refuses to advance when:** the feature is speculative (no user, no buyer, no failure it prevents).
  Then the answer is "declined" in an ADR, which is a valid, recorded outcome.

### 3.2 DECISION — an ADR, always
Every descope, every reversal, every "we choose X over Y because Z" gets an ADR in
`docs/90-history/decisions.md`. Number sequentially; never renumber; never delete. A decision without
its `because` is unusable six months later.
- **Exit:** ADR with Trigger / Decision / Delta (cost, schedule, risk) / "still assumes it".
- **Test:** can a reader reconstruct *why* without asking anyone? If no, the ADR is too short.

### 3.3 CLAIM — spec first, prose second
1. Add the key to `docs/spec_values.json` (`null` if unknown).
2. Write the spec section; it references the key symbolically.
3. Tag the claim.
- **Exit:** Phase 10 (`check_docs_numbers.py`) green; no tag missing; no superseded prose left behind.
- **Refuses to advance when:** the number has no source. That is `null` + ADR, not an estimate
  dressed as a spec.

### 3.4 ARTIFACT — source, not output
Schematics, CAD, C, daemons. Generated artifacts (netlist, gerbers, BOM exports, bundles) are always
regenerated from source in the same commit; never hand-edited; never the only copy of a fact.
- **Exit:** the artifact can be regenerated byte-identically by a script in `hardware/`, `scripts/`, or
  `tools/`.
- **Refuses to advance when:** an output was edited directly, or a value appears in the artifact but
  not in `spec_values.json`.

### 3.5 VERIFICATION — a phase, not a vibe
`python3 scripts/verify_all.py` is the only gate. Current phases and what each proves are in
`docs/HARDWARE_VERIFICATION_WORKFLOW.md`.
- **Exit:** all phases green, and the change's *specific* check exists (a new claim needs a new
  assertion, not just a passing suite).
- **Refuses to advance when:** a test asserts its own hardcoded literal (tautology), or the phase would
  pass with the artifact deleted.
- **The banner is load-bearing:** "internally consistent — NOT a design sign-off" means exactly that.
  Never quote a green run as evidence a board works.

### 3.6 LEDGER — INDEX, HANDOFF, CHANGELOG
- `docs/INDEX.md` is generated; do not hand-edit rows.
- `docs/HANDOFF_TO_FABLE.md` is the reviewer's entry point; update it at each stable checkpoint.
- `CHANGELOG.md` for behaviour changes, not for doc churn.
- **Exit:** the next contributor can start from `docs/README.md` and not need the previous chat.

---

## 4. Non-negotiables, by failure mode

Each rule maps to an audit finding. They are not style preferences.

| # | Rule | Why (audit evidence) |
| :-- | :--- | :--- |
| 1 | A green check that cannot fail is not a check | `last_wake_elapsed_us = 42000;` asserted `< 300000` — tautology, B9 |
| 2 | Netlist/BOM/CPL must agree, and coverage must be printed | 20 netlist parts vs 61 BOM lines, 0 wires, B1 |
| 3 | Partial capture is stated at the top of the doc, not implied | placeholder gerbers read as fabrication-ready, B1 |
| 4 | Check the *package* against the part, not just the function | TMUX1575 "8-channel" is a 4-channel DSBGA-only part, B2 |
| 5 | Architecture must match the panel's real interface | DSI-to-LVDS bridge for a panel that accepts neither, B3 |
| 6 | Stackups must be closed arithmetic, from `spec_values.json` | display + cell + PCB exceeded the cavity in the pre-audit geometry, B4 |
| 7 | One implementation per function | three competing solar designs in three docs, B5 |
| 8 | One bus, one connector — delete the losing design | pogo bus vs USB-C, B6 |
| 9 | A pillar needs a test or a downgrade path | unverified CM4 S2idle, B7 |
| 10 | Single source of truth for every number | 20 located contradictions, B10 / ADR-016 |
| 11 | Defer a number rather than invent it | `kaleido4_fps: null`, ADR-017 |
| 12 | Physical-layer conflicts are designed, not discovered | digitizer over panel → `solardeck-penarb`, ADR-018 |
| 13 | Fast-feel is a policy question before a hardware question | Boox-class ladder, ADR-019 |

---

## 5. Deferred claims: how to be honest about not knowing

1. Create the ADR first. It states: what is unknown, why, what measurement or dev kit resolves it, and
   what the doc claims in the meantime.
2. Put `null` in `spec_values.json`.
3. Prose says "TBD" or "unmeasured" — never a range that looks measured.
4. Add the unlock condition to `HANDOFF_TO_FABLE.md` so the next reviewer sees it as an open gate, not a
   missing feature.
5. When it is measured, promote the tag, delete the ADR's "unknown" wording by *superseding* it with a
   new ADR entry.

A deferred claim is **not** technical debt if it is recorded; it is the cheapest form of honesty. It
becomes debt the moment a number appears without its source.

---

## 6. Agent procedure (humans: same, minus the trailers)

1. **Read**, in this order: `docs/README.md` → `docs/AUDIT_6_2026-10-21.md` → the spec section you touch →
   `docs/90-history/decisions.md` ADRs that mention it. Do not edit before you have read the audit;
   half the traps are already documented there.
2. **Classify** the change (C1–C5, §2) and say so in one line.
3. **Search structurally** — `ast-grep`/`sg --json` for code, `rg` for config/prose, `kicad-cli` for
   hardware. Do not text-grep a syntax tree.
4. **Decide** if there is a decision to make: write the ADR *before* the code, not after.
5. **Implement** the minimum that satisfies the intent (Ponytail ladder: YAGNI → reuse → stdlib →
   native platform → existing dependency → one line → minimum code).
6. **Verify** with `python3 scripts/verify_all.py`. If the suite cannot catch your change, add the
   assertion that can — that assertion *is* part of the change.
7. **Self-review** the actual `git diff`: correctness, edge cases, safety, and whether you left
   superseded prose behind.
8. **Commit** with the attribution trailers below; one logical change per commit; regenerated artifacts
   in the same commit as their source edit.
9. **Report** what changed, what was skipped and when to add it, and what is still unmeasured. Three
   lines, not an essay.

### Stop and ask instead of guessing when
- The change would alter a safety parameter (charge voltage, thermal cutoff, EIRP, DC balance).
- A number has no source and no dev kit to produce one.
- Two designs disagree and neither is documented as the winner.
- The fix requires deleting a specification section the user has not seen.
- An artifact would have to be faked to keep a gate green.

### Never
- Invent a measurement, dimension, or datasheet value.
- Close a blocker without an artifact or a phase that fails when the blocker returns.
- Hand-edit a generated file (netlist, gerber, BOM export, bundle, INDEX).
- Restate a number that already lives in `spec_values.json`.
- Leave "descoped" prose next to the full spec of the descoped thing.
- Bypass a failing phase by lowering its threshold — raise the artifact or downgrade the claim.

---

## 7. Attribution

- **Commits:** `Co-Authored-By: <model> <noreply@anthropic.com>` and
  `Harness: pi (<provider>/<model>, session <8-char id>)` via `git commit --trailer`.
- **Documents/records:** `Written <YYYY-MM-DD HH:MM> UTC in <harness, e.g. the Pi harness or Claude Code> by <provider>/<model>` in the
  header or at the start of the appended section.
- **Tracker comments:** `[Pi · <provider>/<model> · session <id>]`.
- Subagents inherit these rules; pass them in the prompt.

---

## 8. Cadence

| When | What | Output |
| :--- | :--- | :--- |
| Every commit | `verify_all.py`, Phase 9/10 green | green run |
| Every stable checkpoint | HANDOFF rewrite + INDEX regen | committed handoff |
| Every release | full every phase + bundle diff review | release notes |
| Every quarter, or after 3 surprise findings | **audit pass** in the shape of `AUDIT_2026-10-20.md`: what is measured vs modelled vs aspirational, what artifact is missing, what claim is unsupported | audit doc + fix plan |
| Any descope | ADR | decision log entry |

The audit is not a crisis ritual. It is the scheduled moment where claims are re-tagged and dead prose
is deleted. Its value is the *findings list with file:line*, not the prose around it.

---

## 9. Definition of done (copy into the PR/commit body)

```
[ ] class: C1 | C2 | C3 | C4 | C5
[ ] numbers in docs/spec_values.json, referenced symbolically (C1+)
[ ] every new claim tagged measured/datasheet/modelled/aspirational/null
[ ] decision recorded as ADR (if any choice was made)
[ ] superseded prose deleted; reasoning moved to 90-history/decisions.md
[ ] generated artifacts regenerated from source, same commit
[ ] one runnable check added or updated for the changed logic
[ ] python3 scripts/verify_all.py green (every phase)
[ ] self-review of git diff complete
[ ] attribution trailers / Written line present
[ ] what is still unmeasured is stated in one line
```
