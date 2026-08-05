import json
from typing import TypeVar

import requests
from pydantic import BaseModel, ValidationError

from backend.core.config import OLLAMA_MODEL, OLLAMA_URL


class OllamaError(RuntimeError):
    pass


ModelType = TypeVar(
    "ModelType",
    bound=BaseModel,
)


def _raise_ollama_http_error(
    response: requests.Response,
) -> None:
    try:
        details = response.json()
    except ValueError:
        details = response.text

    raise OllamaError(
        f"Ollama a refusé la requête avec le code "
        f"{response.status_code} : {details}"
    )


def ask_ollama(prompt: str) -> str:
    endpoint = f"{OLLAMA_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": (
            "Tu es un assistant professionnel français. "
            "Tu réponds toujours en français."
        ),
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.2,
        },
    }

    try:
        response = requests.post(
            endpoint,
            json=payload,
            timeout=180,
        )

    except requests.RequestException as error:
        raise OllamaError(
            f"Impossible de contacter Ollama : {error}"
        ) from error

    if not response.ok:
        _raise_ollama_http_error(response)

    try:
        data = response.json()
    except ValueError as error:
        raise OllamaError(
            "Ollama a renvoyé une réponse HTTP invalide."
        ) from error

    answer = data.get("response", "").strip()

    if not answer:
        raise OllamaError(
            "Ollama a renvoyé une réponse vide."
        )

    return answer


def ask_ollama_structured(
    prompt: str,
    response_model: type[ModelType],
) -> ModelType:
    endpoint = f"{OLLAMA_URL}/api/generate"

    json_schema = response_model.model_json_schema()

    schema_text = json.dumps(
        json_schema,
        ensure_ascii=False,
        indent=2,
    )

    structured_prompt = f"""
{prompt}

Consignes obligatoires :

- Réponds uniquement en français.
- Toutes les valeurs textuelles doivent être en français.
- Réponds uniquement avec un objet JSON valide.
- N'ajoute aucun texte avant ou après le JSON.
- N'utilise pas de bloc Markdown.
- Respecte exactement les noms des champs du schéma.
- Respecte exactement les types attendus.
- N'invente aucune information absente.
- Ne considère comme certain que ce qui est explicitement fourni.
- Lorsqu'une information est inconnue, indique clairement qu'elle est inconnue.
- Le champ priority doit être exactement : low, medium ou high.
- Le champ global_score doit être compris entre 0 et 100.

Le JSON doit respecter exactement ce schéma :

{schema_text}
""".strip()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": structured_prompt,
        "system": (
            "Tu es un consultant français spécialisé en sites web, "
            "SEO local, marketing et conversion commerciale. "
            "Tu réponds toujours en français. "
            "Tu ne dois jamais inventer de faits. "
            "Pour les réponses structurées, tu renvoies uniquement "
            "du JSON valide."
        ),
        "format": "json",
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.1,
        },
    }

    try:
        response = requests.post(
            endpoint,
            json=payload,
            timeout=240,
        )

    except requests.RequestException as error:
        raise OllamaError(
            f"Impossible de contacter Ollama : {error}"
        ) from error

    if not response.ok:
        _raise_ollama_http_error(response)

    try:
        data = response.json()
    except ValueError as error:
        raise OllamaError(
            "Ollama a renvoyé une réponse HTTP invalide."
        ) from error

    raw_answer = data.get("response", "").strip()

    if not raw_answer:
        raise OllamaError(
            "Ollama a renvoyé une réponse structurée vide."
        )

    try:
        return response_model.model_validate_json(
            raw_answer
        )

    except ValidationError as error:
        raise OllamaError(
            "La réponse de l'IA est bien en JSON, mais elle ne "
            "respecte pas le schéma demandé.\n"
            f"Erreur Pydantic : {error}\n"
            f"Réponse reçue : {raw_answer}"
        ) from error