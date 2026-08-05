from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_writer import AIWriterResult
from backend.services.email_quality_service import (
    EmailQualityError,
    collect_quality_issues,
    validate_writer_result,
)
from backend.services.ollama_service import (
    ask_ollama_structured,
)
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


def _get_business_goal(
    sector: str | None,
) -> str:
    normalized_sector = (
        sector or ""
    ).strip().lower()

    sector_goals = {
        "restaurant": (
            "Aider davantage de clients locaux à trouver "
            "l'établissement, consulter les informations utiles "
            "et réserver plus facilement."
        ),
        "bar": (
            "Donner envie de découvrir l'établissement et faciliter "
            "l'accès aux horaires, événements et moyens de contact."
        ),
        "garage": (
            "Augmenter les demandes de devis et simplifier "
            "la prise de rendez-vous."
        ),
        "automobile": (
            "Augmenter les demandes de devis et simplifier "
            "la prise de rendez-vous."
        ),
        "coiffeur": (
            "Faciliter la prise de rendez-vous, présenter les "
            "prestations et rassurer les nouveaux clients."
        ),
        "coiffure": (
            "Faciliter la prise de rendez-vous, présenter les "
            "prestations et rassurer les nouveaux clients."
        ),
        "dentiste": (
            "Améliorer la visibilité du cabinet et simplifier "
            "la prise de rendez-vous pour les patients."
        ),
        "médecin": (
            "Faciliter l'accès aux informations du cabinet "
            "et la prise de rendez-vous."
        ),
        "avocat": (
            "Renforcer la confiance et faciliter les demandes "
            "de consultation."
        ),
        "hôtel": (
            "Augmenter les réservations directes et mieux présenter "
            "les chambres et services."
        ),
        "hotel": (
            "Augmenter les réservations directes et mieux présenter "
            "les chambres et services."
        ),
        "artisan": (
            "Augmenter les demandes de devis et mettre en valeur "
            "le savoir-faire de l'entreprise."
        ),
        "plombier": (
            "Faciliter les demandes d'intervention et de devis "
            "dans la zone locale."
        ),
        "électricien": (
            "Faciliter les demandes d'intervention et de devis "
            "dans la zone locale."
        ),
        "immobilier": (
            "Générer davantage de demandes de contact et mieux "
            "présenter les biens et services."
        ),
        "commerce": (
            "Attirer davantage de clients locaux et faciliter "
            "la découverte des produits et services."
        ),
    }

    for keyword, goal in sector_goals.items():
        if keyword in normalized_sector:
            return goal

    return (
        "Renforcer la visibilité de l'entreprise, rassurer les "
        "visiteurs et faciliter la prise de contact."
    )


def build_writer_prompt(
    company: Company,
    audit: Audit,
    score: Score,
) -> str:
    template = load_prompt(
        "writer_email.txt"
    )

    business_goal = _get_business_goal(
        company.sector
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
            business_goal=business_goal,
        )

    except KeyError as error:
        raise EmailQualityError(
            "Variable manquante dans le prompt Writer : "
            f"{error}"
        ) from error


def build_correction_prompt(
    company: Company,
    writer_result: AIWriterResult,
    issues: list[str],
) -> str:
    template = load_prompt(
        "writer_correction.txt"
    )

    quality_issues = "\n".join(
        f"- {issue}"
        for issue in issues
    )

    try:
        return template.format(
            company_name=company.name,
            sector=company.sector or "non renseigné",
            email_subject=writer_result.email_subject,
            email_body=writer_result.email_body,
            commercial_offer=(
                writer_result.commercial_offer
            ),
            call_to_action=(
                writer_result.call_to_action
            ),
            quality_issues=quality_issues,
        )

    except KeyError as error:
        raise EmailQualityError(
            "Variable manquante dans le prompt "
            f"de correction Writer : {error}"
        ) from error


def generate_writer_result(
    company: Company,
    audit: Audit,
    score: Score,
) -> AIWriterResult:
    initial_prompt = build_writer_prompt(
        company=company,
        audit=audit,
        score=score,
    )

    writer_result = ask_ollama_structured(
        prompt=initial_prompt,
        response_model=AIWriterResult,
    )

    issues = collect_quality_issues(
        writer_result
    )

    if not issues:
        return writer_result

    correction_prompt = build_correction_prompt(
        company=company,
        writer_result=writer_result,
        issues=issues,
    )

    corrected_result = ask_ollama_structured(
        prompt=correction_prompt,
        response_model=AIWriterResult,
    )

    validate_writer_result(
        corrected_result
    )

    return corrected_result