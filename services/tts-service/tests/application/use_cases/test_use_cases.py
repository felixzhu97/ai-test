"""Tests for application use cases."""

import pytest
from unittest.mock import AsyncMock

from src.application.use_cases import (
    SynthesizeSpeechUseCase,
    SynthesizeSpeechInput,
    StreamSpeechUseCase,
    StreamSpeechInput,
    ListVoicesUseCase,
    ListVoicesInput,
    GetHealthUseCase,
)
from src.domain.entities import SynthesisResult, OutputFormat


class TestSynthesizeSpeechUseCase:
    """Tests for SynthesizeSpeechUseCase."""
    
    @pytest.mark.asyncio
    async def test_execute_success(self, mock_provider, sample_synthesis_input):
        """Test successful synthesis."""
        use_case = SynthesizeSpeechUseCase(
            tts_provider_port=mock_provider,
            config_adapter=None,
        )
        
        result = await use_case.execute(sample_synthesis_input)
        
        assert result.audio_data == b"fake_audio_data"
        assert result.content_type == "audio/mpeg"
        assert result.filename.startswith("speech_")
        mock_provider.synthesize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_empty_text(self, mock_provider):
        """Test with empty text."""
        use_case = SynthesizeSpeechUseCase(tts_provider_port=mock_provider)
        
        with pytest.raises(ValueError, match="cannot be empty"):
            await use_case.execute(SynthesizeSpeechInput(text=""))
    
    @pytest.mark.asyncio
    async def test_execute_whitespace_text(self, mock_provider):
        """Test with whitespace-only text."""
        use_case = SynthesizeSpeechUseCase(tts_provider_port=mock_provider)
        
        with pytest.raises(ValueError, match="cannot be empty"):
            await use_case.execute(SynthesizeSpeechInput(text="   "))
    
    @pytest.mark.asyncio
    async def test_execute_text_too_long(self, mock_provider):
        """Test with text exceeding max length."""
        use_case = SynthesizeSpeechUseCase(tts_provider_port=mock_provider)
        
        long_text = "a" * 10001
        with pytest.raises(ValueError, match="exceeds maximum length"):
            await use_case.execute(SynthesizeSpeechInput(text=long_text))
    
    @pytest.mark.asyncio
    async def test_execute_with_config_defaults(self, mock_provider, mock_config_adapter, sample_synthesis_input):
        """Test with config adapter providing defaults."""
        use_case = SynthesizeSpeechUseCase(
            tts_provider_port=mock_provider,
            config_adapter=mock_config_adapter,
        )
        
        # Clear voice/language to test defaults
        input_no_voice = SynthesizeSpeechInput(
            text="Hello!",
            voice=None,
            language=None,
            speed=1.0,
            output_format="mp3",
        )
        
        result = await use_case.execute(input_no_voice)
        
        assert result.audio_data == b"fake_audio_data"
    
    @pytest.mark.asyncio
    async def test_execute_provider_error(self, mock_provider, sample_synthesis_input):
        """Test handling provider errors."""
        mock_provider.synthesize.side_effect = RuntimeError("Provider error")
        
        use_case = SynthesizeSpeechUseCase(tts_provider_port=mock_provider)
        
        with pytest.raises(RuntimeError, match="failed"):
            await use_case.execute(sample_synthesis_input)
    
    @pytest.mark.asyncio
    async def test_input_from_dto(self, sample_synthesis_input):
        """Test input creation from DTO-like object."""
        input_data = SynthesizeSpeechInput(
            text="Hello!",
            voice="en-US-JennyNeural",
            language="en-US",
            speed=1.5,
            pitch=0,
            output_format="mp3",
        )
        
        assert input_data.text == "Hello!"
        assert input_data.voice == "en-US-JennyNeural"
        assert input_data.speed == 1.5


