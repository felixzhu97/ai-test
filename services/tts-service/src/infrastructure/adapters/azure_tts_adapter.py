"""Azure TTS Adapter.

Implements TTSProviderPort using Azure Cognitive Services.
"""

from typing import Optional, List, AsyncIterator

from ...domain.entities import Voice, SynthesisRequest, SynthesisResult
from .base_adapter import BaseTTSAdapter


# Common Azure Neural voices
AZURE_VOICES = [
    Voice(id="en-US-JennyNeural", name="Jenny", language="en-US", 
          language_name="English (US)", gender="Female", provider="azure", is_default=True),
    Voice(id="en-US-GuyNeural", name="Guy", language="en-US", 
          language_name="English (US)", gender="Male", provider="azure"),
    Voice(id="zh-CN-XiaoxiaoNeural", name="Xiaoxiao", language="zh-CN", 
          language_name="Chinese (Mandarin, Simplified)", gender="Female", provider="azure"),
    Voice(id="zh-CN-YunxiNeural", name="Yunxi", language="zh-CN", 
          language_name="Chinese (Mandarin, Simplified)", gender="Male", provider="azure"),
    Voice(id="ja-JP-NanamiNeural", name="Nanami", language="ja-JP", 
          language_name="Japanese", gender="Female", provider="azure"),
    Voice(id="ko-KR-SunHiNeural", name="SunHi", language="ko-KR", 
          language_name="Korean", gender="Female", provider="azure"),
    Voice(id="fr-FR-DeniseNeural", name="Denise", language="fr-FR", 
          language_name="French (France)", gender="Female", provider="azure"),
    Voice(id="de-DE-KatjaNeural", name="Katja", language="de-DE", 
          language_name="German (Germany)", gender="Female", provider="azure"),
]


class AzureTTSAdapter(BaseTTSAdapter):
    """Azure TTS implementation of TTSProviderPort."""
    
    provider_name = "azure"
    
    def __init__(
        self,
        speech_key: Optional[str] = None,
        speech_region: str = "eastus",
        default_voice: str = "en-US-JennyNeural",
    ):
        """Initialize Azure TTS adapter.
        
        Args:
            speech_key: Azure subscription key
            speech_region: Azure region
            default_voice: Default voice identifier
        """
        self._speech_key = speech_key
        self._speech_region = speech_region
        self._default_voice = default_voice
        self._client = None
        self._voices_cache: Optional[List[Voice]] = None
    
    def _get_client(self):
        """Get or create Azure TTS client."""
        if self._client is None:
            try:
                import azure.cognitiveservices.speech as speechsdk
                
                speech_config = speechsdk.SpeechConfig(
                    subscription=self._speech_key,
                    region=self._speech_region
                )
                self._client = speech_config
            except ImportError:
                raise RuntimeError("Azure SDK not installed. Install with: pip install azure-cognitiveservices-speech")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Azure TTS: {e}")
        
        return self._client
    
    def _do_synthesize(self, request: SynthesisRequest) -> bytes:
        """Perform synthesis using Azure TTS."""
        import azure.cognitiveservices.speech as speechsdk
        from azure.cognitiveservices.speech import SpeechSynthesisOutputFormat
        
        speech_config = self._get_client()
        
        # Set voice
        voice = request.voice or self._default_voice
        speech_config.speech_synthesis_voice_name = voice
        
        # Set output format
        format_map = {
            "mp3": SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
            "wav": SpeechSynthesisOutputFormat.Audio16Khz16BitMonoPcm,
            "ogg": SpeechSynthesisOutputFormat.Ogg16Khz16BitMonoOpus,
        }
        output_format = format_map.get(request.output_format.value, SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
        speech_config.set_speech_synthesis_output_format(output_format)
        
        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        # SSML for speed and pitch
        pitch_str = f"+{request.pitch}Hz" if request.pitch >= 0 else f"{request.pitch}Hz"
        speed_str = str(int(request.speed * 100))
        language = request.language or "en-US"
        
        ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{language}'>
            <voice name='{voice}'>
                <prosody rate='{speed_str}%' pitch='{pitch_str}'>{request.text}</prosody>
            </voice>
        </speak>"""
        
        # Synthesize
        result = synthesizer.speak_ssml_async(ssml).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return bytes(result.audio_data)
        else:
            error_details = getattr(result, 'cancellation_details', None)
            error_msg = getattr(error_details, 'error_details', 'Unknown error') if error_details else 'Unknown error'
            raise RuntimeError(f"TTS synthesis failed: {error_msg}")
    
    async def _do_stream(self, request: SynthesisRequest) -> AsyncIterator[bytes]:
        """Stream synthesis using Azure TTS."""
        # Azure TTS doesn't support true streaming, yield entire audio
        audio_data = self._do_synthesize(request)
        yield audio_data
    
    def _do_list_voices(self, language: Optional[str] = None) -> List[Voice]:
        """List Azure TTS voices."""
        if self._voices_cache is None:
            self._voices_cache = AZURE_VOICES
        
        if language:
            lang_prefix = language.lower()
            return [v for v in self._voices_cache if v.language.lower().startswith(lang_prefix)]
        
        return self._voices_cache
    
    def _do_health_check(self) -> bool:
        """Check Azure TTS health."""
        try:
            speech_config = self._get_client()
            return speech_config is not None and self._speech_key is not None
        except Exception:
            return False
