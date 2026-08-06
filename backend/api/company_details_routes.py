from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.models.writer import Writer
from backend.schemas.company_details import CompanyDetailsResponse


router = APIRouter(
    prefix="/companies",
    tags=["Company Details"],
)


@router.get(
    "/{company_id}/details",
    response_model=CompanyDetailsResponse,
)
def get_company_details(
    company_id: int,
    db: Session = Depends(get_db),
):
    company = db.get(
        Company,
        company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Entreprise introuvable.",
        )

    audits = list(
        db.scalars(
            select(Audit)
            .where(
                Audit.company_id == company_id
            )
            .order_by(
                Audit.id.desc()
            )
        ).all()
    )

    scores = list(
        db.scalars(
            select(Score)
            .where(
                Score.company_id == company_id
            )
            .order_by(
                Score.id.desc()
            )
        ).all()
    )

    writers = list(
        db.scalars(
            select(Writer)
            .where(
                Writer.company_id == company_id
            )
            .order_by(
                Writer.id.desc()
            )
        ).all()
    )

    scores_by_audit_id = {
        score.audit_id: score
        for score in scores
    }

    writers_by_audit_id = {
        writer.audit_id: writer
        for writer in writers
    }

    history = [
        {
            "audit": audit,
            "score": scores_by_audit_id.get(
                audit.id
            ),
            "writer": writers_by_audit_id.get(
                audit.id
            ),
        }
        for audit in audits
    ]

    latest_audit = (
        audits[0]
        if audits
        else None
    )

    latest_score = (
        scores_by_audit_id.get(
            latest_audit.id
        )
        if latest_audit is not None
        else None
    )

    latest_writer = (
        writers_by_audit_id.get(
            latest_audit.id
        )
        if latest_audit is not None
        else None
    )

    return {
        "company": company,
        "latest_audit": latest_audit,
        "latest_score": latest_score,
        "latest_writer": latest_writer,
        "history": history,
    }