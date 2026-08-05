from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIRECTORY = PROJECT_ROOT / "prompts"


class PromptError(RuntimeError):
    """Erreur lors du chargement d'un fichier de prompt."""


def load_prompt(filename: str) -> str:
    if not filename:
        raise PromptError(
            "Le nom du fichier de prompt est obligatoire."
        )

    prompt_path = PROMPTS_DIRECTORY / filename

    if not prompt_path.is_file():
        raise PromptError(
            f"Le fichier de prompt est introuvable : {prompt_path}"
        )

    try:
        content = prompt_path.read_text(
            encoding="utf-8"
        ).strip()

    except OSError as error:
        raise PromptError(
            f"Impossible de lire le prompt : {prompt_path}"
        ) from error

    if not content:
        raise PromptError(
            f"Le fichier de prompt est vide : {prompt_path}"
        )

    return content