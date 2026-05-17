"""Completion Use Case - Business logic for text completion."""

import time
from typing import Iterator

from src.domain import LLMServiceError
from src.application.dto.completion_dto import CompletionRequestDTO, CompletionResponseDTO


class CompletionUseCase:
    """Use case for simple text completion."""

    def __init__(
        self,
        llm_gateway: "LLMGatewayPort",
    ):
        """Initialize with dependencies.

        Args:
            llm_gateway: LLM service adapter (injected, not imported)
        """
        self._llm = llm_gateway

    def execute(self, request: CompletionRequestDTO) -> CompletionResponseDTO:
        """Execute text completion.

        Args:
            request: Completion request with prompt and options

        Returns:
            Completion response with generated text
        """
        start_time = time.time()

        try:
            response_text = self._llm.complete(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                provider=request.provider,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except Exception as e:
            raise LLMServiceError(f"Completion failed: {e}")

        elapsed_ms = int((time.time() - start_time) * 1000)

        return CompletionResponseDTO(
            text=response_text,
            provider=request.provider or self._llm.default_provider,
            model=request.model or self._llm.default_model,
            usage={"latency_ms": elapsed_ms},
            finish_reason="stop",
        )

    def execute_stream(
        self,
        request: CompletionRequestDTO,
    ) -> Iterator[str]:
        """Execute streaming text completion.

        Args:
            request: Completion request with prompt and options

        Yields:
            Text chunks as they are generated
        """
        try:
            yield from self._llm.complete_stream(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                provider=request.provider,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except Exception as e:
            raise LLMServiceError(f"Streaming completion failed: {e}")
