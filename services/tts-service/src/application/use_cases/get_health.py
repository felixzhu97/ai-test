"""Get Health Use Case.

This use case checks the health status of the TTS service and its dependencies.
"""

from dataclasses import dataclass
from typing import Dict

from ..dtos import HealthResponseDTO


@dataclass(frozen=True)
class GetHealthOutput:
    """Output value object for health check use case."""
    status: str
    provider: str
    provider_status: str
    version: str
    components: Dict[str, str]

    def to_dto(self) -> HealthResponseDTO:
        """Convert to response DTO."""
        return HealthResponseDTO(
            status=self.status,
            provider=self.provider,
            provider_status=self.provider_status,
            version=self.version,
            components=self.components,
        )


class GetHealthUseCase:
    """Use case for checking service health.
    
    Responsibilities:
    - Check provider health
    - Aggregate component statuses
    - Determine overall service status
    """
    
    SERVICE_VERSION = "0.1.0"
    
    def __init__(self, tts_provider_port, config_adapter=None):
        """Initialize use case with dependencies.
        
        Args:
            tts_provider_port: TTS provider port implementation
            config_adapter: Optional configuration adapter for provider name
        """
        self._provider = tts_provider_port
        self._config = config_adapter

    async def execute(self) -> GetHealthOutput:
        """Execute health check use case.
        
        Returns:
            GetHealthOutput with health status and component details
        """
        components = {}
        provider_name = "unknown"
        provider_status = "unknown"
        overall_status = "healthy"
        
        # Get provider name from config
        if self._config:
            provider_name = self._config.get_provider_name()
            components["config"] = "healthy"
        else:
            components["config"] = "unavailable"
        
        # Check provider health
        try:
            provider_healthy = await self._provider.health_check()
            provider_status = "healthy" if provider_healthy else "unhealthy"
            components["provider"] = provider_status
            
            if not provider_healthy:
                overall_status = "degraded"
        except Exception as e:
            provider_status = "error"
            components["provider"] = f"error: {str(e)}"
            overall_status = "unhealthy"
        
        # Check cache if enabled
        if self._config and self._config.is_cache_enabled():
            components["cache"] = "enabled"
        else:
            components["cache"] = "disabled"
        
        return GetHealthOutput(
            status=overall_status,
            provider=provider_name,
            provider_status=provider_status,
            version=self.SERVICE_VERSION,
            components=components,
        )
