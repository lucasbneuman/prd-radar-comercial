import os
import unittest
from unittest.mock import patch

from radar_comercial.llm_provider import (
    LlmProviderConfig,
    build_llm_provider_from_env,
    enrich_report_with_provider,
)


class FakeProvider:
    def generate_report_narrative(self, *, case, report):
        return {"summary": f"Narrativa {case['company']}", "rationale": "Rationale generado"}


class LlmProviderConfigTest(unittest.TestCase):
    def test_build_provider_returns_none_without_required_env(self):
        with patch.dict(os.environ, {}, clear=True):
            provider = build_llm_provider_from_env()
        self.assertIsNone(provider)

    def test_build_provider_supports_deepseek_defaults(self):
        env = {
            "RADAR_LLM_PROVIDER": "deepseek",
            "DEEPSEEK_API_KEY": "secret",
        }
        with patch.dict(os.environ, env, clear=True):
            provider = build_llm_provider_from_env()

        self.assertIsNotNone(provider)
        self.assertEqual(provider.config.provider, "deepseek")
        self.assertEqual(provider.config.model, "deepseek-chat")
        self.assertEqual(provider.config.base_url, "https://api.deepseek.com")

    def test_build_provider_supports_generic_openai_compatible_config(self):
        env = {
            "RADAR_LLM_PROVIDER": "openai-compatible",
            "RADAR_LLM_API_KEY": "secret",
            "RADAR_LLM_BASE_URL": "https://llm.example.com/v1",
            "RADAR_LLM_MODEL": "demo-model",
        }
        with patch.dict(os.environ, env, clear=True):
            provider = build_llm_provider_from_env()

        self.assertIsNotNone(provider)
        self.assertEqual(provider.config.provider, "openai-compatible")
        self.assertEqual(provider.config.model, "demo-model")
        self.assertEqual(provider.config.base_url, "https://llm.example.com/v1")

    def test_enrich_report_with_provider_falls_back_if_provider_errors(self):
        class BrokenProvider:
            def generate_report_narrative(self, *, case, report):
                raise RuntimeError("boom")

        report = {"summary": "base", "rationale": "base rationale"}
        enriched = enrich_report_with_provider(
            case={"company": "Acme"},
            report=report,
            llm_provider=BrokenProvider(),
        )
        self.assertEqual(enriched, report)

    def test_enrich_report_with_provider_uses_provider_when_available(self):
        report = {"summary": "base", "rationale": "base rationale"}
        enriched = enrich_report_with_provider(
            case={"company": "Acme"},
            report=report,
            llm_provider=FakeProvider(),
        )
        self.assertEqual(enriched["summary"], "Narrativa Acme")
        self.assertEqual(enriched["rationale"], "Rationale generado")


if __name__ == "__main__":
    unittest.main()
