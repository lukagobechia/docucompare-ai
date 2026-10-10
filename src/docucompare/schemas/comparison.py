from pydantic import BaseModel


class ComparisonRequest(BaseModel):
    document_a_id: str
    document_b_id: str
    query: str = "contract terms and obligations"
    top_k: int = 5


class RetrievedDocument(BaseModel):
    document_id: str
    file_name: str
    text: str
    page_number: int
    score: float

class ClauseDifference(BaseModel):
    clause: str
    document_a_value: str
    document_b_value: str
    explanation: str

class AIComparisonResponse(BaseModel):
    document_a_id: str
    document_b_id: str
    summary: str
    differences: list[ClauseDifference]


class ComparisonResponse(BaseModel):
    document_a_id: str
    document_b_id: str
    summary: str
    differences: list[ClauseDifference]
    document_a_results: list[RetrievedDocument]
    document_b_results: list[RetrievedDocument]

    verification_passed: bool
    verification_errors: list[str]
    verification_attempts: int