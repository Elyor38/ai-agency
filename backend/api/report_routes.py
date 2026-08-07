from io import BytesIO
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.registry import registry
from backend.database.connection import get_db
from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.services.ollama_service import OllamaError
from backend.services.opportunity_service import OpportunityError
from backend.services.pdf_report_service import (
    PDFReportError,
    generate_company_report,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/companies/{company_id}/latest.pdf",
)
def download_latest_company_report(
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

    audit = db.scalar(
        select(Audit)
        .where(
            Audit.company_id == company_id
        )
        .order_by(
            Audit.id.desc()
        )
        .limit(1)
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Aucun audit disponible pour "
                "cette entreprise."
            ),
        )

    score = db.scalar(
        select(Score)
        .where(
            Score.audit_id == audit.id
        )
        .order_by(
            Score.id.desc()
        )
        .limit(1)
    )

    if score is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Aucun score disponible pour "
                "le dernier audit."
            ),
        )

    opportunity_agent = registry.get(
        "opportunity"
    )

    try:
        opportunity = opportunity_agent.run(
            company=company,
            audit=audit,
            score=score,
        )

        pdf_data = generate_company_report(
            company=company,
            audit=audit,
            score=score,
            opportunity=opportunity,
        )

    except (
        OllamaError,
        OpportunityError,
        PDFReportError,
    ) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    safe_company_name = quote(
        company.name.replace(
            " ",
            "_",
        )
    )

    filename = (
        f"rapport_{safe_company_name}.pdf"
    )

    return StreamingResponse(
        BytesIO(pdf_data),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )