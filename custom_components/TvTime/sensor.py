import logging

from datetime import timedelta
from typing import Any, Callable, Dict, Optional

from .tvTime import TvTime
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=10)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable
) -> None:
    tv = TvTime(hass, config['login'], config['password'])
    sensors = [
        TvTimeSensor(tv, 'time-spent'),
        TvTimeSensor(tv, 'watched-episodes'),
        TvTimeSensor(tv, 'time-to-watch'),
        TvTimeSensor(tv, 'remaining-episodes'),
        TvTimeSensor(tv, 'series')
    ]
    async_add_entities(sensors, update_before_add=True)

async def async_setup_entry(hass: HomeAssistantType, config: ConfigType, async_add_devices: Callable) -> None:
    tv = hass.data['tv_time'][config.entry_id]
    new_devices = []
    new_devices.append(TvTimeSensor(tv, 'time-spent'))
    new_devices.append(TvTimeSensor(tv, 'watched-episodes'))
    new_devices.append(TvTimeSensor(tv, 'time-to-watch'))
    new_devices.append(TvTimeSensor(tv, 'remaining-episodes'))
    new_devices.append(TvTimeSensor(tv, 'series'))
    async_add_devices(new_devices, update_before_add=True)

class TvTimeSensor(Entity):
    def __init__(self, tv: TvTime, name: str):
        super().__init__()
        self.tv = tv
        self.attrs = None
        self._name = name
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return str(self.name)

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    @property
    def unit_of_measurement(self):
        if self.name == 'time-spent' or self.name == 'time-to-watch':
            return 'hours'
        if self.name == 'watched-episodes' or self.name == 'remaining-episodes':
            return 'episodes'
        else:
            return self.name

    @property
    def device_info(self):
        return {
            'identifiers': {('tv_time',)},
            'manufacturer': 'www.tvtime.com',
            'model': 'Series',
            'default_name': 'tvtime',
            'entry_type': DeviceEntryType.SERVICE,
        }

    async def async_update(self):
        try:
            if self.name == 'time-spent' or self.name == 'watched-episodes':
                info = await self.tv.get_info()
            elif self.name == 'time-to-watch' or self.name == 'remaining-episodes':
                info = await self.tv.get_info_remaining()
            else:
                info = await self.tv.get_info_series()
                info_details = await self.tv.get_info_series_details()

            if self.name == 'time-spent' or self.name == 'time-to-watch':
                self._state = info['total']
                self.attrs = {'months': info['months'], 'days': info['days'], 'hours': info['hours']}
            elif self.name == 'watched-episodes' or self.name == 'remaining-episodes':
                self._state = info['episodes']
            else:
                self._state = info['series']
                self.attrs = {
                    'not_started_yet': info['not_started_yet'],
                    'coming_soon': info['coming_soon'],
                    'watching': info['watching'],
                    'up_to_date': info['up_to_date'],
                    'finished': info['finished'],
                    'stopped_watching': info['stopped_watching'],
                    'for_later': info['for_later'],
                    'still_production': info_details['still_production'],
                    'genre': info_details['genre'],
                    'network': info_details['network'],
                    'gender': info_details['gender'],
                    'average_age': info_details['average'],
                }

            self._available = True

        except Exception as e:
            _LOGGER.error(f"Error on get info {e}")
