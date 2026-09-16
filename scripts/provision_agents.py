"""Create the three live Foundry agent definitions used by the demo.

Run only after infrastructure provisioning and search-index seeding.
"""

from __future__ import annotations

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
from dotenv import load_dotenv

from meridian_iq.config import Settings
from meridian_iq.patterns.prompt_agent import create_live_prompt_agent


def main() -> None:
    load_dotenv()
    settings = Settings.from_env()
    settings.require_live()
    project = AIProjectClient(
        endpoint=settings.project_endpoint,
        credential=DefaultAzureCredential(),
    )
    bing = project.connections.get(settings.bing_connection_name)

    client_agent = project.agents.create_version(
        agent_name=settings.client_data_agent_name,
        definition=PromptAgentDefinition(
            model=settings.model_deployment,
            instructions=(
                "Retrieve Alex Rivera's engagement context with Work IQ and "
                "structured tax/property records with Fabric IQ. Call both "
                "tools, show calculation inputs, and cite each record."
            ),
            tools=[
                WorkIQPreviewTool(
                    work_iq_preview=WorkIQPreviewToolParameters(
                        project_connection_id=settings.work_iq_connection_id
                    )
                ),
                MicrosoftFabricPreviewTool(
                    fabric_dataagent_preview=FabricDataAgentToolParameters(
                        project_connections=[
                            ToolProjectConnection(
                                project_connection_id=(
                                    settings.fabric_iq_connection_id
                                )
                            )
                        ]
                    )
                ),
            ],
        ),
    )

    research_agent = project.agents.create_version(
        agent_name=settings.research_agent_name,
        definition=PromptAgentDefinition(
            model=settings.model_deployment,
            instructions=(
                "Research home-sale tax rules. Always use both the curated "
                "Foundry IQ index and Bing-grounded Web IQ. Prefer IRS primary "
                "sources, identify current-year changes, and preserve citations."
            ),
            tools=[
                AzureAISearchTool(
                    azure_ai_search=AzureAISearchToolResource(
                        indexes=[
                            AISearchIndexResource(
                                project_connection_id=settings.search_connection_id,
                                index_name=settings.search_index_name,
                                query_type=AzureAISearchQueryType.SEMANTIC,
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
            ],
        ),
    )
    _, prompt_agent = create_live_prompt_agent(settings)
    print(f"FOUNDRY_PROMPT_AGENT_NAME={prompt_agent.name}")
    print(f"FOUNDRY_RESEARCH_AGENT_NAME={research_agent.name}")
    print(f"FOUNDRY_RESEARCH_AGENT_VERSION={research_agent.version}")
    print(f"FOUNDRY_CLIENT_DATA_AGENT_NAME={client_agent.name}")
    print(f"FOUNDRY_CLIENT_DATA_AGENT_VERSION={client_agent.version}")


if __name__ == "__main__":
    main()
