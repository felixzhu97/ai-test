"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import List

from src.domain.entities import Voice, SynthesisRequest, SynthesisResult, OutputFormat
from src.domain.ports import TTSProviderPort
from src.domain.services import SynthesisService
from src.infrastructure.adapters.edge_tts_adapter import EdgeTTSAdapter
from src.application.use_cases import (
    SynthesizeSpeechUseCase,
    SynthesizeSpeechInput,
)


@pytest.fixture
def mock_voices() -> List[Voice]:
    """Create mock voice list."""
    return [
        Voice(
            id="zh-CN-XiaoxiaoNeural",
            name="Xiaoxiao",
            language="zh-CN",
            language_name="Chinese (Mandarin)",
            gender="Female",
            provider="edge",
            is_default=True,
        ),
        Voice(
            id="en-US-JennyNeural",
            name="Jenny",
            language="en-US",
            language_name="English (US)",
            gender="Female",
            provider="edge",
            is_default=False,
        ),
        Voice(
            id="ja-JP-NanamiNeural",
            name="Nanami",
            language="ja-JP",
            language_name="Japanese",
            gender="Female",
            provider="edge",
            is_default=False,
        ),
    ]


@pytest.fixture
def synthesis_service() -> SynthesisService:
    """Create synthesis service instance."""
    return SynthesisService(
        default_voice="zh-CN-XiaoxiaoNeural",
        default_language="zh-CN",
    )


@pytest.fixture
def mock_provider(mock_voices) -> MagicMock:
    """Create mock TTS provider."""
    provider = MagicMock(spec=TTSProviderPort)
    provider.provider_name = "edge"
    provider.synthesize = AsyncMock(return_value=SynthesisResult(
        audio_data=b"fake_audio_data",
        format=OutputFormat.MP3,
        provider="edge",
    ))
    provider.stream = AsyncMock(return_value=iter([b"chunk1", b"chunk2", b"chunk3"]))
    provider.list_voices = AsyncMock(return_value=mock_voices)
    provider.health_check = AsyncMock(return_value=True)
    return provider


@pytest.fixture
def mock_config_adapter() -> MagicMock:
    """Create mock config adapter."""
    config = MagicMock()
    config.get_provider_name.return_value = "edge"
    config.get_default_voice.return_value = "zh-CN-XiaoxiaoNeural"
    config.get_default_language.return_value = "zh-CN"
    config.is_cache_enabled.return_value = True
    config.get.side_effect = lambda key, default=None: {
        "azure_speech_key": None,
        "azure_speech_region": "eastus",
        "elevenlabs_api_key": None,
    }.get(key, default)
    return config


@pytest.fixture
def sample_synthesis_request() -> SynthesisRequest:
    """Create sample synthesis request."""
    return SynthesisRequest(
        text="你好，世界！",
        voice="zh-CN-XiaoxiaoNeural",
        language="zh-CN",
        speed=1.0,
        pitch=0,
        output_format=OutputFormat.MP3,
    )


@pytest.fixture
def sample_synthesis_input() -> SynthesizeSpeechInput:
    """Create sample synthesis input."""
    return SynthesizeSpeechInput(
        text="Hello, world!",
        voice="en-US-JennyNeural",
        language="en-US",
        speed=1.0,
        pitch=0,
        output_format="mp3",
    )
