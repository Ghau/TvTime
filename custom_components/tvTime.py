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
        try:
            await self.tv.login()
        except Exception as e:
            return False

        return await self.tv.get_info()

