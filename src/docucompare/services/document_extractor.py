from io import BytesIO
from pathlib import Path

import pymupdf

from docucompare.schemas.document import (
    DocumentExtractionResponse,
    ExtractedPage,
)


MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


class DocumentExtractionError(Exception):
    pass


def extract_document(
    file_name: str,
    content: bytes,
) -> DocumentExtractionResponse:
    extension = Path(file_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise DocumentExtractionError(
            "Unsupported file type. Upload a PDF or TXT file."
        )

    if not content:
        raise DocumentExtractionError("The uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise DocumentExtractionError(
            "File size exceeds the 10 MB limit."
        )

    if extension == ".pdf":
        return _extract_pdf(file_name, content)

    return _extract_txt(file_name, content)


def _extract_pdf(
    file_name: str,
    content: bytes,
) -> DocumentExtractionResponse:
    try:
        with pymupdf.open(
            stream=BytesIO(content),
            filetype="pdf",
        ) as pdf:
            pages = [
                ExtractedPage(
                    page_number=index + 1,
                    text=page.get_text("text").strip(),
                )
                for index, page in enumerate(pdf)
            ]
    except Exception as exc:
        raise DocumentExtractionError(
            "Unable to read the PDF. Check that it is a valid PDF."
        ) from exc

    if not pages:
        raise DocumentExtractionError(
            "The PDF contains no pages."
        )

    full_text = "\n".join(page.text for page in pages)

    if not full_text.strip():
        raise DocumentExtractionError(
            "No text was found. This may be a scanned PDF; "
            "OCR support is not implemented yet."
        )

    return DocumentExtractionResponse(
        file_name=file_name,
        file_type="pdf",
        page_count=len(pages),
        character_count=len(full_text),
        pages=pages,
        text_preview=full_text[:500],
    )


def _extract_txt(
    file_name: str,
    content: bytes,
) -> DocumentExtractionResponse:
    try:
        text = content.decode("utf-8-sig").strip()
    except UnicodeDecodeError as exc:
        raise DocumentExtractionError(
            "The TXT file must use UTF-8 encoding."
        ) from exc

    if not text:
        raise DocumentExtractionError(
            "The TXT file contains no text."
        )

    pages = [
        ExtractedPage(
            page_number=1,
            text=text,
        )
    ]

    return DocumentExtractionResponse(
        file_name=file_name,
        file_type="txt",
        page_count=1,
        character_count=len(text),
        pages=pages,
        text_preview=text[:500],
    )