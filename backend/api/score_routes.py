from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.score import ScoreResponse
from backend.services.ollama_service import OllamaError
from backend.services.scorer_service import score_audit


router = APIRouter(
    prefix="/scores",
    tags=["Scorer"],
)


@router.post(
    "/audits/{audit_id}",
    response_model=ScoreResponse,
)
def create_score(
    audit_id: int,
    db: Session = Depends(get_db),
):
    audit = db.get(Audit, audit_id)

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit introuvable.",
        )

    company = db.get(
        Company,
        audit.company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Entreprise introuvable.",
        )

    try:
        ai_score = score_audit(
            company_name=company.name,
            sector=company.sector,
            city=company.city,
            audit=audit,
        )

    except OllamaError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    score = Score(
        company_id=company.id,
        audit_id=audit.id,
        **ai_score.model_dump(),
    )

    try:
        db.add(score)
        db.commit()
        db.refresh(score)

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Impossible d'enregistrer le score.",
        ) from error

    return score


@router.get(
    "/companies/{company_id}",
    response_model=list[ScoreResponse],
)
def list_company_scores(
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

    statement = (
        select(Score)
        .where(
            Score.company_id == company_id
        )
        .order_by(
            Score.id.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )