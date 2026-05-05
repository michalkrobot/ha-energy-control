"""Config flow for HA Energy Control."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import APPLIANCE_DEFAULTS, DEFAULTS, DOMAIN


def _base_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                "fve_load_power_sensor",
                default=defaults.get("fve_load_power_sensor"),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                "fve_grid_power_sensor",
                default=defaults.get("fve_grid_power_sensor"),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                "fve_pv_power_sensor",
                default=defaults.get("fve_pv_power_sensor"),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                "fve_battery_power_sensor",
                default=defaults.get("fve_battery_power_sensor"),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                "fve_battery_soc_sensor",
                default=defaults.get("fve_battery_soc_sensor"),
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                "fve_battery_capacity",
                default=defaults.get("fve_battery_capacity", 0),
            ): int,
            vol.Optional(
                "fve_battery_soc_min",
                default=defaults.get("fve_battery_soc_min", DEFAULTS["fve_battery_soc_min"]),
            ): int,
            vol.Optional(
                "fve_battery_max_power_in",
                default=defaults.get(
                    "fve_battery_max_power_in", DEFAULTS["fve_battery_max_power_in"]
                ),
            ): int,
            vol.Optional(
                "fve_battery_max_power_out",
                default=defaults.get(
                    "fve_battery_max_power_out", DEFAULTS["fve_battery_max_power_out"]
                ),
            ): int,
            vol.Optional(
                "use_forecast_solar",
                default=defaults.get("use_forecast_solar", DEFAULTS["use_forecast_solar"]),
            ): bool,
            vol.Optional(
                "use_openweather",
                default=defaults.get("use_openweather", DEFAULTS["use_openweather"]),
            ): bool,
            vol.Optional(
                "update_interval_sec",
                default=defaults.get("update_interval_sec", DEFAULTS["update_interval_sec"]),
            ): int,
            vol.Optional(
                "decision_interval_sec",
                default=defaults.get(
                    "decision_interval_sec", DEFAULTS["decision_interval_sec"]
                ),
            ): int,
            vol.Optional(
                "history_in_minutes",
                default=defaults.get("history_in_minutes", DEFAULTS["history_in_minutes"]),
            ): int,
            vol.Optional(
                "analytics",
                default=defaults.get("analytics", DEFAULTS["analytics"]),
            ): bool,
            vol.Optional(
                "treshold_power",
                default=defaults.get("treshold_power", DEFAULTS["treshold_power"]),
            ): int,
            vol.Optional(
                "force_stop_power",
                default=defaults.get("force_stop_power", DEFAULTS["force_stop_power"]),
            ): int,
        }
    )


def _appliance_schema(defaults: dict | None = None) -> vol.Schema:
    values = dict(APPLIANCE_DEFAULTS)
    values.update(defaults or {})
    return vol.Schema(
        {
            vol.Required("name", default=values.get("name", "")): str,
            vol.Required("type", default=values.get("type", "constant_load")): vol.In(
                ["constant_load", "wallbox"]
            ),
            vol.Required("min_power", default=values.get("min_power", 0)): int,
            vol.Optional("max_power", default=values.get("max_power")): vol.Any(int, None),
            vol.Optional("step_power", default=values.get("step_power")): vol.Any(int, None),
            vol.Optional("power_sensor", default=values.get("power_sensor")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(
                "switch_sensor",
                default=values.get("switch_sensor", ""),
            ): selector.EntitySelector(selector.EntitySelectorConfig()),
            vol.Required(
                "availability_sensor",
                default=values.get("availability_sensor", ""),
            ): selector.EntitySelector(selector.EntitySelectorConfig()),
            vol.Optional(
                "static_priority",
                default=values.get("static_priority", APPLIANCE_DEFAULTS["static_priority"]),
            ): int,
            vol.Optional("priority_sensor", default=values.get("priority_sensor")): selector.EntitySelector(
                selector.EntitySelectorConfig()
            ),
            vol.Optional(
                "minimal_running_minutes",
                default=values.get(
                    "minimal_running_minutes", APPLIANCE_DEFAULTS["minimal_running_minutes"]
                ),
            ): int,
            vol.Optional(
                "startup_time_minutes",
                default=values.get(
                    "startup_time_minutes", APPLIANCE_DEFAULTS["startup_time_minutes"]
                ),
            ): int,
        }
    )


class FVEControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Energy Control."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        return FVEControlOptionsFlow(config_entry)

    def __init__(self) -> None:
        self._base_config: dict = {}
        self._appliances: list[dict] = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            self._base_config = dict(DEFAULTS)
            self._base_config.update(user_input)
            self._appliances = []
            return await self.async_step_appliances()

        return self.async_show_form(
            step_id="user",
            data_schema=_base_schema(DEFAULTS),
        )

    async def async_step_appliances(self, user_input=None):
        """Show appliance action selector."""
        if user_input is not None:
            if user_input["action"] == "add_appliance":
                return await self.async_step_add_appliance()
            return await self.async_step_finish()

        return self.async_show_form(
            step_id="appliances",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        {
                            "add_appliance": "Add appliance",
                            "finish": "Finish setup",
                        }
                    )
                }
            ),
        )

    async def async_step_add_appliance(self, user_input=None):
        """Add one appliance definition."""
        if user_input is not None:
            appliance = dict(APPLIANCE_DEFAULTS)
            appliance.update(user_input)
            self._appliances.append(appliance)
            return await self.async_step_appliances()

        return self.async_show_form(
            step_id="add_appliance",
            data_schema=_appliance_schema(),
        )

    async def async_step_finish(self, user_input=None):
        """Create the final config entry."""
        data = dict(self._base_config)
        data["appliances"] = self._appliances
        return self.async_create_entry(title="HA Energy Control", data=data)

    async def async_step_import(self, import_data):
        """Handle YAML import."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        data = dict(DEFAULTS)
        data.update(import_data)
        data["appliances"] = [
            {**APPLIANCE_DEFAULTS, **appliance}
            for appliance in data.get("appliances", [])
        ]
        return self.async_create_entry(title="HA Energy Control", data=data)


