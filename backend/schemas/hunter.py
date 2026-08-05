from pydantic import BaseModel, Field


class HunterSearchRequest(BaseModel):
    city: str = Field(
        min_length=2,
        max_length=150,
        examples=["Lyon, France"],
    )

    business_type: str = Field(
        min_length=2,
        max_length=100,
        examples=["restaurant"],
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=50,
    )


class HunterCompany(BaseModel):
    id: int
    name: str
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    sector: str | None = None


class HunterResult(BaseModel):
    found: int
    created: int
    skipped: int
    companies: list[HunterCompany]