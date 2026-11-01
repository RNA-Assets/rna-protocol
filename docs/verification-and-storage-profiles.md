# Verification, settlement and storage profiles

Design clarification accompanying [RNA/0 Draft 0.3](RNA_Protocol_0_Architecture_RFC_en_v0.3.md). The dual-Cell reference layout and invariants remain in force. This note distinguishes acceptance mechanisms and alternative storage designs; it adds no deployed verifier, new wire fields or conforming single-Cell profile.

## What a verifier accepts

A schema check establishes an encoding, field types and bounds. A transition check relates an accepted prior State to an action and a permitted successor. For a recipe, that can include exact ingredient consumption, output calculation, required authority and an issuance budget. For game execution, it also needs a committed program, starting context and admitted inputs.

A pinned verifier can execute a complete transition function; its fixed code identity does not limit it to schema validation. Conversely, a signature check plus `level <= 100` permits an authorised authority to endorse level 99 without supplying a battle history. That deployment advertises attestation and its protected limits. Refusing a fabricated result requires a stronger acceptance predicate, with the required input evidence available.

The game client can display provisional or invalid values. Canonical L1 changes remain conditional on the asset's actual acceptance path. The State Type must enforce both its kernel checks and the selected verifier; merely including a verifier hash or code Cell does not invoke its logic. An implementation using VM calls or an execution hand-off must preserve every required core check across that boundary.

## Policy identity as a verification contract

The existing `policy_hash` can commit to a canonical descriptor containing:

- Verifier code identity, version, configuration and invocation ABI.
- State and action schemas, plus the permitted transition scope.
- Input identities, authentication, ordering, replay protection, time and randomness policies.
- Execution program/runtime identity and a resource envelope, when execution evidence is used.
- Evidence encoding, required payloads and retention/retrieval assumptions.
- L1 acceptance mechanism, settlement selection, challenge/fallback conditions and applicable authority scheme.
- Declared administrator powers and policy migration/consent conditions.

This is a descriptor proposal, not a frozen Molecule structure. A supported profile must define its canonical bytes and bounds, make its schema identity agree with the State fields and bind every required value in the action/proof statement. The descriptor must remain within the definition's protected rights and migration rules. It cannot delegate the Asset Type's identity, custody, carrier or owner-control invariants away.

For direct verification, a small CKB-VM policy can check the specific economic transition without executing the surrounding game. An execution profile can use deterministic game code and traces. Different games may commit different code/configuration and State schemas while sharing the kernel and transition interface.

## Replay, finality and L1 acceptance

Keep the three Draft 0.3 acceptance profiles. Replay is an evidence and verification method, rather than an additional guarantee level automatically attached to a receipt.

| Mechanism used by an application | L1 acceptance classification |
|---|---|
| Operator or committee signs a result, including after local replay | `ATTESTED`; disclose that authority/quorum and what it checks |
| The L1 verifier directly checks the recipe, transition or bounded replay | `SCRIPT_VERIFIED`; identify the actual relation checked |
| L1 verifies a validity proof of the declared transition relation | `PROOF_VERIFIED`; identify the program, public inputs and proof assumptions |
| An optimistic claim becomes acceptable after an executable dispute procedure | `PROOF_VERIFIED` under that specified dispute construction, including deadlines, challenge access, data and final claim selection |

Executing signature-verification code in CKB-VM still gives an attested result when the signature is the decisive game-result evidence. A proof whose statement establishes only an authority's signature retains that authority dependency. Descriptions must identify the computation and input assumptions covered, not just the tool producing the evidence.

