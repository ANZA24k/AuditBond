# Deployment

Target: **stable Studionet**, chain ID 61999, https://studio.genlayer.com/api, Studio https://studio.genlayer.com. Do not substitute `studio-dev` or Bradbury addresses. Studio simulates consensus and balances; it has no real EVM/ghost layer.

Official references checked 2026-10-12:
- https://docs.genlayer.com/developers/networks
- https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle
- https://docs.genlayer.com/developers/intelligent-contracts/features/web-access
- https://docs.genlayer.com/developers/intelligent-contracts/features/value-transfers
- https://docs.genlayer.com/developers/intelligent-contracts/features/transaction-context
- https://docs.genlayer.com/api-references/genlayer-linter

The source pins the same runner as stable Studio's v0.2.16 template. A linter notice about the newer release candidate does not justify changing stable runtime blindly.

Deploy `contracts/auditbond.py` unchanged after checks. Constructor takes no arguments. Select **Normal / Full Consensus** (not leader-only). Use built-in Studio accounts and simulated faucet amounts, never export private keys. Create a funded audit, switch to a distinct account for submission, then evaluate. Inspect finalized deployment/evaluation receipts, validator votes, view reads and Explorer source readback. Wait until the chosen deadline, settle and inspect credits. Record every successful receipt, exact deployed commit and source hash in `evidence/LIVE_VERIFICATION.md`.

The fixture URL must include the Git commit containing the fixture, and its SHA-256 must hash the exact raw bytes. Policy and manifest examples for the live run will be recorded in the live verification report. Synthetic observations test qualitative interpretation; they do not establish real-world compliance.

Stable-runtime correction: the pinned SDK defines `gl.nondet.web.Response.status` (not `status_code`) and optional raw `body`. This was verified against the runner's exact `py-lib-genlayer-std` dependency and then exercised live. The stable read API uses positional `gen_getContractCode` and `gen_call` with `transaction_hash_variant=latest-final`, matching its SDK; preview RPC examples should not be substituted.
