import voluptuous as vol

from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.config_entries import ConfigFlow

from . import DOMAIN
from .tv_time_client import TvTimeClient

class TvTimeFlowHandler(ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None, error=None):
        if user_input is not None:
            session = async_create_clientsession(self.hass)
            tv = TvTimeClient(session, user_input['login'],user_input['password'])
            if await tv.login():
                user_input.update(tv.auth)
                return self.async_create_entry(title="Tv Time", data=user_input)
            else:
                return await self.async_step_user(error='cant_login')

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required('login'): str,
                    vol.Required('password'): str
                }
            ),
            errors={'base': error} if error else None
        )