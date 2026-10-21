from copy import deepcopy
import unittest
from elo.core import build_report, cashflow, load_scenario, apply_saving, safety, purchase, validate
from elo.server import DemoSession


class CashflowTests(unittest.TestCase):
    def test_gap_before_income_even_with_positive_closing_balance(self):
        report = cashflow(load_scenario("month"))
        self.assertEqual(report["minimum_cents"], -10000)
        self.assertEqual(report["first_negative_date"], "2026-10-13")
        self.assertEqual(report["closing_cents"], 170000)

    def test_plan_reaches_buffer_without_cutting_essential_expenses(self):
        original = load_scenario("month")
        changed = apply_saving(original, 30000)
        self.assertEqual(cashflow(changed)["minimum_cents"], 20000)
        self.assertEqual(original["events"][3]["amount_cents"], 30000)
        for before, after in zip(original["events"], changed["events"]):
            if not before["flexible"]:
                self.assertEqual(before, after)

    def test_insufficient_flexible_spending_does_not_claim_success(self):
        data = load_scenario("month")
        data["balance_cents"] = 100000
        action = build_report(data, True)["actions"][0]
        self.assertFalse(action["meets_buffer"])
        self.assertEqual(action["reduction_cents"], 30000)

    def test_same_day_events_are_combined_before_daily_projection(self):
        data = load_scenario("month")
        data["events"] = [
            {"id":"a","date":"2026-10-08","label":"Saída","amount_cents":200000,"direction":"out","flexible":False},
            {"id":"b","date":"2026-10-08","label":"Entrada","amount_cents":200000,"direction":"in","flexible":False}]
        self.assertEqual(cashflow(data)["minimum_cents"], 150000)

    def test_invalid_and_duplicate_amounts_are_rejected(self):
        for bad in [-1, 1.5, True]:
            data = load_scenario("month")
            data["events"][0]["amount_cents"] = bad
            with self.assertRaises(ValueError): cashflow(data)
        data = load_scenario("month")
        data["events"].append(deepcopy(data["events"][0]))
        with self.assertRaises(ValueError): cashflow(data)

    def test_purchase_shows_cash_gap_and_limited_installment_horizon(self):
        comparison = purchase(load_scenario("purchase"))
        self.assertEqual(comparison["cash_minimum_cents"], -30000)
        self.assertEqual(comparison["first_installment_cents"], 35000)
        self.assertEqual(comparison["installment_minimum_cents"], 285000)

    def test_pix_is_an_alert_never_a_payment_or_fraud_confirmation(self):
        result = safety(load_scenario("pix"))
        self.assertEqual(len(result["reasons"]), 3)
        self.assertFalse(result["payment_executed"])
        self.assertIn("não provam fraude", result["limitation"])

    # ── T1: zero balance ─────────────────────────────────────────────────────
    def test_zero_balance_with_upcoming_bills_goes_immediately_negative(self):
        data = load_scenario("month")
        data["balance_cents"] = 0
        result = cashflow(data)
        self.assertLess(result["minimum_cents"], 0)
        self.assertIsNotNone(result["first_negative_date"])

    # ── T2: multiple flexible bills on the same day ───────────────────────────
    def test_multiple_same_day_flexible_bills_apply_saving_distributes(self):
        data = load_scenario("month")
        # Replace leisure event with two flexible events on same day
        data["events"] = [
            e for e in data["events"] if e["id"] != "leisure"
        ] + [
            {"id":"leis1","date":"2026-10-13","label":"Lazer A","amount_cents":15000,"direction":"out","flexible":True},
            {"id":"leis2","date":"2026-10-13","label":"Lazer B","amount_cents":15000,"direction":"out","flexible":True},
        ]
        changed = apply_saving(data, 30000)
        flex_total = sum(e["amount_cents"] for e in changed["events"] if e.get("flexible"))
        self.assertEqual(flex_total, 0)
        result = cashflow(changed)
        self.assertGreaterEqual(result["minimum_cents"], 20000)

    def test_non_boolean_flexible_field_is_rejected(self):
        data = load_scenario("month")
        data["events"][0]["flexible"] = 1
        with self.assertRaises(ValueError):
            validate(data)

    # ── T3: delayed income (no income within horizon) ─────────────────────────
    def test_no_income_within_horizon_projections_stay_negative(self):
        data = load_scenario("month")
        data["events"] = [e for e in data["events"] if e["direction"] != "in"]
        result = cashflow(data)
        self.assertLess(result["minimum_cents"], 0)
        # With no income event the balance stays negative throughout.
        self.assertIsNotNone(result["first_negative_date"])
        self.assertLess(result["closing_cents"], 0)


