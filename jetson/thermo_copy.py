import time,board,busio
import numpy as np
import adafruit_mlx90640
import datetime as dt
import cv2


i2c = busio.I2C(board.SCL_1, board.SDA_1, frequency=1200000) # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ # set refresh rate

mlx_shape = (24,32)

print ('---')

frame = np.zeros((24*32,)) # setup array for storing all 768 temperatures

Tmax = 40
Tmin = 20

def td_to_image(f):
	norm = np.uint8((f + 40)*6.4)
	norm.shape = (24,32)
	return norm

time.sleep(4)

t0 = time.time()

try:
        while True:
                # waiting for data frame
                mlx.getFrame(frame) # read MLX temperatures into frame var
                img16 = (np.reshape(frame,mlx_shape)) # reshape to 24x32 
                #img16 = (np.fliplr(img16))
                
                ta_img = td_to_image(img16)
                # Image processing
                img = cv2.applyColorMap(ta_img, cv2.COLORMAP_JET)
                img = cv2.resize(img, (640,480), interpolation = cv2.INTER_CUBIC)
                img = cv2.flip(img, 1)

                #text = 'Average MLX90640 Temperature: {0:2.1f}C ({1:2.1f}F)'.format(np.mean(frame),(((9.0/5.0)*np.mean(frame))+32.0))
                text = 'Tmin = {:+.1f} Tmax = {:+.1f} FPS = {:.2f}'.format(frame.min(), frame.max(), 1/(time.time() - t0))
                cv2.putText(img, text, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
                print ('--imshow')
                cv2.imshow('Output', img)

                # if 's' is pressed - saving of picture
                key = cv2.waitKey(1) & 0xFF
                if key == ord("s"):
                        fname = 'pic_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.jpg'
                        cv2.imwrite(fname, img)
                        print('Saving image ', fname)

                t0 = time.time()

except KeyboardInterrupt:
        # to terminate the cycle
        cv2.destroyAllWindows()
        print(' Stopped')

# just in case
cv2.destroyAllWindows()