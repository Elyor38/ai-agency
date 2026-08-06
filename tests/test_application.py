from backend.main import app


def test_application_version() -> None:
    assert app.version == "0.12"


def test_required_routes_exist() -> None:
    paths = app.openapi()["paths"]

    required_paths = {
        "/",
        "/database",
        "/companies",
        "/companies/{company_id}",
        "/companies/{company_id}/details",
        "/hunter/search",
        "/workflow/companies/{company_id}",
        "/website-offers/companies/{company_id}",
        "/dashboard/stats",
    }

    missing_paths = required_paths.difference(paths)

    assert not missing_paths, (
        "Routes manquantes : "
        + ", ".join(sorted(missing_paths))
    )