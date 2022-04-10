# TvTime integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Get metrics from your [TvTime](https://www.tvtime.com/) profile.

## Install

### HACS 

You can add this integration in [HACS](https://github.com/custom-components/hacs).

### Manual install

You need to copy the `tvTime` folder from this repo to the `custom_components` folder in the root of your configuration:
```
└── ...
└── configuration.yaml
└── custom_components
    └── tv_time
        └── __init__.py
        └── config_flow.py
        └── const.py
        └── manifest.json
        └── sensor.py
        └── tv_time_client.py
```

## Config

### GUI

Add new integration Congifuration -> Integration -> Tv Time
Set your email and password

### Entities
Shows
- sensor.series

     total shows with some infos in attributes
- sensor.time_spent

     total time in hours spent in series
- sensor.time_to_watch

     total time in hours see the remaining series
- sensor.watched_episodes

     total episode watched
- sensor.remaining_episodes

     total episode remaining

Other entities
- sensor.gender
- sensor.genre
- sensor.network
- sensor.average_age

Movies
- sensor.movie_time_watched
- sensor.movie_watched_count