from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WriterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    audit_id: int
    score_id: int
    email_subject: str
    email_body: str
    commercial_offer: str
    call_to_action: str
    created_at: datetime