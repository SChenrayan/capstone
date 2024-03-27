import pika, sys, os, time
import argparse
import json
import threading
import sensor_viewer

from util import log

parser = argparse.ArgumentParser(
    prog='sensor_receiver.py',
    description='Receives data from SiamiLab JetsonTX2'
)
parser.add_argument('ip')
parser.add_argument('--port', default=5672, required=False)

view = sensor_viewer.SensorViewer()


def open_channel(channel):
    channel.queue_declare(queue='thermo-camera')
    channel.queue_declare(queue='sensor-data')

    def thermo_callback(ch, method, properties, body):
        print("[x] Received temp data")
        body_json = json.loads(body)
        view.set_thermo_data(body_json)

    def sensor_callback(ch, method, properties, body):
        print("[x] Received sensor data")
        body_json = json.loads(body)
        view.set_sensor_data(body_json)

    channel.basic_consume(queue='thermo-data', on_message_callback=thermo_callback, auto_ack=True)
    channel.basic_consume(queue='sensor-data', on_message_callback=sensor_callback, auto_ack=True)

    print(" [*] Waiting for messages. To exit press CTRL+C")


def open_connection(conn):
    conn.channel(on_open_callback=open_channel)


def mock_connection():
    thermo_data = json.load(open("example_temps.json"))
    sensor_data = json.load(open("example_sensor.json"))
    while True:
        view.set_sensor_data(sensor_data)
        view.set_thermo_data(thermo_data)
        time.sleep(1)


class SensorReceiver:
    def __init__(self, view, ip, port):
        self.ip = ip
        self.port = port
        self._view = view
        self._running = False

    def _thermo_callback(self, ch, method, properties, body):
        log("thermo callback called")
        body_json = json.loads(body)
        self._view.set_thermo_data(body_json)

    def _sensor_callback(self, ch, method, properties, body):
        log("sensor callback called")
        body_json = json.loads(body)
        self._view.set_sensor_data(body_json)

    def start(self):
        log("[Rabbit] opening conn")
        self._running = True
        creds = pika.PlainCredentials('jetson-rabbitmq', 'jetson-rabbitmq')
        conn_params = pika.ConnectionParameters(self.ip, self.port, '/', creds)
        connection = pika.BlockingConnection(conn_params)
        channel = connection.channel()

        log("[Rabbit] declaring queues")
        channel.queue_declare(queue='thermo-data')
        channel.queue_declare(queue='sensor-data')

        log("[Rabbit] subscribing to queues")
        channel.basic_consume(queue='thermo-data', on_message_callback=self._thermo_callback, auto_ack=True)
        channel.basic_consume(queue='sensor-data', on_message_callback=self._sensor_callback, auto_ack=True)

        log(" [*] Waiting for messages. To exit press CTRL+C")
        while self._running:
            connection.process_data_events()
            time.sleep(0.05)
        
        log("[Rabbit] Cleaning up")
        connection.close()
            
    def request_stop(self):
        self._running = False


def main(args):
    # try:
    #     creds = pika.PlainCredentials('jetson-rabbitmq', 'jetson-rabbitmq')
    #     conn_params = pika.ConnectionParameters(args.ip, args.port, '/', creds)
    #     connection = pika.SelectConnection(conn_params, on_open_callback=open_connection)
    #     connection.ioloop.start()
    #
    #     # mock_connection()
    #
    # except KeyboardInterrupt:
    #     connection.close()
    #     print('Interrupted, closing connection')
    #     try:
    #         sys.exit(0)
    #     except SystemExit:
    #         os._exit(0)
    receiver = SensorReceiver(args.ip, args.port)
    receiver.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        receiver.close()


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)

