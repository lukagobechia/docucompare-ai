from docucompare.services.document_indexer import DocumentIndexer

_indexer: DocumentIndexer | None = None


def get_indexer() -> DocumentIndexer:
    global _indexer

    if _indexer is None:
        _indexer = DocumentIndexer()

    return _indexer
