from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)

    email: str | None = None
    phone: str | None = None
    website: str | None = None
    city: str | None = None
    sector: str | None = None
    notes: str | None = None


class CompanyResponse(CompanyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime