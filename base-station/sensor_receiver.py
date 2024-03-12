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
parser.add_argument('port', default=5672)

def main(args):
    creds = pika.PlainCredentials('jetson-rabbitmq', 'jetson-rabbitmq')
    conn_params = pika.ConnectionParameters(args.ip, args.port, '/', creds)
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()

    channel.queue_declare(queue='thermo-camera')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f" [x] Received data")
        temps = np.array(data['temps'], dtype=np.uint8)
        
        img = cv.applyColorMap(temps, cv.COLORMAP_JET)
        img = cv.resize(img, (640, 480), interpolation = cv.INTER_CUBIC)
        img = cv.flip(img, 1)
        cv.imshow('Temps', img)
        cv.waitKey(50)

    channel.basic_consume(queue='thermo-camera', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        args = parser.parse_args()
        main(args)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

