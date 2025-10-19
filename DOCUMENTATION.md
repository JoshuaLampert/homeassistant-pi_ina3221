# INA3221 Integration Documentation

## Overview

This Home Assistant integration provides support for the Texas Instruments INA3221 three-channel power monitor. The INA3221 can simultaneously monitor voltage, current, and power on three independent channels, making it ideal for monitoring multiple power rails in a system.

## Hardware Setup

### Required Hardware
- Raspberry Pi (or compatible device with I2C support)
- INA3221 breakout board (e.g., Adafruit INA3221)
- Shunt resistors (typically 0.1Ω, but configurable)

### Wiring
Connect the INA3221 to your Raspberry Pi via I2C:
- VCC → 3.3V or 5V
- GND → GND
- SDA → GPIO2 (SDA)
- SCL → GPIO3 (SCL)

### Enable I2C
Enable I2C on your Raspberry Pi:
```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

### Verify Connection
Check if the device is detected:
```bash
sudo i2cdetect -y 1
```
You should see the device at address 0x40 (default).

## Installation

### HACS Installation (Recommended)
1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots menu → "Custom repositories"
4. Add this repository URL: `https://github.com/JoshuaLampert/homeassistant-pi_ina3221`
5. Select category: "Integration"
6. Click "Add"
7. Search for "INA3221 Power Monitor"
8. Click "Download"
9. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/pi_ina3221` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

### Adding the Integration
1. Go to **Settings** → **Devices & Services**
2. Click **"+ ADD INTEGRATION"**
3. Search for **"INA3221 Power Monitor"**
4. Fill in the configuration form:

#### Configuration Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| I2C Bus Number | The I2C bus number on your Raspberry Pi | 1 | 0-255 |
| I2C Address | The I2C address of the INA3221 (hexadecimal) | 0x40 | 0x00-0x7F |
| Channel 1 Shunt Resistor Value | Shunt resistor value for channel 1 in Ohms | 0.1 | 0.001-1.0 |
| Channel 2 Shunt Resistor Value | Shunt resistor value for channel 2 in Ohms | 0.1 | 0.001-1.0 |
| Channel 3 Shunt Resistor Value | Shunt resistor value for channel 3 in Ohms | 0.1 | 0.001-1.0 |
| Enable Channel 1 | Enable or disable channel 1 | True | Boolean |
| Enable Channel 2 | Enable or disable channel 2 | True | Boolean |
| Enable Channel 3 | Enable or disable channel 3 | True | Boolean |

5. Click **"Submit"**

The integration will validate the connection to the INA3221 before completing setup.

## Entities

For each enabled channel, the integration creates three sensor entities:

### Voltage Sensors
- `sensor.ina3221_power_monitor_channel_1_voltage`
- `sensor.ina3221_power_monitor_channel_2_voltage`
- `sensor.ina3221_power_monitor_channel_3_voltage`

**Unit**: Volts (V)  
**Device Class**: voltage  
**State Class**: measurement

### Current Sensors
- `sensor.ina3221_power_monitor_channel_1_current`
- `sensor.ina3221_power_monitor_channel_2_current`
- `sensor.ina3221_power_monitor_channel_3_current`

**Unit**: Amperes (A)  
**Device Class**: current  
**State Class**: measurement

### Power Sensors
- `sensor.ina3221_power_monitor_channel_1_power`
- `sensor.ina3221_power_monitor_channel_2_power`
- `sensor.ina3221_power_monitor_channel_3_power`

**Unit**: Watts (W)  
**Device Class**: power  
**State Class**: measurement

## Update Interval

The integration polls the INA3221 every 30 seconds by default. This interval is optimized for:
- Reasonable update frequency for monitoring
- Low CPU usage
- Minimal I2C bus traffic

## Example Automations

### Low Voltage Alert
```yaml
automation:
  - alias: "Low Voltage Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ina3221_power_monitor_channel_1_voltage
        below: 11.0
    action:
      - service: notify.mobile_app
        data:
          message: "Battery voltage is low: {{ states('sensor.ina3221_power_monitor_channel_1_voltage') }} V"
