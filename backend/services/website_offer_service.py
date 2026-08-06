from backend.models.company import Company
from backend.schemas.ai_website_offer import AIWebsiteOffer
from backend.services.ollama_service import ask_ollama_structured
from backend.utils.prompt_loader import load_prompt


class WebsiteOfferError(RuntimeError):
    pass


def _get_business_goal(
    sector: str | None,
) -> str:
    normalized_sector = (
        sector or ""
    ).strip().lower()

    goals = {
        "restaurant": (
            "Permettre aux clients de découvrir l'établissement, "
            "consulter les horaires et le menu, puis réserver "
            "ou prendre contact facilement."
        ),
        "bar": (
            "Présenter l'ambiance, les horaires, les événements "
            "et faciliter la venue des clients."
        ),
        "garage": (
            "Présenter les services, augmenter les demandes de devis "
            "et faciliter la prise de rendez-vous."
        ),
        "coiffeur": (
            "Présenter les prestations et faciliter la prise "
            "de rendez-vous."
        ),
        "coiffure": (
            "Présenter les prestations et faciliter la prise "
            "de rendez-vous."
        ),
        "artisan": (
            "Présenter le savoir-faire, les réalisations et faciliter "
            "les demandes de devis."
        ),
        "plombier": (
            "Présenter les services et faciliter les demandes "
            "d'intervention ou de devis."
        ),
        "électricien": (
            "Présenter les services et faciliter les demandes "
            "d'intervention ou de devis."
        ),
        "avocat": (
            "Présenter les domaines d'intervention, renforcer "
            "la confiance et faciliter les demandes de consultation."
        ),
        "hôtel": (
            "Présenter les chambres et services, puis faciliter "
            "les demandes de réservation."
        ),
        "hotel": (
            "Présenter les chambres et services, puis faciliter "
            "les demandes de réservation."
        ),
        "commerce": (
            "Présenter l'activité, les produits, les horaires "
            "et aider les clients locaux à trouver l'établissement."
        ),
    }

    for keyword, goal in goals.items():
        if keyword in normalized_sector:
            return goal

    return (
        "Présenter clairement l'activité, renforcer la confiance "
        "et faciliter la prise de contact."
    )


def build_website_offer_prompt(
    company: Company,
) -> str:
    template = load_prompt(
        "website_creation_offer.txt"
    )

    try:
        return template.format(
            company_name=company.name,
            sector=company.sector or "non renseigné",
            city=company.city or "non renseignée",
            phone=company.phone or "non renseigné",
            email=company.email or "non renseigné",
            business_goal=_get_business_goal(
                company.sector
            ),
        )

    except KeyError as error:
        raise WebsiteOfferError(
            "Variable manquante dans le prompt "
            f"de création de site : {error}"
        ) from error


def generate_website_offer(
    company: Company,
) -> AIWebsiteOffer:
    prompt = build_website_offer_prompt(
        company=company,
    )

    return ask_ollama_structured(
        prompt=prompt,
        response_model=AIWebsiteOffer,
    )