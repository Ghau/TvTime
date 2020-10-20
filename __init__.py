from homeassistant.core import HomeAssistant
from .tvTime import TvTime
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'tv_time'

async def async_setup(hass: HomeAssistant, hass_config: dict):
    config = hass_config.get(DOMAIN) or {}
    hass.data[DOMAIN] = {'config': config}

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry):
    hass.data[DOMAIN][config_entry.entry_id] = TvTime(hass, config_entry.data['login'], config_entry.data['password'])
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, 'sensor')
    )

    return True
