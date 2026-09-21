from sqlalchemy import desc, select

from app.backend.common.repository import BaseRepository
from app.backend.db.enterprise_models import ChatMessage


class ChatMessageRepository(BaseRepository[ChatMessage]):
    model = ChatMessage

    def list_for_project(self, project_id: str) -> list[ChatMessage]:
        stmt = select(ChatMessage).where(ChatMessage.project_id == project_id).order_by(desc(ChatMessage.created_at))
        return list(self.session.scalars(stmt))

    def list_for_session(self, session_id: str) -> list[ChatMessage]:
        return self.list_for_project(session_id)

    def latest_for_project(self, project_id: str) -> ChatMessage | None:
        stmt = select(ChatMessage).where(ChatMessage.project_id == project_id).order_by(desc(ChatMessage.created_at))
        return self.session.scalar(stmt)

    def latest_for_session(self, session_id: str) -> ChatMessage | None:
        return self.latest_for_project(session_id)