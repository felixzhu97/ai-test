"""ElevenLabs TTS Adapter.

Implements TTSProviderPort using ElevenLabs API.
"""

from typing import Optional, List, AsyncIterator

from ...domain.entities import Voice, SynthesisRequest, SynthesisResult
from .base_adapter import BaseTTSAdapter


# Common ElevenLabs voices
ELEVENLABS_VOICES = [
    Voice(id="rachel", name="Rachel", language="en", 
          language_name="English", gender="Female", provider="elevenlabs", is_default=True),
    Voice(id="domi", name="Domi", language="en", 
          language_name="English", gender="Female", provider="elevenlabs"),
    Voice(id="bella", name="Bella", language="en", 
          language_name="English", gender="Female", provider="elevenlabs"),
    Voice(id="anton", name="Anton", language="en", 
          language_name="English", gender="Male", provider="elevenlabs"),
    Voice(id="adam", name="Adam", language="en", 
          language_name="English", gender="Male", provider="elevenlabs"),
]


class ElevenLabsTTSAdapter(BaseTTSAdapter):
    """ElevenLabs TTS implementation of TTSProviderPort."""
    
    provider_name = "elevenlabs"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_voice: str = "rachel",
    ):
        """Initialize ElevenLabs TTS adapter.
        
        Args:
            api_key: ElevenLabs API key
            default_voice: Default voice identifier
        """
        self._api_key = api_key
        self._default_voice = default_voice
        self._voices_cache: Optional[List[Voice]] = None
    
    def _do_synthesize(self, request: SynthesisRequest) -> bytes:
        """Perform synthesis using ElevenLabs."""
        try:
            from elevenlabs import generate, set_api_key
            
            if self._api_key:
                set_api_key(self._api_key)
            
            audio_data = generate(
                text=request.text,
                voice=request.voice or self._default_voice,
                model="eleven_monolingual_v1",
            )
            
            return audio_data if isinstance(audio_data, bytes) else audio_data.read()
            
        except ImportError:
            raise RuntimeError("ElevenLabs SDK not installed. Install with: pip install elevenlabs")
        except Exception as e:
            raise RuntimeError(f"ElevenLabs synthesis failed: {e}")
    
    async def _do_stream(self, request: SynthesisRequest) -> AsyncIterator[bytes]:
        """Stream synthesis using ElevenLabs."""
        try:
            from elevenlabs import generate, set_api_key
            
            if self._api_key:
                set_api_key(self._api_key)
            
            # ElevenLabs streaming
            from elevenlabs import stream
            from io import BytesIO
            
            audio_stream = stream(
                text=request.text,
                voice=request.voice or self._default_voice,
                model="eleven_monolingual_v1",
            )
            
            buffer = BytesIO()
            async for chunk in audio_stream:
                buffer.write(chunk if isinstance(chunk, bytes) else chunk.read())
                yield chunk if isinstance(chunk, bytes) else chunk.read()
            
        except ImportError:
            raise RuntimeError("ElevenLabs SDK not installed. Install with: pip install elevenlabs")
        except Exception as e:
            raise RuntimeError(f"ElevenLabs streaming failed: {e}")
    
    def _do_list_voices(self, language: Optional[str] = None) -> List[Voice]:
        """List ElevenLabs voices."""
        if self._voices_cache is None:
            self._voices_cache = ELEVENLABS_VOICES
        
        if language:
            lang_prefix = language.lower()
            return [v for v in self._voices_cache if v.language.lower().startswith(lang_prefix)]
        
        return self._voices_cache
    
    def _do_health_check(self) -> bool:
        """Check ElevenLabs availability."""
        try:
            return self._api_key is not None
        except Exception:
            return False
