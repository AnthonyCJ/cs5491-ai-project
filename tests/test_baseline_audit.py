"""Small counterexamples for errors that reference-only scoring can miss."""

from decimal import Decimal
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bootplacement.audit import audit_baseline
from bootplacement.reference import load_reference


class BaselineAuditTests(unittest.TestCase):
    """Exercise shared cost, free merging, B2 eligibility and graph preservation."""

    def setUp(self):
        self.base = [("s", "Identity", 0, "input"), ("a", "Mul", 1, "left"),
                     ("b", "Mul", 1, "right"), ("out", "Add", 0, "merge")]
        self.edges = [("s", "a", 8), ("s", "b", 8), ("a", "out", 8), ("b", "out", 8)]

    def shared(self, op="Bootstrap2"):
        nodes = self.base + [("refresh", op, 0, "refresh once")]
        edges = [("s", "refresh", 8), ("refresh", "a", 8), ("refresh", "b", 8)] + self.edges[2:]
        return nodes, edges

    def audit(self, nodes, edges, level=0):
        return audit_baseline(self.base, self.edges, nodes, edges, level)

    def test_shared_bootstrap2_charges_four_pairs_once(self):
        result = self.audit(*self.shared())
        self.assertEqual(result["n_b2"], 4)
        self.assertEqual(result["budget"], 52)
        self.assertEqual(result["depth"], 1)
        self.assertEqual(result["l_out"]["refresh"], 13)
        # Hand calculation: one shared refresh plus two Muls and one Add.
        self.assertEqual(Decimal(result["latency_decimal_ms"]), Decimal("5175.1609"))

    def test_merge_takes_minimum_without_paid_modswitch(self):
        nodes = self.base + [("refresh", "Bootstrap1", 0, "left only")]
        edges = [("s", "refresh", 8), ("refresh", "a", 8), self.edges[1], *self.edges[2:]]
        result = self.audit(nodes, edges, level=5)
        self.assertEqual(result["l_in"]["out"], 4)
        self.assertEqual(result["n_b1"], 8)

    def test_bootstrap2_rejects_four_ciphertexts(self):
        nodes, edges = self.shared()
        self.edges = [(u, v, 4) for u, v, _ in self.edges]
        with self.assertRaisesRegex(ValueError, "requires #ct 8 or 16"):
            self.audit(nodes, [(u, v, 4) for u, v, _ in edges])

    def test_identical_refreshes_must_be_shared(self):
        nodes = self.base + [("r1", "Bootstrap1", 0, ""), ("r2", "Bootstrap1", 0, "")]
        edges = [("s", "r1", 8), ("s", "r2", 8), ("r1", "a", 8), ("r2", "b", 8), *self.edges[2:]]
        with self.assertRaisesRegex(ValueError, "must share"):
            self.audit(nodes, edges)

    def test_removing_original_branch_is_invalid(self):
        nodes, edges = self.shared()
        with self.assertRaisesRegex(ValueError, "changes original edges"):
            self.audit(nodes, edges[:-1])

    def test_modswitch_is_a_level_drop_but_not_depth(self):
        nodes, edges = self.shared()
        nodes += [("down", "Modswitch", 8, "13 to 5")]
        edges = [("s", "refresh", 8), ("refresh", "down", 8), ("down", "a", 8), ("down", "b", 8), *self.edges[2:]]
        result = self.audit(nodes, edges)
        self.assertEqual(result["l_out"]["down"], 5)
        self.assertEqual(result["depth"], 1)
        self.assertEqual(Decimal(result["node_latency_decimal_ms"]["down"]), 0)

    def test_level_underflow_is_invalid(self):
        with self.assertRaisesRegex(ValueError, "outside valid range"):
            self.audit(self.base, self.edges)

    def test_noninteger_level_is_invalid(self):
        with self.assertRaisesRegex(ValueError, "Invalid input level"):
            self.audit(*self.shared(), level=1.5)

    def test_out_of_range_level_is_invalid(self):
        with self.assertRaisesRegex(ValueError, "Invalid input level"):
            self.audit(*self.shared(), level=15)

    def test_zero_drop_modswitch_is_invalid(self):
        nodes = self.base + [("down", "Modswitch", 0, "no drop")]
        edges = [("s", "down", 8), ("down", "a", 8), ("down", "b", 8), *self.edges[2:]]
        with self.assertRaisesRegex(ValueError, "Wrong level cost"):
            self.audit(nodes, edges, level=5)

    def test_cycle_is_invalid(self):
        nodes, edges = self.shared()
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.audit(nodes, edges + [("out", "s", 8)])

    def test_reference_tampering_fails_before_execution(self):
        with patch("bootplacement.reference.Path.read_bytes", return_value=b"changed source"):
            with self.assertRaisesRegex(ValueError, "checksum differs"):
                load_reference()


if __name__ == "__main__":
    unittest.main()
