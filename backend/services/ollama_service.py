import json
import re
from typing import Any, TypeVar

import requests
from pydantic import BaseModel, ValidationError

from backend.core.config import (
    OLLAMA_MODEL,
    OLLAMA_URL,
)


StructuredModel = TypeVar(
    "StructuredModel",
    bound=BaseModel,
)


class OllamaError(RuntimeError):
    """Erreur liée à la communication ou à la réponse d'Ollama."""


def _build_generate_url() -> str:
    """
    Construit l'adresse de l'endpoint Ollama.

    Accepte par exemple :
    - http://localhost:11434
    - http://localhost:11434/
    """
    return f"{OLLAMA_URL.rstrip('/')}/api/generate"


def _clean_json_text(content: str) -> str:
    """
    Nettoie une réponse JSON éventuellement entourée
    de balises Markdown.
    """
    cleaned_content = content.strip()

    if cleaned_content.startswith("```"):
        cleaned_content = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned_content,
            flags=re.IGNORECASE,
        )

        cleaned_content = re.sub(
            r"\s*```$",
            "",
            cleaned_content,
        )

    return cleaned_content.strip()


def _extract_json_object(content: str) -> Any:
    """
    Transforme la réponse textuelle d'Ollama en objet Python.

    Cette fonction tente d'abord de lire toute la réponse comme JSON.
    Si du texte parasite entoure le JSON, elle extrait le premier objet
    compris entre une accolade ouvrante et une accolade fermante.
    """
    cleaned_content = _clean_json_text(content)

    try:
        return json.loads(cleaned_content)

    except json.JSONDecodeError:
        start_index = cleaned_content.find("{")
        end_index = cleaned_content.rfind("}")

        if (
            start_index == -1
            or end_index == -1
            or end_index <= start_index
        ):
            raise OllamaError(
                "La réponse de l'IA ne contient pas de JSON valide."
            )

        json_fragment = cleaned_content[
            start_index : end_index + 1
        ]

        try:
            return json.loads(json_fragment)

        except json.JSONDecodeError as error:
            raise OllamaError(
                "La réponse de l'IA n'est pas un JSON valide."
            ) from error


def _unwrap_structured_payload(
    payload: Any,
    response_model: type[StructuredModel],
) -> Any:
    """
    Corrige les réponses dans lesquelles Ollama place les données
    attendues sous une clé intermédiaire.

    Exemple reçu :

    {
        "properties": {
            "approved": false,
            "issues": []
        }
    }

    Exemple attendu :

    {
        "approved": false,
        "issues": []
    }
    """
    if not isinstance(payload, dict):
        return payload

    expected_fields = set(
        response_model.model_fields.keys()
    )

    payload_fields = set(
        payload.keys()
    )

    # La réponse possède déjà tout ou partie des champs attendus
    # à la racine.
    if expected_fields.intersection(payload_fields):
        return payload

    possible_wrappers = (
        "properties",
        "data",
        "result",
        "response",
        "output",
        "content",
        "value",
    )

    for wrapper in possible_wrappers:
        nested_payload = payload.get(wrapper)

        if not isinstance(nested_payload, dict):
            continue

        nested_fields = set(
            nested_payload.keys()
        )

        if expected_fields.intersection(nested_fields):
            return nested_payload

    # Certains modèles peuvent ajouter plusieurs niveaux.
    for value in payload.values():
        if not isinstance(value, dict):
            continue

        normalized_value = _unwrap_structured_payload(
            payload=value,
            response_model=response_model,
        )

        if not isinstance(normalized_value, dict):
            continue

        normalized_fields = set(
            normalized_value.keys()
        )

        if expected_fields.intersection(normalized_fields):
            return normalized_value

    return payload


