from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from agents.registry import registry
from backend.database.connection import get_db
from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.models.writer import Writer
from backend.schemas.writer import WriterResponse
from backend.services.email_quality_service import (
    EmailQualityError,
)
from backend.services.ollama_service import OllamaError


router = APIRouter(
    prefix="/writers",
    tags=["Writer"],
)


@router.post(
    "/scores/{score_id}",
    response_model=WriterResponse,
)
def create_writer_draft(
    score_id: int,
    db: Session = Depends(get_db),
):
    score = db.get(
        Score,
        score_id,
    )

    if score is None:
        raise HTTPException(
            status_code=404,
            detail="Score introuvable.",
        )

    audit = db.get(
        Audit,
        score.audit_id,
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit introuvable.",
        )

    company = db.get(
        Company,
        score.company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Entreprise introuvable.",
        )

    writer_agent = registry.get(
        "writer"
    )

    try:
        result = writer_agent.run(
            company=company,
            audit=audit,
            score=score,
        )

    except (
        OllamaError,
        EmailQualityError,
    ) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    writer = Writer(
        company_id=company.id,
        audit_id=audit.id,
        score_id=score.id,
        email_subject=result.email_subject,
        email_body=result.email_body,
        commercial_offer=result.commercial_offer,
        call_to_action=result.call_to_action,
    )

    try:
        db.add(writer)
        db.commit()
        db.refresh(writer)

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Impossible d'enregistrer le brouillon.",
        ) from error

    return writer


@router.get(
    "/companies/{company_id}",
    response_model=list[WriterResponse],
)
def list_company_writers(
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
        select(Writer)
        .where(
            Writer.company_id == company_id
        )
        .order_by(
            Writer.id.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )