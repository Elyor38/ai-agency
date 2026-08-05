from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.models.writer import Writer
from backend.schemas.workflow import CompanyWorkflowResponse
from backend.services.auditor_service import AuditorError
from backend.services.ollama_service import OllamaError
from backend.services.scorer_service import ScorerError
from backend.utils.prompt_loader import PromptError
from workflows.company_workflow import CompanyWorkflow


router = APIRouter(
    prefix="/workflow",
    tags=["Workflow"],
)


@router.post(
    "/companies/{company_id}",
    response_model=CompanyWorkflowResponse,
)
def run_company_workflow(
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
            detail=(
                "Cette entreprise ne possède pas "
                "de site internet."
            ),
        )

    workflow = CompanyWorkflow()

    try:
        # 1. Analyse technique et audit IA
        audit_result = workflow.run_audit(
            company=company,
        )

        # Objet temporaire non encore enregistré.
        # Le Scorer a seulement besoin de ses données.
        audit = Audit(
            company_id=company.id,
            **audit_result,
        )

        # 2. Score structuré
        ai_score = workflow.run_score(
            company=company,
            audit=audit,
        )

        # Objet temporaire pour préparer le Writer.
        # audit_id sera remplacé après l'enregistrement de l'audit.
        score = Score(
            company_id=company.id,
            audit_id=0,
            **ai_score.model_dump(),
        )

        # 3. Brouillon commercial
        writer_result = workflow.run_writer(
            company=company,
            audit=audit,
            score=score,
        )

    except (
        AuditorError,
        OllamaError,
        ScorerError,
        PromptError,
    ) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    try:
        # 4. Enregistrer l'audit et obtenir son ID
        db.add(audit)
        db.flush()

        # 5. Enregistrer le score avec le véritable audit_id
        score.audit_id = audit.id
        db.add(score)
        db.flush()

        # 6. Enregistrer le brouillon Writer
        writer = Writer(
            company_id=company.id,
            audit_id=audit.id,
            score_id=score.id,
            email_subject=writer_result.email_subject,
            email_body=writer_result.email_body,
            commercial_offer=writer_result.commercial_offer,
            call_to_action=writer_result.call_to_action,
        )

        db.add(writer)
        db.commit()

        db.refresh(audit)
        db.refresh(score)
        db.refresh(writer)

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Impossible d'enregistrer les résultats "
                "du workflow."
            ),
        ) from error

    return {
        "company_id": company.id,
        "company_name": company.name,
        "audit": audit,
        "score": score,
        "writer": writer,
    }