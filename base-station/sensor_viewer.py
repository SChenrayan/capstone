import cv2 as cv
import numpy as np
import datetime
from threading import Lock
from util import log

class SensorViewer:
    def __init__(self):
        self.window_name = "Jetson Sensor"
        self.img = np.zeros((720, 640, 3), dtype=np.uint8)
        self.mutex = Lock()
        cv.namedWindow(self.window_name)

    def set_thermo_data(self, data):
        log("in set thermo data")
        temps = np.array(data["temps"], dtype=np.uint8)
        colored_temps = cv.applyColorMap(temps, cv.COLORMAP_JET)
        colored_temps = cv.resize(colored_temps, (640, 480), interpolation=cv.INTER_CUBIC)
        colored_temps = cv.flip(colored_temps, 1)
        hsv = cv.cvtColor(colored_temps, cv.COLOR_BGR2HSV)
        lower_red = np.array([0, 10, 120])
        upper_red = np.array([16, 255, 255])
        hot_obj = cv.inRange(hsv, lower_red, upper_red)
        contours, _ = cv.findContours(hot_obj.copy(),
                                      cv.RETR_TREE,
                                      cv.CHAIN_APPROX_SIMPLE)
        for c in contours:
            x, y, w, h = cv.boundingRect(c)
            if 80 < w < 400 and h > 80:
                cv.rectangle(colored_temps, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv.putText(colored_temps, 'Hot!', (x, y-10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        self.mutex.acquire()
        self.img[0:480, 0:640] = colored_temps
        self.mutex.release()

    def set_sensor_data(self, data):
        log("in set sensor data")
        self.mutex.acquire()
        self.img[550:720, 0:640] = 0

        self.write(f"Humidity: {data['humidity']}", (10, 580))
        self.write(f"Pressure: {data['pressure']}", (10, 620))
        self.write(f"Altitude: {data['altitude']}", (10, 660))
        self.write(f"Temperature: {data['temp']}", (10, 700))
        self.mutex.release()

    def log_popup(self, log_string):
        self.mutex.acquire()
        self.img[480:550, 0:640] = 0

        self.write(log_string, (10, 500))
        self.mutex.release()

    def write(self, text, pos):
        font = cv.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        fontColor = (255, 255, 255)
        thickness = 1
        lineType = 2
        cv.putText(
            self.img,
            text,
            pos,
            font,
            fontScale,
            fontColor,
            thickness,
            lineType
        )

    def show(self):
        cv.imshow(self.window_name, self.img)
        cv.waitKey(50)

    def destroy(self):
        cv.destroyWindow(self.window_name)

