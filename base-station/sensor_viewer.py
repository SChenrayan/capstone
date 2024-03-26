import cv2 as cv
import numpy as np
import datetime


class SensorViewer:
    def __init__(self):
        self.window_name = "Jetson Sensor"
        self.img = np.zeros((720, 640, 3), dtype=np.uint8)
        cv.namedWindow(self.window_name)

    def set_thermo_data(self, data):
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

        self.img[0:480, 0:640] = colored_temps
        self.update_img()

    def set_sensor_data(self, data):
        self.img[480:720, 0:640] = 0

        self.write(f"Humidity: {data['humidity']}", (10, 550))
        self.write(f"Pressure: {data['pressure']}", (10, 600))
        self.write(f"Altitude: {data['altitude']}", (10, 650))
        self.write(f"Temperature: {data['temp']}", (10, 700))
        self.update_img()

    def log_popup(self, log_string):
        cv.namedWindow("Logger")
        log_img = np.zeros((200, 800, 3), dtype=np.uint8)
        cv.putText(
            log_img,
            "[" + str(datetime.datetime.now()) + "] " + log_string,
            (50, 50),
            cv.FONT_HERSHEY_COMPLEX,
            1,
            (255, 255, 255),
            1,
            2
        )
        cv.imshow("Logger", log_img)

        k = cv.waitKey(33)
        if k == 27:    # Esc key to close log window
            cv.destroyWindow("Logger")

        # def close_logger(args):
        #     cv.destroyWindow("Logger")

        # cv.createButton(buttonName="Close", onChange=close_logger, userData=None, buttonType=cv.QT_PUSH_BUTTON,initialButtonState=1)

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

    def update_img(self):
        cv.imshow(self.window_name, self.img)
        cv.waitKey(50)


