# AuditBond live verification

Verified 2026-10-12 on **stable Studionet**, chain ID **61999**. Studio-hosted consensus and balances are simulated; this is not a real-money production escrow certification.

## Canonical deployment

- Contract: `0xA5435aDC4f8038Ad3D027a026fc775222Ca0A5A1`
- Explorer: https://explorer-studio.genlayer.com/address/0xA5435aDC4f8038Ad3D027a026fc775222Ca0A5A1
- Deployed commit: `c9b8cc328abd14760824639d29cb13dd9a14fa0b`
- Source: `contracts/auditbond.py`, **15,602 bytes**, SHA-256 `31fb5efbe8bb5d30340e9b2c5f56584142ae7b84b3dbc371d1d079c8fac9bc98`
- Complete deployed code readback matches the repository source byte for byte.
- Stable runner: v0.2.16, `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.
- Local checks: **32 passed**, GenVM lint **3 checks passed**, full SDK validation **passed**, 9 public methods.
- GitHub CI: https://github.com/ANZA24k/AuditBond/actions/runs/38221733450 — **success**.

## Finalized Full Consensus transactions

| Action | Explorer transaction |
|---|---|
| Deploy | https://explorer-studio.genlayer.com/tx/0x59560bd42abee42b5a1bdd310c7c43f83ba53b10b999678f50d5d0394538c4d0 |
| Create audit 0 | https://explorer-studio.genlayer.com/tx/0xd6139e94964a44dce6da90e04d495b97c147212cd9d77ebe3787e40760d3a112 |
| Submit evidence and bond | https://explorer-studio.genlayer.com/tx/0x3c61d316fa5e03440a706703cfe2da6a9917dc6cd1a398abb7f252767ebca6a1 |
| Evaluate | https://explorer-studio.genlayer.com/tx/0x1e10696dbcdcb8c099721e3ee112aaebeee57431833819957baea0fa8938d7e5 |

All four have `FINALIZED`, `MAJORITY_AGREE`, `NORMAL`, `leader_only=false`, successful leader execution and agreeing validator quorum. Idle validators were canceled after quorum and are not claimed as completed judgments. Evaluation required leader rotations before successful agreement; the accepted result and source-grounded findings are recorded in [live-records.json](live-records.json).

## Locked audit and evidence

Sponsor: `0x9e3CCf51f19057182D8cdbC16B6B87b4BfCEFF78`.
Independent submitter: `0xFE858F4f7b3F0Fff7947F40f83F0CF3b626fF580`.
Reward and bond: **1 simulated GEN each**, `1000000000000000000` wei each.
Submission deadline: `1791804198`; settlement deadline: `1791804318`.

Checklist:
1. Unprivileged access to the test record is denied without exposing contents.
2. Deleted test account is unavailable and its access token is rejected.

Evidence requirements: public synthetic test observations with explicit HTTP outcomes for both checks.

Immutable evidence URL: https://raw.githubusercontent.com/ANZA24k/AuditBond/c9b8cc328abd14760824639d29cb13dd9a14fa0b/evidence/synthetic-audit.txt

Exact raw evidence: **700 bytes**, SHA-256 `b8190c5ceba55c04a843b2fde2b274127c5f3961496aa98f70d02035e3ecb6a4`.
Policy commitment: `7a555b9cd711462ea199ff7681ab6bf75fc4b3c5fe641cb1b065c5bf6e9ff1d3`.
Evidence manifest commitment: `5833fdc966851f620a5b2a053b089c35f8235c389a3edeb821fcba3ec4dc64ca`.

## Accepted verdict

- Revision: **1**, verdict **COMPLIANT**, criterion statuses **PASS / PASS**, integrity **VERIFIED**.
- Decision hash: `bdb7db6f1c10a7c43f1a547582942b6c8db16e5ce714b948187126a8adc217a4`.
- Decision hash independently reproduced from canonical JSON after excluding citation wording and timestamp, as specified in SECURITY.md.
- Findings cite actual verbatim HTTP 403/no-disclosure and HTTP 404/401 observations.
- All fixture observations are explicitly synthetic; no real company was assessed.

## Earlier diagnostic deployment

The earlier address `0xD88e39f9474Eb416868903Da90604Def6a80B0CB` is **not** the submitted deployment. Its first evaluation failed because a documentation example used `Response.status_code`; the exact stable SDK exposes `Response.status`. The actual traceback was inspected, the minimal fix was committed, affected checks passed, and the corrected exact source was redeployed at the canonical address above. No successful judgment is claimed for the earlier failed evaluation.

## Final settlement and withdrawal

Both additional transactions are **FINALIZED**, **MAJORITY_AGREE**, Normal Full Consensus, GenVM **SUCCESS**:
- Settle: https://explorer-studio.genlayer.com/tx/0x7b0511f6be36e1c5c9b3832d6bad157a16989edb85850ade22cb2646394ca886
- Withdraw: https://explorer-studio.genlayer.com/tx/0x8756d5a93acf269a90f3edd8f71b5d61b0c7a5a20f01d42a6e5beed1262cf800

Finalized `get_audit("0")`: **SETTLED**, revision **1**, settlement verdict **COMPLIANT**, sponsor credit **0**, submitter allocation **2 GEN**, settled at `1791804335`, decision hash unchanged.

After finalized withdrawal:
- `get_credit(submitter)`: **0**.
- `get_accounting()`: `{"audits_created":1,"liability":0}`.
- Contract simulated balance: **0 GEN**.
- Submitter simulated account balance: **11 GEN**, from 10 GEN faucet balance minus 1 GEN bond plus 2 GEN payout.

This directly verifies simulated value delivery and complete escrow recovery, not merely a cleared internal ledger. Real chain-layer payout integration remains outside Studionet's simulated environment. Settlement and withdrawal replay rejection are covered by offline tests; no redundant live replay transaction was submitted.

The withdrawal emitted a separate finalized simulated value-transfer transaction: https://explorer-studio.genlayer.com/tx/0x471f36682582f3d68e75e4c1cad457c46844070ba4059da9d17d5625ca083162. Explorer shows it as an outgoing Send to the submitter; it is additional to the six GenVM transactions above.
