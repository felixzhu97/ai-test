"""Tests for infrastructure adapters."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from src.infrastructure.adapters.edge_tts_adapter import EdgeTTSAdapter, EDGE_VOICES
from src.infrastructure.adapters.base_adapter import BaseTTSAdapter
from src.domain.entities import SynthesisRequest, OutputFormat


class TestEdgeTTSAdapter:
    """Tests for EdgeTTSAdapter."""
    
    def test_provider_name(self):
        """Test provider name."""
        adapter = EdgeTTSAdapter()
        assert adapter.provider_name == "edge"
    
    def test_list_voices(self):
        """Test listing voices."""
        adapter = EdgeTTSAdapter()
        voices = adapter._do_list_voices()
        
        assert len(voices) > 0
        assert all(v.provider == "edge" for v in voices)
    
    def test_list_voices_filtered(self):
        """Test listing voices with language filter."""
        adapter = EdgeTTSAdapter()
        voices = adapter._do_list_voices(language="zh-CN")
        
        assert len(voices) > 0
        assert all(v.language.startswith("zh") for v in voices)
    
    def test_speed_conversion(self):
        """Test speed format conversion."""
        adapter = EdgeTTSAdapter()
        
        assert adapter._speed_to_edge_rate(1.0) == "+0%"
        assert adapter._speed_to_edge_rate(1.5) == "+50%"
        assert adapter._speed_to_edge_rate(0.5) == "-50%"
    
    def test_pitch_conversion(self):
        """Test pitch format conversion."""
        adapter = EdgeTTSAdapter()
        
        # Zero pitch returns None (omit parameter)
        assert adapter._pitch_to_edge_pitch(0) is None
        # Positive pitch in Hz format
        assert adapter._pitch_to_edge_pitch(5) == "+5Hz"
        # Negative pitch in Hz format
        assert adapter._pitch_to_edge_pitch(-10) == "-10Hz"
    
    def test_speed_bounds(self):
        """Test speed bounds clamping."""
        adapter = EdgeTTSAdapter()
        
        # Below minimum (0.5 is min)
        rate = adapter._speed_to_edge_rate(0.1)
        assert rate == "-50%"  # Clamped to 0.5
        
        # Above maximum (2.0 is max)
        rate = adapter._speed_to_edge_rate(3.0)
        assert rate == "+100%"  # Clamped to 2.0 (2.0 - 1.0) * 100 = 100%
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test health check when edge-tts is available."""
        adapter = EdgeTTSAdapter()
        
        # Mock the _ensure_edge_tts to succeed
        with patch.object(adapter, '_ensure_edge_tts', return_value=MagicMock()):
            result = await adapter.health_check()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check when edge-tts is not available."""
        adapter = EdgeTTSAdapter()
        
        # Mock to raise ImportError
        with patch.object(adapter, '_ensure_edge_tts', side_effect=RuntimeError("Not installed")):
            result = await adapter.health_check()
            assert result is False


class TestBaseTTSAdapter:
    """Tests for BaseTTSAdapter."""
    
    def test_is_protocol(self):
        """Test that BaseTTSAdapter implements TTSProviderPort."""
        adapter = MagicMock(spec=BaseTTSAdapter)
        # This is a structural test - if it doesn't raise, the interface is compatible
        assert hasattr(adapter, 'provider_name')
