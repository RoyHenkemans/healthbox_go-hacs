"""Select controls for Renson Healthbox Go."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity

from .const import API_TO_PROFILE, API_TO_RH, PROFILE_TO_API, RH_TO_API
from .entity import HealthboxGoEntity
from .helpers import nested, room_value


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities(
        (
            HealthboxProfileSelect(entry.runtime_data),
            HealthboxRhSelect(entry.runtime_data),
        )
    )


class HealthboxProfileSelect(HealthboxGoEntity, SelectEntity):
    _attr_translation_key = "profile"
    _attr_options = list(PROFILE_TO_API)

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "profile")

    @property
    def current_option(self):
        return API_TO_PROFILE.get(room_value(self.data, "profile"))

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_write(self.coordinator.api.set_profile, PROFILE_TO_API[option])


class HealthboxRhSelect(HealthboxGoEntity, SelectEntity):
    _attr_translation_key = "rh_sensitivity"
    _attr_options = list(RH_TO_API)

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "rh_sensitivity")
        self._optimistic_value: int | None = None

    @property
    def current_option(self):
        presets = self.data.get("sensor_presets", {})
        value = None
        if isinstance(presets, list):
            for preset in presets:
                if (
                    isinstance(preset, dict)
                    and str(preset.get("sensor_type", "")).lower() == "rh"
                ):
                    value = preset.get("sensitivity")
                    break
        elif isinstance(presets, dict):
            value = nested(presets, "sensitivity")
            if value is None:
                value = nested(presets, "rh", "sensitivity")
        if value is None:
            value = self._optimistic_value
        return API_TO_RH.get(value)

    async def async_select_option(self, option: str) -> None:
        value = RH_TO_API[option]
        await self.coordinator.async_write(self.coordinator.api.set_rh_sensitivity, value)
        self._optimistic_value = value
        self.async_write_ha_state()