class FVEControlOptionsFlow(config_entries.OptionsFlowWithReload):
    """Handle options for HA Energy Control."""

    def __init__(self, config_entry) -> None:
        self._entry = config_entry
        self._data = dict(DEFAULTS)
        self._data.update(config_entry.data)
        self._data.update(config_entry.options)
        self._appliances = list(self._data.get("appliances", []))
        self._selected_appliance_idx: int | None = None

    async def async_step_init(self, user_input=None):
        """Main options action selector."""
        if user_input is not None:
            action = user_input["action"]
            if action == "edit_base":
                return await self.async_step_edit_base()
            if action == "manage_appliances":
                return await self.async_step_manage_appliances()
            return await self.async_step_finish()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        {
                            "edit_base": "Edit base settings",
                            "manage_appliances": "Manage appliances",
                            "finish": "Save and reload",
                        }
                    )
                }
            ),
        )

    async def async_step_edit_base(self, user_input=None):
        """Edit base integration settings."""
        if user_input is not None:
            for key, value in user_input.items():
                self._data[key] = value
            return await self.async_step_init()

        return self.async_show_form(
            step_id="edit_base",
            data_schema=_base_schema(self._data),
        )

    async def async_step_manage_appliances(self, user_input=None):
        """Manage appliance list actions."""
        if user_input is not None:
            action = user_input["action"]
            if action == "options_add_appliance":
                return await self.async_step_options_add_appliance()
            if action == "options_edit_appliance":
                return await self.async_step_options_edit_appliance()
            if action == "options_remove_appliance":
                return await self.async_step_options_remove_appliance()
            if action == "options_clear_appliances":
                return await self.async_step_options_clear_appliances()
            return await self.async_step_init()

        return self.async_show_form(
            step_id="manage_appliances",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        {
                            "options_add_appliance": "Add appliance",
                            "options_edit_appliance": "Edit appliance",
                            "options_remove_appliance": "Remove appliance",
                            "options_clear_appliances": "Clear all appliances",
                            "init": "Back",
                        }
                    )
                }
            ),
        )

    async def async_step_options_add_appliance(self, user_input=None):
        """Add one appliance from options flow."""
        if user_input is not None:
            appliance = dict(APPLIANCE_DEFAULTS)
            appliance.update(user_input)
            self._appliances.append(appliance)
            return await self.async_step_manage_appliances()

        return self.async_show_form(
            step_id="options_add_appliance",
            data_schema=_appliance_schema(),
            description_placeholders={"count": str(len(self._appliances))},
        )

    async def async_step_options_remove_appliance(self, user_input=None):
        """Remove appliance by name."""
        options_map = _appliance_choice_map(self._appliances)
        if not options_map:
            return await self.async_step_manage_appliances()

        if user_input is not None:
            idx = int(user_input["appliance"])
            if 0 <= idx < len(self._appliances):
                self._appliances.pop(idx)
            return await self.async_step_manage_appliances()

        return self.async_show_form(
            step_id="options_remove_appliance",
            data_schema=vol.Schema(
                {vol.Required("appliance"): vol.In(options_map)}
            ),
            description_placeholders={"count": str(len(self._appliances))},
        )

    async def async_step_options_edit_appliance(self, user_input=None):
        """Pick appliance to edit."""
        options_map = _appliance_choice_map(self._appliances)
        if not options_map:
            return await self.async_step_manage_appliances()

        if user_input is not None:
            idx = int(user_input["appliance"])
            if 0 <= idx < len(self._appliances):
                self._selected_appliance_idx = idx
                return await self.async_step_options_edit_appliance_values()
            return await self.async_step_manage_appliances()

        return self.async_show_form(
            step_id="options_edit_appliance",
            data_schema=vol.Schema(
                {vol.Required("appliance"): vol.In(options_map)}
            ),
            description_placeholders={"count": str(len(self._appliances))},
        )

    async def async_step_options_edit_appliance_values(self, user_input=None):
        """Edit selected appliance values."""
        idx = self._selected_appliance_idx
        if idx is None or idx < 0 or idx >= len(self._appliances):
            return await self.async_step_manage_appliances()

        current = self._appliances[idx]
        if user_input is not None:
            updated = dict(APPLIANCE_DEFAULTS)
            updated.update(user_input)
            self._appliances[idx] = updated
            self._selected_appliance_idx = None
            return await self.async_step_manage_appliances()

        return self.async_show_form(
            step_id="options_edit_appliance_values",
            data_schema=_appliance_schema(current),
            description_placeholders={"name": str(current.get("name", ""))},
        )

    async def async_step_options_clear_appliances(self, user_input=None):
        """Clear all appliances from options."""
        if user_input is not None:
            if user_input.get("confirm"):
                self._appliances = []
            return await self.async_step_manage_appliances()

        return self.async_show_form(
            step_id="options_clear_appliances",
            data_schema=vol.Schema({vol.Required("confirm", default=False): bool}),
            description_placeholders={"count": str(len(self._appliances))},
        )

    async def async_step_finish(self, user_input=None):
        """Store options and reload entry."""
        options = dict(self._data)
        options["appliances"] = self._appliances
        return self.async_create_entry(title="", data=options)


def _appliance_choice_map(appliances: list[dict]) -> dict[str, str]:
    out: dict[str, str] = {}
    for idx, item in enumerate(appliances):
        name = str(item.get("name", f"appliance_{idx}"))
        kind = str(item.get("type", "unknown"))
        out[str(idx)] = f"{idx + 1}. {name} ({kind})"
    return out
