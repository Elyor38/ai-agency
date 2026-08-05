from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    website: str
    http_status: int | None
    response_time_ms: int | None
    technical_score: int
    page_title: str | None
    meta_description: str | None
    observations: str
    ai_analysis: str
    created_at: datetime