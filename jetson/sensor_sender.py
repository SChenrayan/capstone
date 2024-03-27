import time
import pika
import json
import thermo_sensor as ts
import humidity_sensor as hs
import argparse

parser = argparse.ArgumentParser(
    prog='sensor_sender.py',
    description='Sends data from SiamiLab JetsonTX2'
)
parser.add_argument('--sleep_rate', default=0.1, required=False)


def main(args):
    sleep_rate = float(args.sleep_rate)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='sensor-data')
    channel.queue_declare(queue='thermo-data')

    thermo_sensor = ts.ThermoSensor()
    humidity_sensor = hs.HumiditySensor()

    while True:
        try:
            channel.basic_publish(exchange='', routing_key='sensor-data', body=json.dumps(humidity_sensor.data()))
            channel.basic_publish(exchange='', routing_key='thermo-data', body=json.dumps(thermo_sensor.data()))
            time.sleep(sleep_rate)
        except ValueError:
            pass
        except KeyboardInterrupt:
            break
    connection.close()


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
