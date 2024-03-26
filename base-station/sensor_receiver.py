import pika, sys, os, time
import argparse
import json
import sensor_viewer

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
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self._creds = pika.PlainCredentials('jetson-rabbitmq', 'jetson-rabbitmq')
        self._conn_params = pika.ConnectionParameters(args.ip, args.port, '/', self._creds)
        self._connection = pika.SelectConnection(self._conn_params)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue='thermo-data', on_message_callback=self._thermo_callback, auto_ack=True)
        self._channel.queue_declare(queue='sensor-data', on_message_callback=self._sensor_callback, auto_ack=True)

        self._view = sensor_viewer.SensorViewer()

    def _thermo_callback(self, ch, method, properties, body):
        body_json = json.loads(body)
        self._view.set_thermo_data(body_json)

    def _sensor_callback(self, ch, method, properties, body):
        body_json = json.loads(body)
        self._view.set_sensor_data(body_json)

    def run(self):
        self._connection.ioloop.start()

    def close(self):
        self._connection.close()

    def log_popup(self, log_string):
        self._view.log_popup(log_string)


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

