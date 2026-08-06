from backend.models.company import Company
from backend.schemas.ai_website_offer import AIWebsiteOffer
from backend.services.website_offer_service import (
    generate_website_offer,
)


class WebsiteCreationAgent:
    """
    Agent responsable de la création d'une proposition
    commerciale pour une entreprise sans site internet connu.
    """

    name = "website_creation"

    description = (
        "Génère une proposition de création de site internet "
        "adaptée au secteur de l'entreprise."
    )

    def run(
        self,
        company: Company,
    ) -> AIWebsiteOffer:
        return generate_website_offer(
            company=company,
        )