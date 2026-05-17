"""Voice entity - represents a TTS voice."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Voice:
    """Represents a TTS voice available from a provider.
    
    Voice is a value object that identifies a specific voice
    configuration offered by a TTS provider.
    
    Attributes:
        id: Unique identifier for the voice (e.g., 'zh-CN-XiaoxiaoNeural')
        name: Human-readable name (e.g., 'Xiaoxiao')
        language: Language code (e.g., 'zh-CN')
        language_name: Full language name (e.g., 'Chinese (Mandarin)')
        gender: Voice gender ('Male', 'Female', or None)
        provider: Provider identifier (e.g., 'azure', 'edge')
        is_default: Whether this is the default voice for the provider
    """
    id: str
    name: str
    language: str
    provider: str
    language_name: Optional[str] = None
    gender: Optional[str] = None
    is_default: bool = False
    
    def __post_init__(self):
        """Validate voice attributes after initialization."""
        if not self.id:
            raise ValueError("Voice ID cannot be empty")
        if not self.language:
            raise ValueError("Voice language cannot be empty")
    
    def supports_language(self, language_code: str) -> bool:
        """Check if this voice supports the given language.
        
        Args:
            language_code: Language code to check (e.g., 'zh-CN', 'en')
            
        Returns:
            True if the voice supports the language
        """
        return self.language.lower().startswith(language_code.lower())
    
    def matches_filter(self, language: Optional[str] = None, gender: Optional[str] = None) -> bool:
        """Check if voice matches optional filter criteria.
        
        Args:
            language: Optional language filter
            gender: Optional gender filter
            
        Returns:
            True if voice matches all specified filters
        """
        if language and not self.supports_language(language):
            return False
        if gender and self.gender != gender:
            return False
        return True
