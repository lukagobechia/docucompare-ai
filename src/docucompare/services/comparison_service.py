from docucompare.schemas.comparison import (
    ComparisonRequest,
    ComparisonResponse,
    RetrievedDocument,
    AIComparisonResponse,
)
from docucompare.api.dependencies import get_indexer
from docucompare.services.openai_comparator import OpenAIComparator


class ComparisonService:
    def __init__(self) -> None:
        self.indexer = get_indexer()
        self.comparator = OpenAIComparator()

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

        if not documents_a or not documents_b:
            raise ValueError(
                "Could not retrieve text for both documents. "
                "Check the document IDs and indexed content."
            )

        document_a_text = "\n\n".join(
            document.text for document in documents_a
        )
        document_b_text = "\n\n".join(
            document.text for document in documents_b
        )

        ai_result: AIComparisonResponse = self.comparator.compare(
            document_a_id=request.document_a_id,
            document_b_id=request.document_b_id,
            document_a_text=document_a_text,
            document_b_text=document_b_text,
        )

        return ComparisonResponse(
            document_a_id=request.document_a_id,
            document_b_id=request.document_b_id,
            summary=ai_result.summary,
            differences=ai_result.differences,
            document_a_results=documents_a,
            document_b_results=documents_b,
        )

