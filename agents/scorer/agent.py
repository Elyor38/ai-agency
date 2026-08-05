from backend.models.audit import Audit
from backend.schemas.ai_score import AIScore
from backend.services.scorer_service import score_audit


class ScorerAgent:
    """
    Agent responsable de l'évaluation commerciale
    d'un audit existant.
    """

    name = "scorer"
    description = (
        "Analyse un audit et produit un score commercial structuré."
    )

    def run(
        self,
        company_name: str,
        sector: str | None,
        city: str | None,
        audit: Audit,
    ) -> AIScore:
        return score_audit(
            company_name=company_name,
            sector=sector,
            city=city,
            audit=audit,
        )