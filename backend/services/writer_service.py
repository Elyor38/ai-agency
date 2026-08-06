from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_opportunity import AIOpportunityResult
from backend.schemas.ai_writer import AIWriterResult
from backend.services.email_quality_service import (
    EmailQualityError,
    collect_quality_issues,
    validate_writer_result,
)
from backend.services.ollama_service import ask_ollama_structured
from backend.services.opportunity_service import choose_opportunity
from backend.utils.prompt_loader import load_prompt


ALLOWED_WRITER_SERVICES = {
    "website_creation",
    "website_redesign",
    "seo_local",
    "google_business",
    "social_media",
    "conversion_optimization",
    "reputation_management",
    "no_priority",
}


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


def _get_writer_prompt_filename(
    service: str,
) -> str:
    if service not in ALLOWED_WRITER_SERVICES:
        raise EmailQualityError(
            "Service Writer non pris en charge : "
            f"{service}"
        )

    return (
        "writer/"
        f"writer_{service}.txt"
    )


def _load_writer_instructions(
    service: str,
) -> str:
    base_prompt = load_prompt(
        "writer/writer_base.txt"
    )

    specialized_prompt = load_prompt(
        _get_writer_prompt_filename(
            service
        )
    )

    return (
        f"{base_prompt}\n\n"
        "Instructions spécifiques au service :\n\n"
        f"{specialized_prompt}"
    )


def build_writer_prompt(
    company: Company,
    audit: Audit,
    score: Score,
    opportunity: AIOpportunityResult,
) -> str:
    instructions = _load_writer_instructions(
        opportunity.service
    )

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

    return f"""
{instructions}

Entreprise

Nom : {company.name}
Secteur : {company.sector or "non renseigné"}
Ville : {company.city or "non renseignée"}
Site : {company.website or "non renseigné"}

Décision commerciale

Service recommandé : {opportunity.service}
Niveau de confiance : {opportunity.confidence}
Raison du choix : {opportunity.reason}

Problème métier identifié :

{opportunity.business_problem}

Action recommandée :

{opportunity.recommended_action}

Angle commercial à utiliser :

{opportunity.sales_angle}

Résultats de l'analyse

Score technique : {audit.technical_score}/100
Score commercial : {score.global_score}/100
Priorité : {score.priority}

Forces :

{strengths}

Faiblesses :

{weaknesses}

Opportunités :

{opportunities}

Offre initialement recommandée :

{score.recommended_offer}

Résumé :

{score.summary}

Observations techniques internes :

{audit.observations}

Consignes finales :

- L'email doit être principalement centré sur le service recommandé.
- Utilise l'angle commercial défini par l'OpportunityAgent.
- Les observations techniques servent uniquement de contexte interne.
- Ne copie jamais le jargon technique dans l'email.
- Transforme les problèmes en bénéfices compréhensibles.
- Ne présente pas toutes les faiblesses du site.
- Sélectionne uniquement les deux ou trois éléments les plus pertinents.
- Réponds uniquement selon le schéma JSON demandé.
""".strip()


def build_correction_prompt(
    company: Company,
    writer_result: AIWriterResult,
    opportunity: AIOpportunityResult,
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
        correction_prompt = template.format(
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

    opportunity_context = f"""
Service commercial à conserver :
{opportunity.service}

Problème métier principal :
{opportunity.business_problem}

Action recommandée :
{opportunity.recommended_action}

Angle commercial :
{opportunity.sales_angle}

La version corrigée doit rester centrée sur ce service.
""".strip()

    return (
        f"{correction_prompt}\n\n"
        f"{opportunity_context}"
    )


def generate_writer_result(
    company: Company,
    audit: Audit,
    score: Score,
    opportunity: AIOpportunityResult | None = None,
) -> AIWriterResult:
    selected_opportunity = opportunity

    if selected_opportunity is None:
        selected_opportunity = choose_opportunity(
            company=company,
            audit=audit,
            score=score,
        )

    initial_prompt = build_writer_prompt(
        company=company,
        audit=audit,
        score=score,
        opportunity=selected_opportunity,
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
        opportunity=selected_opportunity,
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