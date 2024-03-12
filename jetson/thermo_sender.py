import time,board,busio
import numpy as np
import adafruit_mlx90640
import datetime as dt
import cv2
import pika
import json


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')


i2c = busio.I2C(board.SCL_1, board.SDA_1, frequency=1200000) # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ # set refresh rate

mlx_shape = (24,32)

print ('---')

frame = np.zeros((24*32,)) # setup array for storing all 768 temperatures

Tmax = 100
Tmin = 0

print("Tmax" + str(Tmax))
print("Tmin" + str(Tmin))

def td_to_image(f):
    norm = np.uint8((f + 40)*6.4)
    norm.shape = (24,32)
    return norm

time.sleep(2)
t0 = time.time()

try:
    count = 0
    while True:
        count += 1
        # waiting for data frame
        mlx.getFrame(frame) # read MLX temperatures into frame var
        
        img16 = (np.reshape(frame,mlx_shape)) # reshape to 24x32 
        #img16 = (np.fliplr(img16))
                
        ta_img = td_to_image(img16)
        
        data = {
            'count': count,
            'temps': list(list(int(num) for num in lst) for lst in ta_img),
            't_min': int(frame.min()),
            't_max': int(frame.max()),
            't_avg': int(np.mean(frame)),
        }
                
        channel.basic_publish(
            exchange='',
            routing_key='hello',
            body=json.dumps(data),
        )
        print(count)
        # Image processing
        #img = cv2.applyColorMap(ta_img, cv2.COLORMAP_JET)
        #img = cv2.resize(img, (640,480), interpolation = cv2.INTER_CUBIC)
        #img = cv2.flip(img, 1)

        #text = 'Average MLX90640 Temperature: {0:2.1f}C ({1:2.1f}F)'.format(np.mean(frame),(((9.0/5.0)*np.mean(frame))+32.0))
        #text = 'Tmin = {:+.1f} Tmax = {:+.1f} FPS = {:.2f}'.format(frame.min(), frame.max(), 1/(time.time() - t0))
        #cv2.putText(img, text, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
        #print ('--imshow')
        #cv2.imshow('Output', img)

        # if 's' is pressed - saving of picture
        #key = cv2.waitKey(1) & 0xFF
        #if key == ord("s"):
        #    fname = 'pic_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.jpg'
        #    cv2.imwrite(fname, img)
        #    print('Saving image ', fname)

        #t0 = time.time()
        
        time.sleep(0.25)
                
except KeyboardInterrupt:
    # to terminate the cycle
    cv2.destroyAllWindows()
    print(' Stopped')

# just in case
cv2.destroyAllWindows()
