"""Config flow for INA3221 Power Monitor integration."""

from __future__ import annotations

import logging
from typing import Any

from adafruit_ina3221 import INA3221
import board
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_CHANNEL_1_ENABLED,
    CONF_CHANNEL_2_ENABLED,
    CONF_CHANNEL_3_ENABLED,
    CONF_I2C_ADDRESS,
    CONF_I2C_BUS,
    CONF_SHUNT_OHMS_CH1,
    CONF_SHUNT_OHMS_CH2,
    CONF_SHUNT_OHMS_CH3,
    DEFAULT_CHANNEL_ENABLED,
    DEFAULT_I2C_ADDRESS,
    DEFAULT_I2C_BUS,
    DEFAULT_SHUNT_OHMS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_I2C_BUS, default=DEFAULT_I2C_BUS): int,
        vol.Required(CONF_I2C_ADDRESS, default=DEFAULT_I2C_ADDRESS): vol.All(
            vol.Coerce(int), vol.Range(min=0x00, max=0x7F)
        ),
        vol.Required(CONF_SHUNT_OHMS_CH1, default=DEFAULT_SHUNT_OHMS): vol.All(
            vol.Coerce(float), vol.Range(min=0.001, max=1.0)
        ),
        vol.Required(CONF_SHUNT_OHMS_CH2, default=DEFAULT_SHUNT_OHMS): vol.All(
            vol.Coerce(float), vol.Range(min=0.001, max=1.0)
        ),
        vol.Required(CONF_SHUNT_OHMS_CH3, default=DEFAULT_SHUNT_OHMS): vol.All(
            vol.Coerce(float), vol.Range(min=0.001, max=1.0)
        ),
        vol.Required(CONF_CHANNEL_1_ENABLED, default=DEFAULT_CHANNEL_ENABLED): bool,
        vol.Required(CONF_CHANNEL_2_ENABLED, default=DEFAULT_CHANNEL_ENABLED): bool,
        vol.Required(CONF_CHANNEL_3_ENABLED, default=DEFAULT_CHANNEL_ENABLED): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    i2c_bus = data[CONF_I2C_BUS]
    i2c_address = data[CONF_I2C_ADDRESS]

    # Test if we can initialize the INA3221
    def _test_connection():
        try:
            # Get I2C bus using busio
            import busio
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Determine which channels to enable
            enabled_channels = []
            if data[CONF_CHANNEL_1_ENABLED]:
                enabled_channels.append(0)
            if data[CONF_CHANNEL_2_ENABLED]:
                enabled_channels.append(1)
            if data[CONF_CHANNEL_3_ENABLED]:
                enabled_channels.append(2)
            
            # Initialize INA3221
            ina = INA3221(i2c, address=i2c_address, enable=enabled_channels)
            
            # Set shunt resistances for each channel
            ina.channels[0].shunt_resistance = data[CONF_SHUNT_OHMS_CH1]
            ina.channels[1].shunt_resistance = data[CONF_SHUNT_OHMS_CH2]
            ina.channels[2].shunt_resistance = data[CONF_SHUNT_OHMS_CH3]
            
            # Try to read voltage from an enabled channel to verify connection
            for channel_idx in enabled_channels:
                ina[channel_idx].bus_voltage
                break
            
            return True
        except Exception as err:
            _LOGGER.error("Failed to connect to INA3221: %s", err)
            raise CannotConnect from err

    await hass.async_add_executor_job(_test_connection)

    # Return info that you want to store in the config entry.
    return {"title": f"INA3221 (0x{i2c_address:02X})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for INA3221 Power Monitor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on I2C address
                await self.async_set_unique_id(
                    f"{user_input[CONF_I2C_BUS]}_{user_input[CONF_I2C_ADDRESS]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
