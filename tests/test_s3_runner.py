"""Adversarial coverage, evidence and failure-path checks for full-instance runs."""

import copy
from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bootplacement import s3_runner as s3
from bootplacement.reference import load_reference


class S3RunnerTests(unittest.TestCase):
    """Reject misleading coverage or scores and retain all failed attempts."""

    @classmethod
    def setUpClass(cls):
        cls.config_path = s3.ROOT / "configs/s3-all-instances.json"
        cls.config = s3.read_json(cls.config_path)
        cls.reference = load_reference()

    def case(self, case_id="attention-L00"):
        value = s3.read_json(s3.S2 / "cases" / (case_id + ".json"))
        value["outcome"] = "improved"
        return value

    def ledger(self):
        cases = []
        for module, level in s3.INSTANCES:
            case_id = f"{module}-L{level:02}"
            if (s3.S2 / "cases" / (case_id + ".json")).exists():
                cases.append(self.case(case_id))
            else:
                cases.append({"case_id": case_id, "module": module, "l_init": level,
                    "l_max": 14, "baseline_decimal_ms": "53558.1718", "outcome": "no_solution",
                    "solution": {"status": "UNKNOWN", "has_solution": False},
                    "validated": None, "comparison": None, "resources": None})
        return cases

    def test_required_matrix_has_exactly_thirty_unique_instances(self):
        values = s3.validate_config(self.config)
        self.assertEqual(len(values), 30)
        self.assertEqual(len(set(values)), 30)

    def test_partial_attention_cannot_claim_full_stage(self):
        bad = copy.deepcopy(self.config)
        bad["instances"]["attention"] = [0, 9, 14]
        with self.assertRaisesRegex(ValueError, "all 15 levels"):
            s3.validate_config(bad)

    def test_duplicate_level_cannot_replace_missing_level(self):
        bad = copy.deepcopy(self.config)
        bad["instances"]["attention"][-1] = 13
        with self.assertRaisesRegex(ValueError, "exactly once"):
            s3.validate_config(bad)

    def test_boolean_level_is_not_an_integer_input(self):
        bad = copy.deepcopy(self.config)
        bad["instances"]["mlp"][1] = True
        with self.assertRaisesRegex(ValueError, "Integer"):
            s3.validate_config(bad)

    def test_missing_module_is_rejected(self):
        bad = copy.deepcopy(self.config)
        del bad["instances"]["attention"]
        with self.assertRaisesRegex(ValueError, "Both required"):
            s3.validate_config(bad)

    def test_invalid_resource_settings_are_rejected(self):
        for key, value in (("time_limit_seconds", float("nan")), ("time_limit_seconds", -1),
                           ("time_limit_seconds", True), ("workers", 8), ("seed", -1)):
            bad = copy.deepcopy(self.config)
            bad["solver"][key] = value
            with self.subTest(setting=key, value=value), self.assertRaises(ValueError):
                s3.validate_config(bad)

    def test_saved_valid_case_is_reconstructed_and_scored(self):
        s3.validate_case(self.case(), self.reference)

    def test_wrong_case_input_cannot_reuse_another_score(self):
        bad = self.case()
        bad["l_init"] = 1
        with self.assertRaisesRegex(ValueError, "identity"):
            s3.validate_case(bad, self.reference)

    def test_changed_baseline_cannot_inflate_improvement(self):
        bad = self.case()
        bad["baseline_decimal_ms"] = "99999"
        with self.assertRaisesRegex(ValueError, "Baseline comparison"):
            s3.validate_case(bad, self.reference)

    def test_tampered_saved_dag_is_rejected(self):
        bad = self.case()
        bad["validated"]["edges"].pop()
        with self.assertRaisesRegex(ValueError, "Saved DAG"):
            s3.validate_case(bad, self.reference)

    def test_nonfinite_resource_observation_is_rejected(self):
        bad = self.case()
        bad["resources"]["pipeline_wall_seconds"] = float("nan")
        with self.assertRaisesRegex(ValueError, "observed time"):
            s3.validate_case(bad, self.reference)

    def test_unsolved_case_cannot_keep_an_accepted_placement(self):
        bad = self.case()
        bad["solution"]["has_solution"] = False
        bad["solution"]["status"] = "UNKNOWN"
        bad["outcome"] = "no_solution"
        with self.assertRaisesRegex(ValueError, "Unsolved case"):
            s3.validate_case(bad, self.reference)

    def test_partial_success_has_gaps_not_passed_status(self):
        totals = s3.summarise(self.ledger())
        self.assertEqual(totals["status"], "gaps")
        self.assertEqual(totals["cases_improved"], 18)
        self.assertEqual(totals["cases_completed"], 30)

    def test_missing_and_duplicate_case_records_are_rejected(self):
        cases = self.ledger()
        for bad in (cases[:-1], cases[:-1] + [cases[0]]):
            with self.assertRaisesRegex(ValueError, "30-case coverage"):
                s3.summarise(bad)

    def test_fabricated_improvement_flag_is_rejected(self):
        cases = self.ledger()
        cases[0]["comparison"]["improved"] = False
        with self.assertRaisesRegex(ValueError, "comparison is inconsistent"):
            s3.summarise(cases)

    def test_solver_errors_are_saved_for_all_thirty_cases(self):
        # Fault injection performs no course placement search. The temporary
        # directory is constrained to ignored repository-local test output.
        with tempfile.TemporaryDirectory(prefix="local-s3-test-", dir=s3.ROOT / "results") as folder:
            folder = Path(folder).resolve()
            self.assertTrue(folder.is_relative_to(s3.ROOT / "results"))
            output = folder / "failed-run"
            saved_examples = s3.read_json(s3.S2 / "tiny-examples.json")
            with patch.object(s3, "solve_placement", side_effect=ValueError("injected solver failure")), \
                 patch.object(s3, "run_examples", return_value=saved_examples), redirect_stdout(io.StringIO()):
                record = s3.run(self.config_path, output)
            self.assertEqual(record["status"], "failed")
            self.assertEqual(record["cases_with_errors"], 30)
            self.assertEqual(len(list((output / "cases").glob("*.json"))), 30)
            self.assertEqual(set(record["case_states"].values()), {"error"})
            s3.verify(output)
            # Even when hashes are recomputed, semantic verification must catch
            # a fabricated successful summary rather than trusting its manifest.
            summary = s3.read_json(output / "summary.json")
            summary["status"] = "passed"
            s3.write_json(output / "summary.json", summary)
            manifest = s3.read_json(output / "artifacts.sha256.json")
            manifest["summary.json"] = s3.digest(output / "summary.json")
            s3.write_json(output / "artifacts.sha256.json", manifest)
            with self.assertRaisesRegex(ValueError, "Summary JSON"):
                s3.verify(output)


if __name__ == "__main__":
    unittest.main()
