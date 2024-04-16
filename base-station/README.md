# Base Station

# Basic Info
This can be any laptop, as long as it is compatible with the ZED SDK and NVIDIA CUDA (the latter is more of a limiting factor usually). RabbitMQ is required to send and receive data between the jetson. 
A joystick (in our case the Logitech F710) is required. We used the inputs library to capture input events from the joystick
For 2 way audio, just install the Mumble client online and connect to the jetson using its IP address.

# How to Run
TL;DR: Run `main.py ip` where ip is the IP Address of the jetson.
This will take a bit to spool up. The main slowpoke here is the ZED connection. Once that works, the rest should spool up right after. You'll see the thermal/humidity sensors' OpenCV window hang as the rest spools up (this is normal). The ZED's OpenGL window will not open until it has connected. There is occasional logging for different events such as adding a marker or saving the mesh file.

## Troubleshooting
Sometimes the ZED will fail to connect and the program will end. We found this varies with what WiFi is being used and how good the connection was, but it's just a timeout issue. If the issue persists, stop the camera streaming on the jetson and rerun it, then try rerunning `main.py`.
Sometimes the ZED will connect, its window will pop up and will have a black screen for one frame, and then crash. We found this is when the ZED Streaming on the jetson had registered the base station connecting on the previous run but never registered it disconnecting. The second disconnect will cause this "black screen of death". Try restarting the ZED Camera Streaming on the jetson, same as above.
If it is failing to save the mesh files due to some issue with the directory, ensure you have created a `base-station/mesh_objs/` directory. This is not in the github so that we are not accidentally commiting a bunch of random .obj files, but you could add it if this is confusing :)
