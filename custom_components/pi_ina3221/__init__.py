"""The INA3221 Power Monitor integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall


from .const import (
    ATTR_I2C_ADDRESS,
    ATTR_I2C_BUS,
    ATTR_SCAN_INTERVAL,
    CONF_CHANNEL_1_ENABLED,
    CONF_CHANNEL_2_ENABLED,
    CONF_CHANNEL_3_ENABLED,
    CONF_I2C_ADDRESS,
    CONF_I2C_BUS,
    CONF_SCAN_INTERVAL,
    CONF_SHUNT_OHMS_CH1,
    CONF_SHUNT_OHMS_CH2,
    CONF_SHUNT_OHMS_CH3,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SERVICE_SET_SCAN_INTERVAL,
)
from .sensor import INA3221DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


PLATFORMS: list[Platform] = [Platform.SENSOR]

SET_SCAN_INTERVAL_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_I2C_BUS): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Required(ATTR_I2C_ADDRESS): vol.All(
            vol.Coerce(int), vol.Range(min=0x00, max=0x7F)
        ),
        vol.Required(ATTR_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=3600)
        ),
    }
)


def _get_scan_interval(entry: ConfigEntry) -> int:
    """Return scan interval from options or entry data."""
    return entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )


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
        scan_interval=_get_scan_interval(entry),
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SCAN_INTERVAL,
        async_set_scan_interval_service,
        schema=SET_SCAN_INTERVAL_SERVICE_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading INA3221 Power Monitor integration")

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle reloading when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_set_scan_interval_service(call: ServiceCall) -> None:
    """Set scan interval via service call for a specific device."""
    scan_interval = call.data[ATTR_SCAN_INTERVAL]
    i2c_bus = call.data[ATTR_I2C_BUS]
    i2c_address = call.data[ATTR_I2C_ADDRESS]

    hass = call.hass

    # Find the config entry with matching I2C bus and address
    entry = None
    for candidate_entry in hass.config_entries.async_entries(DOMAIN):
        if (
            candidate_entry.data.get(CONF_I2C_BUS) == i2c_bus
            and candidate_entry.data.get(CONF_I2C_ADDRESS) == i2c_address
        ):
            entry = candidate_entry
            break

    if entry is None:
        _LOGGER.warning(
            "No INA3221 entry found with I2C bus %d and address 0x%02X",
            i2c_bus,
            i2c_address,
        )
        return

    _LOGGER.debug(
        "Setting scan interval to %d seconds for %s",
        scan_interval,
        entry.title,
    )

    hass.config_entries.async_update_entry(
        entry, options={**entry.options, CONF_SCAN_INTERVAL: scan_interval}
    )
    await hass.config_entries.async_reload(entry.entry_id)
