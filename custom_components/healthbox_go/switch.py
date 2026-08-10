"""Switch controls for Renson Healthbox Go."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import EntityCategory

from .entity import HealthboxGoEntity
from .helpers import nested


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities(
        (
            HealthboxBreezeSwitch(entry.runtime_data),
            HealthboxSilentSwitch(entry.runtime_data),
        )
    )


class HealthboxBreezeSwitch(HealthboxGoEntity, SwitchEntity):
    _attr_translation_key = "breeze"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "breeze")

    @property
    def is_on(self):
        return nested(self.data.get("breeze", {}), "enable")

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_write(self.coordinator.api.set_breeze, enable=True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_write(self.coordinator.api.set_breeze, enable=False)


class HealthboxSilentSwitch(HealthboxGoEntity, SwitchEntity):
    _attr_translation_key = "silent"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "silent")

    @property
    def is_on(self):
        return nested(self.data.get("silent", {}), "enable")

    @property
    def extra_state_attributes(self):
        return {
            key: value
            for key, value in self.data.get("silent", {}).items()
            if key not in ("enable", "reduction")
        }

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_write(
            self.coordinator.api.set_silent,
            self.data.get("silent"),
            enable=True,
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_write(
            self.coordinator.api.set_silent,
            self.data.get("silent"),
            enable=False,
        )
