from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from loguru import logger
from typing import Optional
from ..config import get_settings


class LLMGateway:
    """Unified LLM gateway supporting multiple providers."""

    _instance: Optional[BaseChatModel] = None
    _provider: Optional[str] = None
    _model: Optional[str] = None
    _temperature: Optional[float] = None

    @classmethod
    def get_llm(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
    ) -> BaseChatModel:
        settings = get_settings()
        provider = provider or settings.LLM_PROVIDER
        
        if provider == "openai":
            model = model or settings.LLM_MODEL
        elif provider == "anthropic":
            model = model or settings.LLM_MODEL
        elif provider == "ollama":
            model = model or settings.OLLAMA_MODEL
        elif provider == "deepseek":
            model = model or settings.LLM_MODEL
        else:
            model = model or settings.LLM_MODEL

        # Cache key includes temperature to properly handle different temperature settings
        if (cls._instance is not None 
                and cls._provider == provider 
                and cls._model == model
                and cls._temperature == temperature):
            return cls._instance

        logger.info(f"Initializing LLM: provider={provider}, model={model}, temperature={temperature}")

        if provider == "openai":
            cls._instance = ChatOpenAI(
                model=model,
                api_key=settings.OPENAI_API_KEY or None,
                base_url=settings.OPENAI_BASE_URL or None,
                temperature=temperature,
            )
        elif provider == "anthropic":
            cls._instance = ChatAnthropic(
                model=model,
                anthropic_api_key=settings.ANTHROPIC_API_KEY or None,
                temperature=temperature,
            )
        elif provider == "ollama":
            cls._instance = ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=model,
                temperature=temperature,
            )
        elif provider == "deepseek":
            cls._instance = ChatOpenAI(
                model=model,
                api_key=settings.DEEPSEEK_API_KEY or None,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=temperature,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

        cls._provider = provider
        cls._model = model
        cls._temperature = temperature
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the LLM instance."""
        cls._instance = None
        cls._provider = None
        cls._model = None
        cls._temperature = None


def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> BaseChatModel:
    """Factory function for getting LLM instance."""
    return LLMGateway.get_llm(provider, model, temperature)
