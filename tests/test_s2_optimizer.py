"""Cross-method checks and deliberately corrupted assignments for the S2 model."""

import copy
from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bootplacement.audit import audit_baseline
from bootplacement.reference import load_reference
from bootplacement.s2_model import formulate, scaled, solve_placement
from bootplacement.s2_oracle import enumerate_tiny, tiny_examples
from bootplacement.s2_placement import reconstruct
from bootplacement.s2_validation import validate_solution


class S2OptimizerTests(unittest.TestCase):
    """Test correctness at model, reconstruction, scoring and rejection boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.reference = load_reference()
        cls.example = tiny_examples()[2]
        e = cls.example
        cls.solution = solve_placement(e["nodes"], e["edges"], e["level"], time_limit_seconds=10)

    def validate(self, solution):
        e = self.example
        return validate_solution(e["nodes"], e["edges"], solution, self.reference)

    def test_all_tiny_optima_match_exhaustive_search_and_hand_calculation(self):
        for e in tiny_examples():
            with self.subTest(example=e["id"]):
                exhaustive = enumerate_tiny(e["nodes"], e["edges"], e["level"])
                found = solve_placement(e["nodes"], e["edges"], e["level"], time_limit_seconds=10)
                checked = validate_solution(e["nodes"], e["edges"], found, self.reference)
                self.assertEqual(found["status"], "OPTIMAL")
                self.assertGreater(exhaustive["complete_placements"], 0)
                self.assertEqual(Decimal(exhaustive["minimum_decimal_ms"]), Decimal(e["hand_cost_ms"]))
                self.assertEqual(Decimal(checked["audit"]["latency_decimal_ms"]), Decimal(e["hand_cost_ms"]))

    def test_shared_refresh_and_identical_drop_are_single_nodes(self):
        checked = self.validate(self.solution)
        self.assertEqual(checked["audit"]["n_b2"], 4)
        self.assertEqual(sum(n[1] == "Bootstrap2" for n in checked["nodes"]), 1)
        self.assertEqual(sum(n[1] == "Modswitch" for n in checked["nodes"]), 1)

    def test_cost_tampering_is_rejected(self):
        bad = copy.deepcopy(self.solution)
        bad["objective_scaled"] += 1
        with self.assertRaisesRegex(ValueError, "objective disagrees"):
            self.validate(bad)

    def test_claimed_levels_cannot_override_computed_levels(self):
        bad = copy.deepcopy(self.solution)
        bad["original_input_levels"]["a"] = 14
        with self.assertRaisesRegex(ValueError, "input level disagrees"):
            self.validate(bad)

    def test_missing_edge_decision_is_rejected(self):
        bad = copy.deepcopy(self.solution)
        bad["edge_decisions"].pop()
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            self.validate(bad)

    def test_illegal_b2_is_rejected_before_scoring(self):
        nodes = tiny_examples()[0]["nodes"]
        with self.assertRaisesRegex(ValueError, "B2 requires"):
            reconstruct(nodes, [("s", "a", 1)],
                        [{"from": "s", "to": "a", "ciphertexts": 1, "refresh": 2, "delivered_level": 1}],
                        {"s": 0, "a": 0})

    def test_modswitch_cannot_raise_a_level(self):
        nodes = tiny_examples()[0]["nodes"]
        with self.assertRaisesRegex(ValueError, "increase level"):
            reconstruct(nodes, [("s", "a", 1)],
                        [{"from": "s", "to": "a", "ciphertexts": 1, "refresh": 0, "delivered_level": 1}],
                        {"s": 0, "a": 0})

    def test_both_refresh_types_can_exist_after_same_producer(self):
        nodes = [("s", "Identity", 0, ""), ("a", "PCMM3", 2, ""), ("b", "Mul", 1, "")]
        edges = [("s", "a", 8), ("s", "b", 8)]
        decisions = [{"from": "s", "to": "a", "ciphertexts": 8, "refresh": 1, "delivered_level": 14},
                     {"from": "s", "to": "b", "ciphertexts": 8, "refresh": 2, "delivered_level": 1}]
        placed = reconstruct(nodes, edges, decisions, {"s": 0, "a": 12, "b": 0})
        checked = audit_baseline(nodes, edges, *placed, 0)
        self.assertEqual((checked["n_b1"], checked["n_b2"]), (8, 4))

    def test_b2_cannot_deliver_level_fourteen(self):
        e = self.example
        bad = copy.deepcopy(self.solution)
        bad["edge_decisions"][0]["refresh"] = 2
        bad["edge_decisions"][0]["delivered_level"] = 14
        with self.assertRaisesRegex(ValueError, "increase level"):
            reconstruct(e["nodes"], e["edges"], bad["edge_decisions"], bad["original_output_levels"])

    def test_bound_cannot_exceed_objective(self):
        bad = copy.deepcopy(self.solution)
        bad["best_bound_scaled"] = bad["objective_scaled"] + 10
        with self.assertRaisesRegex(ValueError, "Bound exceeds"):
            self.validate(bad)

    def test_unknown_status_cannot_be_presented_as_a_solution(self):
        bad = copy.deepcopy(self.solution)
        bad["status"] = "UNKNOWN"
        with self.assertRaisesRegex(ValueError, "non-feasible status"):
            self.validate(bad)

    def test_feasible_status_cannot_be_labelled_optimal(self):
        bad = copy.deepcopy(self.solution)
        bad["status"] = "FEASIBLE"
        with self.assertRaisesRegex(ValueError, "Optimality flag"):
            self.validate(bad)

    def test_reported_gap_is_checked(self):
        bad = copy.deepcopy(self.solution)
        bad["relative_gap"] = 0.5
        with self.assertRaisesRegex(ValueError, "gap disagrees"):
            self.validate(bad)

    def test_shared_activation_tampering_is_rejected(self):
        bad = copy.deepcopy(self.solution)
        bad["shared_refreshes"] = []
        with self.assertRaisesRegex(ValueError, "activation disagrees"):
            self.validate(bad)

    def test_precision_loss_and_invalid_input_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "precision"):
            scaled("0.00001")
        e = self.example
        for value in (-1, 15, 1.5, True):
            with self.subTest(level=value), self.assertRaisesRegex(ValueError, "Invalid input"):
                formulate(e["nodes"], e["edges"], value)

    def test_exhaustive_search_cannot_accidentally_run_on_course_blocks(self):
        with self.assertRaisesRegex(ValueError, "restricted to tiny"):
            enumerate_tiny(*self.reference.get_mlp_empty(), 0)


if __name__ == "__main__":
    unittest.main()
