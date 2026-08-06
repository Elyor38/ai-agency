from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_opportunity import AIOpportunityResult
from backend.schemas.ai_writer import AIWriterResult
from backend.services.writer_service import generate_writer_result


class WriterAgent:
    """
    Agent chargé de rédiger une proposition commerciale
    adaptée au service choisi par l'OpportunityAgent.
    """

    name = "writer"

    description = (
        "Génère un email commercial spécialisé selon "
        "l'opportunité recommandée."
    )

    def run(
        self,
        company: Company,
        audit: Audit,
        score: Score,
        opportunity: AIOpportunityResult | None = None,
    ) -> AIWriterResult:
        return generate_writer_result(
            company=company,
            audit=audit,
            score=score,
            opportunity=opportunity,
        )