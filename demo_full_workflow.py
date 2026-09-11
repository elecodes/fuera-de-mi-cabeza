import asyncio
import json
from app.llm.providers.mock import MockLLMClient
from app.services.session_manager import SessionManager
from app.services.idea_explorer import IdeaExplorer
from app.services.content_planner import ContentPlanner
from app.services.draft_generator import DraftGenerator
from app.services.voice_editor import VoiceEditor


async def run_full_workflow_demo():
    print("==================================================")
    print("FUERA DE MI CABEZA — DEMO DEL FLUJO COMPLETO MVP v0.1")
    print("==================================================")

    # 1. Sesión
    session_manager = SessionManager()
    idea = "Quiero reflexionar sobre por qué es tan difícil pasar de aprender cosas a construir productos reales."
    session = session_manager.create_session(original_idea=idea)
    print(f"\n1. Sesión creada: ID={session.id}")
    print(f"   Idea inicial: \"{idea}\"")

    # 2. Idea Explorer
    explore_response = {
        "core_idea": "La brecha entre el aprendizaje pasivo y la ejecución de proyectos reales",
        "possible_angles": [
            "La ilusión de aprendizaje mirando tutoriales",
            "El miedo a lanzar algo imperfecto",
            "Cómo diseñar un sistema para forzarte a publicar",
        ],
        "potential_audience": "Desarrolladores, estudiantes y creadores tech",
        "emotional_tone": "Reflexivo, práctico, empático",
        "recommended_format": "article",
        "questions": [
            "¿Qué proyecto intentaste empezar recientemente y se trabó?",
            "¿Cuál sentís que es la traba principal: falta de tiempo o parálisis por análisis?",
        ],
    }
    llm_explore = MockLLMClient(default_response=json.dumps(explore_response, ensure_ascii=False))
    explorer = IdeaExplorer(llm_client=llm_explore)
    analysis = await explorer.analyze(session.original_idea)
    session.analysis = analysis
    session_manager.save_session(session)

    print("\n2. Análisis obtenido:")
    print(f"   - Núcleo: {analysis.core_idea}")
    print("   - Preguntas de profundización:")
    for q in analysis.questions:
        print(f"     • {q}")

    # 3. Respuestas del autor
    answers = [
        "Quise hacer una app en FastAPI pero me quedé refinando la arquitectura semanas sin lanzar.",
        "Definitivamente parálisis por análisis y querer que todo sea perfecto.",
    ]
    session.user_answers = answers
    session_manager.save_session(session)
    print("\n3. Respuestas guardadas del autor.")

    # 4. Content Plan
    plan_response = {
        "format": "article",
        "title_options": [
            "La trampa de aprender sin construir",
            "Parálisis por arquitectura: por qué nunca lanzamos",
            "De la teoría a la realidad: cómo romper el bucle",
        ],
        "central_message": "Construir cosas reales requiere aceptar la imperfección inicial y priorizar el aprendizaje activo.",
        "opening_direction": "Contar la experiencia reciente de quedarse atrapado refinando una arquitectura en FastAPI.",
        "key_points": [
            "La trampa de la comodidad consumiendo tutoriales",
            "El espejismo del código perfecto que nunca ve la luz",
            "Mecanismos concretos para forzarse a cerrar versiones v0.1",
        ],
        "ending_direction": "Reflexión abierta sobre el valor de aprender en público sin moralejas pretenciosas.",
    }
    llm_plan = MockLLMClient(default_response=json.dumps(plan_response, ensure_ascii=False))
    planner = ContentPlanner(llm_client=llm_plan)
    plan = await planner.plan(session.original_idea, session.analysis, session.user_answers)
    session.content_plan = plan
    session_manager.save_session(session)

    print("\n4. Content Plan generado:")
    print(f"   - Título sugerido: {plan.title_options[0]}")
    print(f"   - Mensaje central: {plan.central_message}")

    # 5. Draft Generator
    article_response = {
        "format": "article",
        "title": "La trampa de aprender sin construir",
        "content": (
            "# La trampa de aprender sin construir\n\n"
            "Hace unas semanas empecé un proyecto en FastAPI. Mi intención era simple: poner en práctica "
            "algunas ideas sobre arquitectura y agentes. Sin embargo, pasaron las semanas y me encontré "
            "refinando clases, reorganizando carpetas y puliendo detalles invisibles sin haber lanzado nada.\n\n"
            "## El espejismo del código perfecto\n\n"
            "Es muy fácil confundir la parálisis por análisis con productividad..."
        ),
    }
    llm_draft = MockLLMClient(default_response=json.dumps(article_response, ensure_ascii=False))
    generator = DraftGenerator(llm_client=llm_draft)
    draft = await generator.generate_article(session.original_idea, session.content_plan, session.user_answers)
    session.draft = draft
    session_manager.save_session(session)

    print("\n5. Borrador generado:")
    print(f"   - Título: {draft.title}")
    print(f"   - Fragmento:\n{draft.content[:200]}...")

    # 6. Voice Editor (Revision)
    feedback = "Me gusta, pero quiero que el tono sea más cercano y menos técnico en la segunda sección."
    revised_response = {
        "format": "article",
        "title": "La trampa de aprender sin construir",
        "content": (
            "# La trampa de aprender sin construir\n\n"
            "Hace unas semanas empecé un proyecto en FastAPI. Mi intención era simple: poner en práctica "
            "algunas ideas sobre arquitectura y agentes. Sin embargo, pasaron las semanas y me encontré "
            "refinando clases, reorganizando carpetas y puliendo detalles invisibles sin haber lanzado nada.\n\n"
            "## Lo que nos pasa cuando queremos que todo sea perfecto\n\n"
            "Es fácil caer en la trampa de creer que estamos avanzando solo porque estamos ocupados..."
        ),
    }
    llm_revise = MockLLMClient(default_response=json.dumps(revised_response, ensure_ascii=False))
    editor = VoiceEditor(llm_client=llm_revise)
    revised_draft = await editor.revise(session.original_idea, session.draft, feedback)
    session.feedback.append(feedback)
    session.revisions.append(revised_draft.content)
    session.draft = revised_draft
    session_manager.save_session(session)

    print("\n6. Borrador revisado con el feedback del autor:")
    print(f"   - Feedback enviado: \"{feedback}\"")
    print(f"   - Fragmento revisado:\n{revised_draft.content[:220]}...")
    print("\n==================================================")
    print("DEMO COMPLETADA CON ÉXITO — Sesión guardada en data/sessions/")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_full_workflow_demo())
