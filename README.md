# INA3221 Power Monitor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant integration to measure voltage, current, and power with a three-channel INA3221 sensor on a Raspberry Pi.

## Features

- Read voltage, current, and power from all three channels of the INA3221
- Configure via the Home Assistant UI
- Enable/disable individual channels
- Configure shunt resistor values for each channel independently
- Configurable I2C bus and address
- Ready for HACS integration

## Hardware Requirements

- Raspberry Pi (or compatible device with I2C support)
- [INA3221 Triple 0-26 VDC, ±3.2 Amp Power Monitor](https://www.adafruit.com/product/6062)
- I2C connection between the Raspberry Pi and INA3221

## Installation

### Via HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Install the "INA3221 Power Monitor" integration
3. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/pi_ina3221` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ ADD INTEGRATION"
3. Search for "INA3221 Power Monitor"
4. Configure the following:
   - **I2C Bus Number**: Usually `1` for Raspberry Pi
   - **I2C Address**: Default is `0x40` (64 in decimal)
   - **Shunt Resistor Values**: Configure the shunt resistor value in Ohms for each channel (default: 0.1 Ohms)
   - **Channel Enable**: Enable or disable each channel individually

## Sensors

For each enabled channel, the integration provides three sensors:

- **Channel X Voltage**: Bus voltage in Volts (V)
- **Channel X Current**: Current in Amperes (A)
- **Channel X Power**: Power in Watts (W)

Where X is 1, 2, or 3 depending on the channel.

## Dependencies

This integration uses a pure Python driver based on `smbus2` to communicate with the INA3221 sensor via I2C.

## Troubleshooting

### Cannot connect to sensor

- Verify I2C is enabled on your Raspberry Pi (`sudo raspi-config` → Interface Options → I2C)
- Check I2C address with `sudo i2cdetect -y 1`
- Verify wiring between Raspberry Pi and INA3221
- Ensure proper power supply to the INA3221

### Incorrect readings

- Verify the shunt resistor values match your hardware
- Check that the correct channels are enabled
- Ensure current is within the sensor's range (±3.2A per channel)

## Credits

This integration is based on the [INA219 Power Monitor integration](https://github.com/JoshuaLampert/homeassistant-pi_ina219) and uses a pure Python driver for direct I2C communication with the INA3221.

## License

This project is licensed under the MIT License.
