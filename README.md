# RNA Protocol

**Reactive Non-Fungible Artifacts** is a proposed CKB-native protocol for persistent game asset identity, evolving state, and enforceable rights.

## Architecture RFC

[RNA Protocol / 0: CKB-Native Game Assets and State Protocol — Draft 0.2](docs/RNA_Protocol_0_Architecture_RFC_en_v0.2.md)

The English architecture and security RFC, dated 1 November 2026, proposes a dual-Cell RNA Native profile:

- An **Asset Cell** retains a unique identity and uses the holder's existing CKB wallet Lock.
- A separate **State Cell** records accepted game-state commitments, policy, and scoped update authority.
- Type Scripts enforce canonical lineage binding, coupled asset transfers, and lifecycle constraints.

The initial profile targets independent L1 operation. Game Sessions and adapters for Morph, Myelin, and Fiber are optional or future work, with their implementation and trust boundaries described in the RFC. RNA does not depend on Spore, DOB, or Mutant.

RNA is an open protocol intended for adoption by independent games. UTXOPlay is an intended integration, not a consensus dependency.

## Status

This repository currently contains design documentation, not a deployed implementation. Draft 0.2 leaves specification details, adversarial liveness, evidence availability, and future settlement profiles open. It does not claim audited RNA contracts or production NFT settlement through Morph or Myelin.
