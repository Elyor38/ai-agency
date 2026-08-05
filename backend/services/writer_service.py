from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_writer import AIWriterResult
from backend.services.ollama_service import ask_ollama_structured


def build_writer_prompt(
    company: Company,
    audit: Audit,
    score: Score,
) -> str:
    strengths = "\n".join(
        f"- {item}"
        for item in score.strengths
    )

    weaknesses = "\n".join(
        f"- {item}"
        for item in score.weaknesses
    )

    opportunities = "\n".join(
        f"- {item}"
        for item in score.opportunities
    )

    return f"""
Tu es un rédacteur commercial français spécialisé dans les petites entreprises.

Tu dois préparer un brouillon d'email commercial personnalisé.
Cet email ne sera pas envoyé automatiquement.

Entreprise :
Nom : {company.name}
Secteur : {company.sector or "non renseigné"}
Ville : {company.city or "non renseignée"}
Site : {company.website or "non renseigné"}

Score global :
{score.global_score}/100

Priorité :
{score.priority}

Forces :
{strengths or "- aucune force clairement identifiée"}

Faiblesses :
{weaknesses or "- aucune faiblesse clairement identifiée"}

Opportunités :
{opportunities or "- aucune opportunité clairement identifiée"}

Offre recommandée :
{score.recommended_offer}

Résumé :
{score.summary}

Observations techniques :
{audit.observations}

Règles obligatoires :

- réponds uniquement en français ;
- n'invente aucune information ;
- reste professionnel, humain et concis ;
- ne sois pas agressif ;
- ne prétends pas avoir une relation avec l'entreprise ;
- ne promets pas de résultats garantis ;
- ne critique pas brutalement le site ;
- utilise un ton utile et respectueux ;
- l'email doit être personnalisé avec le nom de l'entreprise ;
- l'objet doit être court et crédible ;
- le corps de l'email doit présenter une observation concrète ;
- propose une amélioration claire ;
- termine par une invitation simple à échanger ;
- ne mentionne jamais l'intelligence artificielle ;
- réponds uniquement selon le schéma JSON demandé.
""".strip()


def generate_writer_result(
    company: Company,
    audit: Audit,
    score: Score,
) -> AIWriterResult:
    prompt = build_writer_prompt(
        company=company,
        audit=audit,
        score=score,
    )

    return ask_ollama_structured(
        prompt=prompt,
        response_model=AIWriterResult,
    )