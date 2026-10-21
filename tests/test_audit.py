"""Trilha observável da sessão, inclusive após revogação."""
import json
import unittest

from elo.server import DemoSession


class AuditTests(unittest.TestCase):
    def test_no_tools_before_consent_and_state_reads_do_not_create_events(self):
        session = DemoSession()
        before = session.public_state()["audit"]
        self.assertEqual(session.public_state()["audit"], before)
        self.assertEqual([entry["event"] for entry in before], ["session_started"])
        self.assertNotIn(session.csrf, json.dumps(before))

    def test_consent_approval_monitoring_and_revocation_are_visible(self):
        session = DemoSession()
        session.set_consent(True)
        report_id = session.report["report_id"]
        session.approve(report_id, "budget-plan")
        session.approve(report_id, "budget-plan")
        session.monitor()
        session.set_consent(False)
        state = session.public_state()
        events = [entry["event"] for entry in state["audit"]]
        self.assertEqual(events.count("action_approved"), 1)
        self.assertIn("tools_consulted", events)
        self.assertIn("event_observed", events)
        self.assertEqual(events[-1], "consent_revoked")
        self.assertNotIn("results", state["report"])
        self.assertEqual(state["history"], [])
        self.assertEqual(state["goals"], [])

    def test_audit_is_bounded_and_public_copy_is_isolated(self):
        session = DemoSession()
        for _ in range(220):
            session.record("event", "Exemplo")
        audit = session.public_state()["audit"]
        self.assertEqual(len(audit), 200)
        self.assertEqual(audit[-1]["sequence"], 221)
        audit.clear()
        self.assertEqual(len(session.audit), 200)

    def test_scenario_reset_keeps_audit_but_sessions_are_isolated(self):
        session = DemoSession()
        session.set_consent(True)
        session.set_scenario("pix")
        self.assertIn("scenario_selected", [entry["event"] for entry in session.audit])
        self.assertEqual(len(DemoSession().audit), 1)
