from __future__ import annotations
from datetime import timedelta

import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.discovery import async_load_platform


from .const import APPLIANCE_DEFAULTS, DEFAULTS, DOMAIN
from .energy_controller import FVE_Controler

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER]

LOAD_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Required("type"): cv.string,
        vol.Required("min_power"): int,
        vol.Optional("max_power"): int,
        vol.Optional("step_power"): int,
        vol.Optional("power_sensor"): cv.entity_id,
        vol.Required("switch_sensor"): cv.entity_id,
        vol.Optional("static_priority"): int,
        vol.Required("availability_sensor"): cv.entity_id,
        vol.Optional("priority_sensor"): cv.entity_id,
        vol.Optional("minimal_running_minutes", default=5): int,
        vol.Optional("startup_time_minutes", default=1): int,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("fve_load_power_sensor"): cv.entity_id,
                vol.Required("fve_grid_power_sensor"): cv.entity_id,
                vol.Required("fve_pv_power_sensor"): cv.entity_id,
                vol.Required("fve_battery_power_sensor"): cv.entity_id,
                vol.Required("fve_battery_soc_sensor"): cv.entity_id,
                vol.Required("fve_battery_capacity"): int,
                vol.Optional("fve_battery_soc_min"): int,
                vol.Optional("fve_battery_max_power_in"): int,
                vol.Optional("fve_battery_max_power_out"): int,
                vol.Optional("use_forecast_solar", default=False): bool,
                vol.Optional("use_openweather", default=False): bool,
                vol.Optional("update_interval_sec", default=10): int,
                vol.Optional("decision_interval_sec", default=60): int,
                vol.Optional("history_in_minutes", default=10): int,
                vol.Optional("appliances"): vol.All(cv.ensure_list, [LOAD_SCHEMA]),
                vol.Optional("analytics", default=True): bool,
                vol.Optional("treshold_power", default=100): int,
                vol.Optional("force_stop_power", default=1000): int,
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HA Energy Control component and import YAML config if present."""

    hass.data.setdefault(DOMAIN, {})
    if DOMAIN not in config:
        return True

    conf = _normalize_config(dict(config[DOMAIN]))
    if not hass.config_entries.async_entries(DOMAIN):
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=conf,
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Energy Control from a config entry."""

    conf = _entry_config(entry)
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer="jst",
        name="HA Energy Control",
        model="HA Energy Control",
        sw_version="1.0.0",
    )
    controller = FVE_Controler(conf, hass, device_info)

    unsub_update = async_track_time_interval(
        hass,
        controller.update,
        timedelta(seconds=conf["update_interval_sec"]),
    )
    unsub_decide = async_track_time_interval(
        hass,
        controller.decide,
        timedelta(seconds=conf["decision_interval_sec"]),
    )

    hass.data[DOMAIN][entry.entry_id] = {
        "controller": controller,
        "unsubscribers": [unsub_update, unsub_decide],
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not ok:
        return False

    entry_data = hass.data[DOMAIN].pop(entry.entry_id)
    for unsub in entry_data["unsubscribers"]:
        unsub()

    return True


def _normalize_appliance(appliance: dict) -> dict:
    out = dict(APPLIANCE_DEFAULTS)
    out.update(appliance)
    return out


def _normalize_config(conf: dict) -> dict:
    out = dict(DEFAULTS)
    out.update(conf)
    out["appliances"] = [_normalize_appliance(a) for a in out.get("appliances", [])]
    return out


def _entry_config(entry: ConfigEntry) -> dict:
    merged = dict(entry.data)
    merged.update(entry.options)
    return _normalize_config(merged)

