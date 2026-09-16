"""Work IQ connector for client communications and engagement content."""

from __future__ import annotations

from meridian_iq.models import SourceFact


def search_client_work(
    client_name: str = "Alex Rivera", query: str = "home sale"
) -> list[SourceFact]:
    """Retrieve relevant client work context.

    Real backend swap: replace the in-memory records with Microsoft Graph
    connectors or the Microsoft 365 Copilot Retrieval API. Keep this function
    signature so the agent tool contract remains stable.
    """
    if client_name.casefold() != "alex rivera":
        return []
    records = [
        SourceFact(
            iq="Work IQ",
            fact="home_sale",
            value={
                "sale_date": "2026-06-18",
                "sale_price": 925_000,
                "address": "214 Cedar Ridge Lane, Bellevue, WA",
            },
            citation="M365 email: Alex Rivera to Jamie Chen, 2026-06-22",
        ),
        SourceFact(
            iq="Work IQ",
            fact="occupancy_and_use",
            value="Primary residence from 2015-08-14 through 2026-06-18",
            citation="Teams thread: Rivera engagement / Home sale, 2026-06-24",
        ),
        SourceFact(
            iq="Work IQ",
            fact="filing_context",
            value={
                "expected_status": "single",
                "rental_or_business_use": False,
                "prior_home_exclusion_last_two_years": False,
            },
            citation="2026 Meridian engagement letter addendum, section 3",
        ),
    ]
    terms = {term for term in query.casefold().split() if len(term) > 2}
    if not terms:
        return records
    return [
        record
        for record in records
        if terms
        & set(
            f"{record.fact} {record.value} {record.citation}"
            .casefold()
            .replace("_", " ")
            .split()
        )
    ] or records


def work_iq_tool(client_name: str, query: str) -> str:
    """Agent-callable JSON representation of Work IQ results."""
    import json

    return json.dumps(
        [fact.as_dict() for fact in search_client_work(client_name, query)]
    )
