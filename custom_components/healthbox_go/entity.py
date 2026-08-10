"""Shared entity helpers."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HealthboxGoCoordinator


class HealthboxGoEntity(CoordinatorEntity[HealthboxGoCoordinator]):
    """Base entity linked to one Healthbox Go device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HealthboxGoCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.info.serial}_{key}"
        info = coordinator.info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, info.serial)},
            manufacturer="Renson",
            model=info.model,
            name=info.name,
            serial_number=info.serial,
            sw_version=info.firmware,
            hw_version=info.pcb_version,
        )

    @property
    def data(self):
        return self.coordinator.data or {}

