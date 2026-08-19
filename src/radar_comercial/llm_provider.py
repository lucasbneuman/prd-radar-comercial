from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class ReportNarrativeProvider(Protocol):
    def generate_report_narrative(self, *, case: dict, report: dict) -> dict: ...


@dataclass(frozen=True)
class LlmProviderConfig:
    provider: str
    api_key: str
    model: str
    base_url: str
    timeout_seconds: int = 20


class OpenAiCompatibleNarrativeProvider:
    def __init__(self, config: LlmProviderConfig):
        self.config = config

    def generate_report_narrative(self, *, case: dict, report: dict) -> dict:
        prompt = self._build_prompt(case=case, report=report)
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres Radar Comercial. Reescribe solo el summary y el rationale de un reporte comercial. "
                        "Mantén la prioridad, scoring y próximos pasos existentes. Responde JSON válido con claves "
                        "summary y rationale. Español neutro, concreto y vendible."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            self._chat_completions_url(),
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
            raw = json.loads(response.read().decode("utf-8"))
        content = raw["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise RuntimeError("LLM response content missing")
        narrative = json.loads(content)
        result = {}
        if narrative.get("summary"):
            result["summary"] = str(narrative["summary"]).strip()
        if narrative.get("rationale"):
            result["rationale"] = str(narrative["rationale"]).strip()
        result["llm_provider"] = self.config.provider
        result["llm_model"] = self.config.model
        return result

    def _chat_completions_url(self) -> str:
        return self.config.base_url.rstrip("/") + "/chat/completions"

    @staticmethod
    def _build_prompt(*, case: dict, report: dict) -> str:
        return json.dumps(
            {
                "case": case,
                "report": report,
                "instructions": {
                    "rewrite_summary": True,
                    "rewrite_rationale": True,
                    "preserve_priority": report.get("priority"),
                    "preserve_score_total": report.get("score_total"),
                },
            },
            ensure_ascii=False,
        )


def enrich_report_with_provider(*, case: dict, report: dict, llm_provider: ReportNarrativeProvider | None) -> dict:
    if not llm_provider:
        return report
    try:
        narrative = llm_provider.generate_report_narrative(case=case, report=report)
    except (RuntimeError, ValueError, KeyError, json.JSONDecodeError, urllib.error.URLError):
        return report
    enriched = dict(report)
    if narrative.get("summary"):
        enriched["summary"] = narrative["summary"]
    if narrative.get("rationale"):
        enriched["rationale"] = narrative["rationale"]
    if narrative.get("llm_provider"):
        enriched["llm_provider"] = narrative["llm_provider"]
    if narrative.get("llm_model"):
        enriched["llm_model"] = narrative["llm_model"]
    return enriched


def build_llm_provider_from_env() -> OpenAiCompatibleNarrativeProvider | None:
    provider = os.getenv("RADAR_LLM_PROVIDER", "").strip().lower()
    if not provider:
        return None

    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            return None
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip() or "deepseek-chat"
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip() or "https://api.deepseek.com"
        timeout_seconds = int(os.getenv("RADAR_LLM_TIMEOUT_SECONDS", "20"))
        return OpenAiCompatibleNarrativeProvider(
            LlmProviderConfig(
                provider="deepseek",
                api_key=api_key,
                model=model,
                base_url=base_url,
                timeout_seconds=timeout_seconds,
            )
        )

    if provider == "openai-compatible":
        api_key = os.getenv("RADAR_LLM_API_KEY", "").strip()
        base_url = os.getenv("RADAR_LLM_BASE_URL", "").strip()
        model = os.getenv("RADAR_LLM_MODEL", "").strip()
        if not api_key or not base_url or not model:
            return None
        timeout_seconds = int(os.getenv("RADAR_LLM_TIMEOUT_SECONDS", "20"))
        return OpenAiCompatibleNarrativeProvider(
            LlmProviderConfig(
                provider="openai-compatible",
                api_key=api_key,
                model=model,
                base_url=base_url,
                timeout_seconds=timeout_seconds,
            )
        )

    return None
