from pydantic import BaseModel, Field


class AIWriterResult(BaseModel):
    email_subject: str = Field(
        min_length=5,
        max_length=150,
    )

    email_body: str = Field(
        min_length=50,
        max_length=5000,
    )

    commercial_offer: str = Field(
        min_length=20,
        max_length=3000,
    )

    call_to_action: str = Field(
        min_length=5,
        max_length=500,
    )