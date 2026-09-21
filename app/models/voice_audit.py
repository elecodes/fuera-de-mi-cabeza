from pydantic import BaseModel, Field


class VoiceAuditIssue(BaseModel):
    rule_id: str = Field(..., description="Identificador de la regla violada (ej. antithesis, AI_cliche, inflated_vocabulary, rhythm_monotony)")
    description: str = Field(..., description="Descripción del problema detectado")
    snippet: str | None = Field(default=None, description="Fragmento de texto afectado")
    suggestion: str | None = Field(default=None, description="Sugerencia de corrección")


class VoiceAuditReport(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Puntuación de naturalidad y alineación con el perfil (0-100)")
    authenticity_score: int = Field(default=85, ge=0, le=100, description="Métrica de autenticidad del autor")
    passed: bool = Field(..., description="True si cumple con los criterios editoriales y de autenticidad estrictos")
    issues: list[VoiceAuditIssue] = Field(default_factory=list, description="Lista de problemas detectados")
    inflated_words_detected: list[str] = Field(default_factory=list, description="Palabras infladas o de relleno detectadas")
    warnings: list[str] = Field(default_factory=list, description="Advertencias y banderas rojas de autenticidad")
    cadence_analysis: str = Field(..., description="Análisis del ritmo y variación de longitud de frases")
