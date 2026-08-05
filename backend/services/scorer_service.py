from backend.models.audit import Audit
from backend.schemas.ai_score import AIScore
from backend.services.ollama_service import ask_ollama_structured
from backend.utils.prompt_loader import load_prompt


class ScorerError(RuntimeError):
    """Erreur pendant la construction du prompt du Scorer."""


def build_scoring_prompt(
    company_name: str,
    sector: str | None,
    city: str | None,
    audit: Audit,
) -> str:
    template = load_prompt("score.txt")

    try:
        return template.format(
            company_name=company_name,
            sector=sector or "non renseigné",
            city=city or "non renseignée",
            technical_score=audit.technical_score,
            observations=audit.observations,
            analysis=audit.ai_analysis,
        )

    except KeyError as error:
        raise ScorerError(
            f"Variable manquante dans le prompt Scorer : {error}"
        ) from error


def score_audit(
    company_name: str,
    sector: str | None,
    city: str | None,
    audit: Audit,
) -> AIScore:
    prompt = build_scoring_prompt(
        company_name=company_name,
        sector=sector,
        city=city,
        audit=audit,
    )

    return ask_ollama_structured(
        prompt=prompt,
        response_model=AIScore,
    )