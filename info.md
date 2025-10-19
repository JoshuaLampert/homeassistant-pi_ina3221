# INA3221 Power Monitor

Monitor voltage, current, and power on three independent channels using the INA3221 sensor.

## Features

✅ **Three Independent Channels** - Monitor up to 3 power rails simultaneously  
✅ **UI Configuration** - Easy setup through Home Assistant UI, no YAML required  
✅ **Per-Channel Configuration** - Independent shunt resistor values and enable/disable for each channel  
✅ **Comprehensive Monitoring** - Voltage, current, and power sensors for each channel  
✅ **I2C Flexibility** - Configurable I2C bus and address  
✅ **HACS Compatible** - Easy installation and updates through HACS

## Sensors

For each enabled channel, you get:
- **Voltage Sensor** - Bus voltage in Volts
- **Current Sensor** - Current in Amperes
- **Power Sensor** - Power in Watts

## Quick Setup

1. Enable I2C on your Raspberry Pi
2. Connect your INA3221 sensor via I2C
3. Add the integration through Settings → Devices & Services
4. Configure I2C settings and shunt resistor values
5. Enable the channels you want to monitor

## Hardware

- **Raspberry Pi** (or compatible device with I2C)
- **INA3221 Sensor** ([Adafruit INA3221](https://www.adafruit.com/product/6062))
- **Shunt Resistors** (typically 0.1Ω, but configurable)

## Documentation

For detailed setup instructions, configuration options, and troubleshooting, see [DOCUMENTATION.md](https://github.com/JoshuaLampert/homeassistant-pi_ina3221/blob/main/DOCUMENTATION.md).

## Support

- [Report Issues](https://github.com/JoshuaLampert/homeassistant-pi_ina3221/issues)
- [View Source Code](https://github.com/JoshuaLampert/homeassistant-pi_ina3221)

## Credits

Based on the [INA219 Power Monitor integration](https://github.com/JoshuaLampert/homeassistant-pi_ina219) and uses the [Adafruit CircuitPython INA3221 library](https://github.com/adafruit/Adafruit_CircuitPython_INA3221).
