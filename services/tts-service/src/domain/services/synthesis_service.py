"""Synthesis domain service - business logic for speech synthesis."""

import re
from typing import Optional

from ..entities import SynthesisRequest, SynthesisResult, Voice, OutputFormat


class SynthesisService:
    """Domain service containing business logic for speech synthesis.
    
    This service handles:
    - Text validation and normalization
    - SSML generation for providers that support it
    - Parameter transformation
    - Cache key generation
    
    It is framework-agnostic and can be used by any provider adapter.
    """
    
    # Patterns for text normalization
    ABBREVIATION_PATTERNS = {
        r'\bDr\.': 'Doctor',
        r'\bMr\.': 'Mister',
        r'\bMrs\.': 'Missus',
        r'\bMs\.': 'Miss',
        r'\bProf\.': 'Professor',
        r'\bU\.S\.': 'U S',
        r'\bU\.K\.': 'U K',
        r'\bE\.g\.': 'for example',
        r'\bI\.e\.': 'that is',
    }
    
    def __init__(self, default_voice: str = "en-US-JennyNeural", default_language: str = "en-US"):
        """Initialize synthesis service.
        
        Args:
            default_voice: Default voice identifier
            default_language: Default language code
        """
        self._default_voice = default_voice
        self._default_language = default_language
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better TTS output.
        
        Args:
            text: Raw input text
            
        Returns:
            Normalized text
        """
        result = text
        
        # Apply abbreviation replacements
        for pattern, replacement in self.ABBREVIATION_PATTERNS.items():
            result = re.sub(pattern, replacement, result)
        
        # Remove extra whitespace
        result = re.sub(r'\s+', ' ', result).strip()
        
        # Ensure sentence ends with punctuation
        if result and result[-1] not in '.!?':
            result += '.'
        
        return result
    
    def apply_defaults(self, request: SynthesisRequest) -> SynthesisRequest:
        """Apply default values to synthesis request.
        
        Args:
            request: Original synthesis request
            
        Returns:
            Request with defaults applied
        """
        if request.voice is None:
            request = SynthesisRequest(
                text=request.text,
                voice=self._default_voice,
                language=request.language or self._default_language,
                speed=request.speed,
                pitch=request.pitch,
                output_format=request.output_format,
                audio_config=request.audio_config,
            )
        elif request.language is None:
            request = SynthesisRequest(
                text=request.text,
                voice=request.voice,
                language=self._default_language,
                speed=request.speed,
                pitch=request.pitch,
                output_format=request.output_format,
                audio_config=request.audio_config,
            )
        return request
    
    def generate_cache_key(
        self,
        request: SynthesisRequest,
        provider_name: str,
    ) -> str:
        """Generate cache key for synthesis request.
        
        Args:
            request: Synthesis request
            provider_name: Provider identifier
            
        Returns:
            SHA256 cache key
        """
        import hashlib
        
        key_data = (
            f"{request.text}:"
            f"{request.voice or ''}:"
            f"{request.language or ''}:"
            f"{request.speed}:"
            f"{request.pitch}:"
            f"{request.output_format.value}:"
            f"{provider_name}"
        )
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def generate_ssml(
        self,
        request: SynthesisRequest,
        provider_name: str,
    ) -> str:
        """Generate SSML for providers that support it.
        
        Args:
            request: Synthesis request
            provider_name: Provider identifier
            
        Returns:
            SSML string
            
        Raises:
            ValueError: If provider doesn't support SSML
        """
        # SSML is supported by Azure, Google, and ElevenLabs
        ssml_providers = {"azure", "google", "elevenlabs"}
        
        if provider_name not in ssml_providers:
            raise ValueError(f"Provider '{provider_name}' does not support SSML")
        
        # Convert speed and pitch to SSML format
        speed_percent = int(request.speed * 100)
        pitch_str = f"+{request.pitch}Hz" if request.pitch >= 0 else f"{request.pitch}Hz"
        language = request.language or self._default_language
        voice = request.voice or self._default_voice
        
        ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{language}'>
    <voice name='{voice}'>
        <prosody rate='{speed_percent}%' pitch='{pitch_str}'>{request.text}</prosody>
    </voice>
</speak>"""
        
        return ssml
    
    def transform_speed_for_provider(
        self,
        speed: float,
        provider_name: str,
    ) -> str:
        """Transform speed value for specific provider format.
        
        Args:
            speed: Speed multiplier (0.25-4.0)
            provider_name: Provider identifier
            
        Returns:
            Provider-specific speed format
        """
        # Edge TTS uses percentage format (+/-X%)
        if provider_name == "edge":
            percentage = (speed - 1.0) * 100
            return f"{'+' if percentage >= 0 else ''}{percentage:.0f}%"
        
        # Default: return as multiplier
        return str(speed)
    
    def transform_pitch_for_provider(
        self,
        pitch: float,
        provider_name: str,
    ) -> str:
        """Transform pitch value for specific provider format.
        
        Args:
            pitch: Pitch adjustment in Hz
            provider_name: Provider identifier
            
        Returns:
            Provider-specific pitch format
        """
        # Edge TTS uses percentage format
        if provider_name == "edge":
            return f"{'+' if pitch >= 0 else ''}{pitch:.0f}%"
        
        # Default: return in Hz
        return f"+{pitch}Hz" if pitch >= 0 else f"{pitch}Hz"
    
    def filter_voices(
        self,
        voices: list[Voice],
        language: Optional[str] = None,
        gender: Optional[str] = None,
    ) -> list[Voice]:
        """Filter voices by language and/or gender.
        
        Args:
            voices: List of voices to filter
            language: Optional language filter
            gender: Optional gender filter
            
        Returns:
            Filtered list of voices
        """
        result = voices
        
        if language:
            lang_prefix = language.lower()
            result = [v for v in result if v.language.lower().startswith(lang_prefix)]
        
        if gender:
            result = [v for v in result if v.gender == gender]
        
        return result
    
    @property
    def default_voice(self) -> str:
        """Get default voice identifier."""
        return self._default_voice
    
    @property
    def default_language(self) -> str:
        """Get default language code."""
        return self._default_language
