"""Chat Use Case - Business logic for chat completion."""

import time
from typing import Optional, Iterator, List

from src.domain import Session, SessionRepository, LLMServiceError
from src.application.dto.chat_dto import ChatRequestDTO, ChatResponseDTO, ChatMessageDTO


class ChatUseCase:
    """Use case for chat completion with session management."""

    def __init__(
        self,
        session_repository: SessionRepository,
        llm_gateway: "LLMGatewayPort",
    ):
        """Initialize with dependencies.

        Args:
            session_repository: Storage for chat sessions
            llm_gateway: LLM service adapter (injected, not imported)
        """
        self._session_repo = session_repository
        self._llm = llm_gateway

    def execute(self, request: ChatRequestDTO) -> ChatResponseDTO:
        """Execute chat completion.

        Args:
            request: Chat request with messages and options

        Returns:
            Chat response with generated text
        """
        start_time = time.time()

        session = self._get_or_create_session(request.session_id)
        self._add_user_messages(session, request.messages)

        conversation = session.get_conversation(request.system_prompt)

        try:
            response_text = self._llm.chat(conversation)
        except Exception as e:
            raise LLMServiceError(f"Chat completion failed: {e}")

        session.add_assistant_message(response_text)
        self._session_repo.save(session)

        elapsed_ms = int((time.time() - start_time) * 1000)

        return ChatResponseDTO(
            text=response_text,
            provider=request.provider or self._llm.default_provider,
            model=request.model or self._llm.default_model,
            session_id=session.id,
            usage={
                "latency_ms": elapsed_ms,
                "history_length": len(session.messages),
            },
            finish_reason="stop",
        )

    def execute_stream(
        self,
        request: ChatRequestDTO,
    ) -> tuple[str, Iterator[str], ChatResponseDTO]:
        """Execute streaming chat completion.

        Returns:
            Tuple of (session_id, token_stream, response_metadata)
        """
        start_time = time.time()

        session = self._get_or_create_session(request.session_id)
        self._add_user_messages(session, request.messages)

        conversation = session.get_conversation(request.system_prompt)

        try:
            token_stream = self._llm.chat_stream(conversation)
        except Exception as e:
            raise LLMServiceError(f"Streaming chat failed: {e}")

        elapsed_ms = int((time.time() - start_time) * 1000)

        response = ChatResponseDTO(
            text="",
            provider=request.provider or self._llm.default_provider,
            model=request.model or self._llm.default_model,
            session_id=session.id,
            usage={
                "latency_ms": elapsed_ms,
                "history_length": len(session.messages),
            },
            finish_reason="stop",
        )

        return session.id, token_stream, response

    def finalize_session(
        self,
        session_id: str,
        messages: List[ChatMessageDTO],
        full_response: str,
        max_history: int = 20,
    ) -> Session:
        """Finalize session after streaming (save messages and response)."""
        session = self._session_repo.get(session_id)
        if session:
            self._add_user_messages(session, messages)
            session.add_assistant_message(full_response)
            session.max_history = max_history
            self._session_repo.save(session)
        return session or Session.create(session_id)

    def _get_or_create_session(self, session_id: Optional[str]) -> Session:
        """Get existing session or create new one."""
        if session_id:
            session = self._session_repo.get(session_id)
            if session:
                return session
        return Session.create(session_id)

    def _add_user_messages(self, session: Session, messages: List[ChatMessageDTO]) -> None:
        """Add user messages from DTOs to session."""
        for msg in messages:
            if msg.role == "user":
                session.add_user_message(msg.content)
