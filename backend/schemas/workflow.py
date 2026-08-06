from typing import Literal

from pydantic import BaseModel

from backend.schemas.ai_opportunity import AIOpportunityResult
from backend.schemas.audit import AuditResponse
from backend.schemas.score import ScoreResponse
from backend.schemas.website_offer import WebsiteOfferResponse
from backend.schemas.writer import WriterResponse


class CompanyWorkflowResponse(BaseModel):
    workflow_type: Literal[
        "website_audit",
        "website_creation",
    ]

    company_id: int
    company_name: str

    opportunity: AIOpportunityResult

    audit: AuditResponse | None = None
    score: ScoreResponse | None = None
    writer: WriterResponse | None = None

    website_offer: WebsiteOfferResponse | None = None