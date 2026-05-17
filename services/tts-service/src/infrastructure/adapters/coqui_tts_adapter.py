"""Coqui TTS Adapter.

Implements TTSProviderPort using Coqui TTS (local deployment).
"""

from typing import Optional, List, AsyncIterator

from ...domain.entities import Voice, SynthesisRequest, SynthesisResult
from .base_adapter import BaseTTSAdapter


# Coqui TTS voices (limited set for local model)
COQUI_VOICES = [
    Voice(id="default", name="Default Coqui Model", language="en", 
          language_name="English", gender="Neutral", provider="coqui", is_default=True),
]


class CoquiTTSAdapter(BaseTTSAdapter):
    """Coqui TTS implementation of TTSProviderPort (local deployment)."""
    
    provider_name = "coqui"
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        default_voice: str = "default",
    ):
        """Initialize Coqui TTS adapter.
        
        Args:
            model_path: Path to Coqui TTS model
            default_voice: Default voice identifier
        """
        self._model_path = model_path
        self._default_voice = default_voice
        self._model = None
        self._voices_cache: Optional[List[Voice]] = None
    
    def _load_model(self):
        """Lazy load Coqui TTS model."""
        if self._model is None:
            try:
                from TTS.api import TTS
                
                if self._model_path:
                    self._model = TTS(model_path=self._model_path)
                else:
                    # Use default model
                    self._model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            except ImportError:
                raise RuntimeError("Coqui TTS not installed. Install with: pip install TTS")
            except Exception as e:
                raise RuntimeError(f"Failed to load Coqui TTS model: {e}")
        
        return self._model
    
    def _do_synthesize(self, request: SynthesisRequest) -> bytes:
        """Perform synthesis using Coqui TTS."""
        import tempfile
        import os
        
        model = self._load_model()
        
        # Generate to temporary file
        output_path = tempfile.mktemp(suffix=".wav")
        try:
            model.tts_to_file(
                text=request.text,
                file_path=output_path,
            )
            
            with open(output_path, "rb") as f:
                audio_data = f.read()
            
            return audio_data
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    async def _do_stream(self, request: SynthesisRequest) -> AsyncIterator[bytes]:
        """Stream synthesis using Coqui TTS."""
        # Coqui doesn't support true streaming, yield entire audio
        audio_data = self._do_synthesize(request)
        yield audio_data
    
    def _do_list_voices(self, language: Optional[str] = None) -> List[Voice]:
        """List Coqui TTS voices."""
        if self._voices_cache is None:
            self._voices_cache = COQUI_VOICES
        
        if language:
            lang_prefix = language.lower()
            return [v for v in self._voices_cache if v.language.lower().startswith(lang_prefix)]
        
        return self._voices_cache
    
    def _do_health_check(self) -> bool:
        """Check Coqui TTS availability."""
        try:
            self._load_model()
            return True
        except Exception:
            return False
