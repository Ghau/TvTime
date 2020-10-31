from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from .tvTime import TvTime
from .tv_time_client import TvTimeClient
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'tv_time'

async def async_setup(hass: HomeAssistant, hass_config: dict):
    config = hass_config.get(DOMAIN) or {}
    hass.data[DOMAIN] = {'config': config}

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry):
    data: dict = config_entry.data.copy()
    session = async_create_clientsession(hass)
    tv = TvTimeClient(session, config_entry.data['login'], config_entry.data['password'])
    await tv.login()
    data.update(tv.auth)
    hass.config_entries.async_update_entry(config_entry, data=data)
    hass.data[DOMAIN][config_entry.entry_id] = TvTime(hass, config_entry.data['login'], config_entry.data['password'])
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, 'sensor')
    )

    return True
