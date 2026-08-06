from pydantic import BaseModel

from backend.schemas.audit import AuditResponse
from backend.schemas.company import CompanyResponse
from backend.schemas.score import ScoreResponse
from backend.schemas.writer import WriterResponse


class CompanyHistoryItem(BaseModel):
    audit: AuditResponse
    score: ScoreResponse | None = None
    writer: WriterResponse | None = None


class CompanyDetailsResponse(BaseModel):
    company: CompanyResponse

    latest_audit: AuditResponse | None = None
    latest_score: ScoreResponse | None = None
    latest_writer: WriterResponse | None = None

    history: list[CompanyHistoryItem]