from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.api.ai_routes import router as ai_router
from backend.api.audit_routes import router as audit_router
from backend.api.company_details_routes import (
    router as company_details_router,
)
from backend.api.dashboard_routes import router as dashboard_router
from backend.api.hunter_routes import router as hunter_router
from backend.api.routes import router as companies_router
from backend.api.score_routes import router as score_router
from backend.api.website_offer_routes import (
    router as website_offer_router,
)
from backend.api.workflow_routes import router as workflow_router
from backend.api.writer_routes import router as writer_router

from backend.database.connection import engine

from backend.models.audit import Audit
from backend.models.company import Base
from backend.models.score import Score
from backend.models.writer import Writer


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Création des tables...")

    Base.metadata.create_all(bind=engine)

    print("Base prête !")

    yield

    print("Arrêt du serveur")


app = FastAPI(
    title="AI Agency",
    description=(
        "Assistant commercial local utilisant PostgreSQL, "
        "Ollama et OpenStreetMap."
    ),
    version="0.12",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(companies_router)
app.include_router(company_details_router)
app.include_router(ai_router)
app.include_router(hunter_router)
app.include_router(audit_router)
app.include_router(score_router)
app.include_router(writer_router)
app.include_router(workflow_router)
app.include_router(website_offer_router)
app.include_router(dashboard_router)


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
