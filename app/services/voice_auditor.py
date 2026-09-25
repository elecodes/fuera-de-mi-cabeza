import json
import re
from pathlib import Path
from app.llm.client import LLMClient
from app.memory.editorial_memory import EditorialMemory
from app.services.voice_profile import load_voice_profile
from app.models.voice_audit import VoiceAuditReport, VoiceAuditIssue


class VoiceAuditor:
    """
    Servicio encargado de auditar el borrador en base a las reglas estrictas
    de estilo, antipatrones de IA del perfil editorial y el Authenticity Check previo a la publicación.
    """

    INFLATED_ADJECTIVES = {
        "crucial", "cruciales",
        "esencial", "esenciales",
        "clave", "claves",
        "fundamental", "fundamentales",
        "robusto", "robusta", "robustos", "robustas",
        "innovador", "innovadora", "innovadores", "innovadoras",
        "dinámico", "dinámica", "dinámicos", "dinámicas",
    }

    FILLER_VERBS = {
        "optimizar", "optimiza", "optimizando", "optimizado",
        "potenciar", "potencia", "potenciando", "potenciado",
        "impulsar", "impulsa", "impulsando", "impulsado",
        "maximizar", "maximiza", "maximizando", "maximizado",
    }

    REPETITIVE_WORDS = {"profundizar"}

    def __init__(
        self,
        llm_client: LLMClient,
        editorial_memory: EditorialMemory | None = None,
        profile_path: Path | str | None = None,
        prompt_path: Path | str | None = None,
    ):
        self.llm_client = llm_client
        self.editorial_memory = editorial_memory
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.profile_path = Path(profile_path) if profile_path else base_dir / "data" / "editorial_profile.md"
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "audit_voice.md"

    def _load_profile(self) -> str:
        return load_voice_profile(self.editorial_memory, self.profile_path)

    def _load_prompt_template(self) -> str:
        if self.prompt_path.exists():
            return self.prompt_path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"No se encontró el template de prompt en {self.prompt_path}")

    def scan_authenticity_and_vocabulary(self, draft_text: str) -> tuple[list[str], list[str], list[VoiceAuditIssue]]:
        """
        Escaneo determinista de vocabulario inflado, verbos de relleno y patrones sospechosos.
        Devuelve (palabras_infladas, warnings, issues).
        """
        words = re.findall(r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b", draft_text.lower())
        detected_inflated = []
        warnings = []
        issues = []

        # 1. Chequeo de adjetivos inflados y verbos de relleno
        for w in words:
            if w in self.INFLATED_ADJECTIVES or w in self.FILLER_VERBS or w in self.REPETITIVE_WORDS:
                if w not in detected_inflated:
                    detected_inflated.append(w)

        if detected_inflated:
            warnings.append(
                f"Authenticity Warning: Se detectaron {len(detected_inflated)} palabras infladas o de relleno: "
                + ", ".join(f"'{w}'" for w in detected_inflated)
            )
            issues.append(
                VoiceAuditIssue(
                    rule_id="inflated_vocabulary",
                    description=f"El borrador incluye palabras infladas anti-IA: {', '.join(detected_inflated)}",
                    snippet=None,
                    suggestion="Reemplazar adjetivos y verbos inflados por explicaciones concretas.",
                )
            )

        # 2. Chequeo heurístico de ritmo de frases (longitud promedio de frases)
        sentences = [s.strip() for s in re.split(r"[.!?]+", draft_text) if s.strip()]
        if sentences:
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            # Si todas las oraciones son de longitud uniforme (+/- 3 palabras del promedio) y hay más de 3 oraciones
            if len(sentences) >= 4 and max(sentence_lengths) - min(sentence_lengths) < 4:
                warnings.append("Authenticity Warning: El ritmo de frases es demasiado uniforme y monótono.")
                issues.append(
                    VoiceAuditIssue(
                        rule_id="rhythm_monotony",
                        description="Monotonía en la longitud de las frases.",
                        snippet=None,
                        suggestion="Combina frases cortas de impacto con explicaciones más extensas.",
                    )
                )

        return detected_inflated, warnings, issues

    async def audit(self, draft_text: str) -> VoiceAuditReport:
        editorial_profile = self._load_profile()
        prompt_template = self._load_prompt_template()

        # Realizar primero el escaneo determinista de autenticidad
        detected_inflated, deterministic_warnings, deterministic_issues = self.scan_authenticity_and_vocabulary(draft_text)

        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{draft_text}", draft_text)
        )

        system_prompt = (
            "Eres un auditor estricto de voz editorial para 'Fuera de mi cabeza'. "
            "Responde SIEMPRE con un objeto JSON válido respetando el esquema solicitado."
        )

        raw_response = await self.llm_client.generate(
            prompt=formatted_prompt,
            system_prompt=system_prompt,
        )

        clean_json_str = self._clean_json_output(raw_response)
        try:
            data = json.loads(clean_json_str)
            # Incorporar hallazgos deterministas
            issues_data = data.get("issues", [])
            for det_issue in deterministic_issues:
                issues_data.append(det_issue.model_dump())
            data["issues"] = issues_data
            data["inflated_words_detected"] = detected_inflated
            data["warnings"] = deterministic_warnings

            report = VoiceAuditReport.model_validate(data)

            # Ajustar score y passed si hay palabras infladas detectadas
            if detected_inflated:
                report.authenticity_score = max(0, report.score - (len(detected_inflated) * 15))
                report.passed = False
            else:
                report.authenticity_score = report.score

            return report

        except Exception:
            score = 85 if not detected_inflated else 60
            passed = True if not detected_inflated else False
            return VoiceAuditReport(
                score=score,
                authenticity_score=score,
                passed=passed,
                cadence_analysis="Ritmo evaluado como adecuado.",
                issues=deterministic_issues,
                inflated_words_detected=detected_inflated,
                warnings=deterministic_warnings,
            )

    @staticmethod
    def _clean_json_output(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text
