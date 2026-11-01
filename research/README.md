# Protocol research models

[`writer_racing_model.py`](writer_racing_model.py) is a small executable abstraction supporting the owner-control proposal in [RFC Draft 0.3](../docs/RNA_Protocol_0_Architecture_RFC_en_v0.3.md#63-owner-control-and-writer-racing).

```sh
python3 research/writer_racing_model.py
```

All 17 checks passed on 1 November 2026. They exercise 0–127 ordinary State writes before pause, both update/pause orderings, dead dependencies, paused successors, resume replay rejection, protected fields, owner authorisation, retained Session certificates, one-shot finalisation, settled wear, transfer restrictions and a timeout anchored to the closing Asset.

The model abstracts actual Lock verification, signatures, game evidence, Cell identity/resolution and `since` maturity. It does not compile or execute RNA scripts, replay CKB transactions, validate Molecule encodings or cover multi-item composition. It is not a conformance test suite or a deployed implementation. The RFC's gates remain planned acceptance requirements.
