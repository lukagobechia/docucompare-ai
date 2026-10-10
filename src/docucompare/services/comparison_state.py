from typing import TypedDict

from docucompare.schemas.comparison import (
    RetrievedDocument,
    ClauseDifference,
)


class ComparisonState(TypedDict):
    document_a_id: str
    document_b_id: str
    query: str
    top_k: int

    document_a_results: list[RetrievedDocument]
    document_b_results: list[RetrievedDocument]

    document_a_text: str
    document_b_text: str

    summary: str
    differences: list[ClauseDifference]

    verification_passed: bool
    verification_errors: list[str]
    verification_attempts: int