[Myelin's session lifecycle](https://github.com/Myelin-Labs/Myelin/blob/main/docs/interactions/session-flow.md) binds application and execution context at genesis, executes finite Cell transitions and preserves history/evidence. Its closed-validator finality module determines session acceptance separately from VM transition verification. The application authenticates command identities and payloads; the [session-safety contracts](https://github.com/Myelin-Labs/Myelin/blob/main/docs/architecture/session-safety.md) explicitly require application binding and recovery-evidence verification.

An RNA/Myelin integration must connect that evidence to an L1 acceptance path. Local verification, a finalised session block or a recovery-evidence gate cannot independently authorise an arbitrary CKB custody withdrawal. The public verifier/court/DA deployment is still an implementation boundary. The exact proof or accepted quorum, live custody, prior anchor, result selection, replay protection and obtainable exit data must all be specified by the adapter.

## Input and rule assumptions

Signed chess moves, a starting board, move counters and pinned deterministic rules can establish a reproducible position. A server's omission of an admitted move or a timeout claim needs additional admission, availability and clock rules. For real-time games, an execution trace checks the supplied simulation; the profile must state how it handles discarded inputs, external observations, randomness and privileged commands.

Legal, authenticated commands can come from an assisted client or bot. Preventing aimbot-assisted input requires evidence beyond the replayed command stream; the execution verifier must state the behaviour it actually checks.

A declared `ADMIN_GRANT_LEVEL` action may be valid under faithfully executed rules. Administrator powers, supply limits and upgrade conditions therefore need inspection before assets are issued. Input authentication and correct execution do not choose a fair game economy for holders.

An optimistic or chunked verification design must specify the disputable statement, data access, challenge authority, bounded execution and the L1 verdict actually consumed. A pointer to a chunk or proof hash is insufficient evidence for those promised checks.

## Settlement responsibilities

Execution produces a candidate. Settlement accepts a result as authoritative for the asset and resolves the affected claims. The path must authenticate the exact prior State and policy, ownership/custody epoch, admission or funding context, selected candidate, required proof/authority and available output material. It retires competing claims and prevents a repeated exit under that context.

For an unencumbered direct-L1 item, a verified State successor is already the settlement of that update. An admitted Session may carry provisional rewards and binding losses before its final result. It requires the promised selection/fallback procedure. Custody can require a separate paired withdrawal. The owner-control proposal in RFC Section 6.3 addresses State contention; evidence production and game input fairness have their own predicates.

## When a separate State Cell is useful

Choose physical storage from the signing, update and recovery requirements. Verifier strength and settlement cadence are independent choices.

| Requirement | Candidate representation | Required boundary |
|---|---|---|
| Collectible or skin with no independently persistent upgrades | One immutable asset plus runtime use checks | Precisely describe the entitlements the application offers |
| Rare item update approved by the holder | One mutable Cell under an ordinary holder Lock | Every replacement needs holder authorisation; this consent model must fit losses and obligations |
| Independent game updates through a specialised Lock | One mutable Cell with constrained owner/game branches | Type-enforced field/Capacity preservation, supported signing integration and a liveness/exit mechanism for the shared input |
| Independent game writes while preserving an ordinary holder Lock | Draft 0.3 Asset/State reference pair | Reciprocal lifecycle checks, live Asset dependency, owner control and the extra carrier |
| Many low-value items updated together | Runtime or shared application State, with explicit settlement and selected identity anchors | Valid root selection, per-item data/proofs, authorised claims and independently usable exit |

The four transition classes describe logical item effects. The normative paired genesis, per-item State lineage and wire layout in Draft 0.3 define the dual-Cell reference profile. A single-Cell or shared-root design needs its own contracts, encoding and conformance rules before it can claim that profile's guarantees. An ordinary Spore used as a skin can be appropriate without adopting RNA evolution at all.

A custom single-Cell Lock can authorise both owner spends and scoped game updates. Its Type still enforces who may change each field and how custody/termination work. Both writers consume the same input; the independent-Asset pause argument cannot simply be transplanted into that one-Cell shape.

Spore plus an enforced dependent State also has a separate asset-side input. That structural property is shared with native dual-Cell RNA. Both require a deliberately authorised control-only spend and State validity rules that stop ordinary writes after the control action. The Native reference proposal expresses this through mutable Asset control fields; an equivalent Spore profile needs its own binding/control encoding. An immutable Spore payload does not by itself rule out such a profile. The existing abstract model exercises the native proposal, not a completed Spore implementation.

A Spore managed Lock must preserve State binding across permitted successor Locks/custody contracts. A Type-level Mutant can keep that restriction attached across Lock changes and can retain ordinary wallet Locks, with its reference configured in the Spore's immutable content type. Native RNA chooses its own data layout, Type boundaries and lifecycle rather than inheriting that format and extension interface. A matched comparison must implement the same required controls and recovery conditions on both sides.

The independent control path is particularly relevant when a writer can keep advancing the L1 State input and the deployment promises departure without that writer's cooperation. Cooperative, infrequent or application-ledger flows may use different handoff/closing procedures. Shared input separation alone does not establish a valid pause branch, data availability or a time bound on chain inclusion.

Shared roots can reduce per-item storage, but root updates can stale a proof/dependency needed by another transaction. The profile must define authoritative snapshots and bounded recovery, as well as leaf availability and claim uniqueness. Faster off-chain execution can batch updates for any compatible storage profile; it does not itself choose a safe L1 exit protocol.

## Acceptance cases to add to implementations

- A schema-valid successor violating the declared recipe is rejected by a direct verification profile.
- A correctly signed invented match result is accepted only with the documented attestation assumptions, not relabelled as independently proved execution.
- Stale program/configuration, substituted inputs, invalid actor authority, replayed commands and disallowed administrator actions are rejected by the selected verifier.
- A local replay receipt cannot enter a stronger L1 branch without its required proof or completed dispute result.
- Missing dispute data, conflicting candidates, reused custody contexts and duplicate exits cannot bypass settlement selection.
- Custom single-Cell and shared-root implementations demonstrate their own signing, contention and recovery cases before making liveness claims.
