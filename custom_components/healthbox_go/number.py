"""Number controls for Renson Healthbox Go."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import CONCENTRATION_PARTS_PER_MILLION, PERCENTAGE, UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory

from .entity import HealthboxGoEntity
from .helpers import nested, normal_ventilation, room_value


@dataclass(frozen=True, kw_only=True)
class HealthboxNumberDescription(NumberEntityDescription):
    value_fn: Callable[[dict[str, Any]], float | None]
    set_fn: str


NUMBERS = (
    HealthboxNumberDescription(
        key="normal_ventilation",
        translation_key="normal_ventilation",
        native_min_value=10,
        native_max_value=50,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        value_fn=normal_ventilation,
        set_fn="normal",
    ),
    HealthboxNumberDescription(
        key="co2_threshold",
        translation_key="co2_threshold",
        native_min_value=500,
        native_max_value=2000,
        native_step=50,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        mode=NumberMode.BOX,
        value_fn=lambda d: room_value(
            d, "demand", "CO2", "static", "maximum"
        ),
        set_fn="co2",
    ),
    HealthboxNumberDescription(
        key="breeze_threshold",
        translation_key="breeze_threshold",
        native_min_value=15,
        native_max_value=35,
        native_step=0.5,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode=NumberMode.BOX,
        value_fn=lambda d: nested(d.get("breeze", {}), "temp_threshold"),
        set_fn="breeze",
    ),
    HealthboxNumberDescription(
        key="silent_reduction",
        translation_key="silent_reduction",
        native_min_value=5,
        native_max_value=30,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda d: nested(d.get("silent", {}), "reduction"),
        set_fn="silent",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities(
        HealthboxGoNumber(entry.runtime_data, description) for description in NUMBERS
    )


class HealthboxGoNumber(HealthboxGoEntity, NumberEntity):
    entity_description: HealthboxNumberDescription

    def __init__(self, coordinator, description) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.data)

    async def async_set_native_value(self, value: float) -> None:
        api = self.coordinator.api
        if self.entity_description.set_fn == "normal":
            nominal = float(room_value(self.data, "nominal", default=60.0))
            await self.coordinator.async_write(api.set_normal_level, value, nominal)
        elif self.entity_description.set_fn == "co2":
            await self.coordinator.async_write(api.set_co2_threshold, int(value))
        elif self.entity_description.set_fn == "breeze":
            await self.coordinator.async_write(api.set_breeze, threshold=value)
        else:
            await self.coordinator.async_write(
                api.set_silent, self.data.get("silent"), reduction=value
            )
