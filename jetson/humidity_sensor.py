import board
from adafruit_bme280 import basic as adafruit_bme280

class HumiditySensor:
    PRESSURE = 1025.5

    def __init__(self):
        # Create sensor object, using the board's default I2C bus.
        i2c = board.I2C()  # uses board.SCL and board.SDA
        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
        self.sensor.sea_level_pressure = HumiditySensor.PRESSURE
    
    def data(self):
        temp = self.sensor.temperature
        humidity = self.sensor.relative_humidity
        pressure = self.sensor.pressure
        altitude = self.sensor.altitude

        return {
            "temp": temp,
            "humidity": humidity,
            "pressure": pressure,
            "altitude": altitude
        }