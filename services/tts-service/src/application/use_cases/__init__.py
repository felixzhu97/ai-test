"""Use cases for TTS Application Layer.

Each use case is a single, focused business operation that orchestrates
domain objects and infrastructure to achieve a specific goal.
"""

from .synthesize_speech import (
    SynthesizeSpeechUseCase,
    SynthesizeSpeechInput,
    SynthesizeSpeechOutput,
)
from .stream_speech import StreamSpeechUseCase, StreamSpeechInput
from .list_voices import ListVoicesUseCase, ListVoicesInput, ListVoicesOutput
from .get_health import GetHealthUseCase, GetHealthOutput

__all__ = [
    # Synthesize Speech
    "SynthesizeSpeechUseCase",
    "SynthesizeSpeechInput",
    "SynthesizeSpeechOutput",
    # Stream Speech
    "StreamSpeechUseCase",
    "StreamSpeechInput",
    # List Voices
    "ListVoicesUseCase",
    "ListVoicesInput",
    "ListVoicesOutput",
    # Get Health
    "GetHealthUseCase",
    "GetHealthOutput",
]
