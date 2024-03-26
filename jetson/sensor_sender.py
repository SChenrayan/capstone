import time
import pika
import json
from thermo_sensor import ThermoSensor
from humidity_sensor import HumiditySensor
import argparse

parser = argparse.ArgumentParser(
    prog='sensor_sender.py',
    description='Sends data from SiamiLab JetsonTX2'
)
parser.add_argument('--sleep_rate', default=0.1, required=False)


def main(args):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='sensor-data')
    channel.queue_declare(queue='thermo-data')

    thermo_sensor = ThermoSensor()
    humidity_sensor = HumiditySensor()

    while True:
        channel.basic_publish(exchange='', routing_key='sensor-data', body=json.dumps(humidity_sensor.data()))
        channel.basic_publish(exchange='', routing_key='thermo-data', body=json.dumps(thermo_sensor.data()))
        time.sleep(args.sleep_rate)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
