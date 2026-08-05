import ipaddress
import socket
import time
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from backend.services.ollama_service import ask_ollama


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 AI-Agency-Auditor/0.1"
)


class AuditorError(RuntimeError):
    pass


def normalize_url(website: str) -> str:
    website = website.strip()

    if not website:
        raise AuditorError("L'entreprise ne possède pas de site internet.")

    if not website.startswith(("http://", "https://")):
        website = f"https://{website}"

    parsed = urlparse(website)

    if parsed.scheme not in {"http", "https"}:
        raise AuditorError("Le protocole du site n'est pas autorisé.")

    if not parsed.hostname:
        raise AuditorError("L'adresse du site est invalide.")

    return website


def ensure_public_website(website: str) -> None:
    """
    Empêche l'auditeur d'accéder à localhost ou au réseau privé.
    """
    hostname = urlparse(website).hostname

    if hostname is None:
        raise AuditorError("Nom de domaine invalide.")

    if hostname.lower() in {"localhost", "localhost.localdomain"}:
        raise AuditorError("Les adresses locales ne sont pas autorisées.")

    try:
        addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as error:
        raise AuditorError(
            f"Impossible de résoudre le domaine : {hostname}"
        ) from error

    for address in addresses:
        ip_value = address[4][0].split("%")[0]

        try:
            ip = ipaddress.ip_address(ip_value)
        except ValueError:
            continue

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        ):
            raise AuditorError(
                "L'adresse du site appartient à un réseau local ou privé."
            )


def find_social_links(
    soup: BeautifulSoup,
    base_url: str,
) -> dict[str, str | None]:
    social_domains = {
        "facebook": "facebook.com",
        "instagram": "instagram.com",
        "linkedin": "linkedin.com",
        "youtube": "youtube.com",
        "tiktok": "tiktok.com",
    }

    results: dict[str, str | None] = {
        name: None
        for name in social_domains
    }

    for anchor in soup.find_all("a", href=True):
        href = urljoin(base_url, anchor["href"])

        for name, domain in social_domains.items():
            if domain in href.lower() and results[name] is None:
                results[name] = href

    return results


def calculate_score(data: dict[str, Any]) -> int:
    score = 0

    if data["https"]:
        score += 15

    if data["http_status"] == 200:
        score += 15

    if data["page_title"]:
        score += 10

        title_length = len(data["page_title"])

        if 25 <= title_length <= 65:
            score += 5

    if data["meta_description"]:
        score += 10

        description_length = len(data["meta_description"])

        if 70 <= description_length <= 170:
            score += 5

    if data["h1_count"] == 1:
        score += 10
    elif data["h1_count"] > 0:
        score += 5

    if data["contact_form"]:
        score += 10

    if data["phone_visible"]:
        score += 5

    if data["email_visible"]:
        score += 5

    if any(data["social_links"].values()):
        score += 5

    if data["response_time_ms"] <= 1500:
        score += 5

    return min(score, 100)


def build_observations(data: dict[str, Any]) -> str:
    social_networks = [
        name
        for name, link in data["social_links"].items()
        if link
    ]

    lines = [
        f"URL analysée : {data['website']}",
        f"HTTPS : {'oui' if data['https'] else 'non'}",
        f"Code HTTP : {data['http_status']}",
        f"Temps de réponse : {data['response_time_ms']} ms",
        f"Titre : {data['page_title'] or 'absent'}",
        (
            "Meta description : "
            f"{data['meta_description'] or 'absente'}"
        ),
        f"Nombre de H1 : {data['h1_count']}",
        f"Nombre de H2 : {data['h2_count']}",
        f"Nombre d'images : {data['image_count']}",
        (
            "Images sans texte alternatif : "
            f"{data['images_without_alt']}"
        ),
        (
            "Formulaire détecté : "
            f"{'oui' if data['contact_form'] else 'non'}"
        ),
        (
            "Téléphone visible : "
            f"{'oui' if data['phone_visible'] else 'non'}"
        ),
        (
            "Email visible : "
            f"{'oui' if data['email_visible'] else 'non'}"
        ),
        (
            "Réseaux sociaux : "
            + (
                ", ".join(social_networks)
                if social_networks
                else "aucun détecté"
            )
        ),
        f"Volume de texte visible : {data['visible_text_length']} caractères",
        f"Score technique déterministe : {data['technical_score']}/100",
    ]

    return "\n".join(lines)


