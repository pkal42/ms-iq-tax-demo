"""Single prompt-agent pattern using one tool for each Microsoft IQ."""

from __future__ import annotations

from meridian_iq.config import Settings
from meridian_iq.connectors import (
    get_client_tax_data,
    search_client_work,
    search_current_tax_updates,
    search_tax_knowledge,
)
from meridian_iq.models import AgentTrace, DemoResult
from meridian_iq.patterns.synthesis import synthesize_home_sale

DEFAULT_QUESTION = (
    "Alex Rivera sold a home this year. What is the capital-gains impact, "
    "and do current law changes affect the result?"
)


def run_prompt_agent(
    question: str = DEFAULT_QUESTION, settings: Settings | None = None
) -> DemoResult:
    settings = settings or Settings.from_env()
    if settings.mode == "azure":
        return _run_live_prompt_agent(question, settings)

    calls = [
        ("work_iq", search_client_work("Alex Rivera", question)),
        ("fabric_iq", get_client_tax_data("AR-10482")),
        ("foundry_iq", search_tax_knowledge(question)),
        ("web_iq", search_current_tax_updates(question)),
    ]
    facts = [fact for _, result in calls for fact in result]
    trace = [
        AgentTrace(
            actor="Meridian Prompt Agent",
            action=f"called {tool}",
            sources=(result[0].iq,) if result else (),
        )
        for tool, result in calls
    ]
    trace.append(
        AgentTrace(
            actor="Meridian Prompt Agent",
            action="synthesized grounded client answer",
            sources=("Work IQ", "Fabric IQ", "Foundry IQ", "Web IQ"),
        )
    )
    return DemoResult(question, synthesize_home_sale(facts), facts, trace)


def create_live_prompt_agent(settings: Settings):
    """Create a Foundry prompt-agent version with all four IQ tool contracts.

    All four tools execute in Foundry. Work IQ and Fabric IQ project
    connections are tenant-specific and intentionally configured after the IaC
    run; AI Search and Bing connections are provisioned by Bicep.
    """
    settings.require_live()
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import (
        AISearchIndexResource,
        AzureAISearchQueryType,
        AzureAISearchTool,
        AzureAISearchToolResource,
        BingGroundingSearchConfiguration,
        BingGroundingSearchToolParameters,
        BingGroundingTool,
        FabricDataAgentToolParameters,
        MicrosoftFabricPreviewTool,
        PromptAgentDefinition,
        ToolProjectConnection,
        WorkIQPreviewTool,
        WorkIQPreviewToolParameters,
    )
    from azure.identity import DefaultAzureCredential

    project = AIProjectClient(
        endpoint=settings.project_endpoint,
        credential=DefaultAzureCredential(),
    )
    bing = project.connections.get(settings.bing_connection_name)
    tools = [
        WorkIQPreviewTool(
            work_iq_preview=WorkIQPreviewToolParameters(
                project_connection_id=settings.work_iq_connection_id
            )
        ),
        MicrosoftFabricPreviewTool(
            fabric_dataagent_preview=FabricDataAgentToolParameters(
                project_connections=[
                    ToolProjectConnection(
                        project_connection_id=settings.fabric_iq_connection_id
                    )
                ]
            )
        ),
        AzureAISearchTool(
            azure_ai_search=AzureAISearchToolResource(
                indexes=[
                    AISearchIndexResource(
                        project_connection_id=settings.search_connection_id,
                        index_name=settings.search_index_name,
                        query_type=AzureAISearchQueryType.SEMANTIC,
                        filter="category eq 'home-sale'",
                    )
                ]
            )
        ),
        BingGroundingTool(
            bing_grounding=BingGroundingSearchToolParameters(
                search_configurations=[
                    BingGroundingSearchConfiguration(
                        project_connection_id=bing.id
                    )
                ]
            )
        ),
    ]
    agent = project.agents.create_version(
        agent_name=settings.prompt_agent_name,
        definition=PromptAgentDefinition(
            model=settings.model_deployment,
            instructions=(
                "You are Meridian Tax Advisors' home-sale specialist. You MUST "
                "call Work IQ, Fabric IQ, Foundry IQ (Azure AI Search), and Web "
                "IQ (Bing Grounding) before answering. Attribute every material "
                "fact to an IQ source and preserve citations. State assumptions "
                "and do not present an estimate as a completed tax return."
            ),
            tools=tools,
        ),
    )
    return project, agent


def _run_live_prompt_agent(question: str, settings: Settings) -> DemoResult:
    project, agent = create_live_prompt_agent(settings)
    openai = project.get_openai_client()
    response = openai.responses.create(
        input=question,
        tool_choice="required",
        extra_body={
            "agent_reference": {
                "name": agent.name,
                "type": "agent_reference",
            }
        },
    )
    return DemoResult(
        question=question,
        answer=response.output_text,
        facts=[],
        trace=[
            AgentTrace(
                actor=settings.prompt_agent_name,
                action="executed hosted prompt agent",
                sources=("Work IQ", "Fabric IQ", "Foundry IQ", "Web IQ"),
            )
        ],
    )