class TestStreamSpeechUseCase:
    """Tests for StreamSpeechUseCase."""
    
    @pytest.mark.asyncio
    async def test_execute_success(self, mock_provider):
        """Test successful streaming."""
        use_case = StreamSpeechUseCase(tts_provider_port=mock_provider)
        
        input_data = StreamSpeechInput(
            text="Hello!",
            voice="en-US-JennyNeural",
            output_format="mp3",
        )
        
        # Mock the provider.stream to return an async iterator
        async def mock_stream(*args, **kwargs):
            for chunk in [b"chunk1", b"chunk2", b"chunk3"]:
                yield chunk
        
        mock_provider.stream = mock_stream
        
        chunks = []
        async for chunk in use_case.execute(input_data):
            chunks.append(chunk)
        
        assert len(chunks) == 3
        assert chunks == [b"chunk1", b"chunk2", b"chunk3"]
    
    @pytest.mark.asyncio
    async def test_execute_empty_text(self, mock_provider):
        """Test with empty text."""
        use_case = StreamSpeechUseCase(tts_provider_port=mock_provider)
        
        with pytest.raises(ValueError, match="cannot be empty"):
            async for _ in use_case.execute(StreamSpeechInput(text="")):
                pass


class TestListVoicesUseCase:
    """Tests for ListVoicesUseCase."""
    
    @pytest.mark.asyncio
    async def test_execute_all_voices(self, mock_provider, mock_voices):
        """Test listing all voices."""
        use_case = ListVoicesUseCase(tts_provider_port=mock_provider)
        
        result = await use_case.execute(ListVoicesInput())
        
        assert result.total_count == 3
        assert len(result.voices) == 3
        assert result.language_filter is None
    
    @pytest.mark.asyncio
    async def test_execute_filtered_voices(self, mock_provider, synthesis_service):
        """Test listing voices with language filter."""
        use_case = ListVoicesUseCase(
            tts_provider_port=mock_provider,
            synthesis_service=synthesis_service,  # Use synthesis service for filtering
        )
        
        result = await use_case.execute(ListVoicesInput(language="zh-CN"))
        
        assert result.total_count == 1
        assert result.voices[0].language == "zh-CN"
        assert result.language_filter == "zh-CN"
    
    @pytest.mark.asyncio
    async def test_execute_provider_error(self, mock_provider):
        """Test handling provider errors."""
        mock_provider.list_voices.side_effect = RuntimeError("Provider error")
        
        use_case = ListVoicesUseCase(tts_provider_port=mock_provider)
        
        with pytest.raises(RuntimeError, match="Failed to list voices"):
            await use_case.execute(ListVoicesInput())


class TestGetHealthUseCase:
    """Tests for GetHealthUseCase."""
    
    @pytest.mark.asyncio
    async def test_execute_healthy(self, mock_provider, mock_config_adapter):
        """Test health check when healthy."""
        use_case = GetHealthUseCase(
            tts_provider_port=mock_provider,
            config_adapter=mock_config_adapter,
        )
        
        result = await use_case.execute()
        
        assert result.status == "healthy"
        assert result.provider == "edge"
        assert result.provider_status == "healthy"
        assert result.version == "0.1.0"
    
    @pytest.mark.asyncio
    async def test_execute_degraded(self, mock_provider):
        """Test health check when degraded."""
        mock_provider.health_check = AsyncMock(return_value=False)
        
        use_case = GetHealthUseCase(tts_provider_port=mock_provider)
        
        result = await use_case.execute()
        
        assert result.status == "degraded"
        assert result.provider_status == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_execute_with_config(self, mock_provider, mock_config_adapter):
        """Test health check with config adapter."""
        use_case = GetHealthUseCase(
            tts_provider_port=mock_provider,
            config_adapter=mock_config_adapter,
        )
        
        result = await use_case.execute()
        
        assert result.status == "healthy"
        assert result.provider == "edge"
        assert result.provider_status == "healthy"
        assert "config" in result.components
        assert "cache" in result.components


# Domain entities test imports
from src.domain.entities import Voice
