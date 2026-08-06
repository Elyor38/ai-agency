from agents.registry import registry


def test_required_agents_are_registered() -> None:
    expected_agents = {
        "auditor",
        "opportunity",
        "scorer",
        "website_creation",
        "writer",
    }

    assert set(registry.list_names()) == expected_agents


def test_agents_can_be_loaded() -> None:
    for agent_name in registry.list_names():
        agent = registry.get(agent_name)

        assert agent is not None
        assert agent.name == agent_name