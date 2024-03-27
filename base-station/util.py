import threading
import datetime

def log(msg, namespace="Main"):
    id = threading.get_ident()
    current_time = datetime.datetime.now()
    timestamp = f"[{current_time}]"
    thread_id = '{message:{fill}{align}{width}}'.format(
        message=f"[Thread {id}]",
        fill=' ',
        align='<',
        width=14,
    )
    namespace = '{message:{fill}{align}{width}}'.format(
        message=f"[{namespace}]",
        fill=' ',
        align='<',
        width=16,
    )

    print(f"{timestamp} {thread_id} {namespace} {msg}")