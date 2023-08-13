from __future__ import annotations
from . import common
from typing import Any

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

import asyncio
import voluptuous as vol


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(common.CONF_ID): str
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input."""
    id = data[common.CONF_ID]

    session = async_get_clientsession(hass)
    
    try:
        url = "https://analytics.home-assistant.io/custom_integrations.json"
        async with session.get(url) as resp:
            data = (await resp.json())[id]
    except Exception:
            raise NoDataAvailable

    return {"title": id}


class ConfigFlow(config_entries.ConfigFlow, domain=common.DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except NoDataAvailable:
                errors["base"] = "no_data"
            except Exception:  # pylint: disable=broad-except
                common._LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
        
class NoDataAvailable(exceptions.HomeAssistantError):
    """Error to indicate there is no data available for the ID."""
