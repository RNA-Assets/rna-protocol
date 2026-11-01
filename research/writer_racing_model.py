"""Executable owner-control state-machine model, not a CKB contract implementation.

Dependency liveness is an assumed CKB consensus predicate, checked separately
against RFC 0022 and ckb-types::resolve_transaction. Signatures and game-result
verification are abstract predicates here. The tests check transition rules and
adversarial ordering, not VM execution, cryptography, networking, or mainnet safety.
"""
from dataclasses import dataclass, replace
import unittest


class Rejected(Exception):
    pass


def require(condition, reason):
    if not condition:
        raise Rejected(reason)


@dataclass(frozen=True)
class Asset:
    outpoint: int = 0
    owner: str = "Alice"
    epoch: int = 4
    definition: str = "definition-42"
    state_type: str = "canonical-state-42"
    capacity: int = 202
    mode: str = "OPEN"
    floor: int | None = None
    session: str | None = None
    created_at: int = 0
    transferable: bool = True


@dataclass(frozen=True)
class State:
    outpoint: int = 0
    sequence: int = 46
    durability: int = 63
    owner_epoch: int = 4
    custodian: str = "Alice"
    close_context: int | None = None


@dataclass(frozen=True)
class GameTx:
    state_input: int
    asset_dep: int
    signed_asset_anchor: int
    new_durability: int
    kind: str = "UPDATE"
    valid_game_evidence: bool = True
    signed_kind: str = "UPDATE"
    signed_session: str | None = None


class Model:
    delay = 6

    def __init__(self):
        self.asset = Asset()
        self.state = State()

    def game_tx(self, durability=None, kind="UPDATE"):
        return GameTx(self.state.outpoint, self.asset.outpoint,
                      self.asset.outpoint,
                      self.state.durability if durability is None else durability,
                      kind, signed_kind=kind, signed_session=self.asset.session)

    def apply_game(self, tx):
        require(tx.state_input == self.state.outpoint, "spent State input")
        require(tx.asset_dep == self.asset.outpoint, "dead Asset dependency")
        require(tx.valid_game_evidence, "invalid game evidence")
        require(tx.signed_kind == tx.kind, "wrong signed action domain")
        require(self.state.owner_epoch == self.asset.epoch, "custody epoch mismatch")
        require(self.state.custodian == self.asset.owner, "custody snapshot mismatch")
        if tx.kind == "UPDATE":
            require(tx.signed_asset_anchor == tx.asset_dep, "wrong signed control anchor")
            require(self.asset.mode in {"OPEN", "BOUND"}, "ordinary writing is closed")
            close = self.state.close_context
        else:
            require(tx.kind == "FINAL", "unknown game action")
            require(self.asset.mode == "CLOSING", "not a closing context")
            require(tx.signed_session == self.asset.session, "wrong admitted Session")
            require(self.state.close_context != self.asset.outpoint,
                    "final State already recorded for this close")
            close = self.asset.outpoint
        require(0 <= tx.new_durability <= self.state.durability, "invalid wear")
        if self.asset.floor is not None:
            require(tx.new_durability >= self.asset.floor, "admitted wear bound exceeded")
        self.state = replace(self.state, outpoint=self.state.outpoint + 1,
                             sequence=self.state.sequence + 1,
                             durability=tx.new_durability, close_context=close)

    def control(self, old_asset, new_mode, height=0, owner_signature=True,
                proposed=None, touches_state=False):
        require(old_asset == self.asset.outpoint, "spent Asset input")
        require(owner_signature, "owner signature required")
        require(not touches_state, "control action must not manufacture State effects")
        allowed = {("OPEN", "PAUSED"), ("PAUSED", "OPEN"), ("BOUND", "CLOSING")}
        require((self.asset.mode, new_mode) in allowed, "forbidden control transition")
        expected = replace(self.asset, outpoint=self.asset.outpoint + 1,
                           mode=new_mode, created_at=height)
        proposed = expected if proposed is None else proposed
        require(proposed == expected, "protected Asset field changed")
        self.asset = proposed

    def admit(self, asset_input, state_input, floor, height=0, owner_signature=True):
        require(asset_input == self.asset.outpoint, "spent Asset input")
        require(state_input == self.state.outpoint, "spent State input")
        require(owner_signature, "owner signature required for admission")
        require(self.asset.mode in {"OPEN", "PAUSED"}, "already encumbered")
        require(0 <= floor <= self.state.durability, "invalid admitted floor")
        self.asset = replace(self.asset, outpoint=self.asset.outpoint + 1,
                             mode="BOUND", floor=floor, created_at=height,
                             session=f"session-from-{asset_input}-{state_input}")
        self.state = replace(self.state, outpoint=self.state.outpoint + 1,
                             sequence=self.state.sequence + 1, close_context=None)

    def exit(self, asset_input, state_input, height=0, recipient="Carol",
             owner_signature=True):
        require(asset_input == self.asset.outpoint, "spent Asset input")
        require(state_input == self.state.outpoint, "spent State input")
        require(owner_signature, "owner signature required for transfer")
        require(self.asset.transferable, "transfer policy forbids this destination")
        require(self.asset.mode in {"OPEN", "PAUSED", "CLOSING"}, "active obligation")
        durability = self.state.durability
        if self.asset.mode == "CLOSING":
            finalised = self.state.close_context == self.asset.outpoint
            if not finalised:
                require(height >= self.asset.created_at + self.delay,
                        "relative close delay not mature")
                durability = min(durability, self.asset.floor)
        self.asset = replace(self.asset, outpoint=self.asset.outpoint + 1,
                             owner=recipient, epoch=self.asset.epoch + 1,
                             mode="OPEN", floor=None, session=None, created_at=height)
        self.state = replace(self.state, outpoint=self.state.outpoint + 1,
                             sequence=self.state.sequence + 1,
                             durability=durability, owner_epoch=self.asset.epoch,
                             custodian=recipient, close_context=None)


