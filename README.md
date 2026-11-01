# RNA Protocol

**Reactive Non-Fungible Artifacts** is a proposed CKB-native protocol for persistent game asset identity, evolving state, and enforceable rights.

## Architecture RFC

[RNA Protocol / 0: CKB-Native Game Assets and State Protocol — Draft 0.3](docs/RNA_Protocol_0_Architecture_RFC_en_v0.3.md)

The English architecture and security RFC, dated 1 November 2026, proposes a dual-Cell RNA Native profile:

- An **Asset Cell** retains a unique identity and uses the holder's existing CKB wallet Lock.
- A separate **State Cell** records accepted game-state commitments, policy, and scoped update authority.
- Type Scripts enforce canonical lineage binding, coupled asset transfers, and lifecycle constraints.
- Four core transition classes — **CREATE, EVOLVE, TRANSFER and TERMINATE** — underpin the game-facing item API.
- Scoped grants, atomic recipe manifests and capability discovery expose the policy and evidence required by each operation.
- A restricted owner-control branch proposes **PAUSE/RESUME** without a moving State input. Binding Sessions require explicit admission and a supported closing/settlement profile.

The initial profile targets independent L1 operation. Game Sessions and adapters for Morph, Myelin, and Fiber are optional or future work, with their implementation and trust boundaries described in the RFC. RNA does not depend on Spore, DOB, or Mutant.

RNA is an open protocol intended for adoption by independent games. UTXOPlay is an intended integration, not a consensus dependency.

## Status

This repository contains design documentation and an executable abstract owner-control model. Draft 0.3 proposes live-Asset dependency checks, a limited control-only exception to paired spending, and profile-specific composition/settlement rules. The schema, encodings and script/node verification remain open. No audited RNA contracts or production NFT settlement through Morph or Myelin are claimed.

[Draft 0.2](docs/RNA_Protocol_0_Architecture_RFC_en_v0.2.md) remains available unchanged for historical references. Draft 0.3 changes the proposed layout and I-05; it does not allocate a released wire version.

[Verification, settlement and storage profiles](docs/verification-and-storage-profiles.md) explains pinned policy code, schema/transition/execution checks, replay evidence and the actual L1 acceptance path. It also compares holder-approved single-Cell items, specialised Locks, the dual-Cell reference profile and shared application State.

## Abstract owner-control checks

```sh
python3 research/writer_racing_model.py
```

The 17 checks exercise pause/resume, protected fields, competing State writes, admitted wear, one-shot finalisation and a fixed closing timeout. Signatures, evidence validity, dependency resolution and timing are abstract predicates. These checks do not execute CKB scripts or establish deployment readiness. See [research notes](research/README.md).
