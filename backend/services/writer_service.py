from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_writer import AIWriterResult
from backend.services.ollama_service import ask_ollama_structured
from backend.utils.prompt_loader import load_prompt


def _format_items(
    items: list[str],
    empty_message: str,
) -> str:
    if not items:
        return f"- {empty_message}"

    return "\n".join(
        f"- {item}"
        for item in items
    )


def build_writer_prompt(
    company: Company,
    audit: Audit,
    score: Score,
) -> str:
    template = load_prompt(
        "writer_email.txt"
    )

    try:
        return template.format(
            company_name=company.name,
            sector=company.sector or "non renseigné",
            city=company.city or "non renseignée",
            website=company.website or "non renseigné",
            global_score=score.global_score,
            priority=score.priority,
            strengths=_format_items(
                score.strengths,
                "aucune force clairement identifiée",
            ),
            weaknesses=_format_items(
                score.weaknesses,
                "aucune faiblesse clairement identifiée",
            ),
            opportunities=_format_items(
                score.opportunities,
                "aucune opportunité clairement identifiée",
            ),
            recommended_offer=score.recommended_offer,
            summary=score.summary,
            observations=audit.observations,
        )

    except KeyError as error:
        raise RuntimeError(
            f"Variable manquante dans le prompt Writer : {error}"
        ) from error


def generate_writer_result(
    company: Company,
    audit: Audit,
    score: Score,
) -> AIWriterResult:
    prompt = build_writer_prompt(
        company=company,
        audit=audit,
        score=score,
    )

    return ask_ollama_structured(
        prompt=prompt,
        response_model=AIWriterResult,
    )