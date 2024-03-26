import argparse
import time

from sensor_receiver import SensorReceiver
from joystick_sender import Joystick
from zed import ZedCamera
from util import log

parser = argparse.ArgumentParser(
    prog='main.py',
    description='Run all base station functionality'
)
parser.add_argument('ip')
parser.add_argument('--zed-port', default=8002, required=False)
parser.add_argument('--rabbitmq-port', default=5672, required=False)


def main(args):
    sensor_receiver = SensorReceiver(args.ip, args.rabbitmq_port)
    log("Sensor receiver initialized")
    zed = ZedCamera(args.ip, args.zed_port)
    log("Zed initialized")
    joy = Joystick(zed)
    log("Joy initialized")
    joy.set_popup(sensor_receiver.log_popup)
    joy.run()
    sensor_receiver.run()
    while zed.grab():
        time.sleep(0.01)
    del joy
    sensor_receiver.close()
    log("Connections closed. Goodbye!")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
