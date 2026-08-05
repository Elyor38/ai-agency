from backend.models.audit import Audit
from backend.schemas.ai_score import AIScore
from backend.services.ollama_service import ask_ollama_structured


def build_scoring_prompt(
    company_name: str,
    sector: str | None,
    city: str | None,
    audit: Audit,
) -> str:
    return f"""
Tu es un consultant commercial français spécialisé en :
- création de sites web ;
- SEO local ;
- conversion ;
- visibilité numérique ;
- marketing pour petites entreprises.

Évalue cette entreprise uniquement à partir des données disponibles.

Entreprise : {company_name}
Secteur : {sector or "non renseigné"}
Ville : {city or "non renseignée"}

Score technique calculé :
{audit.technical_score}/100

Observations techniques :
{audit.observations}

Analyse précédente :
{audit.ai_analysis}

Règles obligatoires :

- réponds uniquement en français ;
- n'invente aucune information absente ;
- global_score doit être compris entre 0 et 100 ;
- priority doit être exactement low, medium ou high ;
- high signifie qu'une prestation semble clairement pertinente ;
- recommended_offer doit être une prestation claire et vendable ;
- les forces, faiblesses et opportunités doivent être concrètes ;
- réponds uniquement selon le schéma JSON demandé.
""".strip()


def score_audit(
    company_name: str,
    sector: str | None,
    city: str | None,
    audit: Audit,
) -> AIScore:
    prompt = build_scoring_prompt(
        company_name=company_name,
        sector=sector,
        city=city,
        audit=audit,
    )

    return ask_ollama_structured(
        prompt=prompt,
        response_model=AIScore,
    )