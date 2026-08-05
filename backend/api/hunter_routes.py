from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.company import Company
from backend.schemas.hunter import HunterResult, HunterSearchRequest
from backend.services.hunter_service import HunterError, search_businesses


router = APIRouter(
    prefix="/hunter",
    tags=["Hunter"],
)


@router.post(
    "/search",
    response_model=HunterResult,
)
def hunter_search(
    data: HunterSearchRequest,
    db: Session = Depends(get_db),
):
    try:
        results = search_businesses(
            city=data.city,
            business_type=data.business_type,
            limit=data.limit,
        )

    except HunterError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    created_companies: list[Company] = []
    skipped = 0

    try:
        for item in results:
            conditions = [
                Company.name == item["name"],
                Company.city == item["city"],
            ]

            if item.get("website"):
                conditions.append(Company.website == item["website"])

            statement = select(Company).where(*conditions)
            existing = db.scalar(statement)

            if existing is not None:
                skipped += 1
                continue

            company = Company(**item)
            db.add(company)
            created_companies.append(company)

        db.commit()

        for company in created_companies:
            db.refresh(company)

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erreur pendant l'enregistrement des prospects.",
        ) from error

    return {
        "found": len(results),
        "created": len(created_companies),
        "skipped": skipped,
        "companies": [
            {
                "id": company.id,
                "name": company.name,
                "website": company.website,
                "phone": company.phone,
                "email": company.email,
                "city": company.city,
                "sector": company.sector,
            }
            for company in created_companies
        ],
    }