import os
import socket
import threading
import time
import runpy

import uvicorn


# Public deployment:
# - synthetic telemetry works
# - local AI fallback works
# - private Google Workspace write actions stay disabled
os.environ["NETWORKOPS_PUBLIC_DEMO"] = "1"


def api_is_running():
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    sock.settimeout(0.25)

    try:
        return (
            sock.connect_ex(
                ("127.0.0.1", 8000)
            )
            == 0
        )
    finally:
        sock.close()


def run_api():
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning",
    )


if not api_is_running():

    thread = threading.Thread(
        target=run_api,
        daemon=True,
    )

    thread.start()

    for _ in range(30):
        if api_is_running():
            break
        time.sleep(0.1)


runpy.run_path(
    "dashboard/app.py",
    run_name="__main__",
)
