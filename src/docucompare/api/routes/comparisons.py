from fastapi import APIRouter, HTTPException

from docucompare.schemas.comparison import (
    ComparisonRequest,
    ComparisonResponse,
)
from docucompare.services.comparison_service import ComparisonService

router = APIRouter(
    prefix="/compare",
    tags=["Comparison"],
)


@router.post("", response_model=ComparisonResponse)
def compare_documents(
    request: ComparisonRequest,
) -> ComparisonResponse:
    try:
        service = ComparisonService()
        return service.compare(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
