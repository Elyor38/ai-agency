from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.models.writer import Writer
from backend.schemas.dashboard import DashboardStatsResponse


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
):
    companies_count = db.scalar(
        select(func.count()).select_from(Company)
    ) or 0

    audits_count = db.scalar(
        select(func.count()).select_from(Audit)
    ) or 0

    scores_count = db.scalar(
        select(func.count()).select_from(Score)
    ) or 0

    writers_count = db.scalar(
        select(func.count()).select_from(Writer)
    ) or 0

    return {
        "companies": companies_count,
        "audits": audits_count,
        "scores": scores_count,
        "writers": writers_count,
    }