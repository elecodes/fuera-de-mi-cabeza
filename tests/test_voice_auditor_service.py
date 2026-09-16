import asyncio
import json
from app.services.voice_auditor import VoiceAuditor
from app.llm.providers.mock import MockLLMClient


def test_voice_auditor_success():
    async def _run():
        audit_json = {
            "score": 92,
            "passed": True,
            "cadence_analysis": "Variación espontánea de ritmo.",
            "issues": [],
        }
        mock_llm = MockLLMClient(default_response=json.dumps(audit_json))
        auditor = VoiceAuditor(llm_client=mock_llm)

        report = await auditor.audit("Este es un texto de prueba que suena bastante natural.")

        assert report.score == 92
        assert report.passed is True
        assert report.cadence_analysis == "Variación espontánea de ritmo."
        assert len(report.issues) == 0

    asyncio.run(_run())


def test_voice_auditor_detects_issues():
    async def _run():
        audit_json = {
            "score": 65,
            "passed": False,
            "cadence_analysis": "Ritmo uniforme con frases de igual extensión.",
            "issues": [
                {
                    "rule_id": "antithesis",
                    "description": "Se detectó antítesis 'No es X, es Y'.",
                    "snippet": "No es programar, es pensar.",
                    "suggestion": "La clave está en pensar.",
                }
            ],
        }
        mock_llm = MockLLMClient(default_response=json.dumps(audit_json))
        auditor = VoiceAuditor(llm_client=mock_llm)

        report = await auditor.audit("No es programar, es pensar. Cabe destacar que esto importa.")

        assert report.score == 65
        assert report.passed is False
        assert len(report.issues) == 1
        assert report.issues[0].rule_id == "antithesis"

    asyncio.run(_run())
