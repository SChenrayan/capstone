# C.H.R.I.S.
# Comprehensive Hazard Response and Information System

 
# Components
There are two main parts to the system. The base station's functionality is all built into one file. The jetson's functionality is separated into its individual parts. These could be combined with threading to make one main file to run, but having the individual files can be helpful when testing and diagnosing issues within particular areas of the system.

# Requirements
## Base Station
- ZED (Python) SDK
- NVIDIA CUDA
- OpenGL
- OpenCV
- Joystick Controller (Logitech F710 or equivalent)
- RabbitMQ

## Jetson
- Jetson TX2
- ZED SDK (Currently on a legacy version that is compatible with the current flash on the Jetson. Newest versions would require the Jetson to be flashed)
- ZED Camera
- Adafruit MLX90640
- Adafruit BME280
- RabbitMQ
- ROS (to control your VESC/motors)
