"""Sensors for Renson Healthbox Go."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.entity import EntityCategory

from .entity import HealthboxGoEntity
from .helpers import (
    constellation_index_value,
    constellation_value,
    current_ventilation,
    global_value,
    nested,
    room_value,
)

TRIGGER_OPTIONS = [
    "normal",
    "manual",
    "co2",
    "humidity",
    "voc",
    "breeze",
    "silent",
    "other",
]


@dataclass(frozen=True, kw_only=True)
class HealthboxSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


SENSORS = (
    HealthboxSensorDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: constellation_value(d, "temperature"),
    ),
    HealthboxSensorDescription(
        key="relative_humidity",
        translation_key="relative_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: constellation_value(d, "humidity"),
    ),
    HealthboxSensorDescription(
        key="absolute_humidity",
        translation_key="absolute_humidity",
        native_unit_of_measurement="g/kg",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda d: constellation_index_value(d, "sensor", "2", "humidity")
        or constellation_value(d, "absolute_humidity")
        or constellation_value(d, "humidity_absolute"),
    ),
    HealthboxSensorDescription(
        key="co2",
        translation_key="co2",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: constellation_value(d, "concentration"),
    ),
    HealthboxSensorDescription(
        key="voc_index",
        translation_key="voc_index",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: constellation_value(d, "voc_index"),
    ),
    HealthboxSensorDescription(
        key="ventilation",
        translation_key="ventilation",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=current_ventilation,
    ),
    HealthboxSensorDescription(
        key="trigger",
        translation_key="trigger",
        device_class=SensorDeviceClass.ENUM,
        options=TRIGGER_OPTIONS,
        value_fn=lambda d: _friendly_trigger(constellation_value(d, "trigger")),
    ),
    HealthboxSensorDescription(
        key="manual_remaining",
        translation_key="manual_remaining",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: room_value(d, "boost", "remaining"),
    ),
    HealthboxSensorDescription(
        key="wifi_rssi",
        translation_key="wifi_rssi",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: constellation_value(d, "rssi"),
    ),
    HealthboxSensorDescription(
        key="uptime",
        translation_key="uptime",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: nested(d.get("uptime", {}), "uptime"),
    ),
    HealthboxSensorDescription(
        key="wifi_status",
        translation_key="wifi_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: nested(d.get("wifi", {}), "status"),
    ),
    HealthboxSensorDescription(
        key="firmware",
        translation_key="firmware",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: global_value(
            d, "firmware", "firmware_version", "fw_version"
        ),
    ),
    HealthboxSensorDescription(
        key="configured",
        translation_key="configured",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: global_value(d, "configured", "configured_state"),
    ),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities(
        HealthboxGoSensor(entry.runtime_data, description) for description in SENSORS
    )


class HealthboxGoSensor(HealthboxGoEntity, SensorEntity):
    entity_description: HealthboxSensorDescription

    def __init__(self, coordinator, description) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.data)


def _friendly_trigger(value: Any) -> str | None:
    """Map firmware trigger identifiers to stable, translatable states."""
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if "voc" in normalized or "sgp40" in normalized:
        return "voc"
    if "co2" in normalized:
        return "co2"
    if any(part in normalized for part in ("humid", "h2o", "rh")):
        return "humidity"
    if any(part in normalized for part in ("boost", "manual")):
        return "manual"
    if "breeze" in normalized:
        return "breeze"
    if "silent" in normalized:
        return "silent"
    if any(part in normalized for part in ("minimum", "normal", "base")):
        return "normal"
    return "other"
