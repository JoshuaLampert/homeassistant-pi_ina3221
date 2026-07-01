# INA3221 Power Monitor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg)](https://opensource.org/licenses/MIT)

Home Assistant integration to measure voltage, current, and power with a three-channel [INA3221 sensor](https://www.ti.com/lit/ds/symlink/ina3221.pdf) from Texas Instruments on a Raspberry Pi.

## Features

- Read voltage, current, and power from all three channels of the INA3221
- Easy configuration through the Home Assistant UI
- Enable/disable individual channels
- Configure shunt resistor values for each channel independently
- Automatic updates every 30 seconds

## Hardware Requirements

- Raspberry Pi (or compatible device with I2C support) running Home Assistant
- [INA3221 Triple 0-26 VDC, ±3.2 Amp Power Monitor](https://www.adafruit.com/product/6062)
- I2C connection enabled on your device

Especially, this means no ESP is required because the INA3221 is directly wired to the Raspberry Pi running Home Assistant.

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and show an integration.](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration/?domain=pi_ina3221)

1. Add this repository to HACS as a custom repository:
   - Go to HACS
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add `https://github.com/JoshuaLampert/homeassistant-pi_ina3221` as an Integration
   - Click "Add"

2. Install the integration:
   - Search for "INA3221 Power Monitor" in HACS
   - Click "Download"
   - Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/pi_ina3221` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Preparation

Home Assistant OS requires I2C to be enabled through the system configuration. There are several methods:
The easiest and most reliable method is to use the dedicated app (formerly known as add-on):

1. Install the **"HassOS I2C Configurator"** app:
   - In the app-store (formerly known as add-on store) add the repository: `https://github.com/adamoutler/HassOSConfigurator`
   - Install the app

2. Start the app **"HassOS I2C Configurator"** - it will automatically configure I2C. Check the logs to see if it was successful.

3. **Important:** Reboot your Raspberry Pi twice (full reboot, not just Home Assistant restart):
   - Go to Developer Tools → Restart → Advanced Options → Reboot system
   - Wait for it to come back online, then reboot again
   - This ensures I2C drivers are properly loaded

4. Verify I2C is available using the **Terminal & SSH** or **Advanced SSH & Web Terminal** app:
   ```bash
   ls -l /dev/i2c*
   ```
   You should see devices like `/dev/i2c-0`, `/dev/i2c-1`, etc. Note: In a normal setup on a Raspberry Pi not
   running Home Assistant OS, we would verify the INA3221 is detected at bus number 1 by running
   ```
   i2cdetect -y 1
   ```
   This command returns the I2C Address if it is detected properly. However, on Home Assistant OS, this would normally
   give a permission error. But if you disable the protection-mode in the SSH app, you can execute `i2cdetect` in a
   docker container like this:
   ```sh
   ➜  ~ docker exec -it homeassistant bash -c "apk add i2c-tools && i2cdetect -y 1"
   fetch https://dl-cdn.alpinelinux.org/alpine/v3.21/main/aarch64/APKINDEX.tar.gz
   fetch https://dl-cdn.alpinelinux.org/alpine/v3.21/community/aarch64/APKINDEX.tar.gz
   (1/1) Installing i2c-tools (4.3-r3)
   Executing busybox-1.37.0-r12.trigger
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
   00:                         -- -- -- -- -- -- -- --
   10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
   70: -- -- -- -- -- -- -- --
   ```
   This tells you that at bus number `1` a device at address `0x40` is detected.

For more information and troubleshooting, see the [forum thread](https://community.home-assistant.io/t/add-on-hassos-i2c-configurator/264167).

### Adding the Integration

Add the integration through the Home Assistant UI:
  - Go to Settings -> Devices & Services
  - Click "+ Add Integration"
  - Search for "INA3221 Power Monitor"
  - Enter your configuration:
    - **I2C Bus Number**: Usually `1` for Raspberry Pi
    - **I2C Address**: Default is `0x40` (64 in decimal), note that the slider accepts decimal values, so you have to translate the hex value to decimal
    - **Shunt Resistor Values**: Configure the shunt resistor value in Ohms for each channel (default: `0.05` Ohms)
    - **Channel Enable**: Enable or disable each channel individually
    - **Scan Interval (seconds)**: How often to poll the sensor

After setup you can adjust the scan interval later via the integration's **Options** in Home Assistant (Configure button on the integration card).

Different INA3221 devices can be used if they are configured to have different I2C addresses. For details refer to Section 7.5.1.1 of the
[manual](https://www.ti.com/lit/ds/symlink/ina3221.pdf).

## Configuration Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| I2C Bus Number | The I2C bus number | 1 | - |
| I2C Address | The I2C address of the INA3221 | 0x40 | 0x00-0x7F (0-127 in decimal) |
| Channel X Shunt Resistor Value | The value of the shunt resistor of channel X in ohms | 0.05 | 0.001-1.0 |
| Enable Channel X | Do not create sensors for channel X if disabled | True | True/False |
| Scan Interval (seconds) | How often to poll the sensor | 30 | 5-3600 |

## Sensors

For each enabled channel, the integration provides three sensors:

- **Channel X Voltage**: Bus voltage in Volts (V)
- **Channel X Current**: Current in Amperes (A)
- **Channel X Power**: Power in Watts (W)

Where X is 1, 2, or 3 depending on the channel.

## Services

### `pi_ina3221.set_scan_interval`

Change the scan interval at runtime from an automation or script for a specific device.

**Parameters:**
- `i2c_bus` (required, integer): I2C bus number (typically 1 on Raspberry Pi)
- `i2c_address` (required, integer): I2C address of the INA3221 device (0x40 hexadecimal = 64 decimal; you can use either 0x40 or 64)
- `scan_interval` (required, integer): Scan interval in seconds (range: 5–3600)

**Example automation:**
```yaml
automation:
  - alias: "Decrease INA3221 scan rate at night"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: pi_ina3221.set_scan_interval
      data:
        i2c_bus: 1
        i2c_address: 0x40
        scan_interval: 60
```

**How to find your I2C bus and address:**
The I2C bus and address are the same ones you configured when setting up the integration. Default bus is `1` and default address is `0x40` (64 in decimal). If you configured different values, use those instead. If you did not change the name of a device, you can also find the bus and address in the name of the device.

## Dependencies

This integration uses a pure Python driver based on `smbus2` to communicate with the INA3221 sensor via I2C.

## Troubleshooting

### Cannot connect to sensor

- Verify I2C is enabled on your Raspberry Pi (`ls -l /dev/i2c*`)
- Check I2C address with `sudo i2cdetect -y 1`
- Verify wiring between Raspberry Pi and INA3221:
  - VCC → 3.3V or 5V
  - GND → GND
  - SDA → GPIO 2 (Pin 3) on Raspberry Pi
  - SCL → GPIO 3 (Pin 5) on Raspberry Pi
- Ensure proper power supply to the INA3221

### Incorrect readings

- Verify the shunt resistor values match your hardware
- Check that the correct channels are enabled
- Ensure current is within the sensor's range (±3.2A per channel)
- Check that your power supply is stable

## Similar projects

- [INA3221 3-Channel DC Current Sensor in ESP](https://esphome.io/components/sensor/ina3221/): Also creates current, voltage, and power sensors, but via ESPHome, i.e. an additional ESP device is required
- [INA219 Power Monitor](https://github.com/JoshuaLampert/homeassistant-pi_ina219): Similar integration, but using the INA219 device

## Credits

- The [pi-ina3221](https://github.com/adafruit/Adafruit_CircuitPython_INA3221) Python library by Adafruit served as a reference
- Uses a pure Python driver with [smbus2](https://github.com/kplindegaard/smbus2) for direct I2C communication
- INA3221 chip by Texas Instruments

## Disclaimer

Please note that large parts of this integration are written by GitHub Copilot, see [this PR](https://github.com/JoshuaLampert/homeassistant-pi_ina3221/pull/1).
I have checked the implementation and tested the integration though. However, I do not extend any warranty. Use at your own risk!

## License and contributing

This project is under the MIT License (see [License](https://github.com/JoshuaLampert/homeassistant-pi_ina3221/blob/main/LICENSE)).
I am pleased to accept contributions from everyone, preferably in the form of a PR.

## Support

For issues, questions, or contributions, please [open an issue](https://github.com/JoshuaLampert/homeassistant-pi_ina3221/issues)
or [create a pull request](https://github.com/JoshuaLampert/homeassistant-pi_ina3221/pulls).
