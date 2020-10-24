import logging

from datetime import timedelta
from typing import Any, Callable, Dict, Optional

from .tvTime import TvTime
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
    await tv.login()
    sensors = [TvTimeSensor(tv, 'time-spent'), TvTimeSensor(tv, 'watched-episodes')]
    async_add_entities(sensors, update_before_add=True)

async def async_setup_entry(hass: HomeAssistantType, config: ConfigType, async_add_devices: Callable) -> None:
    tv = hass.data['tv_time'][config.entry_id]
    new_devices = []
    new_devices.append(TvTimeSensor(tv, 'time-spent'))
    new_devices.append(TvTimeSensor(tv, 'watched-episodes'))
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
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    @property
    def unit_of_measurement(self):
        return (None, 'minutes')[self.name == 'time-spent']

    @property
    def device_info(self):
        return {
            'identifiers': {('tv_time',)},
            'manufacturer': 'www.tvtime.com',
            'model': 'Series',
            'default_name': 'tvtime',
            'entry_type': 'service',
        }

    async def async_update(self):
        try:
            info = await self.tv.get_info()

            if self.name == 'time-spent':
                self._state = info['total']
                self.attrs = {'months': info['months'], 'days': info['days'], 'hours': info['hours']}
            elif self.name == 'watched-episodes':
                self._state = info['episodes']

            self._available = True

        except Exception as e:
            _LOGGER.error(f"Error on get info {e}")
