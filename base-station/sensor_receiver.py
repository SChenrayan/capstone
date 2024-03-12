import pika, sys, os
import argparse
import numpy as np
import cv2 as cv
import json

parser = argparse.ArgumentParser(
    prog='RabbitMQ Receiver for Jetson sensor data',
    description='Receives data from SiamiLab JetsonTX2'
)
parser.add_argument('ip')
parser.add_argument('--port', default=5672, required=False)

def open_channel(channel):
    channel.queue_declare(queue='thermo-camera')
    channel.queue_declare(queue='sensor-data')

    def thermo_callback(ch, method, properties, body):
        data = json.loads(body)
        print(f" [x] Received data")
        temps = np.array(data['temps'], dtype=np.uint8)
        
        img = cv.applyColorMap(temps, cv.COLORMAP_JET)
        img = cv.resize(img, (640, 480), interpolation = cv.INTER_CUBIC)
        img = cv.flip(img, 1)
        cv.imshow('Temps', img)
        cv.waitKey(50)
    
    def sensor_callback(ch, method, properties, body):
        print(f" [x] Received data: {body}")

    channel.basic_consume(queue='thermo-camera', on_message_callback=thermo_callback, auto_ack=True)
    channel.basic_consume(queue='sensor-data', on_message_callback=sensor_callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')

def open_connection(conn):
    conn.channel(on_open_callback=open_channel)

def main(args):
    try:
        creds = pika.PlainCredentials('jetson-rabbitmq', 'jetson-rabbitmq')
        conn_params = pika.ConnectionParameters(args.ip, args.port, '/', creds)
        connection = pika.SelectConnection(conn_params, on_open_callback=open_connection)
        connection.ioloop.start()
    except KeyboardInterrupt:
        connection.close()
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)

