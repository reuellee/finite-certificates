#!/usr/bin/env python3
"""Unit tests for the producer's deliberately narrow formula machinery.

These are producer tests, not independent Q0 acceptance.
"""

from __future__ import annotations

import copy
import json
import unittest
from fractions import Fraction
from pathlib import Path

import build_qualification as q


class FormulaCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        q.main()

    def test_m3_is_derived_from_formulas(self):
        payload = q.m3_formulas()
        results = {}
        for name, pair in payload["pairs"].items():
            compiled = q.compile_simplex_formula(
                pair["space"], pair["relative"], payload["simplex_barycentric_polynomials"]
            )
            results[name] = q.relative_h1(compiled)["h1_q"]
        self.assertEqual(results, {"M3_UNFILLED": 1, "M3_FILLED": 0})

    def test_m3_same_one_skeleton(self):
        payload = q.m3_formulas()
        complexes = []
        for pair in payload["pairs"].values():
            compiled = q.compile_simplex_formula(
                pair["space"], pair["relative"], payload["simplex_barycentric_polynomials"]
            )
            complexes.append({tuple(face) for face in compiled["faces"] if len(face) <= 2})
        self.assertEqual(complexes[0], complexes[1])

    def test_out_of_sublanguage_polynomial_is_rejected(self):
        payload = q.m3_formulas()
        pair = copy.deepcopy(payload["pairs"]["M3_FILLED"])
        x_plus_y = q.padd(q.pvar(2, 0), q.pvar(2, 1))
        pair["space"] = q.junction("and", pair["space"], q.atom("ge", x_plus_y))
        with self.assertRaisesRegex(ValueError, "OUTSIDE_EXACT_AFFINE_SIMPLEX_SUBLANGUAGE"):
            q.compile_simplex_formula(
                pair["space"], pair["relative"], payload["simplex_barycentric_polynomials"]
            )

    def test_noncanonical_polynomial_is_rejected(self):
        poly = {"type": "integer_polynomial", "terms": [
            {"coefficient": 1, "exponents": [1, 0]},
            {"coefficient": 1, "exponents": [0, 0]},
        ]}
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            q.pinternal(poly)

    def test_m2_exact_limit_witness(self):
        payload = q.m2_formula()
        union = payload["selected_plus_terminal"]
        for n in range(1, 100):
            self.assertTrue(q.eval_formula(union, (Fraction(1, n), Fraction(3, 2))))
        self.assertFalse(q.eval_formula(union, (Fraction(0), Fraction(3, 2))))
        result = q.analyze_m2(payload)
        self.assertFalse(result["complex_emitted"])

    def test_global_algebra_dimensions(self):
        schema = q.global_algebra_schema()
        counts = schema["counts"]
        self.assertEqual(counts["parent_bracket_occurrences"], 70)
        self.assertEqual(counts["derived_normal_rows"], 56)
        self.assertEqual(counts["derived_normal_coefficient_occurrences"], 224)
        self.assertLessEqual(counts["max_parent_bracket_degree"], 3)
        self.assertLessEqual(counts["max_derived_normal_coefficient_degree"], 3)

    def test_scope_fails_before_required_triple_denominator(self):
        scope = q.discrete_scope_accounting()
        self.assertEqual(scope["certified_finite_inputs"]["realizable_unlabelled_parent_types"], 2604)
        self.assertEqual(
            scope["first_missing_required_denominator"]["id"],
            "ALL_PARENT_PROPER_REGION_AND_PAIRWISE_INCOMPARABILITY_CLASSIFICATION",
        )

    def test_generated_result_fails_closed(self):
        result = json.loads((Path(__file__).with_name("RESULT.json")).read_text(encoding="utf-8"))
        self.assertEqual(result["q0_classification"], "NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND")
        self.assertFalse(result["q0_pass"])
        self.assertFalse(result["q1_eligible"])
        self.assertEqual(result["theorem_credit"], "NONE")
        self.assertFalse(result["cloud_used"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
