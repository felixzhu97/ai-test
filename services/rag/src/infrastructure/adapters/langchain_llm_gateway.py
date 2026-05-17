"""LangChain LLM gateway adapter - implements LLMGatewayPort interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from domain.ports.llm import LLMGatewayPort, Message, LLMResponse


def _get_settings():
    """Lazy import settings to avoid circular imports."""
    from config import get_settings
    return get_settings()


class LangChainLLMGatewayAdapter(LLMGatewayPort):
    """LangChain LLM gateway adapter implementing LLMGatewayPort interface."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> None:
        settings = _get_settings()
        self._provider = provider or settings.LLM_PROVIDER
        self._model_name = model or settings.LLM_MODEL
        self.temperature = temperature

        self._llm: Optional[BaseChatModel] = None

    def _get_llm(self) -> BaseChatModel:
        """Get or create the LLM instance."""
        if self._llm is None:
            settings = _get_settings()

            logger.info(
                f"Initializing LLM: provider={self._provider}, "
                f"model={self._model_name}, temperature={self.temperature}"
            )

            if self._provider == "openai":
                self._llm = ChatOpenAI(
                    model=self._model_name,
                    api_key=settings.OPENAI_API_KEY or None,
                    base_url=settings.OPENAI_BASE_URL or None,
                    temperature=self.temperature,
                )
            elif self._provider == "anthropic":
                self._llm = ChatAnthropic(
                    model=self._model_name,
                    anthropic_api_key=settings.ANTHROPIC_API_KEY or None,
                    temperature=self.temperature,
                )
            elif self._provider == "ollama":
                self._llm = ChatOllama(
                    base_url=settings.OLLAMA_BASE_URL,
                    model=self._model_name,
                    temperature=self.temperature,
                )
            elif self._provider == "deepseek":
                self._llm = ChatOpenAI(
                    model=self._model_name,
                    api_key=settings.DEEPSEEK_API_KEY or None,
                    base_url=settings.DEEPSEEK_BASE_URL,
                    temperature=self.temperature,
                )
            else:
                raise ValueError(f"Unknown LLM provider: {self._provider}")

            logger.info("LLM initialized successfully")

        return self._llm

    @property
    def provider(self) -> str:
        """Get the LLM provider name."""
        return self._provider

    @property
    def model(self) -> str:
        """Get the model name."""
        return self._model_name

    def _convert_messages(self, messages: list[Message]) -> list:
        """Convert domain Message objects to LangChain messages."""
        langchain_messages = []
        for msg in messages:
            if msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                from langchain_core.messages import AIMessage
                langchain_messages.append(AIMessage(content=msg.content))
        return langchain_messages

    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Generate text completion."""
        langchain_messages = self._convert_messages(messages)
        llm = self._get_llm()

        if max_tokens:
            llm.max_tokens = max_tokens

        response = await llm.agenerate([langchain_messages])

        usage = {}
        if hasattr(response, "llm_output") and response.llm_output:
            usage = response.llm_output.get("token_usage", {})

        return LLMResponse(
            content=response.generations[0][0].text,
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
            model=self._model_name,
            finish_reason="stop",
        )

    async def stream_generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream text completion."""
        langchain_messages = self._convert_messages(messages)
        llm = self._get_llm()

        if max_tokens:
            llm.max_tokens = max_tokens

        async for chunk in llm.astream(langchain_messages):
            if chunk.content:
                yield chunk.content
