"""Edge TTS Adapter.

Implements TTSProviderPort using the Edge TTS library.
"""

from typing import Optional, List, AsyncIterator
import tempfile
import os
import asyncio
import concurrent.futures

from ...domain.entities import Voice, SynthesisRequest, SynthesisResult, OutputFormat
from .base_adapter import BaseTTSAdapter


def _run_async(coro):
    """Run coroutine, handling both nested and top-level contexts."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()


# Popular Edge TTS voices
EDGE_VOICES = [
    Voice(id="zh-CN-XiaoxiaoNeural", name="Xiaoxiao (晓晓)", language="zh-CN", 
          language_name="Chinese (Simp)", gender="Female", provider="edge", is_default=True),
    Voice(id="zh-CN-YunxiNeural", name="Yunxi (云希)", language="zh-CN", 
          language_name="Chinese (Simp)", gender="Male", provider="edge"),
    Voice(id="zh-CN-YunyangNeural", name="Yunyang (云扬)", language="zh-CN", 
          language_name="Chinese (Simp)", gender="Male", provider="edge"),
    Voice(id="zh-CN-XiaoyiNeural", name="Xiaoyi (小艺)", language="zh-CN", 
          language_name="Chinese (Simp)", gender="Female", provider="edge"),
    Voice(id="zh-TW-HsiaoYuNeural", name="HsiaoYu", language="zh-TW", 
          language_name="Chinese (Trad)", gender="Female", provider="edge"),
    Voice(id="en-US-JennyNeural", name="Jenny", language="en-US", 
          language_name="English (US)", gender="Female", provider="edge"),
    Voice(id="en-US-GuyNeural", name="Guy", language="en-US", 
          language_name="English (US)", gender="Male", provider="edge"),
    Voice(id="en-US-AriaNeural", name="Aria", language="en-US", 
          language_name="English (US)", gender="Female", provider="edge"),
    Voice(id="en-GB-SoniaNeural", name="Sonia", language="en-GB", 
          language_name="English (UK)", gender="Female", provider="edge"),
    Voice(id="en-GB-RyanNeural", name="Ryan", language="en-GB", 
          language_name="English (UK)", gender="Male", provider="edge"),
    Voice(id="ja-JP-NanamiNeural", name="Nanami (七海)", language="ja-JP", 
          language_name="Japanese", gender="Female", provider="edge"),
    Voice(id="ko-KR-SunHiNeural", name="SunHi (선희)", language="ko-KR", 
          language_name="Korean", gender="Female", provider="edge"),
    Voice(id="fr-FR-DeniseNeural", name="Denise", language="fr-FR", 
          language_name="French", gender="Female", provider="edge"),
    Voice(id="de-DE-KatjaNeural", name="Katja", language="de-DE", 
          language_name="German", gender="Female", provider="edge"),
    Voice(id="es-ES-ElviraNeural", name="Elvira", language="es-ES", 
          language_name="Spanish", gender="Female", provider="edge"),
    Voice(id="ru-RU-SvetlanaNeural", name="Svetlana", language="ru-RU", 
          language_name="Russian", gender="Female", provider="edge"),
]


class EdgeTTSAdapter(BaseTTSAdapter):
    """Edge TTS implementation of TTSProviderPort."""
    
    provider_name = "edge"
    
    def __init__(self, default_voice: str = "zh-CN-XiaoxiaoNeural"):
        """Initialize Edge TTS adapter.
        
        Args:
            default_voice: Default voice identifier
        """
        self._default_voice = default_voice
        self._communicate = None
        self._edge_imported = False
    
    def _ensure_edge_tts(self):
        """Lazy import of edge-tts."""
        if not self._edge_imported:
            try:
                import edge_tts
                self._communicate = edge_tts.Communicate
                self._edge_imported = True
            except ImportError:
                raise RuntimeError("edge-tts library not installed. Install with: pip install edge-tts")
        return self._communicate
    
    def _speed_to_edge_rate(self, speed: float) -> str:
        """Convert speed to edge-tts rate format."""
        if speed < 0.5:
            speed = 0.5
        elif speed > 2.0:
            speed = 2.0
        percentage = (speed - 1.0) * 100
        return f"{'+' if percentage >= 0 else ''}{percentage:.0f}%"
    
    def _pitch_to_edge_pitch(self, pitch: float) -> Optional[str]:
        """Convert pitch to edge-tts pitch format.
        
        Edge TTS expects pitch in format like '+5Hz' or '-10Hz'.
        When pitch is 0, return None to omit the parameter.
        """
        if pitch == 0:
            return None
        sign = '+' if pitch >= 0 else ''
        return f"{sign}{pitch:.0f}Hz"
    
    def _do_synthesize(self, request: SynthesisRequest) -> bytes:
        """Perform synthesis using Edge TTS."""
        import asyncio
        
        Communicate = self._ensure_edge_tts()
        
        voice = request.voice or self._default_voice
        rate = self._speed_to_edge_rate(request.speed)
        pitch = self._pitch_to_edge_pitch(request.pitch)
        
        output_path = tempfile.mktemp(suffix=".mp3")
        try:
            _run_async(self._synthesize_async(Communicate, request.text, voice, rate, pitch, output_path))
            with open(output_path, "rb") as f:
                audio_data = f.read()
            return audio_data
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    async def _synthesize_async(self, Communicate, text: str, voice: str, rate: str, pitch: Optional[str], output_path: str):
        """Async helper for synthesis."""
        communicate = Communicate(text, voice, rate=rate, pitch=pitch) if pitch else Communicate(text, voice, rate=rate)
        await communicate.save(output_path)
    
    async def _do_stream(self, request: SynthesisRequest) -> AsyncIterator[bytes]:
        """Stream synthesis using Edge TTS."""
        Communicate = self._ensure_edge_tts()
        
        voice = request.voice or self._default_voice
        rate = self._speed_to_edge_rate(request.speed)
        pitch = self._pitch_to_edge_pitch(request.pitch)
        
        communicate = Communicate(request.text, voice, rate=rate, pitch=pitch)
        
        async for chunk in communicate.stream():
            yield chunk
    
    def _do_list_voices(self, language: Optional[str] = None) -> List[Voice]:
        """List Edge TTS voices."""
        if language:
            lang_prefix = language.lower()
            filtered = [v for v in EDGE_VOICES if v.language.lower().startswith(lang_prefix)]
            return filtered if filtered else EDGE_VOICES
        return EDGE_VOICES
    
    def _do_health_check(self) -> bool:
        """Check Edge TTS availability."""
        try:
            self._ensure_edge_tts()
            return True
        except Exception:
            return False
