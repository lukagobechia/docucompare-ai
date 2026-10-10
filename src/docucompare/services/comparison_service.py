from docucompare.schemas.comparison import (
    ComparisonRequest,
    ComparisonResponse,
    RetrievedDocument,
)
from docucompare.api.dependencies import get_indexer


class ComparisonService:
    def __init__(self) -> None:
        self.indexer = get_indexer()

    def compare(
        self, request: ComparisonRequest
    ) -> ComparisonResponse:
        results_a = self.indexer.search(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_a_id,
        )

        results_b = self.indexer.search(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_b_id,
        )

        documents_a = [
            RetrievedDocument(
                document_id=request.document_a_id,
                file_name=node.metadata.get("file_name", "unknown"),
                text=node.text,
                page_number=node.metadata.get("page_number", 1),
                score=float(node.score or 0.0),
            )
            for node in results_a
        ]

        documents_b = [
            RetrievedDocument(
                document_id=request.document_b_id,
                file_name=node.metadata.get("file_name", "unknown"),
                text=node.text,
                page_number=node.metadata.get("page_number", 1),
                score=float(node.score or 0.0),
            )
            for node in results_b
        ]

        return ComparisonResponse(
            document_a_id=request.document_a_id,
            document_b_id=request.document_b_id,
            document_a_results=documents_a,
            document_b_results=documents_b,
        )
