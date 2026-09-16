from meridian_iq.connectors.fabric_iq import get_client_tax_data
from meridian_iq.connectors.foundry_iq import search_tax_knowledge
from meridian_iq.connectors.web_iq import search_current_tax_updates
from meridian_iq.connectors.work_iq import search_client_work


def test_work_iq_returns_client_communication_context() -> None:
    facts = search_client_work("Alex Rivera", "home sale")
    assert {fact.fact for fact in facts} >= {
        "home_sale",
        "occupancy_and_use",
        "filing_context",
    }
    assert all(fact.iq == "Work IQ" for fact in facts)


def test_work_iq_is_scoped_to_client() -> None:
    assert search_client_work("Not Alex", "home sale") == []


def test_fabric_iq_returns_reconciled_basis() -> None:
    facts = get_client_tax_data("AR-10482")
    basis = next(item.value for item in facts if item.fact == "property_basis")
    assert basis["adjusted_basis"] == (
        basis["purchase_price"] + basis["capital_improvements"]
    )


def test_fabric_iq_is_scoped_to_client_id() -> None:
    assert get_client_tax_data("unknown") == []


def test_foundry_iq_has_primary_and_internal_sources() -> None:
    facts = search_tax_knowledge("home sale exclusion")
    citations = " ".join(item.citation for item in facts)
    assert "IRS Publication 523" in citations
    assert "Meridian Playbook" in citations


def test_web_iq_returns_current_law_screen() -> None:
    facts = search_current_tax_updates("2026 home sale")
    names = {item.fact for item in facts}
    assert {"current_section_121_status", "niit_screen"} <= names
    assert all(item.iq == "Web IQ" for item in facts)
