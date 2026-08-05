from typing import Literal

from pydantic import BaseModel, Field


class AIScore(BaseModel):
    global_score: int = Field(
        ge=0,
        le=100,
    )

    priority: Literal[
        "low",
        "medium",
        "high",
    ]

    strengths: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    weaknesses: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    opportunities: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    recommended_offer: str = Field(
        min_length=5,
        max_length=500,
    )

    summary: str = Field(
        min_length=10,
        max_length=2000,
    )