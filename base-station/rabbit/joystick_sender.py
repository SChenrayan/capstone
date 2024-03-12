import time
import pika
import inputs
import threading
import json


class Joystick:
    def __init__(self):
        self.x_left = 0
        self.y_left = 0
        self.x_right = 0
        self.y_right = 0
        self.trigger_left = 0
        self.trigger_right = 0
        self.bumper_left = 0
        self.bumper_right = 0
        self.a = 0
        self.x = 0
        self.y = 0
        self.b = 0
        self.thumb_left = 0
        self.thumb_right = 0
        self.back = 0
        self.start = 0
        self.dpad_left = 0
        self.dpad_right = 0
        self.dpad_up = 0
        self.dpad_down = 0

        self.last_sent = time.time()

        self._monitor_thread = threading.Thread(target=self._monitor_events, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self._channel = self._connection.channel()

        self._channel.queue_declare(queue='joy_state')

    def __del__(self):
        self._connection.close()

    def data(self):
        """
        Create a dictionary with the axes and buttons and their respective values

        :return: dict representing the current state of the controller
        """
        data = {
            "axes": {
                "x_left": self.x_left,
                "y_left": self.y_left,
                "x_right": self.x_right,
                "y_right": self.y_right,
                "trigger_left": self.trigger_left,
                "trigger_right": self.trigger_right,
            },
            "buttons": {
                "bumper_left": self.bumper_left,
                "bumper_right": self.bumper_right,
                "a": self.a,
                "x": self.x,
            },
        }

        return json.dumps(data)

    def read(self):
        axes = [self.x_left, self.y_left, self.x_right, self.y_right]
        buttons = [self.bumper_left, self.bumper_right, self.a, self.x]
        print(f"Axes: {axes}")
        print(f"Buttons: {buttons}")

    def _consume_event(self, event):
        if event.code == "SYN_REPORT":
            self._channel.basic_publish(exchange="", routing_key="joy_state", body='i')
            print(f"Published {self.data()}")
        elif event.code == "ABS_X":
            state = event.state if abs(event.state) > 130 else 0
            self.x_left = state
        elif event.code == "ABS_Y":
            state = event.state if abs(event.state) > 130 else 0
            self.y_left = state
        elif event.code == "ABS_RX":
            state = event.state if abs(event.state) > 130 else 0
            self.x_right = state
        elif event.code == "ABS_RY":
            state = event.state if abs(event.state) > 130 else 0
            self.y_right = state
        elif event.code == "BTN_TL":
            self.bumper_left = event.state
        elif event.code == "BTN_TR":
            self.bumper_right = event.state
        elif event.code == "BTN_SOUTH":
            self.a = event.state
        elif event.code == "BTN_WEST":
            self.x = event.state
        else:
            print(f"Unknown event ({event.code}). Skipping.")

    def _monitor_events(self):
        while True:
            events = inputs.get_gamepad()
            for event in events:
                self._consume_event(event)


if __name__ == "__main__":
    joy = Joystick()
    while True:
        joy.read()
        time.sleep(0.5)
