from evdev import UInput, ecodes as e, InputDevice, list_devices, AbsInfo, util
import pika
import json

# Dumping the device capabilities:
# {('EV_SYN', 0): [('SYN_REPORT', 0), ('SYN_CONFIG', 1), ('SYN_DROPPED', 3)], ('EV_KEY', 1): [(['BTN_A', 'BTN_GAMEPAD', 'BTN_SOUTH'], 304), (['BTN_B', 'BTN_EAST'], 305), (['BTN_NORTH', 'BTN_X'], 307), (['BTN_WEST', 'BTN_Y'], 308), ('BTN_TL', 310), ('BTN_TR', 311), ('BTN_SELECT', 314), ('BTN_START', 315), ('BTN_MODE', 316), ('BTN_THUMBL', 317), ('BTN_THUMBR', 318)], ('EV_ABS', 3): [(('ABS_X', 0), AbsInfo(value=-129, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)), (('ABS_Y', 1), AbsInfo(value=-129, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)), (('ABS_Z', 2), AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)), (('ABS_RX', 3), AbsInfo(value=128, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)), (('ABS_RY', 4), AbsInfo(value=-129, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)), (('ABS_RZ', 5), AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)), (('ABS_HAT0X', 16), AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)), (('ABS_HAT0Y', 17), AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0))]}

CAP = {
    e.EV_KEY: [
        304,
        305,
        307,
        308,
        310,
        311,
        314,
        315,
        316,
        317,
        318,
    ],
    e.EV_ABS: [
        (0, AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (1, AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (2, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
        (3, AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (4, AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),
        (5, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
        (16, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        (17, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
    ],
}

virtual_joystick = UInput(CAP, name='Virtual Racecar Joystick')

creds = pika.PlainCredentials("joystick-rabbit", 'joystick-rabbit')
connection = pika.BlockingConnection(pika.ConnectionParameters('10.110.120.227', 5672, "/", creds))
channel = connection.channel()

channel.queue_declare(queue='joy_state')


def callback(ch, method, properties, body):
    print(f"Body: {body}")
    body = json.loads(body)
    state = {
        e.EV_ABS: {
            0: body["axes"]["x_left"],
            1: body["axes"]["y_left"],
            3: body["axes"]["x_right"],
            4: body["axes"]["y_right"],
        },
        e.EV_KEY: {
            310: body["buttons"]["bumper_left"],
        },
    }

    for category in state.keys():
        for event in state[category].keys():
            try:
                value = state[category][event]
                virtual_joystick.write(category, event, value)
            except KeyError:
                pass
    virtual_joystick.syn()


channel.basic_consume(queue='joy_state', on_message_callback=callback, auto_ack=True)

print("consuming")
channel.start_consuming()
print("after consuming")
