from typing import Any

from agents.auditor.agent import AuditorAgent
from agents.opportunity.agent import OpportunityAgent
from agents.scorer.agent import ScorerAgent
from agents.website_creation.agent import WebsiteCreationAgent
from agents.writer.agent import WriterAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Any] = {
            "auditor": AuditorAgent(),
            "opportunity": OpportunityAgent(),
            "scorer": ScorerAgent(),
            "website_creation": WebsiteCreationAgent(),
            "writer": WriterAgent(),
        }

    def get(self, name: str) -> Any:
        agent = self._agents.get(name)

        if agent is None:
            available = ", ".join(
                sorted(self._agents.keys())
            )

            raise KeyError(
                f"Agent introuvable : {name}. "
                f"Agents disponibles : {available}"
            )

        return agent

    def list_names(self) -> list[str]:
        return sorted(
            self._agents.keys()
        )


registry = AgentRegistry()