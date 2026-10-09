from pydantic import BaseModel, Field

class ExtractedPage(BaseModel):
    page_number: int
    text: str

class DocumentExtractionResponse(BaseModel):
    file_name: str
    file_type: str
    page_count: int
    character_count: int
    pages: list[ExtractedPage]
    text_preview: str = Field(
        description="A short preview of the extracted document text"
    )