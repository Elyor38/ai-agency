from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.company import Company
from backend.schemas.company import CompanyCreate, CompanyResponse


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
):
    company = Company(**company_data.model_dump())

    try:
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erreur pendant l'enregistrement de l'entreprise.",
        ) from error


@router.get(
    "",
    response_model=list[CompanyResponse],
)
def list_companies(
    db: Session = Depends(get_db),
):
    statement = select(Company).order_by(Company.id.desc())
    companies = db.scalars(statement).all()

    return list(companies)


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Entreprise introuvable",
        )

    return company