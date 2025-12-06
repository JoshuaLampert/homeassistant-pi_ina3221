"""Sensor platform for INA3221 Power Monitor."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_CHANNEL_1_ENABLED,
    CONF_CHANNEL_2_ENABLED,
    CONF_CHANNEL_3_ENABLED,
    CONF_SCAN_INTERVAL,
    CONF_SHUNT_OHMS_CH1,
    CONF_SHUNT_OHMS_CH2,
    CONF_SHUNT_OHMS_CH3,
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up INA3221 sensor from a config entry."""
    coordinator: INA3221DataUpdateCoordinator = config_entry.runtime_data

    entities = []

    # Add sensors for each enabled channel
    if config_entry.data[CONF_CHANNEL_1_ENABLED]:
        entities.extend([
            INA3221VoltageSensor(coordinator, config_entry, 0),
            INA3221CurrentSensor(coordinator, config_entry, 0),
            INA3221PowerSensor(coordinator, config_entry, 0),
        ])

    if config_entry.data[CONF_CHANNEL_2_ENABLED]:
        entities.extend([
            INA3221VoltageSensor(coordinator, config_entry, 1),
            INA3221CurrentSensor(coordinator, config_entry, 1),
            INA3221PowerSensor(coordinator, config_entry, 1),
        ])

    if config_entry.data[CONF_CHANNEL_3_ENABLED]:
        entities.extend([
            INA3221VoltageSensor(coordinator, config_entry, 2),
            INA3221CurrentSensor(coordinator, config_entry, 2),
            INA3221PowerSensor(coordinator, config_entry, 2),
        ])

    async_add_entities(entities)


class INA3221DataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching INA3221 data."""

    def __init__(
        self,
        hass: HomeAssistant,
        i2c_bus: int,
        i2c_address: int,
        shunt_ohms_ch1: float,
        shunt_ohms_ch2: float,
        shunt_ohms_ch3: float,
        channel_1_enabled: bool,
        channel_2_enabled: bool,
        channel_3_enabled: bool,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="INA3221 Power Monitor",
            update_interval=timedelta(
                seconds=scan_interval or DEFAULT_SCAN_INTERVAL
            ),
        )
        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self.shunt_ohms_ch1 = shunt_ohms_ch1
        self.shunt_ohms_ch2 = shunt_ohms_ch2
        self.shunt_ohms_ch3 = shunt_ohms_ch3
        self.channel_1_enabled = channel_1_enabled
        self.channel_2_enabled = channel_2_enabled
        self.channel_3_enabled = channel_3_enabled

        self._ina = None
        self._i2c = None

    def _init_sensor(self) -> None:
        """Initialize the INA3221 sensor."""
        if self._ina is None:
            # Import our pure Python INA3221 driver
            from .ina3221 import INA3221

            # Initialize INA3221 with shunt resistor values
            self._ina = INA3221(
                i2c_bus=self.i2c_bus,
                address=self.i2c_address,
                shunt_resistors=(
                    self.shunt_ohms_ch1,
                    self.shunt_ohms_ch2,
                    self.shunt_ohms_ch3,
                ),
            )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from INA3221."""
        return await self.hass.async_add_executor_job(self._update_data)

    def _update_data(self) -> dict[str, Any]:
        """Fetch data from INA3221 (runs in executor)."""
        try:
            self._init_sensor()

            data = {}

            # Read data from each enabled channel
            for channel_idx in range(3):
                channel_enabled = [
                    self.channel_1_enabled,
                    self.channel_2_enabled,
                    self.channel_3_enabled,
                ][channel_idx]

                if channel_enabled:
                    # Read channel data (channels are numbered 1, 2, 3 in our driver)
                    channel_data = self._ina.read_channel(channel_idx + 1)

                    voltage = channel_data["voltage"]  # in Volts
                    current = channel_data["current"]  # in Amperes
                    power = channel_data["power"]  # in Watts

                    data[f"ch{channel_idx + 1}_voltage"] = voltage
                    data[f"ch{channel_idx + 1}_current"] = current
                    data[f"ch{channel_idx + 1}_power"] = power

            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with INA3221: {err}") from err


class INA3221SensorBase(CoordinatorEntity[INA3221DataUpdateCoordinator], SensorEntity):
    """Base class for INA3221 sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: INA3221DataUpdateCoordinator,
        config_entry: ConfigEntry,
        channel: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._channel = channel
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}")},
            name="INA3221 Power Monitor",
            manufacturer="Texas Instruments",
            model="INA3221",
        )


class INA3221VoltageSensor(INA3221SensorBase):
    """Sensor for INA3221 voltage measurement."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT

    def __init__(
        self,
        coordinator: INA3221DataUpdateCoordinator,
        config_entry: ConfigEntry,
        channel: int,
    ) -> None:
        """Initialize the voltage sensor."""
        super().__init__(coordinator, config_entry, channel)
        self._attr_name = f"Channel {channel + 1} Voltage"
        self._attr_unique_id = f"{config_entry.entry_id}_ch{channel + 1}_voltage"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(f"ch{self._channel + 1}_voltage")


class INA3221CurrentSensor(INA3221SensorBase):
    """Sensor for INA3221 current measurement."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE

    def __init__(
        self,
        coordinator: INA3221DataUpdateCoordinator,
        config_entry: ConfigEntry,
        channel: int,
    ) -> None:
        """Initialize the current sensor."""
        super().__init__(coordinator, config_entry, channel)
        self._attr_name = f"Channel {channel + 1} Current"
        self._attr_unique_id = f"{config_entry.entry_id}_ch{channel + 1}_current"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(f"ch{self._channel + 1}_current")


class INA3221PowerSensor(INA3221SensorBase):
    """Sensor for INA3221 power measurement."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(
        self,
        coordinator: INA3221DataUpdateCoordinator,
        config_entry: ConfigEntry,
        channel: int,
    ) -> None:
        """Initialize the power sensor."""
        super().__init__(coordinator, config_entry, channel)
        self._attr_name = f"Channel {channel + 1} Power"
        self._attr_unique_id = f"{config_entry.entry_id}_ch{channel + 1}_power"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(f"ch{self._channel + 1}_power")
