import threading

def log(msg):
    id = threading.get_ident()
    print(f"[Thread {id}] {msg}")