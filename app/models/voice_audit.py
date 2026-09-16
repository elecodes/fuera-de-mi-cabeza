from pydantic import BaseModel, Field


class VoiceAuditIssue(BaseModel):
    rule_id: str = Field(..., description="Identificador de la regla violada (ej. antithesis, AI_cliche, rhythm_monotony)")
    description: str = Field(..., description="Descripción del problema detectado")
    snippet: str | None = Field(default=None, description="Fragmento de texto afectado")
    suggestion: str | None = Field(default=None, description="Sugerencia de corrección")


class VoiceAuditReport(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Puntuación de naturalidad y alineación con el perfil (0-100)")
    passed: bool = Field(..., description="True si cumple con los criterios editoriales estrictos")
    issues: list[VoiceAuditIssue] = Field(default_factory=list, description="Lista de problemas detectados")
    cadence_analysis: str = Field(..., description="Análisis del ritmo y variación de longitud de frases")
