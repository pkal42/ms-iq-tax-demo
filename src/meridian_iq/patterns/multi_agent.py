"""Agent Framework pattern with two specialized Foundry-hosted agents."""

from __future__ import annotations

from meridian_iq.config import Settings
from meridian_iq.connectors import (
    get_client_tax_data,
    search_client_work,
    search_current_tax_updates,
    search_tax_knowledge,
)
from meridian_iq.models import AgentTrace, DemoResult
from meridian_iq.patterns.prompt_agent import DEFAULT_QUESTION
from meridian_iq.patterns.synthesis import synthesize_home_sale


def run_multi_agent(
    question: str = DEFAULT_QUESTION, settings: Settings | None = None
) -> DemoResult:
    settings = settings or Settings.from_env()
    if settings.mode == "azure":
        return _run_live_multi_agent(question, settings)

    client_facts = [
        *search_client_work("Alex Rivera", question),
        *get_client_tax_data("AR-10482"),
    ]
    research_facts = [
        *search_tax_knowledge(question),
        *search_current_tax_updates(question),
    ]
    facts = [*client_facts, *research_facts]
    return DemoResult(
        question=question,
        answer=synthesize_home_sale(facts),
        facts=facts,
        trace=[
            AgentTrace(
                actor="Local Meridian Planner",
                action="delegated client-specific fact gathering",
                sources=("Client Data Agent",),
            ),
            AgentTrace(
                actor="Client Data Agent (Foundry hosted)",
                action="queried Work IQ and Fabric IQ",
                sources=("Work IQ", "Fabric IQ"),
            ),
            AgentTrace(
                actor="Local Meridian Planner",
                action="delegated law and policy research",
                sources=("Research Agent",),
            ),
            AgentTrace(
                actor="Research Agent (Foundry hosted)",
                action="queried Foundry IQ and Web IQ",
                sources=("Foundry IQ", "Web IQ"),
            ),
            AgentTrace(
                actor="Local Meridian Planner",
                action="combined specialist outputs",
                sources=("Client Data Agent", "Research Agent"),
            ),
        ],
    )


def _run_live_multi_agent(question: str, settings: Settings) -> DemoResult:
    """Run two remote Foundry agents through Microsoft Agent Framework.

    The two immutable agent definitions are created by
    ``scripts/provision_agents.py``. Agent Framework's FoundryAgent wrappers
    make those remote agents participants in a local concurrent workflow; the
    local planner then asks the model to combine their grounded responses.
    """
    settings.require_live(require_agent_versions=True)
    import asyncio

    return asyncio.run(_run_live_multi_agent_async(question, settings))


async def _run_live_multi_agent_async(
    question: str, settings: Settings
) -> DemoResult:
    from agent_framework.orchestrations import ConcurrentBuilder
    from agent_framework.foundry import FoundryAgent, FoundryChatClient
    from azure.identity.aio import DefaultAzureCredential

    credential = DefaultAzureCredential()
    client_agent = FoundryAgent(
        project_endpoint=settings.project_endpoint,
        agent_name=settings.client_data_agent_name,
        agent_version=settings.client_data_agent_version,
        credential=credential,
    )
    research_agent = FoundryAgent(
        project_endpoint=settings.project_endpoint,
        agent_name=settings.research_agent_name,
        agent_version=settings.research_agent_version,
        credential=credential,
    )
    workflow = ConcurrentBuilder(
        participants=[client_agent, research_agent]
    ).build()
    specialist_output = await workflow.run(question)
    planner_client = FoundryChatClient(
        project_endpoint=settings.project_endpoint,
        model=settings.model_deployment,
        credential=credential,
    )
    planner = planner_client.as_agent(
        name="meridian-local-planner",
        instructions=(
            "Combine the specialist outputs into a concise tax-preparer answer. "
            "Preserve every IQ attribution and citation, show the gain math, "
            "and state that the result is an estimate."
        ),
    )
    response = await planner.run(str(specialist_output))
    await credential.close()
    return DemoResult(
        question=question,
        answer=str(response),
        facts=[],
        trace=[
            AgentTrace(
                actor="Microsoft Agent Framework planner",
                action="coordinated two Foundry-hosted agents",
                sources=(
                    settings.client_data_agent_name,
                    settings.research_agent_name,
                ),
            )
        ],
    )
