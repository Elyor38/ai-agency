from datetime import datetime

from pydantic import ConfigDict

from backend.schemas.ai_score import AIScore


class ScoreResponse(AIScore):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    audit_id: int
    created_at: datetime