def _send_generate_request(
    payload: dict[str, Any],
    timeout: tuple[int, int] = (10, 180),
) -> dict[str, Any]:
    """
    Envoie une requête à l'endpoint /api/generate d'Ollama.
    """
    try:
        response = requests.post(
            _build_generate_url(),
            json=payload,
            timeout=timeout,
        )

        response.raise_for_status()

    except requests.Timeout as error:
        raise OllamaError(
            "Ollama a mis trop de temps à répondre."
        ) from error

    except requests.ConnectionError as error:
        raise OllamaError(
            "Impossible de contacter Ollama. "
            "Vérifie que le service Ollama est démarré."
        ) from error

    except requests.HTTPError as error:
        response_text = ""

        if error.response is not None:
            response_text = error.response.text.strip()

        detail = (
            f" Détail : {response_text}"
            if response_text
            else ""
        )

        raise OllamaError(
            "Ollama a refusé la requête."
            f"{detail}"
        ) from error

    except requests.RequestException as error:
        raise OllamaError(
            f"Erreur pendant la communication avec Ollama : {error}"
        ) from error

    try:
        response_data = response.json()

    except ValueError as error:
        raise OllamaError(
            "Ollama a renvoyé une réponse HTTP invalide."
        ) from error

    if not isinstance(response_data, dict):
        raise OllamaError(
            "Le format de la réponse Ollama est invalide."
        )

    if response_data.get("error"):
        raise OllamaError(
            f"Ollama a renvoyé une erreur : "
            f"{response_data['error']}"
        )

    return response_data


def ask_ollama(
    prompt: str,
    system_prompt: str | None = None,
) -> str:
    """
    Envoie un prompt simple à Ollama et retourne une réponse textuelle.
    """
    if not prompt.strip():
        raise OllamaError(
            "Le prompt envoyé à Ollama est vide."
        )

    payload: dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
        },
    }

    if system_prompt:
        payload["system"] = system_prompt

    response_data = _send_generate_request(
        payload=payload,
    )

    generated_text = response_data.get(
        "response"
    )

    if not isinstance(generated_text, str):
        raise OllamaError(
            "La réponse d'Ollama ne contient pas de texte."
        )

    generated_text = generated_text.strip()

    if not generated_text:
        raise OllamaError(
            "Ollama a renvoyé une réponse vide."
        )

    return generated_text


def ask_ollama_structured(
    prompt: str,
    response_model: type[StructuredModel],
    system_prompt: str | None = None,
) -> StructuredModel:
    """
    Demande à Ollama une réponse JSON validée par un modèle Pydantic.

    La fonction :
    1. transmet le schéma JSON du modèle à Ollama ;
    2. récupère le texte généré ;
    3. transforme le texte en JSON ;
    4. retire une éventuelle clé d'enveloppe comme 'properties' ;
    5. valide le résultat avec Pydantic.
    """
    if not prompt.strip():
        raise OllamaError(
            "Le prompt structuré envoyé à Ollama est vide."
        )

    json_schema = response_model.model_json_schema()

    structured_instruction = f"""
{prompt}

Format de sortie obligatoire :

- Retourne uniquement un objet JSON valide.
- Ne retourne aucun texte avant ou après le JSON.
- Ne retourne pas un schéma JSON.
- Ne place pas la réponse dans une clé "properties".
- Les champs demandés doivent être directement à la racine de l'objet JSON.

Schéma JSON attendu :

{json.dumps(json_schema, ensure_ascii=False, indent=2)}
""".strip()

    payload: dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": structured_instruction,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
        },
    }

    if system_prompt:
        payload["system"] = system_prompt

    response_data = _send_generate_request(
        payload=payload,
    )

    generated_text = response_data.get(
        "response"
    )

    if not isinstance(generated_text, str):
        raise OllamaError(
            "La réponse structurée d'Ollama ne contient pas de texte."
        )

    generated_text = generated_text.strip()

    if not generated_text:
        raise OllamaError(
            "Ollama a renvoyé une réponse structurée vide."
        )

    parsed_data = _extract_json_object(
        generated_text
    )

    normalized_data = _unwrap_structured_payload(
        payload=parsed_data,
        response_model=response_model,
    )

    try:
        return response_model.model_validate(
            normalized_data
        )

    except ValidationError as error:
        raise OllamaError(
            "La réponse de l'IA est bien en JSON, "
            "mais elle ne respecte pas le schéma demandé. "
            f"Erreur Pydantic : {error}. "
            f"Réponse reçue : {normalized_data}"
        ) from error