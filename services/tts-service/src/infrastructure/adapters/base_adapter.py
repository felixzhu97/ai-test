"""Base adapter for TTS providers.

This adapter implements the TTSProviderPort interface by delegating
to existing provider implementations, providing a clean transition path
for the Clean Architecture refactoring.
"""

from typing import Optional, List, AsyncIterator
from abc import ABC, abstractmethod

from ...domain.entities import Voice, SynthesisRequest, SynthesisResult, OutputFormat
from ...domain.ports import TTSProviderPort, SynthesisError, ProviderUnavailableError


class BaseTTSAdapter(ABC):
    """Base adapter that wraps existing provider implementations.
    
    This adapter pattern allows us to use existing provider code while
    conforming to the new domain port interface.
    """
    
    provider_name: str = "base"
    
    @abstractmethod
    def _do_synthesize(self, request: SynthesisRequest) -> bytes:
        """Perform actual synthesis using the wrapped provider.
        
        Args:
            request: Synthesis request
            
        Returns:
            Raw audio bytes
        """
        pass
    
    @abstractmethod
    async def _do_stream(self, request: SynthesisRequest) -> AsyncIterator[bytes]:
        """Perform actual streaming using the wrapped provider.
        
        Args:
            request: Synthesis request
            
        Yields:
            Audio chunks
        """
        pass
    
    @abstractmethod
    def _do_list_voices(self, language: Optional[str] = None) -> List[Voice]:
        """List voices from the wrapped provider.
        
        Args:
            language: Optional language filter
            
        Returns:
            List of voices
        """
        pass
    
    @abstractmethod
    def _do_health_check(self) -> bool:
        """Check health of the wrapped provider.
        
        Returns:
            True if healthy
        """
        pass
    
    async def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        """Synthesize text to speech.
        
        Args:
            request: Synthesis request
            
        Returns:
            SynthesisResult with audio data
        """
        try:
            audio_data = self._do_synthesize(request)
            
            return SynthesisResult(
                audio_data=audio_data,
                format=request.output_format,
                provider=self.provider_name,
            )
        except Exception as e:
            raise SynthesisError(
                message=f"Synthesis failed: {str(e)}",
                provider=self.provider_name,
                cause=e,
            )
    
    async def stream(self, request: SynthesisRequest) -> AsyncIterator[bytes]:
        """Stream synthesized speech.
        
        Args:
            request: Synthesis request
            
        Yields:
            Audio chunks
        """
        try:
            async for chunk in self._do_stream(request):
                yield chunk
        except Exception as e:
            raise SynthesisError(
                message=f"Streaming failed: {str(e)}",
                provider=self.provider_name,
                cause=e,
            )
    
    async def list_voices(self, language: Optional[str] = None) -> List[Voice]:
        """List available voices.
        
        Args:
            language: Optional language filter
            
        Returns:
            List of voices
        """
        try:
            return self._do_list_voices(language)
        except Exception as e:
            raise SynthesisError(
                message=f"Failed to list voices: {str(e)}",
                provider=self.provider_name,
                cause=e,
            )
    
    async def health_check(self) -> bool:
        """Check provider health.
        
        Returns:
            True if healthy
        """
        try:
            return self._do_health_check()
        except Exception:
            return False
