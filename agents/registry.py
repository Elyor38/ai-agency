from agents.scorer.agent import ScorerAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents = {
            "scorer": ScorerAgent(),
        }

    def get(self, name: str):
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