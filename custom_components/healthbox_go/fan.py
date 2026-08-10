"""Manual ventilation fan entity for Renson Healthbox Go."""

from __future__ import annotations

from homeassistant.components.fan import FanEntity, FanEntityFeature

from .const import API_TO_PROFILE, PROFILE_TO_API
from .entity import HealthboxGoEntity
from .helpers import current_ventilation, normal_ventilation, room_value


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([HealthboxGoFan(entry.runtime_data)])


class HealthboxGoFan(HealthboxGoEntity, FanEntity):
    """Represent the temporary/manual ventilation control."""

    _attr_translation_key = "manual_ventilation"
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_speed_count = 91
    _attr_preset_modes = list(PROFILE_TO_API)

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "manual_ventilation")

    @property
    def is_on(self) -> bool:
        return bool(room_value(self.data, "boost", "enable", default=False))

    @property
    def percentage(self) -> int | None:
        if self.is_on:
            value = room_value(self.data, "boost", "level")
        else:
            value = current_ventilation(self.data)
        try:
            return round(float(value))
        except (TypeError, ValueError):
            return None

    @property
    def preset_mode(self) -> str | None:
        """Return the automatic profile when no manual override is active."""
        if self.is_on:
            return None
        return API_TO_PROFILE.get(room_value(self.data, "profile"))

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs,
    ) -> None:
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
            return
        if percentage is None:
            percentage = round(normal_ventilation(self.data) or 30)
        # The fan UI uses the device's default manual duration (usually 15 min).
        duration = int(room_value(self.data, "boost", "default_timeout", default=900))
        duration = max(60, min(36000, duration))
        await self.coordinator.async_write(
            self.coordinator.api.set_manual_override, percentage, duration
        )

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage == 0:
            await self.async_turn_off()
            return
        await self.async_turn_on(percentage=max(10, percentage))

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_write(self.coordinator.api.stop_manual_override)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Stop a manual override and activate an automatic ventilation profile."""
        if self.is_on:
            await self.coordinator.api.stop_manual_override()
        await self.coordinator.async_write(
            self.coordinator.api.set_profile, PROFILE_TO_API[preset_mode]
        )
