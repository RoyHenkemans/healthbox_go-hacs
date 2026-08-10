"""Binary sensors for Renson Healthbox Go."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.entity import EntityCategory

from .entity import HealthboxGoEntity
from .helpers import constellation_index_value, room_value


@dataclass(frozen=True, kw_only=True)
class HealthboxBinaryDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSORS = (
    HealthboxBinaryDescription(
        key="manual_override",
        translation_key="manual_override",
        value_fn=lambda d: bool(
            room_value(d, "boost", "enable", default=False)
        ),
    ),
    HealthboxBinaryDescription(
        key="co2_error",
        translation_key="co2_error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: _problem_value(d, "error_condition"),
    ),
    HealthboxBinaryDescription(
        key="co2_flash_error",
        translation_key="co2_flash_error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: _problem_value(d, "flash_error"),
    ),
    HealthboxBinaryDescription(
        key="co2_calibration_error",
        translation_key="co2_calibration_error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: _problem_value(d, "calibration_error"),
    ),
)


def _problem_value(data: dict[str, Any], parameter: str) -> bool | None:
    value = constellation_index_value(data, "sensor", "3", parameter)
    if value is None:
        return None
    return value not in (False, 0, "0", "None", "none", "OK", "ok")


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities(
        HealthboxGoBinarySensor(entry.runtime_data, description)
        for description in BINARY_SENSORS
    )


class HealthboxGoBinarySensor(HealthboxGoEntity, BinarySensorEntity):
    entity_description: HealthboxBinaryDescription

    def __init__(self, coordinator, description) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self):
        return self.entity_description.value_fn(self.data)
