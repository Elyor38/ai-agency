from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_opportunity import AIOpportunityResult
from backend.services.opportunity_service import choose_opportunity


class OpportunityAgent:
    """
    Agent responsable du choix de la meilleure
    opportunité commerciale pour une entreprise.
    """

    name = "opportunity"

    description = (
        "Analyse la situation d'une entreprise et recommande "
        "le service commercial le plus pertinent."
    )

    def run(
        self,
        company: Company,
        audit: Audit | None = None,
        score: Score | None = None,
    ) -> AIOpportunityResult:
        return choose_opportunity(
            company=company,
            audit=audit,
            score=score,
        )