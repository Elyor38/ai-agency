from pydantic import BaseModel

from backend.schemas.ai_website_offer import AIWebsiteOffer


class WebsiteOfferResponse(AIWebsiteOffer):
    company_id: int
    company_name: str
    sector: str | None
    city: str | None