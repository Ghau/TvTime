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
STATS_REMAINING = "/v2/user/{user_id}/statistics?stat_type=remaining&viewer_id={user_id}&lang=fr"
STATS_SERIES = "/v2/my_shows?fields=shows.fields(id,name,stripped_name,country)"

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

    def format_data(self, data: dict):
        episodes, total, months, days, hours = 0, 0, 0, 0, 0
        for stats in data:
            if stats['name'] == 'Watched episodes' or stats['name'] == 'Remaining episodes':
                episodes = int(stats['value'])
            if stats['name'] == 'Time spent' or stats['name'] == 'Time to watch':
                months = int(stats['nb_months'])
                days = int(stats['nb_days'])
                hours = int(stats['nb_hours'])
                total = (months * 24 * 30) + (days * 24) + hours

        return {'total': total, 'episodes': episodes, 'months': months, 'days': days, 'hours': hours}

    def format_series_data(self, data: dict):
        series, not_started_yet, coming_soon, watching, up_to_date, finished, stopped_watching, for_later = 0, 0, 0, 0, 0, 0, 0, 0
        for stats in data:
            if stats['id'] == 'not_started_yet':
                not_started_yet = len(stats['shows'])
            if stats['id'] == 'coming_soon':
                coming_soon = len(stats['shows'])
            if stats['id'] == 'watching':
                watching = len(stats['shows'])
            if stats['id'] == 'up_to_date':
                up_to_date = len(stats['shows'])
            if stats['id'] == 'finished':
                finished = len(stats['shows'])
            if stats['id'] == 'stopped_watching':
                stopped_watching = len(stats['shows'])
            if stats['id'] == 'for_later':
                for_later = len(stats['shows'])

        series = not_started_yet + coming_soon + watching + up_to_date + finished + stopped_watching + for_later

        return {
            'series': series,
            'not_started_yet': not_started_yet,
            'coming_soon': coming_soon,
            'watching': watching,
            'up_to_date': up_to_date,
            'finished': finished,
            'stopped_watching': stopped_watching,
            'for_later': for_later
        }


    async def call_tv_time(self, url: str):
        if self.auth == None:
            await self.login()
        try:
            r = await self.session.get('https://' + BASE_URL + url.replace('{user_id}', self.auth['user_id']),
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

        return await r.read()

    async def get_info(self):
        raw = await self.call_tv_time(STATS_WATCHED)
        resp: dict = json.loads(raw)

        return self.format_data(resp)

    async def get_info_remaining(self):
        raw = await self.call_tv_time(STATS_REMAINING)
        resp: dict = json.loads(raw)

        return self.format_data(resp)

    async def get_info_series(self):
        raw = await self.call_tv_time(STATS_SERIES)
        resp: dict = json.loads(raw)

        return self.format_series_data(resp)