# Security model

AuditBond is a Studionet pilot, not an independently audited production escrow. Do not deposit real funds on the basis of simulated Studio testing.

## Trust boundaries

- Policy, evidence requirements and evidence contents are untrusted prompt data. The fixed task disallows role changes, outside browsing and instructions about money. JSON framing, short prompts, required source citations and independently repeated judgments reduce prompt injection; they cannot eliminate correlated LLM errors.
- Hashes prove byte integrity, not truthful observations. Sponsors choose criteria; submitters choose evidence. Neither party can alter those commitments after funding/submission. Reviewers must assess whether a locked policy is meaningful before participating.
- A single committed submission exists per audit. Rechecks reuse the same evidence; correcting evidence requires a new audit. Three assessment requests can be consumed by any caller. This bounds cost but permits review-budget exhaustion; it cannot erase an accepted verdict or prevent deadline refunds.
- Validators re-fetch all files and independently classify all criteria. Strict status matching may cause disagreement for ambiguous criteria. No accepted consensus means no state change. Transient errors never become FAIL/INSUFFICIENT by fallback.
- Settlement conserves reward + bond with integer arithmetic. State becomes SETTLED before credits are added. Withdrawal clears credit before external message emission. Transaction-level emission failure must roll back the transaction. There is no internal IC payout message whose failed child silently burns the bond.
- `withdraw` routes to the caller's **chain-layer** address, not an arbitrary recipient. Use directly controlled EOAs as sponsor and submitter; contract callers must understand chain-layer message receipt behavior. External chain messages execute at finalization; a future chain/runtime failure is outside contract guarantees. Stable Studio cannot establish real EVM/ghost transfer behavior. Real-fund use requires chain-layer integration testing, independent review and finalized receipt inspection.
- Settlement is permissionless, but someone must send the settle transaction after the deadline and each beneficiary must withdraw. Refundability does not mean autonomous timers. There is no global admin fund recovery.

## Commitments and history

`policy_hash` and `evidence_hash` hash canonical ASCII JSON (sorted keys, no whitespace, UTF-8). Decision hash covers domain, contract address, audit ID, revision, both commitments, criterion statuses, integrity vector, derived verdict and previous decision hash. Citation wording and evaluation time are stored but intentionally excluded from decision identity. Every revision is append-only and chained. No cancellation race, replacement, upgrade, or repeated settlement exists.

## Reporting

Report a reproducible issue privately to the repository owner through GitHub's available private reporting/contact route. Do not publish keys or personal evidence. Fixture data is synthetic and public.
