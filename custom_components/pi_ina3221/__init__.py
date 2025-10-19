"""The INA3221 Power Monitor integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_CHANNEL_1_ENABLED,
    CONF_CHANNEL_2_ENABLED,
    CONF_CHANNEL_3_ENABLED,
    CONF_I2C_ADDRESS,
    CONF_I2C_BUS,
    CONF_SHUNT_OHMS_CH1,
    CONF_SHUNT_OHMS_CH2,
    CONF_SHUNT_OHMS_CH3,
)
from .sensor import INA3221DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

DOMAIN = "pi_ina3221"
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up INA3221 Power Monitor from a config entry."""
    _LOGGER.debug("Setting up INA3221 Power Monitor integration")

    coordinator = INA3221DataUpdateCoordinator(
        hass,
        i2c_bus=entry.data[CONF_I2C_BUS],
        i2c_address=entry.data[CONF_I2C_ADDRESS],
        shunt_ohms_ch1=entry.data[CONF_SHUNT_OHMS_CH1],
        shunt_ohms_ch2=entry.data[CONF_SHUNT_OHMS_CH2],
        shunt_ohms_ch3=entry.data[CONF_SHUNT_OHMS_CH3],
        channel_1_enabled=entry.data[CONF_CHANNEL_1_ENABLED],
        channel_2_enabled=entry.data[CONF_CHANNEL_2_ENABLED],
        channel_3_enabled=entry.data[CONF_CHANNEL_3_ENABLED],
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading INA3221 Power Monitor integration")

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
