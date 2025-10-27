# Troubleshooting Guide

## 500 Internal Server Error During Configuration

If you encounter a "500 Internal Server Error" or "Der Konfigurationsfluss konnte nicht geladen werden" when trying to add the integration, try these steps:

### 1. Clear Python Bytecode Cache

Home Assistant may have cached the old version of the integration. Clear the cache:

```bash
# Stop Home Assistant first
# Then clear the cache
find /config/custom_components/pi_ina3221 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find /config/custom_components/pi_ina3221 -name "*.pyc" -delete 2>/dev/null

# If using Docker, use:
docker exec homeassistant find /config/custom_components/pi_ina3221 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
docker exec homeassistant find /config/custom_components/pi_ina3221 -name "*.pyc" -delete 2>/dev/null

# Restart Home Assistant
```

### 2. Completely Remove and Reinstall

1. Remove the integration from HACS or delete the folder:
   ```bash
   rm -rf /config/custom_components/pi_ina3221
   ```

2. Restart Home Assistant

3. Reinstall the integration through HACS or manually

4. Restart Home Assistant again

5. Try adding the integration through Settings → Devices & Services

### 3. Check Home Assistant Logs

Check the Home Assistant logs for more details about the error:

```bash
# View logs
docker logs homeassistant

# Or check in the UI
# Settings → System → Logs
```

Look for any error messages related to `pi_ina3221` or `config_flow`.

### 4. Verify Dependencies

Make sure the required dependencies can be installed:

```bash
# In the Home Assistant container
pip3 install adafruit-circuitpython-ina3221==1.2.0
```

### 5. Check File Permissions

Ensure all files have the correct permissions:

```bash
chmod -R 755 /config/custom_components/pi_ina3221
```

### 6. Verify Integration Structure

The integration should have this structure:
```
custom_components/pi_ina3221/
├── __init__.py
├── config_flow.py
├── const.py
├── manifest.json
├── sensor.py
├── strings.json
└── translations/
    ├── en.json
    └── de.json
```

## Connection Issues After Setup

If the integration loads but shows "unavailable" sensors:

### 1. Verify I2C is Enabled

```bash
# On Raspberry Pi
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

### 2. Check I2C Device

```bash
# Check if the device is detected
sudo i2cdetect -y 1

# You should see the device at address 0x40 (or your configured address)
```

### 3. Check Permissions

The Home Assistant user needs access to the I2C bus:

```bash
# Add the user to the i2c group
sudo usermod -a -G i2c homeassistant

# Or if using Docker, ensure the container has access to /dev/i2c-1
```

### 4. Verify Wiring

Check the physical connections:
- VCC → 3.3V or 5V
- GND → GND
- SDA → GPIO2 (SDA)
- SCL → GPIO3 (SCL)

### 5. Check Home Assistant Logs

Look for specific error messages about I2C communication or sensor initialization.

## Still Having Issues?

If none of these steps help, please open an issue on GitHub with:
- Your Home Assistant version
- The exact error message from the logs
- Your hardware setup (Raspberry Pi model, INA3221 board)
- Steps you've already tried

GitHub Issues: https://github.com/JoshuaLampert/homeassistant-pi_ina3221/issues
