"""Web IQ connector for current tax-year law and threshold updates."""

from __future__ import annotations

from meridian_iq.models import SourceFact


def search_current_tax_updates(
    query: str = "2026 home sale capital gains"
) -> list[SourceFact]:
    """Return a stable mock of current web grounding results.

    Real backend swap: attach BingGroundingTool using
    BING_PROJECT_CONNECTION_NAME. Bing results must be treated as external
    content and verified against primary IRS or statutory sources.
    """
    return [
        SourceFact(
            iq="Web IQ",
            fact="current_section_121_status",
            value=(
                "The principal-residence exclusion remains $250,000 for a "
                "single filer and $500,000 for qualifying joint filers."
            ),
            citation="IRS Topic No. 701 and IRS Publication 523 (accessed 2026)",
        ),
        SourceFact(
            iq="Web IQ",
            fact="niit_screen",
            value={
                "rate": "3.8%",
                "single_magi_threshold": 200_000,
                "note": "Only the lesser of net investment income or MAGI excess is subject.",
            },
            citation="IRS Topic No. 559, Net Investment Income Tax",
        ),
        SourceFact(
            iq="Web IQ",
            fact="reporting_update",
            value=(
                "A Form 1099-S generally requires reporting the sale even when "
                "all gain may be excludable; retain the settlement statement."
            ),
            citation="IRS Publication 523, Reporting the Sale",
        ),
    ]


def web_iq_tool(query: str) -> str:
    """Agent-callable JSON representation of Web IQ results."""
    import json

    return json.dumps(
        [fact.as_dict() for fact in search_current_tax_updates(query)]
    )
