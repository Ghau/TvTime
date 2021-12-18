import logging
from .tv_time_client import TvTimeClient
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.core import HomeAssistant

class TvTime():
    pair_model = None
    pair_payload = None

    def __init__(self, hass: HomeAssistant, login: str, password: str):
        self.hass = hass
        self.login = login
        self.password = password
        self._id = login

        session = async_create_clientsession(self.hass)
        self.tv = TvTimeClient(session, self.login, self.password)

    @property
    def device(self):
        return 'ok'

    @property
    def hub_id(self):
        return self._id

    def run(self):
        return

    async def get_info(self):
        return await self.tv.get_info()

    async def get_info_remaining(self):
        return await self.tv.get_info_remaining()

    async def get_info_series(self):
        return await self.tv.get_info_series()

    async def get_info_series_details(self):
        return await self.tv.get_info_series_details()
