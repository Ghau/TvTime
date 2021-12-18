# TvTime integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Get metrics from your TvTime profile.

## Install

### HACS 

You can add this integration in [HACS](https://github.com/custom-components/hacs).

### Manual install

You need to copy the `tvTime` folder from this repo to the `custom_components` folder in the root of your configuration:
```
└── ...
└── configuration.yaml
└── custom_components
    └── tvTime
        └── __init__.py
        └── config_flow.py
        └── manifest.json
        └── sensor.py
        └── tv_time_client.py
        └── tvTime.py
```

## Config

### GUI

Add new integration Congifuration -> Integration -> Tv Time
Set your email and password

## Manual

```yaml
tvTime:
  login: example@email.com
  password: BestPasswordEver
```

### Entities
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

