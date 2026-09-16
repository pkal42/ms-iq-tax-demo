"""Foundry IQ connector for curated tax publications and firm playbooks."""

from __future__ import annotations

from meridian_iq.models import SourceFact


def search_tax_knowledge(query: str = "home sale exclusion") -> list[SourceFact]:
    """Search curated tax-domain knowledge.

    Real backend swap: query the Azure AI Search index configured by
    AI_SEARCH_PROJECT_CONNECTION_ID and AI_SEARCH_INDEX_NAME, or attach the
    same index as AzureAISearchTool on a Foundry prompt agent.
    """
    documents = [
        SourceFact(
            iq="Foundry IQ",
            fact="section_121_exclusion",
            value={
                "single": 250_000,
                "married_filing_jointly": 500_000,
                "ownership_and_use_test": "2 of the 5 years before sale",
            },
            citation="IRS Publication 523, Selling Your Home",
        ),
        SourceFact(
            iq="Foundry IQ",
            fact="gain_formula",
            value=(
                "Amount realized minus selling expenses minus adjusted basis; "
                "apply any eligible Section 121 exclusion afterward."
            ),
            citation="Meridian Playbook TX-4.7, Residential Dispositions",
        ),
        SourceFact(
            iq="Foundry IQ",
            fact="documentation_checklist",
            value=[
                "closing disclosure",
                "original purchase statement",
                "capital improvement invoices",
                "occupancy history",
                "Form 1099-S",
            ],
            citation="Meridian Playbook TX-4.7 checklist",
        ),
    ]
    terms = set(query.casefold().replace("-", " ").split())
    return [
        item
        for item in documents
        if terms
        & set(f"{item.fact} {item.value}".casefold().replace("_", " ").split())
    ] or documents


def foundry_iq_tool(query: str) -> str:
    """Agent-callable JSON representation of curated knowledge."""
    import json

    return json.dumps(
        [fact.as_dict() for fact in search_tax_knowledge(query)]
    )
