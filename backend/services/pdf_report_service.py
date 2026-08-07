import re
from html import escape
from io import BytesIO

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.models.audit import Audit
from backend.models.company import Company
from backend.models.score import Score
from backend.schemas.ai_opportunity import (
    AIOpportunityResult,
)


class PDFReportError(RuntimeError):
    """Erreur pendant la génération du rapport PDF."""


# ============================================================
# COULEURS
# ============================================================

DARK_BLUE = HexColor("#1F365F")
DARK_BLUE_2 = HexColor("#294D82")
BLUE = HexColor("#2E64A5")
LIGHT_BLUE = HexColor("#EEF4FB")

TEXT = HexColor("#26384F")
MUTED = HexColor("#6F7D8E")

CARD_BACKGROUND = HexColor("#F8F9FC")
CARD_BORDER = HexColor("#DDE3EB")

GREEN = HexColor("#328A61")
GREEN_BACKGROUND = HexColor("#EDF8F1")
GREEN_BORDER = HexColor("#C9E7D5")

RED = HexColor("#B74D40")
RED_BACKGROUND = HexColor("#FFF1ED")
RED_BORDER = HexColor("#F0CEC7")

YELLOW = HexColor("#C29A16")
YELLOW_BACKGROUND = HexColor("#FFF8DC")

GREY_LINE = HexColor("#E2E7EE")

SOFT_BLUE = HexColor("#EAF2FC")
SOFT_BLUE_BORDER = HexColor("#CAD9EC")


# ============================================================
# LABELS
# ============================================================

SERVICE_LABELS = {
    "website_creation": (
        "Création d'un site internet"
    ),
    "website_redesign": (
        "Refonte du site internet"
    ),
    "seo_local": (
        "Amélioration de la visibilité locale"
    ),
    "google_business": (
        "Optimisation de la présence sur Google"
    ),
    "social_media": (
        "Développement des réseaux sociaux"
    ),
    "conversion_optimization": (
        "Optimisation des réservations "
        "et prises de contact"
    ),
    "reputation_management": (
        "Amélioration de la réputation en ligne"
    ),
    "no_priority": (
        "Aucune priorité commerciale immédiate"
    ),
}


PRIORITY_LABELS = {
    "low": "Faible",
    "medium": "Moyenne",
    "high": "Élevée",
}


# ============================================================
# UTILITAIRES
# ============================================================

def safe(
    value: object | None,
    default: str = "Non renseigné",
) -> str:
    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


def html(
    value: object | None,
    default: str = "Non renseigné",
) -> str:
    return escape(
        safe(
            value=value,
            default=default,
        )
    ).replace(
        "\n",
        "<br/>",
    )


