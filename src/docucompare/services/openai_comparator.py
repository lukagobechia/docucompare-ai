import os

from dotenv import load_dotenv
from openai import OpenAI

from docucompare.schemas.comparison import AIComparisonResponse


load_dotenv()


class OpenAIComparator:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing. Check your .env file."
            )

        self.client = OpenAI(api_key=api_key)

    def compare(
        self,
        document_a_id: str,
        document_b_id: str,
        document_a_text: str,
        document_b_text: str,
        verification_errors: list[str] | None = None,
    ) -> AIComparisonResponse:
        response = self.client.responses.parse(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a document comparison assistant. "
                        "Compare the two supplied documents carefully. "
                        "Identify meaningful differences in clauses, "
                        "obligations, deadlines, amounts, and conditions. "
                        "Use only the supplied text. Never invent facts. "
                        "If a clause is missing from one document, "
                        "identify that absence explicitly. "
                        "Explain each difference clearly and neutrally. "
                        "Do not treat a difference as a legal conclusion."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"DOCUMENT A (ID: {document_a_id})\n"
                        f"{document_a_text}\n\n"
                        f"DOCUMENT B (ID: {document_b_id})\n"
                        f"{document_b_text}\n\n"
                        "Compare these documents and provide a concise "
                        "summary and a list of meaningful differences.\n\n"
                        f"Verification errors from the previous attempt: "
                        f"{verification_errors or 'None'}\n\n"
                        "If verification errors are provided, correct the "
                        "unsupported values. Use exact wording from the "
                        "supplied document text wherever possible. Do not "
                        "invent replacement values."
                    ),
                },
            ],
            text_format=AIComparisonResponse,
        )

        result = response.output_parsed

        if result is None:
            raise ValueError(
                "OpenAI did not return a structured comparison."
            )

        return result.model_copy(
            update={
                "document_a_id": document_a_id,
                "document_b_id": document_b_id,
            }
        )
