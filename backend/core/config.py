import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# BASE DE DONNÉES
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")


DB_HOST = os.getenv(
    "DB_HOST",
    "localhost",
)

DB_PORT = os.getenv(
    "DB_PORT",
    "5432",
)

DB_NAME = os.getenv(
    "DB_NAME",
    "agency",
)

DB_USER = os.getenv(
    "DB_USER",
    "postgres",
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD"
)


# Si DATABASE_URL n'est pas fournie,
# on la construit avec les variables DB_*.
if not DATABASE_URL:

    if not DB_PASSWORD:
        raise RuntimeError(
            "DB_PASSWORD est absent. "
            "Vérifie le fichier .env "
            "à la racine du projet."
        )

    DATABASE_URL = (
        f"postgresql+psycopg://"
        f"{DB_USER}:"
        f"{DB_PASSWORD}@"
        f"{DB_HOST}:"
        f"{DB_PORT}/"
        f"{DB_NAME}"
    )


# ============================================================
# OLLAMA
# ============================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:7b",
)