def build_ai_prompt(
    company_name: str,
    sector: str | None,
    city: str | None,
    observations: str,
) -> str:
    return f"""
Tu es consultant spécialisé en marketing local, création de sites web,
référencement naturel et conversion commerciale.

Analyse l'entreprise suivante :

Nom : {company_name}
Secteur : {sector or "non renseigné"}
Ville : {city or "non renseignée"}

Voici les observations techniques relevées automatiquement :

{observations}

Rédige un audit en français, honnête et concret.

Structure obligatoire :

1. Résumé général
2. Points positifs
3. Problèmes prioritaires
4. Cinq améliorations concrètes
5. Opportunité commerciale à proposer
6. Niveau de priorité : faible, moyen ou élevé

Ne prétends pas avoir observé une information absente.
Ne donne pas de garantie de résultats.
Reste professionnel et compréhensible par un dirigeant de petite entreprise.
""".strip()


def audit_website(
    company_name: str,
    website: str,
    sector: str | None,
    city: str | None,
) -> dict[str, Any]:
    normalized_url = normalize_url(website)
    ensure_public_website(normalized_url)

    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.7",
    }

    started_at = time.perf_counter()

    try:
        response = requests.get(
            normalized_url,
            headers=headers,
            timeout=(10, 30),
            allow_redirects=True,
        )
    except requests.RequestException as error:
        raise AuditorError(
            f"Impossible d'ouvrir le site : {error}"
        ) from error

    response_time_ms = round(
        (time.perf_counter() - started_at) * 1000
    )

    content_type = response.headers.get(
        "Content-Type",
        "",
    ).lower()

    if "text/html" not in content_type:
        raise AuditorError(
            "L'adresse ne renvoie pas une page HTML exploitable."
        )

    soup = BeautifulSoup(response.text, "lxml")

    title = None

    if soup.title and soup.title.string:
        title = soup.title.string.strip()[:500]

    meta_tag = soup.find(
        "meta",
        attrs={"name": lambda value: value and value.lower() == "description"},
    )

    meta_description = None

    if meta_tag:
        content = meta_tag.get("content")

        if isinstance(content, str):
            meta_description = content.strip()

    images = soup.find_all("img")
    images_without_alt = sum(
        1
        for image in images
        if not str(image.get("alt", "")).strip()
    )

    forms = soup.find_all("form")

    page_text = soup.get_text(
        separator=" ",
        strip=True,
    )

    lowered_text = page_text.lower()

    social_links = find_social_links(
        soup=soup,
        base_url=response.url,
    )

    data: dict[str, Any] = {
        "website": response.url,
        "https": response.url.lower().startswith("https://"),
        "http_status": response.status_code,
        "response_time_ms": response_time_ms,
        "page_title": title,
        "meta_description": meta_description,
        "h1_count": len(soup.find_all("h1")),
        "h2_count": len(soup.find_all("h2")),
        "image_count": len(images),
        "images_without_alt": images_without_alt,
        "contact_form": len(forms) > 0,
        "phone_visible": (
            "tel:" in response.text.lower()
            or "téléphone" in lowered_text
            or "telephone" in lowered_text
        ),
        "email_visible": (
            "mailto:" in response.text.lower()
            or "@" in page_text
        ),
        "social_links": social_links,
        "visible_text_length": len(page_text),
    }

    data["technical_score"] = calculate_score(data)
    observations = build_observations(data)

    prompt = build_ai_prompt(
        company_name=company_name,
        sector=sector,
        city=city,
        observations=observations,
    )

    ai_analysis = ask_ollama(prompt)

    return {
        "website": data["website"],
        "http_status": data["http_status"],
        "response_time_ms": data["response_time_ms"],
        "technical_score": data["technical_score"],
        "page_title": data["page_title"],
        "meta_description": data["meta_description"],
        "observations": observations,
        "ai_analysis": ai_analysis,
    }