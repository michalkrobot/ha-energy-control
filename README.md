# HA Energy Control

Custom Home Assistant integration for photovoltaic surplus load control with full UI configuration support.

## Included in this repository

This repository contains a Home Assistant custom integration in `custom_components/ha_energy_control`.

Features:
- setup through Home Assistant UI (Config Flow)
- options flow for post-install changes
- appliance management directly in UI
- YAML import path for migration scenarios

## Install via HACS

1. Open HACS.
2. Go to `Custom repositories`.
3. Add `https://github.com/michalkrobot/ha-energy-control` as type `Integration`.
4. Install `HA Energy Control`.
5. Restart Home Assistant.
6. Go to `Settings -> Devices & Services -> Add Integration`.
7. Add `HA Energy Control`.

## Manual installation

Copy `custom_components/ha_energy_control` to your Home Assistant config directory under `custom_components`.

Resulting structure:

```text
config/
  custom_components/
    ha_energy_control/
      __init__.py
      config_flow.py
      const.py
      energy_appliance.py
      energy_appliance_decision.py
      energy_controller.py
      manifest.json
      number.py
      sensor.py
      strings.json
```

Then restart Home Assistant and add the integration in the UI.

## HACS publishing notes

- Keep `hacs.json` in repository root.
- Keep integration in `custom_components/ha_energy_control`.
- Publish GitHub releases for stable version tracking in HACS.
