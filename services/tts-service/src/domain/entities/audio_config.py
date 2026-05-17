"""Audio configuration entity."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioConfig:
    """Configuration for audio output.
    
    Attributes:
        sample_rate: Audio sample rate in Hz (8000-48000)
        bit_rate: Audio bit rate in kbps
        channels: Number of audio channels (1=mono, 2=stereo)
    """
    sample_rate: int = 24000
    bit_rate: int = 128
    channels: int = 1
    
    def __post_init__(self):
        """Validate audio configuration after initialization."""
        if not 8000 <= self.sample_rate <= 48000:
            raise ValueError(f"Sample rate must be between 8000 and 48000 Hz, got {self.sample_rate}")
        if self.channels < 1:
            raise ValueError(f"Channels must be at least 1, got {self.channels}")
    
    @classmethod
    def from_dict(cls, data: dict) -> "AudioConfig":
        """Create AudioConfig from dictionary.
        
        Args:
            data: Dictionary with audio configuration
            
        Returns:
            AudioConfig instance
        """
        return cls(
            sample_rate=data.get("sample_rate", 24000),
            bit_rate=data.get("bit_rate", 128),
            channels=data.get("channels", 1),
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with audio configuration
        """
        return {
            "sample_rate": self.sample_rate,
            "bit_rate": self.bit_rate,
            "channels": self.channels,
        }
