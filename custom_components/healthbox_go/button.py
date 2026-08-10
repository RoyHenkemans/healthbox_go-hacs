"""Buttons for Renson Healthbox Go."""

from homeassistant.components.button import ButtonEntity

from .entity import HealthboxGoEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([HealthboxGoStopManualButton(entry.runtime_data)])


class HealthboxGoStopManualButton(HealthboxGoEntity, ButtonEntity):
    _attr_translation_key = "stop_manual_override"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "stop_manual_override")

    async def async_press(self) -> None:
        await self.coordinator.async_write(self.coordinator.api.stop_manual_override)

