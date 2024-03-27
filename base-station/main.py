import argparse
import time
import threading
import signal

from sensor_receiver import SensorReceiver
from joystick_sender import Joystick
from sensor_viewer import SensorViewer
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
    try: 
        sensor_viewer = SensorViewer()
        sensor_receiver = SensorReceiver(sensor_viewer, args.ip, args.rabbitmq_port)
        sensor_thread = threading.Thread(target=sensor_receiver.start, args=())
        sensor_thread.start()
        log("SensorReceiver initialized")
        zed = ZedCamera(args.ip, args.zed_port)
        log("Zed initialized")
        joy = Joystick(zed)
        log("Joy initialized")
        joy.set_popup(sensor_viewer.write_popup)
        joy.run()
        while zed.grab():
            try:
                sensor_viewer.show() 
            except KeyboardInterrupt:
                break
    finally:
        del joy
        sensor_receiver.request_stop()
        sensor_viewer.destroy()
        log("Connections closed. Goodbye!")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
