"""Tests for domain entities."""

import pytest
from src.domain.entities import Voice, AudioConfig, SynthesisRequest, SynthesisResult, OutputFormat


class TestVoice:
    """Tests for Voice entity."""
    
    def test_create_voice(self):
        """Test creating a voice."""
        voice = Voice(
            id="zh-CN-XiaoxiaoNeural",
            name="Xiaoxiao",
            language="zh-CN",
            provider="edge",
        )
        
        assert voice.id == "zh-CN-XiaoxiaoNeural"
        assert voice.name == "Xiaoxiao"
        assert voice.language == "zh-CN"
        assert voice.provider == "edge"
        assert voice.is_default is False
    
    def test_voice_supports_language(self):
        """Test language support check."""
        voice = Voice(
            id="zh-CN-XiaoxiaoNeural",
            name="Xiaoxiao",
            language="zh-CN",
            provider="edge",
        )
        
        assert voice.supports_language("zh-CN") is True
        assert voice.supports_language("zh") is True
        assert voice.supports_language("en") is False
    
    def test_voice_matches_filter(self):
        """Test voice filtering."""
        voice = Voice(
            id="zh-CN-XiaoxiaoNeural",
            name="Xiaoxiao",
            language="zh-CN",
            provider="edge",
            gender="Female",
        )
        
        assert voice.matches_filter(language="zh-CN") is True
        assert voice.matches_filter(gender="Female") is True
        assert voice.matches_filter(gender="Male") is False
    
    def test_voice_validation_empty_id(self):
        """Test voice validation for empty ID."""
        with pytest.raises(ValueError):
            Voice(
                id="",
                name="Xiaoxiao",
                language="zh-CN",
                provider="edge",
            )
    
    def test_voice_validation_empty_language(self):
        """Test voice validation for empty language."""
        with pytest.raises(ValueError):
            Voice(
                id="zh-CN-XiaoxiaoNeural",
                name="Xiaoxiao",
                language="",
                provider="edge",
            )


class TestAudioConfig:
    """Tests for AudioConfig entity."""
    
    def test_create_audio_config(self):
        """Test creating audio config."""
        config = AudioConfig(
            sample_rate=24000,
            bit_rate=128,
            channels=1,
        )
        
        assert config.sample_rate == 24000
        assert config.bit_rate == 128
        assert config.channels == 1
    
    def test_audio_config_from_dict(self):
        """Test creating from dictionary."""
        config = AudioConfig.from_dict({
            "sample_rate": 48000,
            "bit_rate": 256,
            "channels": 2,
        })
        
        assert config.sample_rate == 48000
        assert config.channels == 2
    
    def test_audio_config_validation_sample_rate(self):
        """Test sample rate validation."""
        with pytest.raises(ValueError):
            AudioConfig(sample_rate=1000)  # Too low
        
        with pytest.raises(ValueError):
            AudioConfig(sample_rate=96000)  # Too high


class TestOutputFormat:
    """Tests for OutputFormat enum."""
    
    def test_output_format_values(self):
        """Test output format values."""
        assert OutputFormat.MP3.value == "mp3"
        assert OutputFormat.WAV.value == "wav"
        assert OutputFormat.OGG.value == "ogg"
        assert OutputFormat.FLAC.value == "flac"
    
    def test_output_format_from_string(self):
        """Test creating from string."""
        assert OutputFormat.from_string("mp3") == OutputFormat.MP3
        assert OutputFormat.from_string("WAV") == OutputFormat.WAV
    
    def test_output_format_to_mime_type(self):
        """Test MIME type conversion."""
        assert OutputFormat.MP3.to_mime_type() == "audio/mpeg"
        assert OutputFormat.WAV.to_mime_type() == "audio/wav"


class TestSynthesisRequest:
    """Tests for SynthesisRequest entity."""
    
    def test_create_synthesis_request(self):
        """Test creating synthesis request."""
        request = SynthesisRequest(
            text="Hello, world!",
            voice="en-US-JennyNeural",
            language="en-US",
            speed=1.0,
            pitch=0,
            output_format=OutputFormat.MP3,
        )
        
        assert request.text == "Hello, world!"
        assert request.voice == "en-US-JennyNeural"
        assert request.speed == 1.0
    
    def test_synthesis_request_factory(self):
        """Test factory method."""
        request = SynthesisRequest.create(
            text="Hello!",
            voice="en-US-JennyNeural",
            language="en-US",
            speed=1.5,
            output_format="mp3",
        )
        
        assert request.output_format == OutputFormat.MP3
        assert request.speed == 1.5
    
    def test_synthesis_request_validation_empty_text(self):
        """Test validation for empty text."""
        with pytest.raises(ValueError):
            SynthesisRequest(text="")
    
    def test_synthesis_request_validation_whitespace(self):
        """Test validation for whitespace-only text."""
        with pytest.raises(ValueError):
            SynthesisRequest(text="   ")
    
    def test_synthesis_request_validation_speed(self):
        """Test validation for speed bounds."""
        with pytest.raises(ValueError):
            SynthesisRequest(text="Hello", speed=0.1)  # Too low
        
        with pytest.raises(ValueError):
            SynthesisRequest(text="Hello", speed=5.0)  # Too high
    
    def test_synthesis_request_with_defaults(self):
        """Test applying defaults."""
        request = SynthesisRequest(
            text="Hello!",
            output_format=OutputFormat.MP3,
        )
        
        request_with_defaults = request.with_defaults(
            default_voice="en-US-JennyNeural",
            default_language="en-US",
        )
        
        assert request_with_defaults.voice == "en-US-JennyNeural"
        assert request_with_defaults.language == "en-US"


class TestSynthesisResult:
    """Tests for SynthesisResult entity."""
    
    def test_create_synthesis_result(self):
        """Test creating synthesis result."""
        result = SynthesisResult(
            audio_data=b"fake_audio",
            format=OutputFormat.MP3,
            provider="edge",
        )
        
        assert result.audio_data == b"fake_audio"
        assert result.format == OutputFormat.MP3
        assert result.provider == "edge"
    
    def test_synthesis_result_properties(self):
        """Test result properties."""
        result = SynthesisResult(
            audio_data=b"fake_audio_data",
            format=OutputFormat.MP3,
        )
        
        assert result.size_bytes == 15
        assert result.content_type == "audio/mpeg"
    
    def test_synthesis_result_validation_empty_audio(self):
        """Test validation for empty audio."""
        with pytest.raises(ValueError):
            SynthesisResult(audio_data=b"", format=OutputFormat.MP3)
