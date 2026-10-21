"""Relevância de paráfrases simples e limites da recuperação semântica local."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from elo.core import KNOWLEDGE, guidance, load_scenario
from elo.retrieval import LocalRetriever


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.index = LocalRetriever(KNOWLEDGE)

    def test_cash_shortfall_paraphrase_finds_calendar_guidance(self):
        result = self.index.retrieve("Dinheiro curto antes do salário", "cashflow")
        self.assertEqual(result["retrieval_mode"], "local_concepts")
        self.assertEqual(result["documents"][0]["id"], "calendar-demo")
        self.assertIn("recebimento", result["documents"][0]["matched_concepts"])

    def test_revocation_paraphrase_finds_consent_guidance(self):
        result = self.index.retrieve("Quero cancelar a permissão de leitura", "cashflow")
        self.assertEqual(result["documents"][0]["id"], "of-consent")
        self.assertIn("consentimento", result["documents"][0]["matched_concepts"])

    def test_urgency_and_transfer_find_verification_guidance(self):
        result = self.index.retrieve("Pressa em uma transferência suspeita", "pix")
        self.assertEqual(result["documents"][0]["id"], "pix-demo")
        self.assertEqual(result["retrieval_mode"], "local_concepts")

    def test_unrelated_question_uses_explicit_topic_fallback(self):
        result = self.index.retrieve("Astronomia nebulosa telescópio", "cashflow")
        self.assertEqual(result["retrieval_mode"], "topic_fallback")
        self.assertTrue(result["documents"])
        self.assertTrue(all("cashflow" in doc["topics"] for doc in result["documents"]))
        self.assertTrue(all(not doc["matched_concepts"] for doc in result["documents"]))
        self.assertIn("não garante cobertura", result["limitation"])

    def test_unknown_topic_never_substitutes_unrelated_documents(self):
        result = self.index.retrieve("Elegibilidade para FGTS", "fgts")
        self.assertEqual(result["documents"], [])
        self.assertEqual(result["retrieval_mode"], "topic_fallback")

    def test_response_mutation_cannot_modify_curated_corpus(self):
        first = self.index.retrieve("saldo salário", "cashflow")
        first["documents"][0]["text"] = "Conteúdo adulterado"
        second = self.index.retrieve("saldo salário", "cashflow")
        self.assertNotEqual(second["documents"][0]["text"], "Conteúdo adulterado")

    def test_guidance_does_not_read_files_on_each_call(self):
        with patch.object(Path, "read_text", side_effect=AssertionError("leitura inesperada")):
            for name in ("month", "purchase", "pix"):
                result = guidance(load_scenario(name))
                self.assertTrue(result["documents"])
                self.assertEqual(result["retrieval_mode"], "local_concepts")

    def test_unsafe_urls_are_removed_from_retrieved_documents(self):
        for url in ("javascript:alert(1)", "https://user:password@example.com", "https:///missing-host"):
            with self.subTest(url=url):
                documents = deepcopy(KNOWLEDGE)
                for document in documents:
                    document["url"] = url
                with patch("elo.core._RETRIEVER", LocalRetriever(documents)):
                    result = guidance(load_scenario("month"))
                self.assertTrue(all(document["url"] is None for document in result["documents"]))


if __name__ == "__main__":
    unittest.main()
