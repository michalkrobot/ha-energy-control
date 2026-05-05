DOMAIN = "ha_energy_control"

NAME_PV_POWER = "pv_power"
NAME_LOAD_POWER = "load_power"
NAME_GRID_POWER = "grid_power"
NAME_BATTERY_POWER = "battery_power"
NAME_BATTERY_SOC = "battery_soc"

analytics_url = "https://europe-west1-fve-control.cloudfunctions.net"

DEFAULTS = {
	"fve_battery_soc_min": 20,
	"fve_battery_max_power_in": 1900,
	"fve_battery_max_power_out": 1900,
	"use_forecast_solar": False,
	"use_openweather": False,
	"update_interval_sec": 10,
	"decision_interval_sec": 60,
	"history_in_minutes": 10,
	"analytics": True,
	"treshold_power": 100,
	"force_stop_power": 1000,
	"appliances": [],
}

APPLIANCE_DEFAULTS = {
	"minimal_running_minutes": 5,
	"startup_time_minutes": 1,
	"static_priority": 0,
}

