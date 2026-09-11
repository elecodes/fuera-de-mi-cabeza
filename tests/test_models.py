import pytest
from pydantic import ValidationError
from app.models.idea import IdeaInput
from app.models.analysis import IdeaAnalysis


def test_idea_input_valid():
    inp = IdeaInput(idea="No sé si quiero seguir siendo developer")
    assert inp.idea == "No sé si quiero seguir siendo developer"


def test_idea_input_invalid_empty():
    with pytest.raises(ValidationError):
        IdeaInput(idea="")


def test_idea_analysis_valid():
    analysis = IdeaAnalysis(
        core_idea="Reflexión sobre el trabajo de desarrollador",
        possible_angles=["El desgaste técnico", "Reorientar la carrera"],
        potential_audience="Programadores y tecnólogos",
        emotional_tone="Reflexivo e incierto",
        recommended_format="article",
        questions=[
            "¿Qué desencadenó este sentimiento?",
            "¿Qué parte de programar te sigue gustando?",
        ],
    )
    assert analysis.recommended_format == "article"
    assert len(analysis.questions) == 2


def test_idea_analysis_max_questions():
    with pytest.raises(ValidationError):
        IdeaAnalysis(
            core_idea="Test",
            possible_angles=["Angle"],
            potential_audience="Audience",
            emotional_tone="Tone",
            recommended_format="note",
            questions=["Q1", "Q2", "Q3", "Q4"],  # Exceeds max 3
        )