class ApprovalTests(unittest.TestCase):
    def test_no_consent_no_read_or_action(self):
        session = DemoSession()
        self.assertNotIn("results", session.report)
        with self.assertRaises(PermissionError): session.approve("x", "budget-plan")

    def test_approval_is_bound_to_snapshot_and_idempotent(self):
        session = DemoSession()
        session.set_consent(True)
        old = session.report["report_id"]
        session.approve(old, "budget-plan")
        session.approve(old, "budget-plan")
        self.assertEqual(len(session.history), 1)
        self.assertEqual(session.report["results"]["cashflow"]["minimum_cents"], 20000)

    def test_changed_snapshot_requires_fresh_approval(self):
        session = DemoSession()
        session.set_consent(True)
        old = session.report["report_id"]
        session.monitor()
        with self.assertRaises(ValueError): session.approve(old, "budget-plan")

    def test_revocation_blocks_pending_actions_and_clears_session_plans(self):
        session = DemoSession()
        session.set_consent(True)
        old = session.report["report_id"]
        session.approve(old, "budget-plan")
        session.set_consent(False)
        self.assertEqual(session.history, [])
        self.assertNotIn("results", session.report)
        with self.assertRaises(PermissionError): session.approve(old, "budget-plan")

    def test_monitoring_updates_projection(self):
        session = DemoSession()
        session.set_consent(True)
        session.approve(session.report["report_id"], "budget-plan")
        session.monitor()
        self.assertEqual(session.report["results"]["cashflow"]["minimum_cents"], 5000)
        with self.assertRaises(ValueError): session.monitor()

    def test_sessions_do_not_share_plans_or_consent(self):
        first, second = DemoSession(), DemoSession()
        first.set_consent(True)
        first.approve(first.report["report_id"], "budget-plan")
        self.assertFalse(second.consent)
        self.assertEqual(second.history, [])

    def test_fake_payment_action_is_rejected(self):
        session = DemoSession()
        session.set_consent(True)
        with self.assertRaises(ValueError): session.approve(session.report["report_id"], "send_pix")

    def test_failed_planner_is_disclosed(self):
        class BrokenPlanner:
            def plan(self, snapshot): raise RuntimeError("error")
        report = build_report(load_scenario("month"), True, BrokenPlanner())
        self.assertEqual(report["mode"], "demo_fallback")
        self.assertIsNotNone(report["warning"])

    def test_policy_keeps_mandatory_safety_tools(self):
        class LimitedPlanner:
            def plan(self, snapshot): return ["guidance"]
        report = build_report(load_scenario("pix"), True, LimitedPlanner())
        self.assertEqual(report["mode"], "watsonx")
        self.assertIn("safety", report["results"])
        self.assertIn("cashflow", report["results"])

    # ── T6: malformed watsonx output variants ────────────────────────────────
    def test_watsonx_planner_raises_falls_back(self):
        class Exploding:
            def plan(self, snapshot): raise RuntimeError("timeout")
        report = build_report(load_scenario("month"), True, Exploding())
        self.assertEqual(report["mode"], "demo_fallback")
        self.assertIsNotNone(report["warning"])

    def test_watsonx_returns_none_falls_back(self):
        class ReturnsNone:
            def plan(self, snapshot): return None
        report = build_report(load_scenario("month"), True, ReturnsNone())
        self.assertEqual(report["mode"], "demo_fallback")

    def test_watsonx_unknown_tool_name_falls_back(self):
        class UnknownTool:
            def plan(self, snapshot): return ["cashflow", "hack"]
        report = build_report(load_scenario("month"), True, UnknownTool())
        self.assertEqual(report["mode"], "demo_fallback")

    def test_watsonx_empty_list_falls_back(self):
        class EmptyList:
            def plan(self, snapshot): return []
        report = build_report(load_scenario("month"), True, EmptyList())
        self.assertEqual(report["mode"], "demo_fallback")

    def test_watsonx_tools_list_too_long_falls_back(self):
        class TooManyTools:
            def plan(self, snapshot): return ["cashflow", "purchase", "safety", "guidance", "extra"]
        report = build_report(load_scenario("month"), True, TooManyTools())
        self.assertEqual(report["mode"], "demo_fallback")

    def test_scenario_name_invalid_types_are_rejected(self):
        session = DemoSession()
        for bad in [None, 123, "", "x" * 41, {"name": "month"}]:
            with self.subTest(bad=bad):
                with self.assertRaises((ValueError, TypeError, AttributeError)):
                    session.set_scenario(bad)

    def test_unknown_scenario_name_is_rejected(self):
        session = DemoSession()
        with self.assertRaises(ValueError):
            session.set_scenario("nonexistent")


class HTTPTests(unittest.TestCase):
    pass  # HTTP tests live in tests/test_http.py


if __name__ == "__main__": unittest.main()
