import io
import json
import os
import unittest
from unittest.mock import patch

from radar_comercial.analysis import analyze_case


class FakeHttpResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeLlmProvider:
    def __init__(self):
        self.calls = []

    def generate_report_narrative(self, *, case, report):
        self.calls.append({"case": case, "report": report})
        return {
            "summary": f"LLM summary para {case['company']}",
            "rationale": "LLM rationale enriquecido.",
        }


class LlmProviderIntegrationTest(unittest.TestCase):
    def test_analyze_case_preserves_rules_without_provider(self):
        report = analyze_case(
            {
                "company": "Acme",
                "objective": "ordenar seguimiento",
                "pain_points": ["seguimiento manual"],
                "signals": ["pidió demo"],
                "risks": ["pipeline roto"],
                "case_type": "inbound_hot",
            }
        )

        self.assertEqual(report["priority"], "alta")
        self.assertEqual(report["summary"], "Acme necesita ordenar seguimiento.")
        self.assertIn("demo orientada a cierre", report["rationale"])

    def test_analyze_case_can_enrich_summary_and_rationale_with_provider(self):
        provider = FakeLlmProvider()

        report = analyze_case(
            {
                "company": "Acme",
                "objective": "ordenar seguimiento",
                "pain_points": ["seguimiento manual"],
                "signals": ["pidió demo"],
                "risks": ["pipeline roto"],
                "case_type": "inbound_hot",
            },
            llm_provider=provider,
        )

        self.assertEqual(report["priority"], "alta")
        self.assertEqual(report["summary"], "LLM summary para Acme")
        self.assertEqual(report["rationale"], "LLM rationale enriquecido.")
        self.assertEqual(len(provider.calls), 1)

    def test_analyze_case_can_use_provider_from_env_automatically(self):
        env = {
            "RADAR_LLM_PROVIDER": "deepseek",
            "DEEPSEEK_API_KEY": "secret",
        }
        llm_payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "summary": "Resumen realzado por LLM",
                                "rationale": "Rationale realzado por LLM",
                            },
                            ensure_ascii=False,
                        )
                    }
                }
            ]
        }
        with patch.dict(os.environ, env, clear=True), patch(
            "radar_comercial.llm_provider.urllib.request.urlopen",
            return_value=FakeHttpResponse(llm_payload),
        ):
            report = analyze_case(
                {
                    "company": "Acme",
                    "objective": "ordenar seguimiento",
                    "pain_points": ["seguimiento manual"],
                    "signals": ["pidió demo"],
                    "risks": ["pipeline roto"],
                    "case_type": "inbound_hot",
                }
            )

        self.assertEqual(report["summary"], "Resumen realzado por LLM")
        self.assertEqual(report["rationale"], "Rationale realzado por LLM")
        self.assertEqual(report["llm_provider"], "deepseek")
        self.assertEqual(report["llm_model"], "deepseek-chat")


if __name__ == "__main__":
    unittest.main()
