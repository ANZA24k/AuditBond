# AuditBond

A standalone GenLayer Intelligent Contract for bonded compliance audits of committed public evidence.

A sponsor funds a reward and locks a checklist, evidence requirements, submitter bond, submission deadline and review/settlement deadline. One independent submitter commits an immutable evidence manifest and exact bond. Anyone may request up to three assessments before the review deadline. Anyone may settle afterward; the latest accepted assessment controls settlement. No owner, upgrade switch, hidden policy edits, DApp, or off-chain database.

## Why GenLayer

Every leader and validator retrieves the same commit-addressed files, verifies their complete bytes against SHA-256 and byte counts, then independently interprets qualitative requirements. Validators compare **every criterion status** and evidence integrity, not just an overall label or JSON schema. Leader citations must be verbatim in independently verified evidence. Money and state transitions never come from an LLM.

| Criterion results | Verdict | Sponsor receives | Submitter receives |
|---|---|---|---|
| All PASS | COMPLIANT | 0 | reward + bond |
| Any FAIL | NON_COMPLIANT | reward + bond | 0 |
| PASS and UNKNOWN, no FAIL | PARTIAL | unearned reward | bond + floor(reward × PASS / criteria) |
| All UNKNOWN / incomplete committed bundle | INSUFFICIENT | reward | bond |
| No assessment by deadline | EXPIRED | reward | bond if submitted |

FAIL requires affirmative contradiction; absent evidence is UNKNOWN. All criteria have equal weight. Partial payment and slashing rules are fixed before either party funds the audit. A verdict describes the locked checklist and evidence, not legal certification or a security guarantee.

## Interface

- `create_audit(policy_json, bond_wei, submit_deadline, settle_deadline)` **payable**: send a positive reward; returns numeric string ID.
- `submit(audit_id, manifest_json)` **payable**: independent submitter sends exact bond once.
- `evaluate(audit_id)`: permissionless independent consensus, maximum three immutable revisions.
- `settle(audit_id)`: after deadline, deterministic credits; callable even if consensus never succeeds.
- `withdraw()`: caller withdraws its credit to its own chain-layer address through finalized external transfer.
- `get_audit`, `get_verdict`, `get_credit`, `get_accounting`: read committed state.

Policy JSON: `{ "title": "...", "criteria": ["..."], "evidence_requirements": "..." }`.
Manifest JSON: `[{ "url": "https://raw.githubusercontent.com/OWNER/REPO/FULL_COMMIT/evidence.txt", "sha256": "64 lowercase hex", "bytes": 123 }]`.

Only canonical HTTPS GitHub raw URLs with full lowercase 40-hex commits are accepted. No branch references, credentials, query strings, fragments, ports, escapes, arbitrary hosts or path aliases. Text formats: `.txt`, `.md`, `.json`, `.csv`. Bounds: 1–8 criteria, 1–4 files, 16 KiB/file, 32 KiB total, three revisions, 30-day lifetime and 10,000 audits. Each amount ≤ 10²⁴ wei. Byte limits are checked on the returned body; the host HTTP client may buffer before contract checks. Commit addressing prevents ordinary revision but does not guarantee continued hosting.

HTTP 5xx, 408/429 and request exceptions abort evaluation for retry, never settle funds. Stable missing/changed evidence makes the **entire** committed bundle insufficient. Malformed LLM output aborts evaluation. Deadline expiry always permits credit recovery.

## Reproducible checks

Python 3.12+:

```sh
python -m pip install -r requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests
genvm-lint check contracts/auditbond.py
```

The offline host double executes the actual source with deterministic injected web/LLM results, models transactional rollback and directly exercises validator rejection. It does not prove runtime behavior or real LLM agreement; the deployment and live test are documented separately in [DEPLOYMENT.md](DEPLOYMENT.md) and [evidence/LIVE_VERIFICATION.md](evidence/LIVE_VERIFICATION.md).

The runner matches the stable Studio template (v0.2.16), not the v0.3 release candidate. Official docs were checked on 2026-10-12. [Security model](SECURITY.md).

## Verified Studionet deployment

[AuditBond on Explorer](https://explorer-studio.genlayer.com/address/0xA5435aDC4f8038Ad3D027a026fc775222Ca0A5A1) — exact source from commit `c9b8cc328abd14760824639d29cb13dd9a14fa0b`. Six finalized Full Consensus transactions demonstrate deployment, funding, independent submission, **COMPLIANT** assessment, deterministic settlement and simulated withdrawal. Final liability and contract balance are zero. [Copy-ready submission](SUBMISSION.md) · [Live verification](evidence/LIVE_VERIFICATION.md).