class OwnerControlTests(unittest.TestCase):
    def test_state_writes_never_stale_an_owner_control_input(self):
        for writes in range(128):
            m = Model()
            freeze_input = m.asset.outpoint
            for _ in range(writes):
                m.apply_game(m.game_tx())
            latest = m.state
            m.control(freeze_input, "PAUSED")
            self.assertEqual(m.state, latest)

    def test_old_dependency_and_new_paused_dependency_both_stop_updates(self):
        m = Model()
        old = m.game_tx(60)
        m.control(m.asset.outpoint, "PAUSED")
        with self.assertRaisesRegex(Rejected, "dead Asset"):
            m.apply_game(old)
        with self.assertRaisesRegex(Rejected, "writing is closed"):
            m.apply_game(m.game_tx(60))

    def test_both_block_orderings_have_a_defined_cutoff(self):
        m = Model()
        old = m.game_tx(60)
        control_input = m.asset.outpoint
        m.apply_game(old)
        m.control(control_input, "PAUSED")
        self.assertEqual(m.state.durability, 60)
        with self.assertRaises(Rejected):
            m.apply_game(m.game_tx(59))
        m = Model()
        old = m.game_tx(60)
        m.control(m.asset.outpoint, "PAUSED")
        with self.assertRaises(Rejected):
            m.apply_game(old)

    def test_resume_requires_fresh_asset_anchor_in_game_authorisation(self):
        m = Model()
        old = m.game_tx(60)
        m.control(m.asset.outpoint, "PAUSED")
        m.control(m.asset.outpoint, "OPEN")
        with self.assertRaisesRegex(Rejected, "wrong signed"):
            m.apply_game(replace(old, asset_dep=m.asset.outpoint))
        m.apply_game(m.game_tx(60))

    def test_control_cannot_change_protected_asset_fields(self):
        mutations = dict(owner="Mallory", epoch=99, definition="forged",
                         state_type="other-lineage", capacity=201,
                         transferable=False, floor=0, session="forged")
        for field, value in mutations.items():
            m = Model()
            output = replace(m.asset, outpoint=1, mode="PAUSED")
            with self.assertRaisesRegex(Rejected, "protected Asset"):
                m.control(0, "PAUSED", proposed=replace(output, **{field: value}))

    def test_game_authority_cannot_invoke_owner_control_or_change_state_through_it(self):
        m = Model()
        with self.assertRaisesRegex(Rejected, "owner signature"):
            m.control(0, "PAUSED", owner_signature=False)
        with self.assertRaisesRegex(Rejected, "State effects"):
            m.control(0, "PAUSED", touches_state=True)

    def test_admission_and_transfer_require_owner_authorisation(self):
        m = Model()
        with self.assertRaisesRegex(Rejected, "owner signature"):
            m.admit(0, 0, floor=58, owner_signature=False)
        with self.assertRaisesRegex(Rejected, "owner signature"):
            m.exit(0, 0, owner_signature=False)

    def test_retained_final_certificate_uses_session_and_separate_action_domain(self):
        m = Model()
        m.admit(0, 0, floor=58)
        retained = m.game_tx(60, kind="FINAL")
        ordinary = m.game_tx(60)
        m.control(m.asset.outpoint, "CLOSING", height=20)
        with self.assertRaisesRegex(Rejected, "action domain"):
            m.apply_game(replace(ordinary, asset_dep=m.asset.outpoint, kind="FINAL"))
        with self.assertRaisesRegex(Rejected, "admitted Session"):
            m.apply_game(replace(retained, asset_dep=m.asset.outpoint,
                                 signed_session="other-session"))
        m.apply_game(replace(retained, asset_dep=m.asset.outpoint))
        self.assertEqual(m.state.durability, 60)

    def test_exit_preserves_confirmed_wear_and_ownership_epoch(self):
        m = Model()
        m.apply_game(m.game_tx(60))
        m.control(m.asset.outpoint, "PAUSED")
        m.exit(m.asset.outpoint, m.state.outpoint)
        self.assertEqual(m.state.durability, 60)
        self.assertEqual(m.state.owner_epoch, 5)
        self.assertEqual(m.state.custodian, "Carol")

    def test_pause_preserves_transfer_restrictions(self):
        m = Model()
        m.asset = replace(m.asset, transferable=False)
        m.control(m.asset.outpoint, "PAUSED")
        with self.assertRaisesRegex(Rejected, "transfer policy"):
            m.exit(m.asset.outpoint, m.state.outpoint)

    def bound_closing(self):
        m = Model()
        m.admit(m.asset.outpoint, m.state.outpoint, floor=58)
        m.apply_game(m.game_tx(61))
        m.control(m.asset.outpoint, "CLOSING", height=20)
        return m

    def test_bound_session_cannot_use_unconditional_pause_or_exit(self):
        m = Model()
        m.admit(0, 0, floor=58)
        with self.assertRaisesRegex(Rejected, "forbidden control"):
            m.control(m.asset.outpoint, "PAUSED")
        with self.assertRaisesRegex(Rejected, "active obligation"):
            m.exit(m.asset.outpoint, m.state.outpoint)

    def test_closing_allows_one_final_state_and_blocks_routine_updates(self):
        m = self.bound_closing()
        with self.assertRaisesRegex(Rejected, "writing is closed"):
            m.apply_game(m.game_tx(60))
        m.apply_game(m.game_tx(59, kind="FINAL"))
        with self.assertRaisesRegex(Rejected, "already recorded"):
            m.apply_game(m.game_tx(58, kind="FINAL"))

    def test_final_before_owner_exit_causes_at_most_one_rebuild(self):
        m = self.bound_closing()
        state_input = m.state.outpoint
        close_anchor = m.asset.outpoint
        m.apply_game(m.game_tx(59, kind="FINAL"))
        with self.assertRaisesRegex(Rejected, "spent State"):
            m.exit(close_anchor, state_input, height=26)
        m.exit(close_anchor, m.state.outpoint, height=26)
        self.assertEqual(m.state.durability, 59)

    def test_timeout_uses_fixed_asset_anchor_and_admitted_fallback(self):
        m = self.bound_closing()
        with self.assertRaisesRegex(Rejected, "not mature"):
            m.exit(m.asset.outpoint, m.state.outpoint, height=25)
        m.exit(m.asset.outpoint, m.state.outpoint, height=26)
        self.assertEqual(m.state.durability, 58)

    def test_timeout_first_invalidates_late_final_dependency(self):
        m = self.bound_closing()
        late = m.game_tx(60, kind="FINAL")
        m.exit(m.asset.outpoint, m.state.outpoint, height=26)
        with self.assertRaises(Rejected):
            m.apply_game(late)

    def test_operator_cannot_exceed_admitted_loss(self):
        m = self.bound_closing()
        with self.assertRaisesRegex(Rejected, "wear bound"):
            m.apply_game(m.game_tx(57, kind="FINAL"))

    def test_every_legal_final_result_preserves_bounded_recovery(self):
        for final in range(58, 62):
            m = self.bound_closing()
            close = m.asset
            m.apply_game(m.game_tx(final, kind="FINAL"))
            self.assertEqual(m.asset, close)
            self.assertEqual(m.asset.created_at + m.delay, 26)
            m.exit(m.asset.outpoint, m.state.outpoint, height=26)
            self.assertEqual(m.state.durability, final)


if __name__ == "__main__":
    unittest.main(verbosity=2)
