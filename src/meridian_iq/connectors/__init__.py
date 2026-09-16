"""IQ connector interfaces and mock implementations."""

from meridian_iq.connectors.fabric_iq import get_client_tax_data
from meridian_iq.connectors.foundry_iq import search_tax_knowledge
from meridian_iq.connectors.web_iq import search_current_tax_updates
from meridian_iq.connectors.work_iq import search_client_work

__all__ = [
    "get_client_tax_data",
    "search_client_work",
    "search_current_tax_updates",
    "search_tax_knowledge",
]
