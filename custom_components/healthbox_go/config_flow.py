"""Config flow for Renson Healthbox Go."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HealthboxGoApi, HealthboxGoConnectionError, HealthboxGoError
from .const import DOMAIN


class HealthboxGoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Healthbox Go config flow."""

    VERSION = 1

    async def _validate(self, host: str):
        api = HealthboxGoApi(host, async_get_clientsession(self.hass))
        return await api.async_get_info()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                info = await self._validate(host)
            except HealthboxGoConnectionError:
                errors["base"] = "cannot_connect"
            except HealthboxGoError:
                errors["base"] = "invalid_device"
            else:
                await self.async_set_unique_id(info.serial)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(title=info.name, data={CONF_HOST: host})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=(user_input or {}).get(CONF_HOST, "")): str}
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                info = await self._validate(host)
            except HealthboxGoConnectionError:
                errors["base"] = "cannot_connect"
            except HealthboxGoError:
                errors["base"] = "invalid_device"
            else:
                await self.async_set_unique_id(info.serial)
                self._abort_if_unique_id_mismatch(reason="wrong_device")
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_HOST: host}
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, entry.data[CONF_HOST]),
                    ): str
                }
            ),
            errors=errors,
        )
