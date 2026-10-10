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

class DocumentSearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Question or text to search for in indexed documents",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of relevant chunks to return",
    )
    document_id: str | None = Field(
        default=None,
        description="Document ID to search for in indexed documents",
    )

class SearchResult(BaseModel):
    document_id: str
    text: str
    file_name: str
    page_number: int
    score: float | None = None

class DocumentSearchResponse(BaseModel):
    query: str
    results: list[SearchResult]

class DocumentIndexResponse(BaseModel):
    document_id: str
    file_name: str
    page_count: int
    indexed_chunks: int
    collection_name: str