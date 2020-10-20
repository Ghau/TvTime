import logging
import json

from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)

BASE_URL = "api2.tozelabs.com"
USER_AGENT = "TV Time for Android 8.18.0-2020092504"
X_API_Key = "LhqxB7GE9a95beFHqiNC85GHdrX8hNi34H2uQ7QG"
APP_VERSION = "2020092504"
COUNTRY_CODE = "fr"
USER_LANG_SETTING = "en"

SIGNIN = "/v2/signin"
STATS_WATCHED = "/v2/user/{user_id}/statistics?stat_type=watched&viewer_id={user_id}&lang=fr"

class TvTimeClient:
    auth = None

    def __init__(self, session: ClientSession, email: str, password: str):
        self.session = session
        self.email = email
        self.password = password

    async def login(self):
        if self.auth:
            return True

        _LOGGER.debug(f"Tv Time Connect to https://:{BASE_URL + SIGNIN}")
        try:
            r = await self.session.post('https://' + BASE_URL + SIGNIN,
                data={'username': self.email, 'password': self.password},
                headers={
                    'User-Agent': USER_AGENT,
                    'X-API-Key': X_API_Key,
                    'host': BASE_URL,
                    'app-version': APP_VERSION,
                    'country-code': COUNTRY_CODE,
                    'user-lang-setting': USER_AGENT
                })
        except Exception as e:
            _LOGGER.exception(f"Can't login to Tv Time: {e}")
            return False

        raw = await r.read()
        resp: dict = json.loads(raw)

        _LOGGER.debug(f"Tv Time login: {resp['result']}")

        if resp['result'] != 'OK':
            _LOGGER.error(f"Can't login to Tv Time: bad Credentials")
            return False

        self.auth = {
            'user_id': resp['id'],
            'tvst_access_token': resp['tvst_access_token']
        }

        return True

    async def get_info(self):
        if self.auth == None:
            await self.login()

        try:
            r = await self.session.get('https://' + BASE_URL + STATS_WATCHED.replace('{user_id}', self.auth['user_id']),
                headers={
                    'User-Agent': USER_AGENT,
                    'X-API-Key': X_API_Key,
                    'host': BASE_URL,
                    'app-version': APP_VERSION,
                    'country-code': COUNTRY_CODE,
                    'user-lang-setting': USER_AGENT,
                    'Authorization': 'Bearer ' + self.auth['tvst_access_token']
                })
        except Exception as e:
            _LOGGER.exception(f"Can't get stats watched from Tv Time: {e}")
            return False

        raw = await r.read()
        resp: dict = json.loads(raw)

        episodes, total, months, days, hours = 0, 0, 0, 0, 0
        for stats in resp:
            if stats['name'] == 'Watched episodes':
                episodes = stats['value']
            if stats['name'] == 'Time spent':
                months = stats['nb_months']
                days = stats['nb_days']
                hours = stats['nb_hours']
                total = (months * 24 * 30) + (days * 24) + hours

        return {'total': total, 'episodes': episodes, 'months': months, 'days': days, 'hours': hours}