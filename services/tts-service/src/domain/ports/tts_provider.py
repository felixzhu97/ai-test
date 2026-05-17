"""TTS Provider Port - interface for TTS provider implementations."""

from typing import Protocol, AsyncIterator, List, Optional, runtime_checkable

from ..entities import Voice, SynthesisRequest, SynthesisResult, OutputFormat


@runtime_checkable
class TTSProviderPort(Protocol):
    """Port interface for TTS providers.
    
    This Protocol defines the contract that all TTS provider adapters
    must implement. It enables dependency inversion, allowing the domain
    layer to be independent of specific provider implementations.
    
    Implementations:
        - AzureTTSAdapter
        - GoogleTTSAdapter
        - ElevenLabsAdapter
        - CoquiTTSAdapter
        - EdgeTTSAdapter
    """
    
    @property
    def provider_name(self) -> str:
        """Get the provider identifier.
        
        Returns:
            Provider name (e.g., 'azure', 'google', 'edge')
        """
        ...
    
    async def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        """Synthesize text to speech.
        
        Args:
            request: Synthesis request with text and parameters
            
        Returns:
            SynthesisResult with audio data
            
        Raises:
            TTSProviderError: If synthesis fails
        """
        ...
    
    async def stream(
        self,
        request: SynthesisRequest,
    ) -> AsyncIterator[bytes]:
        """Stream synthesized speech in chunks.
        
        Args:
            request: Synthesis request
            
        Yields:
            Audio data chunks
            
        Raises:
            TTSProviderError: If streaming fails
        """
        ...
    
    async def list_voices(self, language: Optional[str] = None) -> List[Voice]:
        """List available voices from the provider.
        
        Args:
            language: Optional language filter
            
        Returns:
            List of available voices
        """
        ...
    
    async def health_check(self) -> bool:
        """Check if the provider is healthy and available.
        
        Returns:
            True if provider is healthy, False otherwise
        """
        ...


class TTSProviderError(Exception):
    """Base exception for TTS provider errors."""
    
    def __init__(self, message: str, provider: str = "unknown", cause: Optional[Exception] = None):
        """Initialize TTS provider error.
        
        Args:
            message: Error message
            provider: Provider identifier
            cause: Original exception if any
        """
        super().__init__(message)
        self.provider = provider
        self.cause = cause


class SynthesisError(TTSProviderError):
    """Error during speech synthesis."""
    pass


class StreamingError(TTSProviderError):
    """Error during speech streaming."""
    pass


class ProviderUnavailableError(TTSProviderError):
    """Provider is not available or not configured."""
    pass
