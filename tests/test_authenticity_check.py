import asyncio
import json
from app.services.voice_auditor import VoiceAuditor
from app.llm.providers.mock import MockLLMClient


def test_authenticity_check_scanner():
    async def _run():
        audit_json = {
            "score": 90,
            "passed": True,
            "cadence_analysis": "Ritmo fluido.",
            "issues": [],
        }
        mock_llm = MockLLMClient(default_response=json.dumps(audit_json))
        auditor = VoiceAuditor(llm_client=mock_llm)

        # Texto con palabras infladas prohibidas: "crucial", "optimizar"
        draft_with_inflated = (
            "Es crucial entender cómo optimizar el desarrollo de software. "
            "Esta herramienta es fundamental e innovadora."
        )

        report = await auditor.audit(draft_with_inflated)

        assert report.passed is False
        assert "crucial" in report.inflated_words_detected
        assert "optimizar" in report.inflated_words_detected
        assert "fundamental" in report.inflated_words_detected
        assert "innovadora" in report.inflated_words_detected
        assert len(report.warnings) > 0
        assert report.authenticity_score < 90

    asyncio.run(_run())
