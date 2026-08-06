import pytest

from backend.schemas.ai_writer import AIWriterResult
from backend.services.email_quality_service import (
    EmailQualityError,
    find_forbidden_terms,
    validate_writer_result,
)


def build_writer_result(
    email_body: str,
) -> AIWriterResult:
    return AIWriterResult(
        email_subject=(
            "Quelques idées pour faciliter vos réservations"
        ),
        email_body=email_body,
        commercial_offer=(
            "Amélioration du parcours de réservation "
            "et de la prise de contact."
        ),
        call_to_action=(
            "Seriez-vous disponible pour un échange "
            "de 15 minutes, sans engagement ?"
        ),
    )


def test_clear_commercial_email_is_valid() -> None:
    result = build_writer_result(
        "Votre établissement possède déjà une présence en ligne "
        "claire et rassurante. Nous avons identifié quelques "
        "améliorations simples qui pourraient faciliter les "
        "réservations et permettre aux visiteurs de vous contacter "
        "plus rapidement. Nous pouvons vous présenter ces pistes "
        "pendant un échange de 15 minutes, sans engagement."
    )

    validate_writer_result(result)


def test_technical_email_is_rejected() -> None:
    result = build_writer_result(
        "Votre balise H2 et votre méta description doivent être "
        "modifiées afin d'améliorer votre présence en ligne. "
        "Nous pouvons vous présenter les différentes corrections "
        "techniques lors d'un échange de 15 minutes."
    )

    forbidden_terms = find_forbidden_terms(result)

    assert "balise h2" in forbidden_terms
    assert "méta description" in forbidden_terms

    with pytest.raises(EmailQualityError):
        validate_writer_result(result)