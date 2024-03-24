import time
import pika
import inputs
import threading
import json
from zed import ZedCamera


class Joystick:
    def __init__(self, zed: ZedCamera):
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

        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue='joy_state')

        self._zed = zed

    def __del__(self):
        self._connection.close()

    def run(self):
        self._zed.run()
        self._monitor_thread.start()

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
            },
            "buttons": {
                "bumper_left": self.bumper_left,
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
            self._channel.basic_publish(exchange="", routing_key="joy_state", body=self.data())
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
        elif event.code == "BTN_START":
            if event.state == 1:
                self._zed.toggle_mapping()
        elif event.code == "BTN_SOUTH":
            self.a = event.state
            if event.state == 1:
                self._zed.add_marker()
        elif event.code == "BTN_WEST":
            self.x = event.state
            if event.state == 1:
                self._zed.add_warning()
        else:
            print(f"Unknown event ({event.code}). Skipping.")

    def _monitor_events(self):
        while True:
            try:
                events = inputs.get_gamepad()
                for event in events:
                    self._consume_event(event)
            except Exception as e:  # Catch all exceptions so that thread stays alive
            #     print("-------- ERROR IN JOYSTICK THREAD --------")
            #     print(e)
                raise(e)


if __name__ == "__main__":
    zed = ZedCamera("10.110.186.61", 8002)
    print("Zed initialized")
    time.sleep(0.3)
    joy = Joystick(zed)
    print("Joy initialized")
    time.sleep(0.3)
    joy.run()
    print("Running joy")
    while zed.grab():
        time.sleep(0.05)
        pass
    del joy
