from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from agents.registry import registry
from backend.database.connection import get_db
from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.models.writer import Writer
from backend.schemas.workflow import CompanyWorkflowResponse
from backend.services.auditor_service import AuditorError
from backend.services.email_quality_service import EmailQualityError
from backend.services.ollama_service import OllamaError
from backend.services.opportunity_service import OpportunityError
from backend.services.scorer_service import ScorerError
from backend.services.website_offer_service import WebsiteOfferError
from backend.utils.prompt_loader import PromptError
from workflows.company_workflow import CompanyWorkflow


router = APIRouter(
    prefix="/workflow",
    tags=["Workflow"],
)


def _run_website_creation_workflow(
    company: Company,
) -> dict:
    """
    Parcours utilisé lorsqu'aucun site internet
    n'est associé à l'entreprise.
    """
    opportunity_agent = registry.get(
        "opportunity"
    )

    opportunity = opportunity_agent.run(
        company=company,
    )

    website_creation_agent = registry.get(
        "website_creation"
    )

    result = website_creation_agent.run(
        company=company,
    )

    website_offer = {
        "company_id": company.id,
        "company_name": company.name,
        "sector": company.sector,
        "city": company.city,
        **result.model_dump(),
    }

    return {
        "workflow_type": "website_creation",
        "company_id": company.id,
        "company_name": company.name,
        "opportunity": opportunity,
        "audit": None,
        "score": None,
        "writer": None,
        "website_offer": website_offer,
    }


def _run_website_audit_workflow(
    company: Company,
    db: Session,
) -> dict:
    """
    Parcours utilisé lorsqu'un site internet
    est associé à l'entreprise.
    """
    workflow = CompanyWorkflow()

    # 1. Audit du site
    audit_result = workflow.run_audit(
        company=company,
    )

    audit = Audit(
        company_id=company.id,
        **audit_result,
    )

    # 2. Score commercial
    ai_score = workflow.run_score(
        company=company,
        audit=audit,
    )

    score = Score(
        company_id=company.id,
        audit_id=0,
        **ai_score.model_dump(),
    )

    # 3. Choix de la meilleure opportunité commerciale
    opportunity = workflow.run_opportunity(
        company=company,
        audit=audit,
        score=score,
    )

    # 4. Génération de l'email spécialisé
    writer_result = workflow.run_writer(
        company=company,
        audit=audit,
        score=score,
        opportunity=opportunity,
    )

    try:
        # 5. Enregistrement de l'audit
        db.add(audit)
        db.flush()

        # 6. Enregistrement du score
        score.audit_id = audit.id

        db.add(score)
        db.flush()

        # 7. Enregistrement du brouillon commercial
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

    except SQLAlchemyError:
        db.rollback()
        raise

    return {
        "workflow_type": "website_audit",
        "company_id": company.id,
        "company_name": company.name,
        "opportunity": opportunity,
        "audit": audit,
        "score": score,
        "writer": writer,
        "website_offer": None,
    }


@router.post(
    "/companies/{company_id}",
    response_model=CompanyWorkflowResponse,
)
def run_company_workflow(
    company_id: int,
    db: Session = Depends(get_db),
):
    """
    Lance automatiquement le bon parcours :

    - création de site si l'entreprise n'a pas de site ;
    - audit, score, opportunité et email spécialisé sinon.
    """
    company = db.get(
        Company,
        company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Entreprise introuvable.",
        )

    try:
        if not company.website:
            return _run_website_creation_workflow(
                company=company,
            )

        return _run_website_audit_workflow(
            company=company,
            db=db,
        )

    except (
        AuditorError,
        OllamaError,
        ScorerError,
        PromptError,
        EmailQualityError,
        WebsiteOfferError,
        OpportunityError,
    ) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Impossible d'enregistrer les résultats "
                "du workflow."
            ),
        ) from error