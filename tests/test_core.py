from copy import deepcopy
from datetime import date
import unittest
from elo.core import (
    build_report, cashflow, load_scenario, apply_saving, safety, purchase, validate,
    _installment_dates, _split_installments,
)
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
            {
                "id": "a",
                "date": "2026-10-08",
                "label": "Saída",
                "amount_cents": 200000,
                "direction": "out",
                "flexible": False,
            },
            {
                "id": "b",
                "date": "2026-10-08",
                "label": "Entrada",
                "amount_cents": 200000,
                "direction": "in",
                "flexible": False,
            },
        ]
        self.assertEqual(cashflow(data)["minimum_cents"], 150000)

    def test_invalid_and_duplicate_amounts_are_rejected(self):
        for bad in [-1, 1.5, True]:
            data = load_scenario("month")
            data["events"][0]["amount_cents"] = bad
            with self.assertRaises(ValueError):
                cashflow(data)
        data = load_scenario("month")
        data["events"].append(deepcopy(data["events"][0]))
        with self.assertRaises(ValueError):
            cashflow(data)

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
        data["events"] = [e for e in data["events"] if e["id"] != "leisure"] + [
            {
                "id": "leis1",
                "date": "2026-10-13",
                "label": "Lazer A",
                "amount_cents": 15000,
                "direction": "out",
                "flexible": True,
            },
            {
                "id": "leis2",
                "date": "2026-10-13",
                "label": "Lazer B",
                "amount_cents": 15000,
                "direction": "out",
                "flexible": True,
            },
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
        data["events"][-1]["date"] = "2026-10-20"
        result = cashflow(data)
        self.assertLess(result["minimum_cents"], 0)
        # With no income event the balance stays negative throughout.
        self.assertIsNotNone(result["first_negative_date"])
        self.assertLess(result["closing_cents"], 0)


class ApprovalTests(unittest.TestCase):
    def test_no_consent_no_read_or_action(self):
        session = DemoSession()
        self.assertNotIn("results", session.report)
        with self.assertRaises(PermissionError):
            session.approve("x", "budget-plan")

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
        with self.assertRaises(ValueError):
            session.approve(old, "budget-plan")

    def test_revocation_blocks_pending_actions_and_clears_session_plans(self):
        session = DemoSession()
        session.set_consent(True)
        old = session.report["report_id"]
        session.approve(old, "budget-plan")
        session.set_consent(False)
        self.assertEqual(session.history, [])
        self.assertNotIn("results", session.report)
        with self.assertRaises(PermissionError):
            session.approve(old, "budget-plan")

    def test_monitoring_updates_projection(self):
        session = DemoSession()
        session.set_consent(True)
        session.approve(session.report["report_id"], "budget-plan")
        session.monitor()
        self.assertEqual(session.report["results"]["cashflow"]["minimum_cents"], 5000)
        with self.assertRaises(ValueError):
            session.monitor()

    def test_sessions_do_not_share_plans_or_consent(self):
        first, second = DemoSession(), DemoSession()
        first.set_consent(True)
        first.approve(first.report["report_id"], "budget-plan")
        self.assertFalse(second.consent)
        self.assertEqual(second.history, [])

    def test_fake_payment_action_is_rejected(self):
        session = DemoSession()
        session.set_consent(True)
        with self.assertRaises(ValueError):
            session.approve(session.report["report_id"], "send_pix")

    def test_failed_planner_is_disclosed(self):
        class BrokenPlanner:
            def plan(self, snapshot):
                raise RuntimeError("error")

        report = build_report(load_scenario("month"), True, BrokenPlanner())
        self.assertEqual(report["mode"], "demo_fallback")
        self.assertIsNotNone(report["warning"])

    def test_policy_keeps_mandatory_safety_tools(self):
        class LimitedPlanner:
            def plan(self, snapshot):
                return ["guidance"]

        report = build_report(load_scenario("pix"), True, LimitedPlanner())
        self.assertEqual(report["mode"], "watsonx")
        self.assertIn("safety", report["results"])
        self.assertIn("cashflow", report["results"])

    # ── T6: malformed watsonx output variants ────────────────────────────────
    def test_watsonx_planner_raises_falls_back(self):
        class Exploding:
            def plan(self, snapshot):
                raise RuntimeError("timeout")

        report = build_report(load_scenario("month"), True, Exploding())
        self.assertEqual(report["mode"], "demo_fallback")
        self.assertIsNotNone(report["warning"])

    def test_watsonx_returns_none_falls_back(self):
        class ReturnsNone:
            def plan(self, snapshot):
                return None

        report = build_report(load_scenario("month"), True, ReturnsNone())
        self.assertEqual(report["mode"], "demo_fallback")

    def test_watsonx_unknown_tool_name_falls_back(self):
        class UnknownTool:
            def plan(self, snapshot):
                return ["cashflow", "hack"]

        report = build_report(load_scenario("month"), True, UnknownTool())
        self.assertEqual(report["mode"], "demo_fallback")

    def test_watsonx_empty_list_falls_back(self):
        class EmptyList:
            def plan(self, snapshot):
                return []

        report = build_report(load_scenario("month"), True, EmptyList())
        self.assertEqual(report["mode"], "demo_fallback")

    def test_watsonx_tools_list_too_long_falls_back(self):
        class TooManyTools:
            def plan(self, snapshot):
                return ["cashflow", "purchase", "safety", "guidance", "extra"]

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


class InstallmentTests(unittest.TestCase):
    """Testes para a projeção de compras parceladas."""

    # ── helpers ──────────────────────────────────────────────────────────────

    def _purchase_snapshot(self, as_of, horizon, balance, price, installments, extra_events=None):
        """Monta um snapshot mínimo de compra para uso nos testes."""
        snap = {
            "title": "Teste de compra parcelada", "synthetic": True,
            "as_of": as_of, "horizon": horizon, "balance_cents": balance,
            "buffer_cents": 0, "typical_pix_cents": 10000,
            "events": extra_events or [],
            "purchase": {"label": "Item de teste", "price_cents": price, "installments": installments},
        }
        return snap

    # ── I1: distribuição de parcelas em datas mensais ─────────────────────────

    def test_installment_dates_monthly_preserves_reference_day(self):
        dates = _installment_dates(date(2026, 1, 15), 3)
        self.assertEqual(dates, [date(2026, 1, 15), date(2026, 2, 15), date(2026, 3, 15)])

    def test_installment_dates_clamps_to_last_day_of_short_month(self):
        # Dia 31 em Janeiro → Fevereiro não tem dia 31, usa o último
        dates = _installment_dates(date(2026, 1, 31), 3)
        self.assertEqual(dates[0], date(2026, 1, 31))
        self.assertEqual(dates[1], date(2026, 2, 28))
        self.assertEqual(dates[2], date(2026, 3, 31))

    def test_installment_dates_leap_year_february(self):
        # 2024 é ano bissexto: fev tem 29 dias
        dates = _installment_dates(date(2024, 1, 31), 2)
        self.assertEqual(dates[1], date(2024, 2, 29))
        # 2025 não é bissexto: fev tem 28 dias
        dates2 = _installment_dates(date(2025, 1, 31), 2)
        self.assertEqual(dates2[1], date(2025, 2, 28))

    def test_installment_dates_year_rollover(self):
        dates = _installment_dates(date(2026, 11, 10), 3)
        self.assertEqual(dates, [date(2026, 11, 10), date(2026, 12, 10), date(2027, 1, 10)])

    # ── I2: divisão exata das parcelas ────────────────────────────────────────

    def test_split_installments_exact_division(self):
        values = _split_installments(30000, 3)
        self.assertEqual(values, [10000, 10000, 10000])
        self.assertEqual(sum(values), 30000)

    def test_split_installments_remainder_distributed_to_first(self):
        values = _split_installments(10, 3)
        # 10 // 3 = 3, remainder 1 → [4, 3, 3]
        self.assertEqual(values, [4, 3, 3])
        self.assertEqual(sum(values), 10)

    def test_split_installments_sum_equals_price_various(self):
        for price, n in [(35001, 10), (100, 3), (1, 2), (99, 7)]:
            values = _split_installments(price, n)
            self.assertEqual(sum(values), price, f"Falha para price={price}, n={n}")
            self.assertEqual(len(values), n)

    # ── I3: compra com parcela única ──────────────────────────────────────────

    def test_single_installment_purchase(self):
        snap = self._purchase_snapshot("2026-10-07", "2026-10-15", 500000, 100000, 1)
        result = purchase(snap)
        self.assertTrue(result["available"])
        self.assertEqual(result["installments"], 1)
        self.assertEqual(result["first_installment_cents"], 100000)
        self.assertEqual(len(result["schedule"]), 1)
        self.assertEqual(result["out_of_horizon"], 0)
        self.assertEqual(result["schedule"][0]["amount_cents"], 100000)
        self.assertEqual(result["schedule"][0]["date"], "2026-10-07")
        # Com 1 parcela, projeção == base - primeira parcela
        self.assertEqual(result["installment_projected_minimum_cents"], result["installment_minimum_cents"])

    # ── I4: várias parcelas distribuídas mensalmente ──────────────────────────

    def test_multi_installment_schedule_within_horizon(self):
        # Horizonte de 3 meses para garantir 3 parcelas dentro
        snap = self._purchase_snapshot("2026-10-07", "2026-12-31", 600000, 30000, 3)
        result = purchase(snap)
        self.assertEqual(len(result["schedule"]), 3)
        self.assertEqual(result["out_of_horizon"], 0)
        dates = [e["date"] for e in result["schedule"]]
        self.assertEqual(dates, ["2026-10-07", "2026-11-07", "2026-12-07"])
        # Soma deve ser igual ao preço
        total = sum(e["amount_cents"] for e in result["schedule"])
        self.assertEqual(total, 30000)

    def test_multi_installment_sum_equals_price_with_remainder(self):
        # 7 parcelas, preço 100: 100 // 7 = 14 rem 2 → [15,15,14,14,14,14,14]
        snap = self._purchase_snapshot("2026-10-07", "2027-04-30", 500000, 100, 7)
        result = purchase(snap)
        self.assertEqual(len(result["schedule"]), 7)
        total = sum(e["amount_cents"] for e in result["schedule"])
        self.assertEqual(total, 100)
        self.assertEqual(result["schedule"][0]["amount_cents"], 15)
        self.assertEqual(result["schedule"][1]["amount_cents"], 15)
        self.assertEqual(result["schedule"][2]["amount_cents"], 14)

    # ── I5: recálculo do menor saldo com parcelas projetadas ──────────────────

    def test_projected_minimum_accounts_for_all_scheduled_installments(self):
        # 3 parcelas de 10000, horizonte que inclui todas as 3
        snap = self._purchase_snapshot("2026-10-01", "2026-12-31", 100000, 30000, 3)
        result = purchase(snap)
        self.assertEqual(result["out_of_horizon"], 0)
        # Saldo inicial 100000; parcelas 10000 cada em out, nov, dez
        # Menor saldo: após a 3ª parcela = 100000 - 10000 - 10000 - 10000 = 70000
        self.assertEqual(result["installment_projected_minimum_cents"], 70000)
        self.assertEqual(result["installment_projected_closing_cents"], 70000)

    def test_projected_closing_balance(self):
        snap = self._purchase_snapshot("2026-10-01", "2026-12-31", 200000, 30000, 3)
        result = purchase(snap)
        # 200000 - 3×10000 = 170000
        self.assertEqual(result["installment_projected_closing_cents"], 170000)

    # ── I6: parcelas fora do horizonte ────────────────────────────────────────

    def test_out_of_horizon_installments_are_not_included(self):
        # Horizonte curto: apenas 1ª parcela cabe (5 parcelas de 20000 cada)
        snap = self._purchase_snapshot("2026-10-07", "2026-10-15", 500000, 100000, 5)
        result = purchase(snap)
        self.assertEqual(len(result["schedule"]), 1)
        self.assertEqual(result["out_of_horizon"], 4)
        # Projeção usa apenas 1 parcela de 20000; 500000 - 20000 = 480000
        self.assertEqual(result["installment_projected_minimum_cents"], 480000)

    def test_out_of_horizon_count_in_assumption(self):
        snap = self._purchase_snapshot("2026-10-07", "2026-10-15", 500000, 100000, 5)
        result = purchase(snap)
        self.assertIn("4 parcela(s) fora do horizonte", result["assumption"])

    def test_all_installments_within_horizon_no_out_of_horizon(self):
        snap = self._purchase_snapshot("2026-10-07", "2026-12-31", 500000, 30000, 3)
        result = purchase(snap)
        self.assertEqual(result["out_of_horizon"], 0)
        self.assertIn("Todas as parcelas estão dentro do horizonte", result["assumption"])

    # ── I7: cenário original não é alterado ───────────────────────────────────

    def test_original_scenario_preserved_after_purchase(self):
        original = load_scenario("purchase")
        original_events = deepcopy(original["events"])
        purchase(original)
        # Eventos originais não devem ter sido modificados
        self.assertEqual(original["events"], original_events)

    def test_original_scenario_preserved_deep_copy(self):
        snap = self._purchase_snapshot("2026-10-07", "2026-12-31", 500000, 30000, 3)
        snap_copy = deepcopy(snap)
        purchase(snap)
        self.assertEqual(snap["events"], snap_copy["events"])

    # ── I8: compra à vista preservada ────────────────────────────────────────

    def test_cash_purchase_fields_unchanged(self):
        result = purchase(load_scenario("purchase"))
        self.assertEqual(result["cash_minimum_cents"], -30000)
        # Saldo de encerramento: 500000 - 180000 + 280000 = 600000; à vista: 600000 - 350000 = 250000
        self.assertEqual(result["cash_closing_cents"], 250000)
        # preço à vista correto
        self.assertEqual(result["price_cents"], 350000)

    # ── I9: fim de mês e datas limite ────────────────────────────────────────

    def test_end_of_month_day_clamp_in_schedule(self):
        # Dia 31 de outubro → novembro só tem 30 dias
        snap = self._purchase_snapshot("2026-10-31", "2026-12-31", 500000, 20000, 2)
        result = purchase(snap)
        self.assertEqual(len(result["schedule"]), 2)
        self.assertEqual(result["schedule"][0]["date"], "2026-10-31")
        self.assertEqual(result["schedule"][1]["date"], "2026-11-30")

    # ── I10: rejeição de valores inválidos (mantém validações existentes) ─────

    def test_invalid_price_is_rejected(self):
        for bad_price in [-1, 1.5, True, "100"]:
            snap = self._purchase_snapshot("2026-10-07", "2026-10-15", 500000, 0, 1)
            snap["purchase"]["price_cents"] = bad_price
            with self.assertRaises((ValueError, TypeError)):
                purchase(snap)

    def test_invalid_installment_count_is_rejected(self):
        for bad_n in [0, 61, -1, 1.5, "2"]:
            snap = self._purchase_snapshot("2026-10-07", "2026-10-15", 500000, 100000, 1)
            snap["purchase"]["installments"] = bad_n
            with self.assertRaises((ValueError, TypeError)):
                purchase(snap)

    def test_zero_price_single_installment(self):
        snap = self._purchase_snapshot("2026-10-07", "2026-10-15", 500000, 0, 1)
        result = purchase(snap)
        self.assertTrue(result["available"])
        self.assertEqual(result["schedule"][0]["amount_cents"], 0)
        self.assertEqual(sum(e["amount_cents"] for e in result["schedule"]), 0)


if __name__ == "__main__":
    unittest.main()