```

### High Current Alert
```yaml
automation:
  - alias: "High Current Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ina3221_power_monitor_channel_1_current
        above: 2.5
    action:
      - service: persistent_notification.create
        data:
          title: "High Current Detected"
          message: "Channel 1 current exceeded 2.5A"
```

### Energy Monitoring Dashboard
```yaml
type: entities
title: Power Monitoring
entities:
  - entity: sensor.ina3221_power_monitor_channel_1_voltage
    name: Battery Voltage
  - entity: sensor.ina3221_power_monitor_channel_1_current
    name: Battery Current
  - entity: sensor.ina3221_power_monitor_channel_1_power
    name: Battery Power
```

## Troubleshooting

### Integration Fails to Add
**Symptoms**: Error message "Failed to connect to INA3221 sensor"

**Solutions**:
1. Verify I2C is enabled: `sudo raspi-config`
2. Check I2C address: `sudo i2cdetect -y 1`
3. Verify wiring connections
4. Check power supply to the INA3221
5. Try a different I2C address if you've configured the device differently

### Incorrect Readings

**Symptoms**: Current or power readings are incorrect

**Solutions**:
1. Verify the shunt resistor values in the configuration match your hardware
2. Ensure the current is within the sensor's range (±3.2A per channel)
3. Check for loose connections
4. Verify the shunt resistor is properly connected in series with the load

### Sensor Values Show "Unavailable"

**Symptoms**: Entities show as "unavailable" in Home Assistant

**Solutions**:
1. Check Home Assistant logs for errors
2. Verify the INA3221 is still detected: `sudo i2cdetect -y 1`
3. Restart the integration from Settings → Devices & Services
4. Check if the I2C bus is being used by another process

### Permission Denied on I2C

**Symptoms**: Errors related to I2C permissions in the logs

**Solutions**:
1. Ensure the Home Assistant user is in the `i2c` group:
   ```bash
   sudo usermod -a -G i2c homeassistant
   ```
2. Restart Home Assistant

## Technical Details

### Data Update Coordinator
The integration uses Home Assistant's `DataUpdateCoordinator` for efficient data fetching and entity updates. All sensors for enabled channels are updated simultaneously in a single I2C transaction.

### Device Information
- **Manufacturer**: Texas Instruments
- **Model**: INA3221
- **Integration Type**: Device
- **IoT Class**: Local Polling

### Dependencies
- `adafruit-circuitpython-ina3221` - Python library for INA3221 communication
- `adafruit-blinka` - CircuitPython compatibility layer (automatically installed)
- `adafruit-circuitpython-busdevice` - I2C bus device support (automatically installed)

## Advanced Configuration

### Multiple INA3221 Devices
You can add multiple INA3221 devices if they have different I2C addresses:
1. Configure each INA3221 to use a different I2C address (using the A0 pin)
2. Add each device as a separate integration instance in Home Assistant
3. Each will appear as a separate device with its own sensors

### Custom Shunt Resistors
The default shunt resistor value is 0.1Ω, but you can use different values:
- Smaller values (e.g., 0.01Ω) for high-current applications
- Larger values (e.g., 0.5Ω) for better precision at low currents
- Remember: Lower resistance = higher current capacity but lower precision

## Support

For issues, feature requests, or contributions:
- GitHub Issues: https://github.com/JoshuaLampert/homeassistant-pi_ina3221/issues
- GitHub Repository: https://github.com/JoshuaLampert/homeassistant-pi_ina3221

## Credits

- Based on the [INA219 Power Monitor integration](https://github.com/JoshuaLampert/homeassistant-pi_ina219)
- Uses the [Adafruit CircuitPython INA3221 library](https://github.com/adafruit/Adafruit_CircuitPython_INA3221)
- Hardware: [Adafruit INA3221](https://www.adafruit.com/product/6062)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
