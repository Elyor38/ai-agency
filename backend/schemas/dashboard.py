from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    companies: int
    audits: int
    scores: int
    writers: int