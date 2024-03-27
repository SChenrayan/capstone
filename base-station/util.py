import threading
import datetime

def log(msg, namespace="Main"):
    id = threading.get_ident()
    current_time = datetime.datetime.now()
    print(f"[{current_time}] [Thread {id}] [{namespace}] {msg}")