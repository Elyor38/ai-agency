import re

from backend.schemas.ai_writer import AIWriterResult


FORBIDDEN_TERMS = {
    "seo",
    "meta description",
    "méta description",
    "balise h1",
    "balise h2",
    "attribut alt",
    "html",
    "css",
    "robots.txt",
    "sitemap",
    "temps de réponse serveur",
}


class EmailQualityError(RuntimeError):
    pass


def _normalize_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text.lower(),
    ).strip()


def _contains_term(
    text: str,
    term: str,
) -> bool:
    pattern = (
        rf"(?<!\w)"
        rf"{re.escape(term.lower())}"
        rf"(?!\w)"
    )

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    ) is not None


def find_forbidden_terms(
    writer_result: AIWriterResult,
) -> list[str]:
    full_text = " ".join(
        [
            writer_result.email_subject,
            writer_result.email_body,
            writer_result.commercial_offer,
            writer_result.call_to_action,
        ]
    )

    normalized_text = _normalize_text(
        full_text
    )

    return [
        term
        for term in sorted(FORBIDDEN_TERMS)
        if _contains_term(
            normalized_text,
            term,
        )
    ]


def collect_quality_issues(
    writer_result: AIWriterResult,
) -> list[str]:
    issues: list[str] = []

    forbidden_terms = find_forbidden_terms(
        writer_result
    )

    if forbidden_terms:
        issues.append(
            "Jargon technique détecté : "
            + ", ".join(forbidden_terms)
        )

    email_subject = (
        writer_result.email_subject.strip()
    )

    email_body = (
        writer_result.email_body.strip()
    )

    commercial_offer = (
        writer_result.commercial_offer.strip()
    )

    call_to_action = (
        writer_result.call_to_action.strip()
    )

    if not email_subject:
        issues.append(
            "L'objet de l'email est absent."
        )

    if len(email_subject) > 150:
        issues.append(
            "L'objet de l'email est trop long."
        )

    if len(email_body) < 120:
        issues.append(
            "Le corps de l'email est trop court."
        )

    if len(email_body) > 2500:
        issues.append(
            "Le corps de l'email est trop long."
        )

    if not commercial_offer:
        issues.append(
            "La proposition commerciale est absente."
        )

    if not call_to_action:
        issues.append(
            "L'appel à l'action est absent."
        )

    return issues


def validate_writer_result(
    writer_result: AIWriterResult,
) -> None:
    issues = collect_quality_issues(
        writer_result
    )

    if issues:
        raise EmailQualityError(
            " ".join(issues)
        )