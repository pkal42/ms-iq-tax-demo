"""Deterministic synthesis used by offline demonstration modes."""

from __future__ import annotations

from typing import Iterable

from meridian_iq.models import SourceFact


def _fact(facts: Iterable[SourceFact], name: str) -> SourceFact:
    return next(item for item in facts if item.fact == name)


def synthesize_home_sale(facts: list[SourceFact]) -> str:
    sale = _fact(facts, "home_sale").value
    basis = _fact(facts, "property_basis").value
    costs = _fact(facts, "sale_costs").value
    rules = _fact(facts, "section_121_exclusion").value
    income = _fact(facts, "income_profile").value

    amount_realized = sale["sale_price"] - costs["broker_and_closing_costs"]
    preliminary_gain = amount_realized - basis["adjusted_basis"]
    exclusion = rules["single"]
    estimated_taxable_gain = max(0, preliminary_gain - exclusion)

    return f"""## Executive answer

Alex appears to qualify for the principal-residence exclusion based on the recorded ownership and use history. The preliminary gain is **${preliminary_gain:,.0f}**. Applying the **${exclusion:,.0f}** single-filer exclusion leaves an estimated **${estimated_taxable_gain:,.0f} of long-term capital gain** before final return-level adjustments.

## How Meridian arrived at it

- **Work IQ** confirmed a ${sale["sale_price"]:,.0f} sale on {sale["sale_date"]}, continuous primary-residence use since 2015, single filing status, no business use, and no exclusion claimed in the prior two years.
- **Fabric IQ** supplied the ${basis["purchase_price"]:,.0f} purchase price, ${basis["capital_improvements"]:,.0f} of improvements, ${costs["broker_and_closing_costs"]:,.0f} of selling costs, and the income profile. Amount realized is ${amount_realized:,.0f}; adjusted basis is ${basis["adjusted_basis"]:,.0f}.
- **Foundry IQ** applied the Section 121 ownership/use test and the curated Meridian disposition formula.
- **Web IQ** confirmed the current exclusion amount, flagged a possible 3.8% Net Investment Income Tax screen once MAGI exceeds $200,000 for a single filer, and confirmed the Form 1099-S reporting consideration.

## Preparer next actions

Obtain the closing disclosure, Form 1099-S, original purchase statement, and improvement invoices. Validate whether every improvement is capitalizable and run the final capital-gain and NIIT calculations with Alex's complete 2026 income. Prior-year AGI was ${income["2025_agi"]:,.0f}; current W-2 data is incomplete and should not be treated as final taxable income.

> Demo estimate only. This is not a completed return or legal/tax advice."""
