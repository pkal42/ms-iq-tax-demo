"""Environment-backed settings for mock and Azure modes."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mode: str = "mock"
    project_endpoint: str = ""
    model_deployment: str = "gpt-5-mini"
    prompt_agent_name: str = "meridian-tax-advisor"
    research_agent_name: str = "meridian-research-agent"
    client_data_agent_name: str = "meridian-client-data-agent"
    research_agent_version: str = ""
    client_data_agent_version: str = ""
    search_connection_id: str = ""
    search_index_name: str = "meridian-tax-knowledge"
    bing_connection_name: str = "meridian-bing"
    work_iq_connection_id: str = ""
    fabric_iq_connection_id: str = ""

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            mode=os.getenv("MERIDIAN_MODE", "mock").lower(),
            project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT", ""),
            model_deployment=os.getenv(
                "FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-5-mini"
            ),
            prompt_agent_name=os.getenv(
                "FOUNDRY_PROMPT_AGENT_NAME", "meridian-tax-advisor"
            ),
            research_agent_name=os.getenv(
                "FOUNDRY_RESEARCH_AGENT_NAME", "meridian-research-agent"
            ),
            client_data_agent_name=os.getenv(
                "FOUNDRY_CLIENT_DATA_AGENT_NAME", "meridian-client-data-agent"
            ),
            research_agent_version=os.getenv(
                "FOUNDRY_RESEARCH_AGENT_VERSION", ""
            ),
            client_data_agent_version=os.getenv(
                "FOUNDRY_CLIENT_DATA_AGENT_VERSION", ""
            ),
            search_connection_id=os.getenv(
                "AI_SEARCH_PROJECT_CONNECTION_ID", ""
            ),
            search_index_name=os.getenv(
                "AI_SEARCH_INDEX_NAME", "meridian-tax-knowledge"
            ),
            bing_connection_name=os.getenv(
                "BING_PROJECT_CONNECTION_NAME", "meridian-bing"
            ),
            work_iq_connection_id=os.getenv(
                "WORK_IQ_PROJECT_CONNECTION_ID", ""
            ),
            fabric_iq_connection_id=os.getenv(
                "FABRIC_IQ_PROJECT_CONNECTION_ID", ""
            ),
        )

    def require_live(self, *, require_agent_versions: bool = False) -> None:
        required = {
            "FOUNDRY_PROJECT_ENDPOINT": self.project_endpoint,
            "AI_SEARCH_PROJECT_CONNECTION_ID": self.search_connection_id,
            "BING_PROJECT_CONNECTION_NAME": self.bing_connection_name,
            "WORK_IQ_PROJECT_CONNECTION_ID": self.work_iq_connection_id,
            "FABRIC_IQ_PROJECT_CONNECTION_ID": self.fabric_iq_connection_id,
        }
        if require_agent_versions:
            required.update(
                {
                    "FOUNDRY_RESEARCH_AGENT_VERSION": (
                        self.research_agent_version
                    ),
                    "FOUNDRY_CLIENT_DATA_AGENT_VERSION": (
                        self.client_data_agent_version
                    ),
                }
            )
        missing = [
            name
            for name, value in required.items()
            if not value
        ]
        if missing:
            raise ValueError(
                "Azure mode requires: " + ", ".join(sorted(missing))
            )
