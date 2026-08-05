from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_writer import AIWriterResult
from backend.services.writer_service import generate_writer_result


class WriterAgent:
    """
    Agent responsable de la création d'un brouillon
    d'email commercial personnalisé.
    """

    name = "writer"
    description = (
        "Génère un brouillon d'email commercial, "
        "une offre et un appel à l'action."
    )

    def run(
        self,
        company: Company,
        audit: Audit,
        score: Score,
    ) -> AIWriterResult:
        return generate_writer_result(
            company=company,
            audit=audit,
            score=score,
        )