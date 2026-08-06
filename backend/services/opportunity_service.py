from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_opportunity import AIOpportunityResult
from backend.services.ollama_service import ask_ollama_structured
from backend.utils.prompt_loader import load_prompt


class OpportunityError(RuntimeError):
    pass


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


def build_opportunity_prompt(
    company: Company,
    audit: Audit | None,
    score: Score | None,
) -> str:
    template = load_prompt(
        "opportunity.txt"
    )

    if not company.website:
        technical_score = "non applicable"
        global_score = "non applicable"
        priority = "high"

        strengths = "- aucune analyse de site disponible"

        weaknesses = (
            "- aucun site internet clairement associé à l'entreprise"
        )

        opportunities = (
            "- créer une présence internet adaptée à l'activité"
        )

        summary = (
            "L'entreprise ne possède pas de site internet connu."
        )

        observations = (
            "Aucun audit technique n'est possible sans site internet."
        )

    else:
        if audit is None or score is None:
            raise OpportunityError(
                "Un audit et un score sont obligatoires "
                "pour analyser une entreprise avec un site."
            )

        technical_score = str(
            audit.technical_score
        )

        global_score = str(
            score.global_score
        )

        priority = score.priority

        strengths = _format_items(
            score.strengths,
            "aucune force clairement identifiée",
        )

        weaknesses = _format_items(
            score.weaknesses,
            "aucune faiblesse clairement identifiée",
        )

        opportunities = _format_items(
            score.opportunities,
            "aucune opportunité clairement identifiée",
        )

        summary = score.summary
        observations = audit.observations

    try:
        return template.format(
            company_name=company.name,
            sector=company.sector or "non renseigné",
            city=company.city or "non renseignée",
            website=company.website or "aucun site connu",
            technical_score=technical_score,
            global_score=global_score,
            priority=priority,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            summary=summary,
            observations=observations,
        )

    except KeyError as error:
        raise OpportunityError(
            "Variable manquante dans le prompt Opportunity : "
            f"{error}"
        ) from error


def choose_opportunity(
    company: Company,
    audit: Audit | None = None,
    score: Score | None = None,
) -> AIOpportunityResult:
    if not company.website:
        return AIOpportunityResult(
            service="website_creation",
            confidence=1.0,
            reason=(
                "Aucun site internet clairement associé à "
                "l'entreprise n'est disponible."
            ),
            business_problem=(
                "Les clients potentiels disposent de peu d'informations "
                "centralisées pour découvrir l'activité et prendre contact."
            ),
            recommended_action=(
                "Créer un site simple adapté au secteur, présentant "
                "l'activité, les informations pratiques et un moyen "
                "direct de contacter l'entreprise."
            ),
            sales_angle=(
                "Présenter la création du site comme un moyen simple "
                "de rassurer les futurs clients et de faciliter "
                "les demandes de contact."
            ),
        )

    prompt = build_opportunity_prompt(
        company=company,
        audit=audit,
        score=score,
    )

    return ask_ollama_structured(
        prompt=prompt,
        response_model=AIOpportunityResult,
    )