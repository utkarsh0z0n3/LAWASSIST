from typing import Literal, Optional

from pydantic import BaseModel, Field


class BailDraftInput(BaseModel):
    """Structured input for regular-bail style applications (Indian court format)."""

    client_name: str = Field(..., min_length=1, description="Applicant / accused name as on record")
    court: str = Field(..., min_length=1, description="Court line, e.g. Chief Judicial Magistrate, Patiala House")
    offence: str = Field(
        default="",
        description="Short offence label (English or mixed); may be empty if folded into facts",
    )
    facts: str = Field(..., min_length=1, description="Factual narrative supplied by the user")
    language: Literal["en", "hi", "auto"] = "auto"
    in_judicial_custody: bool = True
    date_line: Optional[str] = None
    place_line: Optional[str] = None

    def to_dict(self) -> dict:
        return self.model_dump()
