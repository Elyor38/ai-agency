from pydantic import BaseModel, Field


class AIWebsiteOffer(BaseModel):
    offer_title: str = Field(
        min_length=5,
        max_length=150,
    )

    recommended_pages: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    recommended_features: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    business_benefits: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    email_subject: str = Field(
        min_length=5,
        max_length=150,
    )

    email_body: str = Field(
        min_length=100,
        max_length=3000,
    )

    commercial_offer: str = Field(
        min_length=20,
        max_length=2000,
    )

    call_to_action: str = Field(
        min_length=5,
        max_length=500,
    )