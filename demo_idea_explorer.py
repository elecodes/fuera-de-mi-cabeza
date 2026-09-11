import asyncio
import json
from app.llm.providers.mock import MockLLMClient
from app.services.idea_explorer import IdeaExplorer

EXAMPLE_RESPONSE = {
    "core_idea": "Evaluar si el camino profesional como developer sigue alineado con la búsqueda personal de propósito y construcción",
    "possible_angles": [
        "Transición de picar código a construir productos enteros",
        "El choque entre la expectativa de la industria tech y la realidad del trabajo diario",
        "Redescubrir la curiosidad y la creatividad fuera del rol tradicional de dev",
    ],
    "potential_audience": "Programadores, profesionales tech y creativos en momentos de transición",
    "emotional_tone": "Reflexivo, honesto, inquisitivo",
    "recommended_format": "both",
    "questions": [
        "¿Sentís que te aburre la programación en sí, o la dinámica de los proyectos en los que trabajás?",
        "¿Hay algún proyecto personal reciente donde hayas sentido que volvías a disfrutar de construir algo?",
        "¿Qué significa para vos 'hacer cosas reales' en esta etapa?",
    ],
}


async def main():
    idea = "No sé si quiero seguir trabajando como developer."

    print("==========================================")
    print("FUERA DE MI CABEZA — Personal Editorial Agent")
    print("==========================================")
    print(f"\n[IDEA ORIGINAL]:\n\"{idea}\"\n")

    mock_llm = MockLLMClient(default_response=json.dumps(EXAMPLE_RESPONSE, ensure_ascii=False))
    explorer = IdeaExplorer(llm_client=mock_llm)

    analysis = await explorer.analyze(idea)

    print("Creo que estás intentando explorar:\n")
    print(f"-> {analysis.core_idea}\n")
    print("Posibles enfoques:\n")
    for idx, angle in enumerate(analysis.possible_angles, 1):
        print(f"  {idx}. {angle}")

    print("\nPara entender mejor lo que quieres decir:\n")
    for q in analysis.questions:
        print(f"  - {q}")

    print(f"\nTono sugerido: {analysis.emotional_tone}")
    print(f"Formato recomendado: {analysis.recommended_format}")
    print("==========================================")


if __name__ == "__main__":
    asyncio.run(main())
