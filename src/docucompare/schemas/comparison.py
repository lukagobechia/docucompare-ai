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


class ComparisonResponse(BaseModel):
    document_a_id: str
    document_b_id: str
    document_a_results: list[RetrievedDocument]
    document_b_results: list[RetrievedDocument]