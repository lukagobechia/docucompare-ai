from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from docucompare.schemas.document import ExtractedPage

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "docucompare_documents"

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


class DocumentIndexer:
    def __init__(self) -> None:
        self.client = QdrantClient(url=QDRANT_URL)

        self.embed_model = FastEmbedEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )

        if not self.client.collection_exists(
                collection_name=COLLECTION_NAME
        ):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=COLLECTION_NAME,
        )

        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

        self.splitter = SentenceSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    def index_pages(
        self,
        document_id: str,
        file_name: str,
        pages: list[ExtractedPage],
    ) -> int:
        documents = [
            Document(
                text=page.text,
                metadata={
                    "source_document_id": document_id,
                    "file_name": file_name,
                    "page_number": page.page_number,
                },
            )
            for page in pages
            if page.text.strip()
        ]

        if not documents:
            raise ValueError("No text available to index.")

        nodes = self.splitter.get_nodes_from_documents(documents)

        if not nodes:
            raise ValueError("No text chunks were generated.")

        for node in nodes:
            node.metadata["source_document_id"] = document_id
            node.metadata["file_name"] = file_name

        VectorStoreIndex(
            nodes,
            storage_context=self.storage_context,
            embed_model=self.embed_model,
        )

        return len(nodes)

    def search(
            self,
            query: str,
            top_k: int = 5,
            document_id: str | None = None,
    ):
        index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            embed_model=self.embed_model,
        )

        filters = None

        if document_id is not None:
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="source_document_id",
                        value=document_id,
                        operator=FilterOperator.EQ,
                    )
                ]
            )

        retriever = index.as_retriever(
            similarity_top_k=top_k,
            filters=filters,
        )

        return retriever.retrieve(query)
