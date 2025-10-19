"""Constants for the INA3221 Power Monitor integration."""

DOMAIN = "pi_ina3221"

# Configuration constants
CONF_I2C_BUS = "i2c_bus"
CONF_I2C_ADDRESS = "i2c_address"
CONF_SHUNT_OHMS_CH1 = "shunt_ohms_ch1"
CONF_SHUNT_OHMS_CH2 = "shunt_ohms_ch2"
CONF_SHUNT_OHMS_CH3 = "shunt_ohms_ch3"
CONF_CHANNEL_1_ENABLED = "channel_1_enabled"
CONF_CHANNEL_2_ENABLED = "channel_2_enabled"
CONF_CHANNEL_3_ENABLED = "channel_3_enabled"

# Default values
DEFAULT_I2C_BUS = 1
DEFAULT_I2C_ADDRESS = 0x40
DEFAULT_SHUNT_OHMS = 0.1
DEFAULT_CHANNEL_ENABLED = True
