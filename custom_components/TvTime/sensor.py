import logging

from datetime import timedelta
from typing import Any, Callable, Dict, Optional

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    HomeAssistantType,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, config: ConfigType, async_add_devices: Callable) -> None:
    coordinator = hass.data[DOMAIN][config.entry_id]['coordinator']

    new_devices = []
    new_devices.append(TvTimeShowSensor(coordinator, 'series', coordinator.login))
    new_devices.append(TvTimeTimeSensor(coordinator, 'time-spent', coordinator.login))
    new_devices.append(TvTimeTimeSensor(coordinator, 'time-to-watch', coordinator.login))
    new_devices.append(TvTimeEpisodeSensor(coordinator, 'watched-episodes', coordinator.login))
    new_devices.append(TvTimeEpisodeSensor(coordinator, 'remaining-episodes', coordinator.login))
    new_devices.append(TvTimeShowDetailsSensor(coordinator, 'genre', coordinator.login))
    new_devices.append(TvTimeShowDetailsSensor(coordinator, 'gender', coordinator.login))
    new_devices.append(TvTimeShowDetailsSensor(coordinator, 'network', coordinator.login))
    new_devices.append(TvTimeShowDetailsSensor(coordinator, 'average_age', coordinator.login))
    new_devices.append(TvTimeMovieTimeSensor(coordinator, 'movie_time_watched', coordinator.login))
    new_devices.append(TvTimeMovieCountSensor(coordinator, 'movie_watched_count', coordinator.login))

    async_add_devices(new_devices, update_before_add=True)

class BaseTvTimeSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, name: str, login: str):
        super().__init__(coordinator)
        self.attrs = None
        self._id = f'{login}_{name}'
        self._name = name
        self._login = login
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._id

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
    def device_info(self):
        return {
            'identifiers': {(self._login, DOMAIN)},
            'manufacturer': 'www.tvtime.com',
            'model': 'Series',
            'default_name': 'tvtime',
            'entry_type': DeviceEntryType.SERVICE,
        }

class TvTimeShowSensor(BaseTvTimeSensor):
    @property
    def unit_of_measurement(self):
        return self.name

    @callback
    def _handle_coordinator_update(self) -> None:
        data = self.coordinator.data
        info = data['info_series']
        info_details = data['info_series_details']

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
        }

        self.async_write_ha_state()


class TvTimeShowDetailsSensor(BaseTvTimeSensor):
    @property
    def unit_of_measurement(self):
        return 'year' if self.name == 'average_age' else self.name

    @callback
    def _handle_coordinator_update(self) -> None:
        data = self.coordinator.data

        info_details = data['info_series_details']

        if self.name == 'average_age':
            self._state = float(info_details[self.name])
        else:
            self._state = len(info_details[self.name])
            self.attrs = info_details[self.name]

        self.async_write_ha_state()


class TvTimeTimeSensor(BaseTvTimeSensor):
    @property
    def unit_of_measurement(self):
        return 'hours'

    @callback
    def _handle_coordinator_update(self) -> None:
        data = self.coordinator.data

        info = data['info'] if self.name == 'time-spent' else data['info_remaining']

        self._state = info['total']
        self.attrs = {'months': info['months'], 'days': info['days'], 'hours': info['hours']}

        self.async_write_ha_state()


class TvTimeEpisodeSensor(BaseTvTimeSensor):
    @property
    def unit_of_measurement(self):
        return 'episodes'

    @callback
    def _handle_coordinator_update(self) -> None:
        data = self.coordinator.data

        info = data['info'] if self.name == 'watched-episodes' else data['info_remaining']

        self._state = info['episodes']

        self.async_write_ha_state()

class TvTimeMovieTimeSensor(BaseTvTimeSensor):
    @property
    def unit_of_measurement(self):
        return 'hours'

    @callback
    def _handle_coordinator_update(self) -> None:
        data = self.coordinator.data

        self._state = data['info_movie']['time_watched']

        self.async_write_ha_state()

class TvTimeMovieCountSensor(BaseTvTimeSensor):
    @property
    def unit_of_measurement(self):
        return 'movies'

    @callback
    def _handle_coordinator_update(self) -> None:
        data = self.coordinator.data

        self._state = data['info_movie']['watched_count']

        self.async_write_ha_state()

