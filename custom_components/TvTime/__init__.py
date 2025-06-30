from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import Platform

from .const import DOMAIN
from .tv_time_client import TvTimeClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    data: dict = config_entry.data.copy()

    coordinator = TvTimeCoordinator(hass, config_entry.data['login'], config_entry.data['password'])
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN] = {
        config_entry.entry_id: {'coordinator': coordinator}
    }

    hass.config_entries.async_update_entry(config_entry, data=data)
    hass.async_create_task(
        await hass.config_entries.async_forward_entry_setups(config_entry, [Platform.SENSOR])
    )

    return True


class TvTimeCoordinator(DataUpdateCoordinator):
    """TvTime coordinator."""

    def __init__(self, hass: HomeAssistant, login: str, password: str):
        super().__init__(
            hass,
            _LOGGER,
            name="TvTime",
            update_interval=timedelta(minutes=10),
        )

        self.login = login
        self.password = password
        self.tv_time = TvTimeClient(async_get_clientsession(self.hass), self.login, self.password)
        self.data = {
            'info': None,
            'info_remaining': None,
            'info_series': None,
            'info_series_details': None,
            'info_movie': None,
        }

    async def _async_update_data(self):
        try:
            self.data = {
                'info': await self.tv_time.get_info(),
                'info_remaining': await self.tv_time.get_info_remaining(),
                'info_series': await self.tv_time.get_info_series(),
                'info_series_details': await self.tv_time.get_info_series_details(),
                'info_movie': await self.tv_time.get_info_movies(),
            }

            return self.data
        except Exception as e:
            _LOGGER.error(f"Error on _async_update_data {e}")
