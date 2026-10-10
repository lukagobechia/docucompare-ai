from docucompare.api.dependencies import get_indexer
from docucompare.schemas.comparison import RetrievedDocument
from docucompare.services.comparison_state import ComparisonState

from docucompare.services.openai_comparator import OpenAIComparator

from langgraph.graph import StateGraph, START, END

def retrieve_documents(state: ComparisonState) -> dict:
    indexer = get_indexer()

    results_a = indexer.search(
        query=state["query"],
        top_k=state["top_k"],
        document_id=state["document_a_id"],
    )

    results_b = indexer.search(
        query=state["query"],
        top_k=state["top_k"],
        document_id=state["document_b_id"],
    )

    documents_a = [
        RetrievedDocument(
            document_id=state["document_a_id"],
            file_name=node.metadata.get("file_name", "unknown"),
            text=node.text,
            page_number=node.metadata.get("page_number", 1),
            score=float(node.score or 0.0),
        )
        for node in results_a
    ]

    documents_b = [
        RetrievedDocument(
            document_id=state["document_b_id"],
            file_name=node.metadata.get("file_name", "unknown"),
            text=node.text,
            page_number=node.metadata.get("page_number", 1),
            score=float(node.score or 0.0),
        )
        for node in results_b
    ]

    if not documents_a or not documents_b:
        raise ValueError(
            "Could not retrieve text for both documents. "
            "Check the document IDs and indexed content."
        )

    return {
        "document_a_results": documents_a,
        "document_b_results": documents_b,
        "document_a_text": "\n\n".join(
            document.text for document in documents_a
        ),
        "document_b_text": "\n\n".join(
            document.text for document in documents_b
        ),
    }


def compare_documents(state: ComparisonState) -> dict:
    comparator = OpenAIComparator()

    verification_errors = (
        state["verification_errors"]
        if state["verification_attempts"] > 0
        else None
    )

    result = comparator.compare(
        document_a_id=state["document_a_id"],
        document_b_id=state["document_b_id"],
        document_a_text=state["document_a_text"],
        document_b_text=state["document_b_text"],
        verification_errors=verification_errors,
    )

    return {
        "summary": result.summary,
        "differences": result.differences,
    }

def verify_comparison(state: ComparisonState) -> dict:
    errors = []

    document_a_text = state["document_a_text"].lower()
    document_b_text = state["document_b_text"].lower()

    for difference in state["differences"]:
        value_a = difference.document_a_value.strip().lower()
        value_b = difference.document_b_value.strip().lower()

        if value_a and value_a not in document_a_text:
            errors.append(
                f"Could not verify Document A value "
                f"for clause: {difference.clause}"
            )

        if value_b and value_b not in document_b_text:
            errors.append(
                f"Could not verify Document B value "
                f"for clause: {difference.clause}"
            )

    return {
        "verification_passed": len(errors) == 0,
        "verification_errors": errors,
        "verification_attempts": (
                state.get("verification_attempts", 0) + 1
        ),
    }

def route_after_verification(
    state: ComparisonState,
) -> str:
    if state["verification_passed"]:
        return "passed"

    if state["verification_attempts"] < 2:
        return "retry"

    return "failed"

def build_comparison_graph():
    builder = StateGraph(ComparisonState)

    builder.add_node("retrieve_documents", retrieve_documents)
    builder.add_node("compare_documents", compare_documents)
    builder.add_node("verify_comparison", verify_comparison)

    builder.add_edge(START, "retrieve_documents")
    builder.add_edge("retrieve_documents", "compare_documents")
    builder.add_edge("compare_documents", "verify_comparison")

    builder.add_conditional_edges(
        "verify_comparison",
        route_after_verification,
        {
            "passed": END,
            "retry": "compare_documents",
            "failed": END,
        },
    )

    return builder.compile()


comparison_graph = build_comparison_graph()


comparison_graph = build_comparison_graph()