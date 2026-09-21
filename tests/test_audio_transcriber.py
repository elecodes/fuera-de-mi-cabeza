import asyncio
import json
from pathlib import Path
from app.services.audio_transcriber import AudioTranscriber
from app.services.idea_explorer import IdeaExplorer
from app.llm.providers.mock import MockLLMClient


def test_audio_transcriber_fallback_and_text(tmp_path):
    async def _run():
        transcriber = AudioTranscriber(api_key=None)

        # 1. Probar con texto directo
        res_text = await transcriber.transcribe_if_audio("Idea pensada en voz alta sobre educación.")
        assert res_text == "Idea pensada en voz alta sobre educación."

        # 2. Probar con archivo txt
        txt_file = tmp_path / "nota_voz.txt"
        txt_file.write_text("Transcripción grabada previamente.", encoding="utf-8")
        res_file_txt = await transcriber.transcribe_if_audio(txt_file)
        assert res_file_txt == "Transcripción grabada previamente."

        # 3. Probar con archivo mp3 mock
        mp3_file = tmp_path / "grabacion.mp3"
        mp3_file.write_bytes(b"dummy audio content")
        res_mp3 = await transcriber.transcribe_if_audio(mp3_file)
        assert "fallback" in res_mp3.lower() or "mock" in res_mp3.lower() or "grabacion.mp3" in res_mp3.lower()

    asyncio.run(_run())


def test_idea_explorer_with_audio(tmp_path):
    async def _run():
        analysis_json = {
            "core_idea": "Transcribir voz ayuda a capturar la identidad real del autor.",
            "connected_thoughts": ["Voz vs teclado"],
            "narrative_arcs": [],
            "possible_angles": ["Ángulo de autenticidad"],
            "potential_audience": "Creadores y escritores",
            "emotional_tone": "Reflexivo",
            "recommended_format": "article",
            "questions": ["¿Qué diferencia notás al hablar frente al teclado?"],
        }
        mock_llm = MockLLMClient(default_response=json.dumps(analysis_json))
        explorer = IdeaExplorer(llm_client=mock_llm)

        audio_file = tmp_path / "idea_voz.mp3"
        audio_file.write_bytes(b"dummy audio")

        result = await explorer.analyze_audio_or_text(audio_file)
        assert result.recommended_format == "article"
        assert len(result.questions) == 1

    asyncio.run(_run())
