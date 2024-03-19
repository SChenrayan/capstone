import time
import pika
import json
import thermo_sensor
import humidity_sensor
import argparse

parser = argparse.ArgumentParser(
    prog='sensor_sender.py',
    description='Sends data from SiamiLab JetsonTX2'
)
parser.add_argument('sleep_rate', default=1)

def main(args):
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='sensor-data')
    channel.queue_declare(queue='thermo-data')

    thermo_sensor = thermo_sensor.ThermoSensor()
    humidity_sensor = humidity_sensor.HumiditySensor()

    while True:
        channel.basic_publish(exchange='', routing_key='sensor-data', body=json.dumps(humidity_sensor.data()))
        channel.basic_publish(exchange='', routing_key='thermo-data', body=json.dumps(thermo_sensor.data()))
        time.sleep(args.sleep_rate) # TODO: make this configurable

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)