def business_text(
    value: object | None,
) -> str:
    """
    Transforme le jargon technique en langage simple
    avant affichage dans le rapport destiné au client.

    Les données techniques originales restent intactes
    dans la base de données.
    """
    text = safe(value)

    replacements = [
        (
            r"\bH1\s*/\s*H2\b",
            "titres et organisation des pages",
        ),
        (
            r"\bbalises?\s+H1\b",
            "titre principal de la page",
        ),
        (
            r"\bbalises?\s+H2\b",
            "titres des différentes sections",
        ),
        (
            r"\bH1\b",
            "titre principal",
        ),
        (
            r"\bH2\b",
            "titres de sections",
        ),
        (
            r"\bmeta description\b",
            (
                "description affichée dans "
                "les résultats de recherche"
            ),
        ),
        (
            r"\bméta description\b",
            (
                "description affichée dans "
                "les résultats de recherche"
            ),
        ),
        (
            r"\battribut\s+ALT\b",
            "description des images",
        ),
        (
            r"\battribut\s+alt\b",
            "description des images",
        ),
        (
            r"\balt text\b",
            "description des images",
        ),
        (
            r"\btexte alternatif\b",
            "description des images",
        ),
        (
            r"\bSEO local\b",
            "visibilité dans les recherches locales",
        ),
        (
            r"\bSEO\b",
            "visibilité dans les moteurs de recherche",
        ),
        (
            r"\bréférencement naturel\b",
            "visibilité dans les recherches",
        ),
        (
            r"\bréférencement local\b",
            "visibilité dans les recherches locales",
        ),
        (
            r"\bCTR\b",
            (
                "nombre de personnes qui choisissent "
                "de visiter le site"
            ),
        ),
        (
            r"\bHTTPS\b",
            "connexion sécurisée",
        ),
        (
            r"\bHTTP\b",
            "fonctionnement du site",
        ),
        (
            r"\bHTML\b",
            "structure du site",
        ),
        (
            r"\bCSS\b",
            "présentation du site",
        ),
        (
            r"\bindexation\b",
            "présence dans les résultats de recherche",
        ),
        (
            r"\bmoteurs de recherche locaux\b",
            "recherches locales",
        ),
        (
            r"\bGoogle My Business\b",
            "fiche établissement sur Google",
        ),
        (
            r"\bGoogle Business Profile\b",
            "fiche établissement sur Google",
        ),
        (
            r"\btemps de réponse\b",
            "rapidité du site",
        ),
        (
            r"\bbalises?\b",
            "éléments de présentation",
        ),
    ]

    for pattern, replacement in replacements:
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE,
        )

    # Quelques reformulations fréquentes
    text = re.sub(
        (
            r"images sans description des images"
        ),
        (
            "images qui pourraient être "
            "mieux décrites"
        ),
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        (
            r"absence de description affichée dans "
            r"les résultats de recherche"
        ),
        (
            "présentation de l'entreprise "
            "à améliorer dans les résultats "
            "de recherche"
        ),
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        (
            r"manque de description des images"
        ),
        (
            "certaines images pourraient être "
            "mieux décrites"
        ),
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s{2,}",
        " ",
        text,
    )

    return text.strip()


def business_html(
    value: object | None,
) -> str:
    return escape(
        business_text(value)
    ).replace(
        "\n",
        "<br/>",
    )


def site_label(
    website: str | None,
) -> str:
    if not website:
        return "Aucun site connu"

    return (
        website
        .replace("https://", "")
        .replace("http://", "")
        .rstrip("/")
    )


def priority_color(
    priority: str,
):
    colors = {
        "low": GREEN,
        "medium": YELLOW,
        "high": RED,
    }

    return colors.get(
        priority,
        BLUE,
    )


def priority_background(
    priority: str,
):
    colors = {
        "low": GREEN_BACKGROUND,
        "medium": YELLOW_BACKGROUND,
        "high": RED_BACKGROUND,
    }

    return colors.get(
        priority,
        CARD_BACKGROUND,
    )


def service_label(
    service: str,
) -> str:
    return SERVICE_LABELS.get(
        service,
        service.replace(
            "_",
            " ",
        ).title(),
    )


# ============================================================
# STYLES
# ============================================================

