"""Silent schedule time controls for Renson Healthbox Go."""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.helpers.entity import EntityCategory

from .entity import HealthboxGoEntity
from .helpers import first_schedule_time


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities(
        (
            HealthboxSilentTime(entry.runtime_data, True),
            HealthboxSilentTime(entry.runtime_data, False),
        )
    )


class HealthboxSilentTime(HealthboxGoEntity, TimeEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, start: bool) -> None:
        super().__init__(coordinator, "silent_start" if start else "silent_end")
        self._start = start
        self._attr_translation_key = "silent_start" if start else "silent_end"

    @property
    def native_value(self) -> time | None:
        return first_schedule_time(self.data, self._start)

    async def async_set_value(self, value: time) -> None:
        formatted = value.strftime("%H:%M")
        kwargs = {"start" if self._start else "end": formatted}
        await self.coordinator.async_write(
            self.coordinator.api.set_silent, self.data.get("silent"), **kwargs
        )
