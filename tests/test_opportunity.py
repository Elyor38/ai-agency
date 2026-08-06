from types import SimpleNamespace

from backend.services.opportunity_service import (
    choose_opportunity,
)


def test_company_without_website_gets_creation_offer() -> None:
    company = SimpleNamespace(
        name="Restaurant Sans Site",
        sector="restaurant",
        city="Lyon",
        website=None,
    )

    result = choose_opportunity(company)

    assert result.service == "website_creation"
    assert result.confidence == 1.0
    assert result.reason
    assert result.recommended_action
    assert result.sales_angle