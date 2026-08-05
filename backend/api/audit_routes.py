from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.audit import Audit
from backend.models.company import Company
from backend.schemas.audit import AuditResponse
from backend.services.auditor_service import AuditorError, audit_website
from backend.services.ollama_service import OllamaError


router = APIRouter(
    prefix="/audits",
    tags=["Auditor"],
)


@router.post(
    "/companies/{company_id}",
    response_model=AuditResponse,
)
def audit_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Entreprise introuvable.",
        )

    if not company.website:
        raise HTTPException(
            status_code=400,
            detail="Cette entreprise ne possède pas de site internet.",
        )

    try:
        result = audit_website(
            company_name=company.name,
            website=company.website,
            sector=company.sector,
            city=company.city,
        )

    except (AuditorError, OllamaError) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    audit = Audit(
        company_id=company.id,
        **result,
    )

    try:
        db.add(audit)
        db.commit()
        db.refresh(audit)

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Impossible d'enregistrer l'audit.",
        ) from error

    return audit


@router.get(
    "/companies/{company_id}",
    response_model=list[AuditResponse],
)
def list_company_audits(
    company_id: int,
    db: Session = Depends(get_db),
):
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Entreprise introuvable.",
        )

    statement = (
        select(Audit)
        .where(Audit.company_id == company_id)
        .order_by(Audit.id.desc())
    )

    return list(db.scalars(statement).all())