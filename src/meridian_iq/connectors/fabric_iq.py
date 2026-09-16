"""Fabric IQ connector for structured client tax and property data."""

from __future__ import annotations

from meridian_iq.models import SourceFact


def get_client_tax_data(client_id: str = "AR-10482") -> list[SourceFact]:
    """Return modeled OneLake/Lakehouse facts for the client.

    Real backend swap: execute parameterized SQL against a Fabric Warehouse or
    Lakehouse SQL analytics endpoint using Microsoft Entra authentication.
    """
    if client_id != "AR-10482":
        return []
    return [
        SourceFact(
            iq="Fabric IQ",
            fact="property_basis",
            value={
                "purchase_date": "2015-08-14",
                "purchase_price": 420_000,
                "capital_improvements": 85_000,
                "adjusted_basis": 505_000,
            },
            citation="OneLake tax_curated.property_basis row AR-10482-01",
        ),
        SourceFact(
            iq="Fabric IQ",
            fact="sale_costs",
            value={"broker_and_closing_costs": 42_000},
            citation="OneLake tax_curated.property_dispositions row AR-10482-01",
        ),
        SourceFact(
            iq="Fabric IQ",
            fact="income_profile",
            value={
                "2025_agi": 172_400,
                "2026_w2_wages_ytd": 165_000,
                "2026_interest_estimate": 6_500,
            },
            citation="Fabric semantic model Client 360 / Income Summary",
        ),
    ]


def fabric_iq_tool(client_id: str) -> str:
    """Agent-callable JSON representation of Fabric IQ results."""
    import json

    return json.dumps(
        [fact.as_dict() for fact in get_client_tax_data(client_id)]
    )
