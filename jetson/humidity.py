# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
from adafruit_bme280 import basic as adafruit_bme280
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

# Create sensor object, using the board's default I2C bus.
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1025.5

count = 0
while True:
    count += 1
    temp_c = bme280.temperature
    temp_f = (temp_c*9/5)+32
    humidity = bme280.relative_humidity
    pressure = bme280.pressure
    altitude = bme280.altitude
    print(f"\nCount: {count}")
    print(f"\nTemperature: {temp_c} C; {temp_f} F")
    print(f"Humidity: {humidity} %")
    print(f"Pressure: {pressure} hPa")
    print(f"Altitude = {altitude} meters")
    body_dict = {
    'count': count,
    'temp C': temp_c,
    'temp F': temp_f,
   	'humidity': humidity,
   	'pressure': pressure,
   	'altitude': altitude,
    }
    channel.basic_publish(exchange='', routing_key='hello', body=json.dumps(body_dict))
    time.sleep(2)
