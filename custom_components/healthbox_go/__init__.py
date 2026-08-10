"""Renson Healthbox Go integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HealthboxGoApi, HealthboxGoError
from .const import DOMAIN, PLATFORMS
from .coordinator import HealthboxGoCoordinator

HealthboxGoConfigEntry = ConfigEntry[HealthboxGoCoordinator]

SERVICE_MANUAL = "set_manual_override"
SERVICE_STOP_MANUAL = "stop_manual_override"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration-level actions."""
    await _async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: HealthboxGoConfigEntry) -> bool:
    """Set up a Healthbox Go from a config entry."""
    api = HealthboxGoApi(entry.data[CONF_HOST], async_get_clientsession(hass))
    try:
        info = await api.async_get_info()
    except HealthboxGoError as err:
        raise ConfigEntryNotReady(str(err)) from err

    coordinator = HealthboxGoCoordinator(hass, api, info)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: HealthboxGoConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unloaded


async def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_MANUAL):
        return

    async def coordinator_for_call(call: ServiceCall) -> HealthboxGoCoordinator:
        device_id = call.data["device_id"]
        device = dr.async_get(hass).async_get(device_id)
        if device is None:
            raise HomeAssistantError("Healthbox Go device not found")
        entry_ids = set(device.config_entries)
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.entry_id in entry_ids and entry.runtime_data:
                return entry.runtime_data
        raise HomeAssistantError("Healthbox Go device is not loaded")

    async def set_manual(call: ServiceCall) -> None:
        coordinator = await coordinator_for_call(call)
        await coordinator.async_write(
            coordinator.api.set_manual_override,
            call.data["percentage"],
            call.data["duration"],
        )

    async def stop_manual(call: ServiceCall) -> None:
        coordinator = await coordinator_for_call(call)
        await coordinator.async_write(coordinator.api.stop_manual_override)

    hass.services.async_register(
        DOMAIN,
        SERVICE_MANUAL,
        set_manual,
        schema=vol.Schema(
            {
                vol.Required("device_id"): str,
                vol.Required("percentage"): vol.All(vol.Coerce(float), vol.Range(min=10, max=100)),
                vol.Required("duration"): vol.All(vol.Coerce(int), vol.Range(min=60, max=36000)),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_MANUAL,
        stop_manual,
        schema=vol.Schema({vol.Required("device_id"): cv.string}),
    )
