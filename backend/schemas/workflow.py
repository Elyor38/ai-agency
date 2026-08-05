from pydantic import BaseModel

from backend.schemas.audit import AuditResponse
from backend.schemas.score import ScoreResponse
from backend.schemas.writer import WriterResponse


class CompanyWorkflowResponse(BaseModel):
    company_id: int
    company_name: str
    audit: AuditResponse
    score: ScoreResponse
    writer: WriterResponse