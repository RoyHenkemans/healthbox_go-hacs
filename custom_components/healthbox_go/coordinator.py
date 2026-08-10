"""Data coordinator for Renson Healthbox Go."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HealthboxGoApi, HealthboxGoError, HealthboxGoInfo
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class HealthboxGoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate polling and writes for one Healthbox."""

    def __init__(self, hass, api: HealthboxGoApi, info: HealthboxGoInfo) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{info.serial}",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api
        self.info = info

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.async_update()
        except HealthboxGoError as err:
            raise UpdateFailed(str(err)) from err

    async def async_write(self, method, *args, **kwargs) -> None:
        await method(*args, **kwargs)
        await self.async_request_refresh()

