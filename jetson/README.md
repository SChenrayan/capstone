# Jetson Rover

# Basic Info
The rover is a Jetson TX2 running Ubuntu 18.04
The password and sudo password are `jetson`
If you are running into issues connecting to the internet because of date mismatches: Go to settings, change it to manually set the date to today's date, then switch back to automatic.

# How to Run
## ZED Streaming
To start the ZED Streaming, just run the executable with whatever port you would like to use. We used 8002 and this is the default on the base station, so if you use a different port, ensure you change the port when running the base station using command line arguments
This executable is from ZED's samples. These and the rest of the ZED SDK can be found on the jetson in `/usr/local/zed/`

## ROS Control
We are using ROS launch files from previous projects. Firstly, open a terminal window and run `roscore`. Then in another terminal window, run `roslaunch racecar teleop.launch`. This will launch a bunch of ROS topics.
We do not utilize all of the topics so you may see (and ignore) some errors (particularly with the IMU). If you are having issues with a certain topic, you can "listen" to what's being broadcast in a new terminal window using `rostopic echo ____` with whatever the topic is. If you are unsure of the topic's name, run `rostopic list` to see a comprehensive list.
More information with ROS can be found in its documentation. It also supports an autonomous mode without user input but this is not used in our implementation. 
Currently the joystick will default to a virtual joystick created in `joystick_receiver.py`. To change this or any other settings having to do with ROS, you will have to go into the Racecar workspace under the home directory.

## Sensor Sender
`sensor_sender.py` will send both thermal camera and humidity sensor readings over RabbitMQ. The RabbitMQ server is hosted on the Jetson. If receiving any AMQPConnection issues, try ensuring that RabbitMQ is running on the jetson, the device trying to connect (base station) has the right IP address, and the device trying to connect has the required credentials on the jetson (see `sensor_receiver.py`).

## Joystick Receiver
`joystick_receiver.py` will receive joystick events from the base station and write them to a virtual input on the jetson. This virtual input is used as the joystick by ROS. To ensure it is able to edit the virtual input, run `sudo joystick_receiver.py ip` where ip is the IP address of the base station. If receiving any AMQPConnection issues, go through the same steps as above but opposite since the base station is hosting the queue.
