from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agents.registry import registry
from backend.database.connection import get_db
from backend.models.company import Company
from backend.schemas.website_offer import WebsiteOfferResponse
from backend.services.ollama_service import OllamaError
from backend.services.website_offer_service import WebsiteOfferError


router = APIRouter(
    prefix="/website-offers",
    tags=["Website Offers"],
)


@router.post(
    "/companies/{company_id}",
    response_model=WebsiteOfferResponse,
)
def create_website_offer(
    company_id: int,
    db: Session = Depends(get_db),
):
    company = db.get(
        Company,
        company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Entreprise introuvable.",
        )

    if company.website:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cette entreprise possède déjà un site internet. "
                "Utilise le workflow d'audit classique."
            ),
        )

    agent = registry.get(
        "website_creation"
    )

    try:
        result = agent.run(
            company=company,
        )

    except (
        OllamaError,
        WebsiteOfferError,
    ) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    return {
        "company_id": company.id,
        "company_name": company.name,
        "sector": company.sector,
        "city": company.city,
        **result.model_dump(),
    }