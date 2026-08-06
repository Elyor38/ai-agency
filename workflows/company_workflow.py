from typing import Any

from agents.registry import registry
from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_opportunity import AIOpportunityResult


class CompanyWorkflow:
    """
    Workflow principal qui orchestre les agents
    pour une entreprise donnée.
    """

    def __init__(self) -> None:
        self.auditor = registry.get(
            "auditor"
        )

        self.scorer = registry.get(
            "scorer"
        )

        self.opportunity = registry.get(
            "opportunity"
        )

        self.writer = registry.get(
            "writer"
        )

    def run_audit(
        self,
        company: Company,
    ) -> dict[str, Any]:
        if not company.website:
            raise ValueError(
                "Cette entreprise ne possède pas "
                "de site internet."
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

    def run_opportunity(
        self,
        company: Company,
        audit: Audit | None = None,
        score: Score | None = None,
    ) -> AIOpportunityResult:
        return self.opportunity.run(
            company=company,
            audit=audit,
            score=score,
        )

    def run_writer(
        self,
        company: Company,
        audit: Audit,
        score: Score,
        opportunity: AIOpportunityResult | None = None,
    ):
        return self.writer.run(
            company=company,
            audit=audit,
            score=score,
            opportunity=opportunity,
        )