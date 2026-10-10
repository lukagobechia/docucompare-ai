
from fastapi import APIRouter, HTTPException

from docucompare.api.dependencies import get_indexer
from docucompare.schemas.document import (
    DocumentSearchRequest,
    DocumentSearchResponse,
    SearchResult,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/search",
    response_model=DocumentSearchResponse,
)
async def search_documents(
    request: DocumentSearchRequest,
) -> DocumentSearchResponse:
    try:
        indexer = get_indexer()

        retrieved_nodes = indexer.search(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
        )

        results = [
            SearchResult(
                document_id=node.metadata.get("source_document_id", "unknown"),
                text=node.get_content(),
                file_name=node.metadata.get("file_name", "unknown"),
                page_number=int(node.metadata.get("page_number", 1)),
                score=node.score,
            )
            for node in retrieved_nodes
        ]

        return DocumentSearchResponse(
            query=request.query,
            results=results,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
