from fastapi import APIRouter, File, HTTPException, UploadFile

from docucompare.schemas.document import (
    DocumentExtractionResponse,
    DocumentIndexResponse,
)
from docucompare.services.document_extractor import (
    DocumentExtractionError,
    extract_document,
)
from docucompare.api.dependencies import get_indexer

from uuid import uuid4

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

@router.post(
    "/index",
    response_model=DocumentIndexResponse,
)
async def index_uploaded_document(
    file: UploadFile = File(...),
) -> DocumentIndexResponse:
    try:
        content = await file.read()

        extracted = extract_document(
            file_name=file.filename or "unnamed",
            content=content,
        )

        document_id = str(uuid4())

        indexer = get_indexer()
        indexed_chunks = indexer.index_pages(
            document_id=document_id,
            file_name=extracted.file_name,
            pages=extracted.pages,
        )

        return DocumentIndexResponse(
            document_id=document_id,
            file_name=extracted.file_name,
            page_count=extracted.page_count,
            indexed_chunks=indexed_chunks,
            collection_name="docucompare_documents",
        )

    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    finally:
        await file.close()