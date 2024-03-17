import pika, sys, os, time
import argparse
import json
import viewer

parser = argparse.ArgumentParser(
    prog='sensor_receiver.py',
    description='Receives data from SiamiLab JetsonTX2'
)
parser.add_argument('ip')
parser.add_argument('--port', default=5672, required=False)

view = viewer.Viewer()

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

def main(args):
    try:
        creds = pika.PlainCredentials('jetson-rabbitmq', 'jetson-rabbitmq')
        conn_params = pika.ConnectionParameters(args.ip, args.port, '/', creds)
        connection = pika.SelectConnection(conn_params, on_open_callback=open_connection)
        connection.ioloop.start()

        # mock_connection()

    except KeyboardInterrupt:
        connection.close()
        print('Interrupted, closing connection')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)

