from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from backend.api.ai_routes import router as ai_router
from backend.api.audit_routes import router as audit_router
from backend.api.hunter_routes import router as hunter_router
from backend.api.routes import router as companies_router
from backend.api.score_routes import router as score_router

from backend.database.connection import engine

from backend.models.company import Base
from backend.models.audit import Audit
from backend.models.score import Score


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Création des tables...")

    Base.metadata.create_all(bind=engine)

    print("Base prête !")

    yield

    print("Arrêt du serveur")


app = FastAPI(
    title="AI Agency",
    description="Assistant commercial local utilisant PostgreSQL, Ollama et OpenStreetMap.",
    version="0.6",
    lifespan=lifespan,
)

app.include_router(companies_router)
app.include_router(ai_router)
app.include_router(hunter_router)
app.include_router(audit_router)
app.include_router(score_router)


@app.get("/")
def home():
    return {
        "status": "OK",
        "message": "AI Agency fonctionne 🚀",
    }


@app.get("/database")
def database_test():

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "Connectée",
    }