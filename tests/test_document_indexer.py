
from unittest.mock import MagicMock, patch

import pytest

from docucompare.services.document_indexer import DocumentIndexer


@pytest.fixture
def indexer():
    with (
        patch(
            "docucompare.services.document_indexer.QdrantClient"
        ) as mock_client,
        patch(
            "docucompare.services.document_indexer.FastEmbedEmbedding"
        ),
        patch(
            "docucompare.services.document_indexer.QdrantVectorStore"
        ),
        patch(
            "docucompare.services.document_indexer.StorageContext"
        ),
        patch(
            "docucompare.services.document_indexer.SentenceSplitter"
        ),
    ):
        mock_client.return_value.collection_exists.return_value = True

        instance = DocumentIndexer()
        instance.client = mock_client.return_value
        instance.splitter = MagicMock()
        yield instance


def test_index_pages_rejects_empty_pages(indexer):
    with pytest.raises(ValueError, match="No text available to index"):
        indexer.index_pages(
            document_id="test-document",
            file_name="empty.txt",
            pages=[],
        )


def test_index_pages_rejects_pages_with_only_whitespace(indexer):
    from docucompare.schemas.document import ExtractedPage

    page = ExtractedPage(page_number=1, text="   ")

    with pytest.raises(ValueError, match="No text available to index"):
        indexer.index_pages(
            document_id="test-document",
            file_name="empty.txt",
            pages=[page],
        )


def test_index_pages_creates_chunks_and_indexes_them(indexer):
    from docucompare.schemas.document import ExtractedPage

    page = ExtractedPage(
        page_number=1,
        text="Payment is due within 30 days.",
    )

    fake_node = MagicMock()
    fake_node.metadata = {}

    indexer.splitter.get_nodes_from_documents.return_value = [fake_node]

    with patch(
        "docucompare.services.document_indexer.VectorStoreIndex"
    ) as mock_vector_index:
        count = indexer.index_pages(
            document_id="test-document",
            file_name="contract.txt",
            pages=[page],
        )

    assert count == 1
    assert fake_node.metadata["source_document_id"] == "test-document"
    assert fake_node.metadata["file_name"] == "contract.txt"

    mock_vector_index.assert_called_once()




def test_search_returns_retrieved_results(indexer):
    fake_result = MagicMock()
    fake_result.text = "Payment is due within 30 days."
    fake_result.score = 0.85
    fake_result.metadata = {
        "source_document_id": "contract-a",
        "file_name": "contract_a.txt",
        "page_number": 1,
    }

    fake_retriever = MagicMock()
    fake_retriever.retrieve.return_value = [fake_result]

    fake_index = MagicMock()
    fake_index.as_retriever.return_value = fake_retriever

    with patch(
        "docucompare.services.document_indexer.VectorStoreIndex"
    ) as mock_vector_index:
        mock_vector_index.from_vector_store.return_value = fake_index

        results = indexer.search(
            query="payment terms",
            top_k=3,
            document_id="contract-a",
        )

    assert len(results) == 1
    assert results[0].text == "Payment is due within 30 days."

    call_kwargs = fake_index.as_retriever.call_args.kwargs

    assert call_kwargs["similarity_top_k"] == 3

    filters = call_kwargs["filters"]
    assert filters is not None
    assert filters.filters[0].value == "contract-a"


def test_search_without_document_id_uses_no_filter(indexer):
    fake_retriever = MagicMock()
    fake_retriever.retrieve.return_value = []

    fake_index = MagicMock()
    fake_index.as_retriever.return_value = fake_retriever

    with patch(
        "docucompare.services.document_indexer.VectorStoreIndex"
    ) as mock_vector_index:
        mock_vector_index.from_vector_store.return_value = fake_index

        results = indexer.search(
            query="payment terms",
            top_k=5,
        )

    assert results == []
    fake_index.as_retriever.assert_called_once_with(
        similarity_top_k=5,
        filters=None,
    )
