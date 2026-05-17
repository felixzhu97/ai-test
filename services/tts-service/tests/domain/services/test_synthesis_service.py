"""Tests for domain services."""

import pytest
from src.domain.entities import SynthesisRequest, Voice, OutputFormat
from src.domain.services import SynthesisService


class TestSynthesisService:
    """Tests for SynthesisService."""
    
    @pytest.fixture
    def service(self) -> SynthesisService:
        """Create synthesis service."""
        return SynthesisService(
            default_voice="zh-CN-XiaoxiaoNeural",
            default_language="zh-CN",
        )
    
    def test_normalize_text_basic(self, service):
        """Test basic text normalization."""
        text = "Hello,   world!"
        normalized = service.normalize_text(text)
        
        assert normalized == "Hello, world!"
    
    def test_normalize_text_abbreviations(self, service):
        """Test abbreviation expansion."""
        text = "Dr. Smith works at U.S."
        normalized = service.normalize_text(text)
        
        assert "Doctor" in normalized
        assert "U S" in normalized
    
    def test_normalize_text_adds_punctuation(self, service):
        """Test adding period if missing."""
        text = "Hello world"
        normalized = service.normalize_text(text)
        
        assert normalized.endswith(".")
    
    def test_normalize_text_preserves_punctuation(self, service):
        """Test preserving existing punctuation."""
        text = "Hello world!"
        normalized = service.normalize_text(text)
        
        assert normalized == "Hello world!"
    
    def test_apply_defaults(self, service):
        """Test applying default values."""
        request = SynthesisRequest(
            text="Hello!",
            output_format=OutputFormat.MP3,
        )
        
        with_defaults = service.apply_defaults(request)
        
        assert with_defaults.voice == "zh-CN-XiaoxiaoNeural"
        assert with_defaults.language == "zh-CN"
    
    def test_apply_defaults_preserves_existing(self, service):
        """Test that existing values are preserved."""
        request = SynthesisRequest(
            text="Hello!",
            voice="en-US-JennyNeural",
            language="en-US",
            output_format=OutputFormat.MP3,
        )
        
        with_defaults = service.apply_defaults(request)
        
        assert with_defaults.voice == "en-US-JennyNeural"
        assert with_defaults.language == "en-US"
    
    def test_generate_cache_key(self, service):
        """Test cache key generation."""
        request = SynthesisRequest(
            text="Hello!",
            voice="zh-CN-XiaoxiaoNeural",
            language="zh-CN",
            speed=1.0,
            pitch=0,
            output_format=OutputFormat.MP3,
        )
        
        key1 = service.generate_cache_key(request, "edge")
        key2 = service.generate_cache_key(request, "edge")
        key3 = service.generate_cache_key(request, "azure")
        
        assert key1 == key2  # Same request should produce same key
        assert key1 != key3  # Different provider should produce different key
        assert len(key1) == 64  # SHA256 hex length
    
    def test_generate_ssml_azure(self, service):
        """Test SSML generation for Azure."""
        request = SynthesisRequest(
            text="Hello!",
            voice="en-US-JennyNeural",
            language="en-US",
            speed=1.0,
            pitch=0,
            output_format=OutputFormat.MP3,
        )
        
        ssml = service.generate_ssml(request, "azure")
        
        assert "<speak" in ssml
        assert "en-US" in ssml
        assert "Hello!" in ssml
        assert "100%" in ssml  # Speed as percentage
    
    def test_generate_ssml_unsupported_provider(self, service):
        """Test SSML generation for unsupported provider."""
        request = SynthesisRequest(
            text="Hello!",
            output_format=OutputFormat.MP3,
        )
        
        with pytest.raises(ValueError):
            service.generate_ssml(request, "edge")  # Edge doesn't support SSML
    
    def test_transform_speed_for_edge(self, service):
        """Test speed transformation for Edge TTS."""
        rate = service.transform_speed_for_provider(1.0, "edge")
        assert rate == "+0%"
        
        rate = service.transform_speed_for_provider(1.5, "edge")
        assert rate == "+50%"
        
        rate = service.transform_speed_for_provider(0.5, "edge")
        assert rate == "-50%"
    
    def test_transform_pitch_for_edge(self, service):
        """Test pitch transformation for Edge TTS."""
        pitch = service.transform_pitch_for_provider(0, "edge")
        assert pitch == "+0%"
        
        pitch = service.transform_pitch_for_provider(5, "edge")
        assert pitch == "+5%"
        
        pitch = service.transform_pitch_for_provider(-10, "edge")
        assert pitch == "-10%"
    
    def test_filter_voices_by_language(self, service, mock_voices):
        """Test filtering voices by language."""
        chinese_voices = service.filter_voices(mock_voices, language="zh-CN")
        
        assert len(chinese_voices) == 1
        assert chinese_voices[0].language == "zh-CN"
    
    def test_filter_voices_by_gender(self, service, mock_voices):
        """Test filtering voices by gender."""
        female_voices = service.filter_voices(mock_voices, gender="Female")
        
        assert len(female_voices) == 3  # All are female in mock
    
    def test_filter_voices_combined(self, service, mock_voices):
        """Test filtering voices by multiple criteria."""
        voices = service.filter_voices(
            mock_voices,
            language="zh-CN",
            gender="Female",
        )
        
        assert len(voices) == 1
        assert voices[0].language == "zh-CN"
    
    def test_default_properties(self, service):
        """Test default property accessors."""
        assert service.default_voice == "zh-CN-XiaoxiaoNeural"
        assert service.default_language == "zh-CN"
