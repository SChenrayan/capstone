import pika, time
import argparse
import json

from util import log

parser = argparse.ArgumentParser(
    prog='sensor_receiver.py',
    description='Receives data from SiamiLab JetsonTX2'
)
parser.add_argument('ip')
parser.add_argument('--port', default=5672, required=False)

class SensorReceiver:
    def __init__(self, view, ip, port):
        self.ip = ip
        self.port = port
        self._view = view
        self._running = False

    def _log(self, msg):
        log(msg, "SensorReceiver")

    def _thermo_callback(self, ch, method, properties, body):
        body_json = json.loads(body)
        self._view.set_thermo_data(body_json)

    def _sensor_callback(self, ch, method, properties, body):
        body_json = json.loads(body)
        self._view.set_sensor_data(body_json)

    def start(self):
        self._log("opening connection")
        self._running = True
        creds = pika.PlainCredentials('jetson-rabbitmq', 'jetson-rabbitmq')
        conn_params = pika.ConnectionParameters(self.ip, self.port, '/', creds)
        connection = pika.BlockingConnection(conn_params)
        channel = connection.channel()

        self._log("declaring queues")
        channel.queue_declare(queue='thermo-data')
        channel.queue_declare(queue='sensor-data')

        self._log("subscribing to queues")
        channel.basic_consume(queue='thermo-data', on_message_callback=self._thermo_callback, auto_ack=True)
        channel.basic_consume(queue='sensor-data', on_message_callback=self._sensor_callback, auto_ack=True)

        self._log(" Waiting for messages. To exit press CTRL+C")
        while self._running:
            connection.process_data_events()
            time.sleep(0.05)
        
        self._log("Cleaning up connection")
        connection.close()
            
    def request_stop(self):
        self._running = False
