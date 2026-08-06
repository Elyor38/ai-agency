from typing import Literal

from pydantic import BaseModel, Field


OpportunityService = Literal[
    "website_creation",
    "website_redesign",
    "seo_local",
    "google_business",
    "social_media",
    "conversion_optimization",
    "reputation_management",
    "no_priority",
]


class AIOpportunityResult(BaseModel):
    service: OpportunityService

    confidence: float = Field(
        ge=0,
        le=1,
    )

    reason: str = Field(
        min_length=20,
        max_length=1000,
    )

    business_problem: str = Field(
        min_length=10,
        max_length=1000,
    )

    recommended_action: str = Field(
        min_length=20,
        max_length=1500,
    )

    sales_angle: str = Field(
        min_length=20,
        max_length=1500,
    )