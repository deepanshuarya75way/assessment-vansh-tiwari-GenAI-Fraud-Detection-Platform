from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.api.deps import get_current_user
from app.backend.db.session import get_db_session
from app.backend.db.database_service import DatabaseService
from app.backend.modules.chatbot.schema import ChatRequest, ChatTurnResponse
from app.backend.modules.chatbot.service import ChatbotService

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/sessions/{session_id}/ask", response_model=ChatTurnResponse)
def ask_session_question(
    session_id: str,
    payload: ChatRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ChatTurnResponse:
    turn = ChatbotService(session).ask(session_id, current_user, payload)
    return ChatTurnResponse.model_validate(turn)


@router.post("/projects/{project_id}/ask", response_model=ChatTurnResponse)
def ask_question(
    project_id: str,
    payload: ChatRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ChatTurnResponse:
    turn = ChatbotService(session).ask(project_id, current_user, payload)
    return ChatTurnResponse.model_validate(turn)


@router.get("/sessions/{session_id}/history", response_model=list[ChatTurnResponse])
def session_history(
    session_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[ChatTurnResponse]:
    turns = ChatbotService(session).history(session_id, current_user)
    return [ChatTurnResponse.model_validate(turn) for turn in turns]


@router.get("/projects/{project_id}/history", response_model=list[ChatTurnResponse])
def history(
    project_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[ChatTurnResponse]:
    turns = ChatbotService(session).history(project_id, current_user)
    return [ChatTurnResponse.model_validate(turn) for turn in turns]


@router.get("/sessions/{session_id}/suggestions", response_model=list[str])
def suggestions(
    session_id: str,
    question: str | None = None,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[str]:
    return ChatbotService(session).suggestions(session_id, current_user, question)