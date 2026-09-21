from app.backend.core.exceptions import ProcessingError


def ensure_chat_question(question: str) -> None:
    if not question or not question.strip():
        raise ProcessingError("Chat question cannot be empty.")