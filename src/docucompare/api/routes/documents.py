from fastapi import APIRouter, File, HTTPException, UploadFile

from docucompare.schemas.document import (
    DocumentExtractionResponse,
)
from docucompare.services.document_extractor import (
    DocumentExtractionError,
    extract_document,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/extract",
    response_model=DocumentExtractionResponse,
)
async def extract_uploaded_document(
    file: UploadFile = File(...),
) -> DocumentExtractionResponse:
    try:
        content = await file.read()
        return extract_document(
            file_name=file.filename or "unnamed",
            content=content,
        )
    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    finally:
        await file.close()