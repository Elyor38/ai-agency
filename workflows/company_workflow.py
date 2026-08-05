from typing import Any

from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score

from agents.registry import registry


class CompanyWorkflow:
    """
    Workflow principal qui orchestre les agents
    pour une entreprise donnée.
    """

    def __init__(self) -> None:
        self.auditor = registry.get("auditor")
        self.scorer = registry.get("scorer")
        self.writer = registry.get("writer")

    def run_audit(
        self,
        company: Company,
    ) -> dict[str, Any]:
        if not company.website:
            raise ValueError(
                "Cette entreprise ne possède pas de site internet."
            )

        return self.auditor.run(
            company_name=company.name,
            website=company.website,
            sector=company.sector,
            city=company.city,
        )

    def run_score(
        self,
        company: Company,
        audit: Audit,
    ):
        return self.scorer.run(
            company_name=company.name,
            sector=company.sector,
            city=company.city,
            audit=audit,
        )

    def run_writer(
        self,
        company: Company,
        audit: Audit,
        score: Score,
    ):
        return self.writer.run(
            company=company,
            audit=audit,
            score=score,
        )

    def run_full(
        self,
        company: Company,
        audit: Audit,
        score: Score,
    ) -> dict[str, Any]:
        """
        Exécute la partie Writer à partir d'un audit
        et d'un score déjà enregistrés.

        Pour l'instant, cette méthode ne sauvegarde rien
        automatiquement dans PostgreSQL.
        """
        writer_result = self.run_writer(
            company=company,
            audit=audit,
            score=score,
        )

        return {
            "company_id": company.id,
            "company_name": company.name,
            "audit_id": audit.id,
            "score_id": score.id,
            "global_score": score.global_score,
            "priority": score.priority,
            "email_subject": writer_result.email_subject,
            "email_body": writer_result.email_body,
            "commercial_offer": writer_result.commercial_offer,
            "call_to_action": writer_result.call_to_action,
        }