def build_styles() -> dict[str, ParagraphStyle]:
    defaults = getSampleStyleSheet()

    return {
        "brand": ParagraphStyle(
            name="Brand",
            parent=defaults["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=HexColor("#D3DEEE"),
            spaceAfter=7 * mm,
        ),

        "main_title": ParagraphStyle(
            name="MainTitle",
            parent=defaults["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=25,
            textColor=white,
            alignment=TA_LEFT,
            spaceAfter=2 * mm,
        ),

        "subtitle": ParagraphStyle(
            name="Subtitle",
            parent=defaults["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=HexColor("#E1E8F4"),
            spaceAfter=6 * mm,
        ),

        "metadata_label": ParagraphStyle(
            name="MetadataLabel",
            parent=defaults["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.4,
            leading=8,
            textColor=HexColor("#9CAFCB"),
            spaceAfter=1.3 * mm,
        ),

        "metadata_value": ParagraphStyle(
            name="MetadataValue",
            parent=defaults["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=10.5,
            textColor=white,
        ),

        "section_title": ParagraphStyle(
            name="SectionTitle",
            parent=defaults["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=TEXT,
            spaceBefore=4.5 * mm,
            spaceAfter=2 * mm,
        ),

        "page2_title": ParagraphStyle(
            name="Page2Title",
            parent=defaults["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            textColor=TEXT,
            spaceAfter=2 * mm,
        ),

        "body": ParagraphStyle(
            name="BodyCustom",
            parent=defaults["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=14,
            textColor=TEXT,
            spaceAfter=2 * mm,
        ),

        "body_center": ParagraphStyle(
            name="BodyCenter",
            parent=defaults["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=14,
            alignment=TA_CENTER,
            textColor=TEXT,
        ),

        "body_small": ParagraphStyle(
            name="BodySmall",
            parent=defaults["BodyText"],
            fontName="Helvetica",
            fontSize=8.4,
            leading=12.5,
            textColor=TEXT,
        ),

        "body_small_bold": ParagraphStyle(
            name="BodySmallBold",
            parent=defaults["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.4,
            leading=12.5,
            textColor=TEXT,
        ),

        "card_value": ParagraphStyle(
            name="CardValue",
            parent=defaults["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=21,
            alignment=TA_CENTER,
            textColor=BLUE,
            spaceAfter=1.2 * mm,
        ),

        "card_label": ParagraphStyle(
            name="CardLabel",
            parent=defaults["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=8.5,
            alignment=TA_CENTER,
            textColor=MUTED,
        ),

        "green_title": ParagraphStyle(
            name="GreenTitle",
            parent=defaults["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=GREEN,
            spaceAfter=2.5 * mm,
        ),

        "red_title": ParagraphStyle(
            name="RedTitle",
            parent=defaults["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=RED,
            spaceAfter=2.5 * mm,
        ),

        "opportunity": ParagraphStyle(
            name="Opportunity",
            parent=defaults["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=TEXT,
        ),

        "commercial_title": ParagraphStyle(
            name="CommercialTitle",
            parent=defaults["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=DARK_BLUE,
            spaceAfter=2 * mm,
        ),

        "commercial_value": ParagraphStyle(
            name="CommercialValue",
            parent=defaults["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13.5,
            textColor=TEXT,
        ),

        "footer": ParagraphStyle(
            name="Footer",
            parent=defaults["BodyText"],
            fontName="Helvetica",
            fontSize=6.3,
            leading=8,
            alignment=TA_CENTER,
            textColor=HexColor("#9AA5B4"),
        ),
    }


# ============================================================
# COMPOSANTS
# ============================================================

def section_heading(
    title: str,
    styles: dict[str, ParagraphStyle],
) -> list:
    return [
        Paragraph(
            escape(title),
            styles["section_title"],
        ),

        Table(
            [[""]],
            colWidths=[174 * mm],
            rowHeights=[0.55 * mm],
            style=TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        BLUE,
                    ),
                ]
            ),
        ),

        Spacer(
            1,
            2.4 * mm,
        ),
    ]


def metadata_cell(
    label: str,
    value: str,
    styles: dict[str, ParagraphStyle],
) -> list:
    return [
        Paragraph(
            escape(label.upper()),
            styles["metadata_label"],
        ),

        Paragraph(
            escape(value),
            styles["metadata_value"],
        ),
    ]


def score_card(
    value: str,
    label: str,
    styles: dict[str, ParagraphStyle],
    value_color=BLUE,
    background=CARD_BACKGROUND,
) -> Table:
    value_style = ParagraphStyle(
        name=f"Value-{label}-{value}",
        parent=styles["card_value"],
        textColor=value_color,
    )

    table = Table(
        [
            [
                Paragraph(
                    escape(value),
                    value_style,
                )
            ],
            [
                Paragraph(
                    escape(label.upper()),
                    styles["card_label"],
                )
            ],
        ],
        colWidths=[40.5 * mm],
        rowHeights=[
            13.5 * mm,
            8 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    background,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    CARD_BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return table


def bullet_paragraphs(
    items: list[str],
    marker: str,
    styles: dict[str, ParagraphStyle],
) -> list:
    result = []

    for item in items:
        result.append(
            Paragraph(
                (
                    f"<b>{escape(marker)}</b>"
                    "&nbsp;&nbsp;"
                    f"{business_html(item)}"
                ),
                styles["body_small"],
            )
        )

        result.append(
            Spacer(
                1,
                1.4 * mm,
            )
        )

    return result


def footer(
    canvas: Canvas,
    document: SimpleDocTemplate,
) -> None:
    canvas.saveState()

    width, _ = A4

    canvas.setStrokeColor(
        GREY_LINE
    )

    canvas.setLineWidth(
        0.5
    )

    canvas.line(
        18 * mm,
        13 * mm,
        width - 18 * mm,
        13 * mm,
    )

    canvas.setFillColor(
        HexColor("#9AA5B4")
    )

    canvas.setFont(
        "Helvetica",
        6.3,
    )

    canvas.drawCentredString(
        width / 2,
        8.5 * mm,
        (
            "Rapport généré automatiquement par AI Agency — "
            "Les recommandations doivent être vérifiées "
            "avant toute utilisation commerciale."
        ),
    )

    canvas.restoreState()


# ============================================================
# PAGE 1
# ============================================================

def build_page_one(
    story: list,
    company: Company,
    audit: Audit,
    score: Score,
    opportunity: AIOpportunityResult,
    styles: dict[str, ParagraphStyle],
) -> None:
    header_content = [
        Paragraph(
            (
                "AI AGENCY   •   "
                "RAPPORT COMMERCIAL INTELLIGENT"
            ),
            styles["brand"],
        ),

        Paragraph(
            html(company.name),
            styles["main_title"],
        ),

        Paragraph(
            (
                "Analyse de présence en ligne "
                "&amp; recommandations stratégiques"
            ),
            styles["subtitle"],
        ),
    ]

    metadata = Table(
        [
            [
                metadata_cell(
                    "Secteur",
                    safe(company.sector),
                    styles,
                ),

                metadata_cell(
                    "Ville",
                    safe(company.city),
                    styles,
                ),

                metadata_cell(
                    "Site internet",
                    site_label(company.website),
                    styles,
                ),

                metadata_cell(
                    "Téléphone",
                    safe(company.phone),
                    styles,
                ),
            ]
        ],
        colWidths=[
            41 * mm,
            42 * mm,
            49 * mm,
            42 * mm,
        ],
    )

    metadata.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    header_content.append(
        metadata
    )

    header = Table(
        [
            [
                header_content
            ]
        ],
        colWidths=[
            190 * mm
        ],
    )

    header.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    DARK_BLUE,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    13 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    13 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8.5 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8.5 * mm,
                ),
            ]
        )
    )

    story.append(header)

    story.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    priority = PRIORITY_LABELS.get(
        score.priority,
        score.priority,
    )

    scores = Table(
        [
            [
                score_card(
                    f"{audit.technical_score}/100",
                    "Score technique",
                    styles,
                ),

                score_card(
                    f"{score.global_score}/100",
                    "Score commercial",
                    styles,
                ),

                score_card(
                    priority,
                    "Priorité d'action",
                    styles,
                    value_color=priority_color(
                        score.priority
                    ),
                    background=priority_background(
                        score.priority
                    ),
                ),

                score_card(
                    (
                        f"{round(opportunity.confidence * 100)}%"
                    ),
                    "Indice de confiance",
                    styles,
                ),
            ]
        ],
        colWidths=[
            43.5 * mm,
            43.5 * mm,
            43.5 * mm,
            43.5 * mm,
        ],
    )

    scores.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.5 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    story.append(scores)

    story.extend(
        section_heading(
            "Synthèse et recommandation",
            styles,
        )
    )

    story.append(
        Paragraph(
            business_html(
                score.summary
            ),
            styles["body"],
        )
    )

    story.append(
        Paragraph(
            (
                "<b>Service recommandé :</b> "
                f"{escape(service_label(opportunity.service))}."
            ),
            styles["body"],
        )
    )

    story.extend(
        section_heading(
            "Problème métier identifié",
            styles,
        )
    )

    story.append(
        Paragraph(
            business_html(
                opportunity.business_problem
            ),
            styles["body"],
        )
    )

    story.extend(
        section_heading(
            "Points forts et axes d'amélioration",
            styles,
        )
    )

    strengths = (
        score.strengths
        or [
            "Aucun point fort spécifique identifié."
        ]
    )

    weaknesses = (
        score.weaknesses
        or [
            (
                "Aucun axe d'amélioration "
                "prioritaire identifié."
            )
        ]
    )

    strengths_content = [
        Paragraph(
            "Points forts",
            styles["green_title"],
        ),
        *bullet_paragraphs(
            strengths,
            "✓",
            styles,
        ),
    ]

    weaknesses_content = [
        Paragraph(
            "Axes d'amélioration",
            styles["red_title"],
        ),
        *bullet_paragraphs(
            weaknesses,
            "!",
            styles,
        ),
    ]

    comparison = Table(
        [
            [
                strengths_content,
                weaknesses_content,
            ]
        ],
        colWidths=[
            85 * mm,
            85 * mm,
        ],
    )

    comparison.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    GREEN_BACKGROUND,
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    RED_BACKGROUND,
                ),
                (
                    "BOX",
                    (0, 0),
                    (0, 0),
                    0.8,
                    GREEN_BORDER,
                ),
                (
                    "BOX",
                    (1, 0),
                    (1, 0),
                    0.8,
                    RED_BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(
        comparison
    )

    story.extend(
        section_heading(
            "Opportunités identifiées",
            styles,
        )
    )

    opportunities = (
        score.opportunities
        or [
            (
                "Aucune opportunité complémentaire "
                "clairement identifiée."
            )
        ]
    )

    for item in opportunities[:4]:
        opportunity_box = Table(
            [
                [
                    Paragraph(
                        business_html(item),
                        styles["opportunity"],
                    )
                ]
            ],
            colWidths=[
                170 * mm
            ],
        )

        opportunity_box.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        LIGHT_BLUE,
                    ),
                    (
                        "LINEBEFORE",
                        (0, 0),
                        (0, -1),
                        2.5,
                        BLUE,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(
            opportunity_box
        )

        story.append(
            Spacer(
                1,
                1.5 * mm,
            )
        )

    story.extend(
        section_heading(
            "Plan d'action recommandé",
            styles,
        )
    )

    action_box = Table(
        [
            [
                Paragraph(
                    business_html(
                        opportunity.recommended_action
                    ),
                    styles["body"],
                )
            ]
        ],
        colWidths=[
            170 * mm
        ],
    )

    action_box.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    CARD_BACKGROUND,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    CARD_BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(
        action_box
    )


# ============================================================
# PAGE 2 — PROPOSITION COMMERCIALE SANS EMAIL
# ============================================================

def build_page_two(
    story: list,
    company: Company,
    audit: Audit,
    score: Score,
    opportunity: AIOpportunityResult,
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(
        Paragraph(
            "Proposition commerciale",
            styles["page2_title"],
        )
    )

    story.append(
        Table(
            [[""]],
            colWidths=[
                174 * mm
            ],
            rowHeights=[
                0.7 * mm
            ],
            style=TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        BLUE,
                    ),
                ]
            ),
        )
    )

    story.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    story.append(
        Paragraph(
            (
                "À partir des éléments observés, "
                "AI Agency a identifié une opportunité "
                "permettant de renforcer la présence "
                f"commerciale de <b>{html(company.name)}</b>."
            ),
            styles["body"],
        )
    )

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    story.extend(
        section_heading(
            "Service prioritaire",
            styles,
        )
    )

    service_box = Table(
        [
            [
                Paragraph(
                    (
                        "<b>"
                        f"{escape(service_label(opportunity.service))}"
                        "</b><br/><br/>"
                        f"{business_html(opportunity.reason)}"
                    ),
                    styles["body"],
                )
            ]
        ],
        colWidths=[
            170 * mm
        ],
    )

    service_box.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    SOFT_BLUE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.9,
                    SOFT_BLUE_BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    story.append(
        service_box
    )

    story.extend(
        section_heading(
            "Pourquoi cette opportunité est intéressante",
            styles,
        )
    )

    story.append(
        Paragraph(
            business_html(
                opportunity.sales_angle
            ),
            styles["body"],
        )
    )

    story.extend(
        section_heading(
            "Actions proposées",
            styles,
        )
    )

    actions = []

    if opportunity.recommended_action:
        actions.append(
            opportunity.recommended_action
        )

    for item in score.opportunities[:3]:
        if item not in actions:
            actions.append(
                item
            )

    for index, item in enumerate(
        actions[:4],
        start=1,
    ):
        number_style = ParagraphStyle(
            name=f"ActionNumber-{index}",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=white,
            alignment=TA_CENTER,
        )

        row = Table(
            [
                [
                    Paragraph(
                        str(index),
                        number_style,
                    ),

                    Paragraph(
                        business_html(item),
                        styles["commercial_value"],
                    ),
                ]
            ],
            colWidths=[
                12 * mm,
                156 * mm,
            ],
        )

        row.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, 0),
                        BLUE,
                    ),
                    (
                        "BACKGROUND",
                        (1, 0),
                        (1, 0),
                        CARD_BACKGROUND,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        CARD_BORDER,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        story.append(
            row
        )

        story.append(
            Spacer(
                1,
                2 * mm,
            )
        )

    story.extend(
        section_heading(
            "Impact commercial attendu",
            styles,
        )
    )

    if opportunity.service == "conversion_optimization":
        impact_items = [
            (
                "Faciliter les réservations "
                "et prises de contact."
            ),
            (
                "Réduire les obstacles entre "
                "la visite du site et l'action du client."
            ),
            (
                "Améliorer l'efficacité commerciale "
                "du site existant."
            ),
        ]

    elif opportunity.service == "seo_local":
        impact_items = [
            (
                "Améliorer la visibilité auprès "
                "des recherches locales."
            ),
            (
                "Attirer davantage de prospects "
                "situés dans la zone d'activité."
            ),
            (
                "Renforcer la présence numérique "
                "de l'établissement."
            ),
        ]

    elif opportunity.service == "google_business":
        impact_items = [
            (
                "Améliorer la visibilité de l'entreprise "
                "dans Google et Maps."
            ),
            (
                "Présenter des informations fiables "
                "aux clients potentiels."
            ),
            (
                "Faciliter les appels, itinéraires "
                "et prises de contact."
            ),
        ]

    elif opportunity.service == "website_redesign":
        impact_items = [
            (
                "Renforcer la première impression "
                "donnée aux visiteurs."
            ),
            (
                "Améliorer la clarté et la navigation "
                "sur le site."
            ),
            (
                "Faciliter la transformation "
                "des visiteurs en prospects."
            ),
        ]

    elif opportunity.service == "website_creation":
        impact_items = [
            (
                "Centraliser les informations "
                "essentielles de l'entreprise."
            ),
            (
                "Renforcer la confiance "
                "des futurs clients."
            ),
            (
                "Faciliter la prise de contact "
                "et la découverte des services."
            ),
        ]

    elif opportunity.service == "social_media":
        impact_items = [
            (
                "Renforcer la présence de la marque "
                "auprès des clients locaux."
            ),
            (
                "Valoriser les produits, services "
                "ou réalisations."
            ),
            (
                "Maintenir un lien régulier "
                "avec la clientèle."
            ),
        ]

    elif opportunity.service == "reputation_management":
        impact_items = [
            (
                "Renforcer la confiance "
                "des futurs clients."
            ),
            (
                "Mettre davantage en valeur "
                "la satisfaction existante."
            ),
            (
                "Améliorer l'image de "
                "l'entreprise en ligne."
            ),
        ]

    else:
        impact_items = [
            "Renforcer la présence en ligne.",
            (
                "Améliorer la compréhension "
                "de l'offre."
            ),
            (
                "Faciliter la prise de contact "
                "avec l'entreprise."
            ),
        ]

    impact_content = []

    for item in impact_items:
        impact_content.append(
            Paragraph(
                (
                    "<font color='#328A61'>✓</font>"
                    "&nbsp;&nbsp;"
                    f"{business_html(item)}"
                ),
                styles["body"],
            )
        )

        impact_content.append(
            Spacer(
                1,
                2 * mm,
            )
        )

    impact_box = Table(
        [
            [
                impact_content
            ]
        ],
        colWidths=[
            170 * mm
        ],
    )

    impact_box.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    GREEN_BACKGROUND,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    GREEN_BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(
        impact_box
    )

    story.extend(
        section_heading(
            "Niveau de priorité",
            styles,
        )
    )

    priority = PRIORITY_LABELS.get(
        score.priority,
        score.priority,
    )

    priority_table = Table(
        [
            [
                Paragraph(
                    "<b>Priorité</b>",
                    styles["body_center"],
                ),

                Paragraph(
                    "<b>Confiance de l'analyse</b>",
                    styles["body_center"],
                ),

                Paragraph(
                    "<b>Score commercial</b>",
                    styles["body_center"],
                ),
            ],

            [
                Paragraph(
                    f"<b>{escape(priority)}</b>",
                    styles["body_center"],
                ),

                Paragraph(
                    (
                        "<b>"
                        f"{round(opportunity.confidence * 100)}%"
                        "</b>"
                    ),
                    styles["body_center"],
                ),

                Paragraph(
                    (
                        "<b>"
                        f"{score.global_score}/100"
                        "</b>"
                    ),
                    styles["body_center"],
                ),
            ],
        ],
        colWidths=[
            56 * mm,
            56 * mm,
            56 * mm,
        ],
    )

    priority_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    DARK_BLUE,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    white,
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, 1),
                    CARD_BACKGROUND,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    CARD_BORDER,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    CARD_BORDER,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(
        priority_table
    )

    story.extend(
        section_heading(
            "Conclusion",
            styles,
        )
    )

    conclusion = (
        f"L'analyse de {safe(company.name)} "
        "met en évidence une opportunité prioritaire "
        "autour de "
        f"{service_label(opportunity.service).lower()}. "
        f"{business_text(opportunity.business_problem)} "
        "La mise en œuvre du plan recommandé permettra "
        "de travailler sur les points identifiés tout "
        "en s'appuyant sur les qualités déjà présentes."
    )

    conclusion_box = Table(
        [
            [
                Paragraph(
                    html(conclusion),
                    styles["body"],
                )
            ]
        ],
        colWidths=[
            170 * mm
        ],
    )

    conclusion_box.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_BLUE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    SOFT_BLUE_BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    story.append(
        conclusion_box
    )

    story.append(
        Spacer(
            1,
            8 * mm,
        )
    )

    signature = Table(
        [
            [
                Paragraph(
                    (
                        "<b>AI AGENCY</b><br/>"
                        "Rapport commercial intelligent<br/>"
                        "Version 1.0"
                    ),
                    styles["body_small"],
                ),
            ]
        ],
        colWidths=[
            170 * mm
        ],
    )

    signature.setStyle(
        TableStyle(
            [
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "LINEABOVE",
                    (0, 0),
                    (-1, 0),
                    0.6,
                    GREY_LINE,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(
        signature
    )


# ============================================================
# GÉNÉRATION PRINCIPALE
# ============================================================

def generate_company_report(
    company: Company,
    audit: Audit,
    score: Score,
    opportunity: AIOpportunityResult,
) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=12 * mm,
        bottomMargin=18 * mm,
        title=(
            f"Rapport AI Agency - "
            f"{safe(company.name)}"
        ),
        author="AI Agency",
        subject=(
            "Analyse de présence en ligne "
            "et recommandations stratégiques"
        ),
    )

    styles = build_styles()

    story = []

    build_page_one(
        story=story,
        company=company,
        audit=audit,
        score=score,
        opportunity=opportunity,
        styles=styles,
    )

    story.append(
        PageBreak()
    )

    build_page_two(
        story=story,
        company=company,
        audit=audit,
        score=score,
        opportunity=opportunity,
        styles=styles,
    )

    try:
        document.build(
            story,
            onFirstPage=footer,
            onLaterPages=footer,
        )

    except Exception as error:
        raise PDFReportError(
            "Impossible de générer "
            "le rapport PDF."
        ) from error

    pdf_data = buffer.getvalue()

    buffer.close()

    if not pdf_data:
        raise PDFReportError(
            "Le rapport PDF généré est vide."
        )

    return pdf_data