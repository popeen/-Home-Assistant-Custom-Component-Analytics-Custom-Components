from __future__ import annotations
from . import common
from datetime import timedelta
from urllib import request

import urllib.request, json, asyncio
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle


MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)
SCAN_INTERVAL = timedelta(minutes=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(common.CONF_ID): cv.string
    }
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    session = async_get_clientsession(hass)
    id = hass.data[common.DOMAIN][config_entry.entry_id]
    
    async_add_entities([AnalyticsCustomComponents(id)], update_before_add=True)


async def get_data(session, id):
    """This is the data we are after"""
    pickup = []
    url = "https://analytics.home-assistant.io/custom_integrations.json"
    async with session.get(url) as resp:
        data = await resp.json()
        return data[id]


class AnalyticsCustomComponents(Entity):
    """Representation of a Sensor."""

    def __init__(self, id):
        """Initialize the sensor."""

        self._attr_unique_id = id
        self._name = "Analytics " + id
        self._state = None
        self._icon = "mdi:poll"
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def icon(self):
        """Icon to use in the frontend."""
        return self._icon

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        session = async_get_clientsession(self.hass)
        # Get all data
        data = await get_data(session, self._attr_unique_id)
        # Only use the data for the specific sensor
        self._state = data['total']
        self._attr_extra_state_attributes = data['versions']
        return None