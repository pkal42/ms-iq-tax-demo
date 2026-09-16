from meridian_iq.config import Settings
from meridian_iq.patterns.multi_agent import run_multi_agent
from meridian_iq.patterns.prompt_agent import run_prompt_agent


def test_prompt_pattern_calls_every_iq() -> None:
    result = run_prompt_agent(settings=Settings(mode="mock"))
    assert {fact.iq for fact in result.facts} == {
        "Work IQ",
        "Fabric IQ",
        "Foundry IQ",
        "Web IQ",
    }
    assert "$128,000" in result.answer
    assert len(result.trace) == 5


def test_multi_agent_pattern_delegates_to_two_specialists() -> None:
    result = run_multi_agent(settings=Settings(mode="mock"))
    actors = {item.actor for item in result.trace}
    assert "Client Data Agent (Foundry hosted)" in actors
    assert "Research Agent (Foundry hosted)" in actors
    assert "$378,000" in result.answer


def test_live_settings_report_missing_configuration() -> None:
    settings = Settings(mode="azure")
    try:
        settings.require_live()
    except ValueError as exc:
        assert "FOUNDRY_PROJECT_ENDPOINT" in str(exc)
    else:
        raise AssertionError("Azure mode accepted incomplete configuration")


def test_provisioning_does_not_require_versions() -> None:
    settings = Settings(
        mode="azure",
        project_endpoint="https://example.test/api/projects/demo",
        search_connection_id="search",
        bing_connection_name="bing",
        work_iq_connection_id="work",
        fabric_iq_connection_id="fabric",
    )
    settings.require_live()
    try:
        settings.require_live(require_agent_versions=True)
    except ValueError as exc:
        assert "FOUNDRY_RESEARCH_AGENT_VERSION" in str(exc)
    else:
        raise AssertionError("Multi-agent mode accepted missing versions")
