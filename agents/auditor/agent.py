from typing import Any

from backend.services.auditor_service import audit_website


class AuditorAgent:
    """
    Agent responsable de l'analyse technique
    et commerciale d'un site internet.
    """

    name = "auditor"
    description = (
        "Analyse le site internet d'une entreprise "
        "et produit un audit technique enrichi par l'IA."
    )

    def run(
        self,
        company_name: str,
        website: str,
        sector: str | None,
        city: str | None,
    ) -> dict[str, Any]:
        return audit_website(
            company_name=company_name,
            website=website,
            sector=sector,
            city=city,
        )