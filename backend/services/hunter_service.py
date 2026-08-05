import time
from typing import Any

import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

OVERPASS_URLS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

HEADERS = {
    "User-Agent": "AI-Agency-Local/0.4 contact=local-development",
    "Accept-Language": "fr",
}

BUSINESS_TAGS: dict[str, tuple[str, str]] = {
    "restaurant": ("amenity", "restaurant"),
    "cafe": ("amenity", "cafe"),
    "bar": ("amenity", "bar"),
    "pharmacy": ("amenity", "pharmacy"),
    "dentist": ("amenity", "dentist"),
    "doctor": ("amenity", "doctors"),
    "garage": ("shop", "car_repair"),
    "hairdresser": ("shop", "hairdresser"),
    "bakery": ("shop", "bakery"),
    "supermarket": ("shop", "supermarket"),
    "hotel": ("tourism", "hotel"),
}


class HunterError(RuntimeError):
    pass


def normalize_business_type(value: str) -> str:
    normalized = value.strip().lower()

    aliases = {
        "restaurants": "restaurant",
        "resto": "restaurant",
        "restos": "restaurant",
        "cafés": "cafe",
        "café": "cafe",
        "garage automobile": "garage",
        "garages automobiles": "garage",
        "garages": "garage",
        "coiffeur": "hairdresser",
        "coiffeurs": "hairdresser",
        "salon de coiffure": "hairdresser",
        "salons de coiffure": "hairdresser",
        "boulangerie": "bakery",
        "boulangeries": "bakery",
        "pharmacie": "pharmacy",
        "pharmacies": "pharmacy",
        "dentiste": "dentist",
        "dentistes": "dentist",
        "médecin": "doctor",
        "médecins": "doctor",
        "docteur": "doctor",
        "docteurs": "doctor",
        "hôtel": "hotel",
        "hôtels": "hotel",
    }

    return aliases.get(normalized, normalized)


def geocode_city(city: str) -> dict[str, float]:
    params = {
        "q": city,
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
    }

    try:
        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=HEADERS,
            timeout=30,
        )
        response.raise_for_status()

    except requests.RequestException as error:
        raise HunterError(
            f"Impossible de localiser la ville « {city} » : {error}"
        ) from error

    results = response.json()

    if not results:
        raise HunterError(
            f"La ville « {city} » est introuvable."
        )

    item = results[0]

    try:
        latitude = float(item["lat"])
        longitude = float(item["lon"])

    except (KeyError, TypeError, ValueError) as error:
        raise HunterError(
            "Nominatim a renvoyé des coordonnées invalides."
        ) from error

    return {
        "latitude": latitude,
        "longitude": longitude,
    }


def build_overpass_query(
    business_type: str,
    latitude: float,
    longitude: float,
    limit: int,
) -> str:
    normalized_type = normalize_business_type(business_type)
    tag = BUSINESS_TAGS.get(normalized_type)

    if tag is None:
        supported = ", ".join(sorted(BUSINESS_TAGS))

        raise HunterError(
            "Type d'entreprise non pris en charge. "
            f"Types disponibles : {supported}"
        )

    key, value = tag

    # Rayon raisonnable autour du centre-ville.
    # Cela évite d'interroger toute la métropole.
    radius = 6000

    # On demande plus de résultats que nécessaire,
    # car certains objets peuvent ne pas avoir de nom.
    overpass_limit = min(max(limit * 4, 20), 200)

    return f"""
    [out:json][timeout:45];
    (
      node["{key}"="{value}"](around:{radius},{latitude},{longitude});
      way["{key}"="{value}"](around:{radius},{latitude},{longitude});
      relation["{key}"="{value}"](around:{radius},{latitude},{longitude});
    );
    out center tags {overpass_limit};
    """


def request_overpass(query: str) -> dict[str, Any]:
    errors: list[str] = []

    for overpass_url in OVERPASS_URLS:
        for attempt in range(1, 3):
            try:
                response = requests.post(
                    overpass_url,
                    data={"data": query},
                    headers=HEADERS,
                    timeout=(15, 90),
                )

                response.raise_for_status()
                return response.json()

            except requests.RequestException as error:
                errors.append(
                    f"{overpass_url} — tentative {attempt}/2 : {error}"
                )

                # Petite attente avant une nouvelle tentative.
                time.sleep(attempt * 2)

            except ValueError as error:
                errors.append(
                    f"{overpass_url} — réponse JSON invalide : {error}"
                )
                break

    details = "\n".join(errors)

    raise HunterError(
        "Tous les serveurs Overpass ont échoué.\n"
        f"{details}"
    )


def extract_company(
    element: dict[str, Any],
    city: str,
    business_type: str,
) -> dict[str, Any] | None:
    tags = element.get("tags") or {}

    name = tags.get("name")

    if not isinstance(name, str) or not name.strip():
        return None

    website = (
        tags.get("website")
        or tags.get("contact:website")
        or tags.get("url")
    )

    email = (
        tags.get("email")
        or tags.get("contact:email")
    )

    phone = (
        tags.get("phone")
        or tags.get("contact:phone")
    )

    street = tags.get("addr:street")
    house_number = tags.get("addr:housenumber")
    postcode = tags.get("addr:postcode")

    address_parts = [
        part
        for part in [house_number, street, postcode]
        if part
    ]

    address = " ".join(address_parts) or "non renseignée"

    latitude = element.get("lat")
    longitude = element.get("lon")

    if latitude is None or longitude is None:
        center = element.get("center") or {}
        latitude = center.get("lat")
        longitude = center.get("lon")

    osm_type = element.get("type", "inconnu")
    osm_id = element.get("id", "inconnu")

    return {
        "name": name.strip(),
        "email": email,
        "phone": phone,
        "website": website,
        "city": city.strip(),
        "sector": normalize_business_type(business_type),
        "notes": (
            "Source : OpenStreetMap. "
            f"Adresse : {address}. "
            f"Coordonnées : {latitude}, {longitude}. "
            f"Objet OSM : {osm_type}/{osm_id}."
        ),
    }


def search_businesses(
    city: str,
    business_type: str,
    limit: int,
) -> list[dict[str, Any]]:
    if limit < 1 or limit > 50:
        raise HunterError(
            "La limite doit être comprise entre 1 et 50."
        )

    location = geocode_city(city)

    # Nominatim demande de ne pas dépasser environ
    # une requête par seconde sur son serveur public.
    time.sleep(1)

    query = build_overpass_query(
        business_type=business_type,
        latitude=location["latitude"],
        longitude=location["longitude"],
        limit=limit,
    )

    data = request_overpass(query)
    elements = data.get("elements", [])

    if not isinstance(elements, list):
        raise HunterError(
            "Overpass a renvoyé un format de données inattendu."
        )

    companies: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for element in elements:
        company = extract_company(
            element=element,
            city=city,
            business_type=business_type,
        )

        if company is None:
            continue

        identity = (
            company["name"].strip().lower(),
            (company["website"] or "").strip().lower(),
            (company["phone"] or "").strip().lower(),
        )

        if identity in seen:
            continue

        seen.add(identity)
        companies.append(company)

        if len(companies) >= limit:
            break

    return companies