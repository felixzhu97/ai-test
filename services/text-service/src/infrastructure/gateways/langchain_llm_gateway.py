"""LangChain LLM Gateway - Infrastructure implementation of LLM protocol."""

from typing import Optional, Iterator, List, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from loguru import logger

from .llm_protocol import LLMGatewayPort
from .config_adapter import ConfigPort


class LangChainLLMGateway(LLMGatewayPort):
    """LangChain-based implementation of LLM gateway.
    
    This gateway provides a unified interface for multiple LLM providers
    (OpenAI, Anthropic, Ollama) using LangChain abstractions.
    """
    
    def __init__(self, config: ConfigPort):
        """Initialize with configuration.
        
        Args:
            config: Configuration adapter providing settings
        """
        self._config = config
        self._llm: Optional[BaseChatModel] = None
        self._current_provider: Optional[str] = None
        self._current_model: Optional[str] = None
        self._current_temperature: Optional[float] = None
    
    @property
    def default_provider(self) -> str:
        return self._config.llm_provider
    
    @property
    def default_model(self) -> str:
        return self._config.llm_model
    
    def _get_llm(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> BaseChatModel:
        """Get or create LLM instance with given parameters."""
        provider = provider or self._config.llm_provider
        
        if provider == "openai":
            model = model or self._config.llm_model
        elif provider == "anthropic":
            model = model or self._config.anthropic_default_model
        elif provider == "ollama":
            model = model or self._config.ollama_model
        else:
            model = model or self._config.llm_model
        
        if (self._llm is None or 
            self._current_provider != provider or 
            self._current_model != model or
            self._current_temperature != temperature):
            
            logger.info(f"Initializing LLM: provider={provider}, model={model}, temperature={temperature}")
            
            self._llm = self._create_llm(provider, model, temperature, max_tokens)
            self._current_provider = provider
            self._current_model = model
            self._current_temperature = temperature
        
        return self._llm
    
    def _create_llm(
        self,
        provider: str,
        model: str,
        temperature: float,
        max_tokens: Optional[int],
    ) -> BaseChatModel:
        """Create a new LLM instance for the given provider."""
        max_tokens = max_tokens or self._config.llm_max_tokens
        
        if provider == "openai":
            return ChatOpenAI(
                model=model,
                api_key=self._config.openai_api_key or None,
                base_url=self._config.openai_base_url or None,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self._config.openai_timeout,
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=model,
                anthropic_api_key=self._config.anthropic_api_key or None,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self._config.anthropic_timeout,
            )
        elif provider == "ollama":
            return ChatOllama(
                base_url=self._config.ollama_base_url,
                model=model,
                temperature=temperature,
                timeout=self._config.ollama_timeout,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text completion."""
        llm = self._get_llm(provider, model, temperature, max_tokens)
        
        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = llm.invoke(messages)
        return self._extract_content(response)
    
    def complete_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Generate streaming text completion."""
        llm = self._get_llm(provider, model, temperature, max_tokens)
        
        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        for chunk in llm.stream(messages):
            content = self._extract_content(chunk)
            if content:
                yield content
    
    def chat(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate chat completion."""
        llm = self._get_llm(provider, model, temperature, max_tokens)
        
        lc_messages = self._convert_messages(messages, system_prompt)
        response = llm.invoke(lc_messages)
        return self._extract_content(response)
    
    def chat_stream(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Generate streaming chat completion."""
        llm = self._get_llm(provider, model, temperature, max_tokens)
        
        lc_messages = self._convert_messages(messages, system_prompt)
        
        for chunk in llm.stream(lc_messages):
            content = self._extract_content(chunk)
            if content:
                yield content
    
    def _convert_messages(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None,
    ) -> List[BaseMessage]:
        """Convert message dicts to LangChain messages."""
        lc_messages: List[BaseMessage] = []
        
        if system_prompt:
            lc_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        return lc_messages
    
    def _extract_content(self, response: Any) -> str:
        """Extract text content from LLM response."""
        if isinstance(response, str):
            return response
        if isinstance(response, dict):
            return response.get("content", str(response))
        if hasattr(response, "content"):
            return response.content
        if hasattr(response, "generations"):
            generations = response.generations
            if generations and len(generations) > 0:
                first_gen = generations[0]
                if isinstance(first_gen, list) and len(first_gen) > 0:
                    return first_gen[0].text if hasattr(first_gen[0], "text") else str(first_gen[0])
                elif hasattr(first_gen, "text"):
                    return first_gen.text
        return str(response)
    
    def reset(self) -> None:
        """Reset cached LLM instance."""
        self._llm = None
        self._current_provider = None
        self._current_model = None
        self._current_temperature = None
