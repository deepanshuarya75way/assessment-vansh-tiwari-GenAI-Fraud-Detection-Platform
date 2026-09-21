from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.backend.core.enums import ChatAnswerSource
from app.backend.modules.chatbot.conversation import ConversationEngine
from app.backend.db.database_service import DatabaseService
from app.backend.db.enterprise_models import AuditActionType
from app.backend.db.enterprise_models import ChatMessage
from app.backend.modules.chatbot.repository import ChatMessageRepository
from app.backend.modules.chatbot.schema import ChatConversationArtifact, ChatRequest
from app.backend.modules.chatbot.validation import ensure_chat_question
from app.backend.modules.logs.service import LogService
from app.backend.modules.projects.service import ProjectService


class ChatbotService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ChatMessageRepository(session)
        self.conversation_engine = ConversationEngine(session)
        self.db_service = DatabaseService(session)
        self.log_service = LogService(session)

    def ask(self, session_id: str, current_user, payload: ChatRequest) -> ChatConversationArtifact:
        ensure_chat_question(payload.question)
        active_session_id = payload.session_id or session_id
        ProjectService(self.session).get_project(active_session_id, current_user)

        turn = self.conversation_engine.ask(active_session_id, current_user, payload.question, payload.session_id)
        message = ChatMessage(
            project_id=active_session_id,
            user_id=current_user.id,
            question=turn["question"],
            answer=turn["answer"],
            answer_source=ChatAnswerSource.RULE_BASED.value,
            context_payload=turn,
        )
        created = self.repository.add(message)
        self.session.commit()
        
        self.log_service.record(
            "chatbot.message",
            "Dataset-grounded chatbot answered a user question.",
            project_id=active_session_id,
            user_id=current_user.id,
            details={"question": payload.question, "session_id": active_session_id, "answer_source": created.answer_source},
        )
        
        # Use db_service to audit the chat action
        self.db_service._audit_action(
            user_id=current_user.id,
            session_id=active_session_id,
            project_id=active_session_id,
            action=AuditActionType.CREATE,
            resource_type="chat_message",
            resource_id=created.id,
            after_value={"question": payload.question, "intent": turn["intent"]},
        )
        
        turn["id"] = created.id
        turn["chat_message_id"] = created.id
        turn["created_at"] = created.created_at
        turn["updated_at"] = created.updated_at
        turn["session_id"] = active_session_id
        return ChatConversationArtifact(**turn)

    def history(self, session_id: str, current_user) -> list[ChatConversationArtifact]:
        ProjectService(self.session).get_project(session_id, current_user)
        turns = self.conversation_engine.history(session_id, current_user)
        return [ChatConversationArtifact(**turn) for turn in turns]

    def suggestions(self, session_id: str, current_user, question: str | None = None) -> list[str]:
        ProjectService(self.session).get_project(session_id, current_user)
        return self.conversation_engine.suggestions(session_id, current_user, question)