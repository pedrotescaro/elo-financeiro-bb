"""Explicações verificáveis e projeção diária em calendários esparsos."""
from datetime import date, timedelta
import unittest

from elo.core import apply_saving, build_report, cashflow, load_scenario


class ExplanationTests(unittest.TestCase):
    def test_each_available_decision_has_data_assumptions_and_exclusions(self):
        for scenario in ("month", "purchase", "pix"):
            with self.subTest(scenario=scenario):
                report = build_report(load_scenario(scenario), True)
                decisions = set(report["results"]) | {action["id"] for action in report["actions"]}
                self.assertEqual(decisions, set(report["explanations"]))
                for explanation in report["explanations"].values():
                    self.assertTrue(explanation["summary"])
                    self.assertTrue(explanation["assumptions"])
                    self.assertTrue(explanation["not_considered"])
                    self.assertTrue(all(type(number["value_cents"]) is int for number in explanation["numbers"]))

    def test_budget_explanation_matches_actual_effect_and_preserves_essentials(self):
        snapshot = load_scenario("month")
        report = build_report(snapshot, True)
        action = next(action for action in report["actions"] if action["id"] == "budget-plan")
        changed = apply_saving(snapshot, action["reduction_cents"])
        numbers = {number["label"]: number["value_cents"] for number in report["explanations"]["budget-plan"]["numbers"]}
        self.assertEqual(numbers["Menor saldo após o ajuste"], cashflow(changed)["minimum_cents"])
        self.assertEqual(numbers["Menor saldo antes"], -10000)
        self.assertEqual(numbers["Redução proposta"], 30000)
        self.assertIn("somente previsões flexíveis", " ".join(report["explanations"]["budget-plan"]["assumptions"]))
        self.assertEqual([event for event in snapshot["events"] if not event["flexible"]],
                         [event for event in changed["events"] if not event["flexible"]])

    def test_partial_improvement_never_claims_margin_is_preserved(self):
        snapshot = load_scenario("month")
        snapshot["balance_cents"] = 100000
        explanation = build_report(snapshot, True)["explanations"]["budget-plan"]
        self.assertIn("ainda não recompõe", explanation["summary"])

    def test_purchase_explanation_discloses_omitted_installments(self):
        report = build_report(load_scenario("purchase"), True)
        explanation = report["explanations"]["purchase"]
        self.assertIn("Parcelas futuras depois da primeira", " ".join(explanation["not_considered"]))
        self.assertIn("sem juros", " ".join(explanation["assumptions"]))
        self.assertIn(35000, [number["value_cents"] for number in explanation["numbers"]])

    def test_pix_explanation_keeps_uncertainty_and_never_confirms_fraud(self):
        explanation = build_report(load_scenario("pix"), True)["explanations"]["safety"]
        self.assertIn("3 sinais ilustrativos", explanation["summary"])
        self.assertIn("não provam fraude", " ".join(explanation["not_considered"]))
        self.assertIn(30000, [number["value_cents"] for number in explanation["numbers"]])

    def test_no_consent_no_financial_explanation_or_retrieval(self):
        report = build_report(load_scenario("month"), False)
        self.assertNotIn("explanations", report)
        self.assertNotIn("results", report)

    def test_late_income_is_excluded_from_used_numbers_and_disclosed(self):
        snapshot = load_scenario("month")
        snapshot["events"][-1]["date"] = "2026-10-20"
        report = build_report(snapshot, True)
        explanation = report["explanations"]["cashflow"]
        numbers = {number["label"]: number["value_cents"] for number in explanation["numbers"]}
        self.assertEqual(numbers["Recebimentos no horizonte"], 0)
        self.assertEqual(numbers["Despesas no horizonte"], 160000)
        self.assertIn("recebimentos atrasados", " ".join(explanation["not_considered"]))


class DailyProjectionTests(unittest.TestCase):
    def test_every_day_has_exactly_one_closing_including_empty_days(self):
        snapshot = load_scenario("month")
        result = cashflow(snapshot)
        start = date.fromisoformat(snapshot["as_of"])
        days = (date.fromisoformat(snapshot["horizon"]) - start).days + 1
        self.assertEqual([row["date"] for row in result["daily"]],
                         [(start + timedelta(days=offset)).isoformat() for offset in range(days)])
        self.assertEqual(result["initial_cents"], 150000)
        self.assertEqual(result["daily"][1]["balance_cents"], result["daily"][2]["balance_cents"])
        self.assertEqual(result["daily"][-1]["balance_cents"], result["closing_cents"])

    def test_initial_day_events_do_not_add_an_extra_opening_balance_point(self):
        snapshot = load_scenario("month")
        snapshot["balance_cents"] = 0
        snapshot["events"] = [
            {"id": "income", "date": snapshot["as_of"], "label": "Renda", "amount_cents": 10000,
             "direction": "in", "flexible": False},
            {"id": "bill", "date": snapshot["as_of"], "label": "Conta", "amount_cents": 4000,
             "direction": "out", "flexible": False},
        ]
        result = cashflow(snapshot)
        self.assertEqual(result["daily"][0]["balance_cents"], 6000)
        self.assertEqual(result["minimum_cents"], 6000)
        self.assertEqual(len({row["date"] for row in result["daily"]}), len(result["daily"]))


if __name__ == "__main__":
    unittest.main()
