"""Pure Python INA3221 driver using smbus2."""

from __future__ import annotations

from typing import Any

from smbus2 import SMBus


# INA3221 Register addresses
_REG_CONFIG = 0x00
_REG_SHUNT_VOLTAGE_1 = 0x01
_REG_BUS_VOLTAGE_1 = 0x02
_REG_SHUNT_VOLTAGE_2 = 0x03
_REG_BUS_VOLTAGE_2 = 0x04
_REG_SHUNT_VOLTAGE_3 = 0x05
_REG_BUS_VOLTAGE_3 = 0x06

# Configuration register bits
_CONFIG_ENABLE_CH1 = 0x4000
_CONFIG_ENABLE_CH2 = 0x2000
_CONFIG_ENABLE_CH3 = 0x1000
_CONFIG_AVG_1 = 0x0000
_CONFIG_AVG_4 = 0x0200
_CONFIG_AVG_16 = 0x0400
_CONFIG_AVG_64 = 0x0600
_CONFIG_AVG_128 = 0x0800
_CONFIG_AVG_256 = 0x0A00
_CONFIG_AVG_512 = 0x0C00
_CONFIG_AVG_1024 = 0x0E00
_CONFIG_VBUS_CT_1MS = 0x0040
_CONFIG_VSH_CT_1MS = 0x0008
_CONFIG_MODE_SHUNT_BUS_CONT = 0x0007

# Default configuration: all channels enabled, continuous mode
_CONFIG_DEFAULT = (
    _CONFIG_ENABLE_CH1
    | _CONFIG_ENABLE_CH2
    | _CONFIG_ENABLE_CH3
    | _CONFIG_AVG_64
    | _CONFIG_VBUS_CT_1MS
    | _CONFIG_VSH_CT_1MS
    | _CONFIG_MODE_SHUNT_BUS_CONT
)


def _to_signed_int(value: int, bits: int = 16) -> int:
    """Convert unsigned int to signed int."""
    if value & (1 << (bits - 1)):
        return value - (1 << bits)
    return value


class INA3221:
    """INA3221 three-channel current/voltage monitor."""

    def __init__(
        self,
        i2c_bus: int = 1,
        address: int = 0x40,
        shunt_resistors: tuple[float, float, float] = (0.1, 0.1, 0.1),
    ) -> None:
        """Initialize the INA3221.

        Args:
            i2c_bus: I2C bus number (default: 1)
            address: I2C address (default: 0x40)
            shunt_resistors: Tuple of shunt resistor values in Ohms for channels 1, 2, 3
        """
        self.bus = SMBus(i2c_bus)
        self.address = address
        self.shunt_resistors = shunt_resistors

        # Reset and configure the device
        self._write_register(_REG_CONFIG, _CONFIG_DEFAULT)

    def _read_register(self, register: int) -> int:
        """Read a 16-bit register."""
        # INA3221 uses big-endian format
        data = self.bus.read_i2c_block_data(self.address, register, 2)
        return (data[0] << 8) | data[1]

    def _write_register(self, register: int, value: int) -> None:
        """Write a 16-bit register."""
        # INA3221 uses big-endian format
        data = [(value >> 8) & 0xFF, value & 0xFF]
        self.bus.write_i2c_block_data(self.address, register, data)

    def _read_shunt_voltage(self, channel: int) -> float:
        """Read shunt voltage for a channel (1, 2, or 3).

        Returns:
            Shunt voltage in millivolts
        """
        register_map = {
            1: _REG_SHUNT_VOLTAGE_1,
            2: _REG_SHUNT_VOLTAGE_2,
            3: _REG_SHUNT_VOLTAGE_3,
        }
        reg = register_map.get(channel)
        if reg is None:
            raise ValueError(f"Invalid channel: {channel}. Must be 1, 2, or 3.")

        raw = self._read_register(reg)
        # Shunt voltage is in bits 15-3, LSB = 40µV
        value = _to_signed_int(raw >> 3, bits=13)
        return value * 0.040  # Convert to millivolts

    def _read_bus_voltage(self, channel: int) -> float:
        """Read bus voltage for a channel (1, 2, or 3).

        Returns:
            Bus voltage in volts
        """
        register_map = {
            1: _REG_BUS_VOLTAGE_1,
            2: _REG_BUS_VOLTAGE_2,
            3: _REG_BUS_VOLTAGE_3,
        }
        reg = register_map.get(channel)
        if reg is None:
            raise ValueError(f"Invalid channel: {channel}. Must be 1, 2, or 3.")

        raw = self._read_register(reg)
        # Bus voltage is in bits 15-3, LSB = 8mV
        value = _to_signed_int(raw >> 3, bits=13)
        return value * 0.008  # Convert to volts

    def read_channel(self, channel: int) -> dict[str, float]:
        """Read voltage, current, and power for a channel.

        Args:
            channel: Channel number (1, 2, or 3)

        Returns:
            Dictionary with 'voltage' (V), 'current' (A), and 'power' (W)
        """
        if channel not in (1, 2, 3):
            raise ValueError(f"Invalid channel: {channel}. Must be 1, 2, or 3.")

        bus_voltage = self._read_bus_voltage(channel)
        shunt_voltage_mv = self._read_shunt_voltage(channel)

        # Calculate current using Ohm's law: I = V / R
        # Shunt voltage is in mV, convert to V and divide by resistance
        shunt_resistor = self.shunt_resistors[channel - 1]
        current = (shunt_voltage_mv / 1000.0) / shunt_resistor  # in Amperes

        # Calculate power: P = V * I
        power = bus_voltage * current  # in Watts

        return {
            "voltage": bus_voltage,
            "current": current,
            "power": power,
        }

    def close(self) -> None:
        """Close the I2C bus."""
        if self.bus:
            self.bus.close()
