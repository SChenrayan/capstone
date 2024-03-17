import time, board, busio
import numpy as np
import adafruit_mlx90640

class ThermoSensor:
    FRAME_SHAPE = (24, 32)

    def __init__(self):
        i2c = busio.I2C(board.SCL_1, board.SDA_1, frequency=1200000) # setup I2C
        self.sensor = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
        self.sensor.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ # set refresh rate
        self.frame = np.zeros(ThermoSensor.FRAME_SHAPE[0] * ThermoSensor.FRAME_SHAPE[1])

    def data(self):
        self.sensor.getFrame(self.frame)
        reshaped = np.reshape(self.frame, ThermoSensor.FRAME_SHAPE)
        normalized = np.uint8((reshaped + 40)* 6.4)
        # normalized.shape = (24,32) # TODO: is this necessary?
        return { "temps": normalized.tolist() }


