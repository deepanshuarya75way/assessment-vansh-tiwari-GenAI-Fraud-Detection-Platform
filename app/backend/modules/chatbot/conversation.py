from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.backend.modules.chatbot.context import ChatContextEngine
from app.backend.modules.chatbot.history import ConversationHistoryManager
from app.backend.modules.chatbot.intent import IntentEngine
from app.backend.modules.chatbot.prompt import ChatPromptEngine
from app.backend.modules.chatbot.response import ChatResponseGenerator
from app.backend.modules.chatbot.suggestions import SuggestionEngine


class ConversationEngine:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.intent_engine = IntentEngine()
        self.context_engine = ChatContextEngine(session)
        self.prompt_engine = ChatPromptEngine()
        self.response_generator = ChatResponseGenerator()
        self.suggestion_engine = SuggestionEngine()
        self.history_manager = ConversationHistoryManager(session)

    def ask(self, session_id: str, current_user, question: str, requested_session_id: str | None = None) -> dict[str, Any]:
        active_session_id = requested_session_id or session_id
        intent = self.intent_engine.detect(question)
        context = self.context_engine.build(active_session_id, current_user, question, intent)
        prompt = self.prompt_engine.build(question, context)
        response = self.response_generator.generate(context, question)

        if context.history and intent == "follow_up":
            previous = context.history[-1]
            if previous.get("visual_response", {}).get("type") == "table":
                response["visual_response"] = previous.get("visual_response", response["visual_response"])
                response["next_suggested_questions"] = self.suggestion_engine.suggest(previous.get("intent", intent), context)

        response["intent"] = intent
        response["context_metadata"] = {
            **context.metadata,
            "session_id": active_session_id,
            "intent": intent,
            "question": question,
        }
        response["prompt"] = prompt
        response["next_suggested_questions"] = response.get("next_suggested_questions") or self.suggestion_engine.suggest(intent, context)
        response["logs"] = [
            {
                "level": "INFO",
                "message": f"Answered chatbot question using active session {active_session_id}.",
                "session_id": active_session_id,
            }
        ]
        response["processing_time_seconds"] = 0.0
        response["session_id"] = active_session_id
        response["user_id"] = current_user.id
        return response

    def history(self, session_id: str, current_user) -> list[dict[str, Any]]:
        return self.history_manager.list_turns(session_id, current_user)

    def suggestions(self, session_id: str, current_user, question: str | None = None) -> list[str]:
        context = self.context_engine.build(session_id, current_user, question or "", self.intent_engine.detect(question or ""))
        intent = context.history[-1]["intent"] if context.history and context.history[-1].get("intent") else self.intent_engine.detect(question or "")
        return self.suggestion_engine.suggest(intent, context)