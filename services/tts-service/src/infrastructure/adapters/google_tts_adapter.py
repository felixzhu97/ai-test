"""Google TTS Adapter.

Implements TTSProviderPort using Google Cloud Text-to-Speech.
"""

from typing import Optional, List, AsyncIterator

from ...domain.entities import Voice, SynthesisRequest, SynthesisResult
from .base_adapter import BaseTTSAdapter


# Common Google TTS voices
GOOGLE_VOICES = [
    Voice(id="en-US-Neural2-A", name="Neural2-A", language="en-US", 
          language_name="English (US)", gender="Female", provider="google", is_default=True),
    Voice(id="en-US-Neural2-C", name="Neural2-C", language="en-US", 
          language_name="English (US)", gender="Male", provider="google"),
    Voice(id="zh-CN-Neural2-A", name="Neural2-A", language="zh-CN", 
          language_name="Chinese (Mandarin)", gender="Female", provider="google"),
    Voice(id="ja-JP-Neural2-A", name="Neural2-A", language="ja-JP", 
          language_name="Japanese", gender="Female", provider="google"),
    Voice(id="ko-KR-Neural2-A", name="Neural2-A", language="ko-KR", 
          language_name="Korean", gender="Female", provider="google"),
    Voice(id="fr-FR-Neural2-A", name="Neural2-A", language="fr-FR", 
          language_name="French", gender="Female", provider="google"),
    Voice(id="de-DE-Neural2-A", name="Neural2-A", language="de-DE", 
          language_name="German", gender="Female", provider="google"),
]


class GoogleTTSAdapter(BaseTTSAdapter):
    """Google TTS implementation of TTSProviderPort."""
    
    provider_name = "google"
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        default_voice: str = "en-US-Neural2-A",
    ):
        """Initialize Google TTS adapter.
        
        Args:
            credentials_path: Path to GCP service account JSON
            default_voice: Default voice identifier
        """
        self._credentials_path = credentials_path
        self._default_voice = default_voice
        self._client = None
        self._voices_cache: Optional[List[Voice]] = None
    
    def _get_client(self):
        """Get or create Google TTS client."""
        if self._client is None:
            try:
                from google.cloud import texttospeech
                
                if self._credentials_path:
                    self._client = texttospeech.TextToSpeechClient.from_service_account_json(
                        self._credentials_path
                    )
                else:
                    self._client = texttospeech.TextToSpeechClient()
            except ImportError:
                raise RuntimeError("Google Cloud TTS SDK not installed. Install with: pip install google-cloud-texttospeech")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Google TTS: {e}")
        
        return self._client
    
    def _do_synthesize(self, request: SynthesisRequest) -> bytes:
        """Perform synthesis using Google TTS."""
        from google.cloud import texttospeech
        
        client = self._get_client()
        
        # Set input text
        synthesis_input = texttospeech.SynthesisInput(text=request.text)
        
        # Set voice
        voice = texttospeech.VoiceSelectionParams(
            language_code=request.language or "en-US",
            name=request.voice or self._default_voice,
        )
        
        # Set audio config
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=request.speed,
            pitch=request.pitch,
        )
        
        # Synthesize
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        
        return response.audio_content
    
    async def _do_stream(self, request: SynthesisRequest) -> AsyncIterator[bytes]:
        """Stream synthesis using Google TTS."""
        # Google TTS doesn't support true streaming, yield entire audio
        audio_data = self._do_synthesize(request)
        yield audio_data
    
    def _do_list_voices(self, language: Optional[str] = None) -> List[Voice]:
        """List Google TTS voices."""
        if self._voices_cache is None:
            self._voices_cache = GOOGLE_VOICES
        
        if language:
            lang_prefix = language.lower()
            return [v for v in self._voices_cache if v.language.lower().startswith(lang_prefix)]
        
        return self._voices_cache
    
    def _do_health_check(self) -> bool:
        """Check Google TTS health."""
        try:
            client = self._get_client()
            return client is not None
        except Exception:
            return False
