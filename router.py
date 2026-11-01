import re


SUMMARY_PATTERN = re.compile(
    r"\b(summarize|summarise|summary|give me an overview|"
    r"give me a summary|provide a summary)\b",
    re.IGNORECASE,
)

DOCUMENT_TERMS = (
    "paper",
    "document",
    "article",
    "pdf",
    "research",
    "study",
    "provided",
    "uploaded",
    "according to",
    "in the text",
    "in this",
    "this work",
    "this paper",
)

DOCUMENT_QUESTION_TERMS = (
    "method",
    "methodology",
    "approach",
    "experiment",
    "result",
    "finding",
    "conclusion",
    "objective",
    "dataset",
    "limitation",
    "author",
    "contribution",
    "proposed",
    "describe",
    "explain",
    "discuss",
)


def route_question(question, has_documents=False):
    """Choose an agent without attempting to answer the question."""
    normalized = question.strip().lower()

    if SUMMARY_PATTERN.search(normalized):
        route = "SUMMARY"
    elif has_documents and (
        any(term in normalized for term in DOCUMENT_TERMS)
        or any(term in normalized for term in DOCUMENT_QUESTION_TERMS)
    ):
        route = "RAG"
    else:
        route = "GENERAL"

    return route
