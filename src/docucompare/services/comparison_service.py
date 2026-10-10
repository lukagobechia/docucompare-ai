from docucompare.schemas.comparison import (
    ComparisonRequest,
    ComparisonResponse,
)
from docucompare.services.comparison_graph import comparison_graph


class ComparisonService:
    def compare(
        self, request: ComparisonRequest
    ) -> ComparisonResponse:
        initial_state = {
            "document_a_id": request.document_a_id,
            "document_b_id": request.document_b_id,
            "query": request.query,
            "top_k": request.top_k,
            "document_a_results": [],
            "document_b_results": [],
            "document_a_text": "",
            "document_b_text": "",
            "summary": "",
            "differences": [],
            "verification_passed": False,
            "verification_errors": [],
            "verification_attempts": 0,
        }

        result = comparison_graph.invoke(initial_state)

        return ComparisonResponse(
            document_a_id=request.document_a_id,
            document_b_id=request.document_b_id,
            summary=result["summary"],
            differences=result["differences"],
            document_a_results=result["document_a_results"],
            document_b_results=result["document_b_results"],
            verification_passed=result["verification_passed"],
            verification_errors=result["verification_errors"],
            verification_attempts=result["verification_attempts"],
        )
