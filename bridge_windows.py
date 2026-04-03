import argparse
import os
import threading
import time
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify
import serial

app = Flask(__name__)
ser = None
API_TOKEN = None
state = {
    "mode": "online",
    "line1": "JARVIS",
    "line2": "Online",
    "line3": "",
    "last_alert": None,
}


def send(cmd: str):
    global ser
    if ser is None:
        raise RuntimeError("Serial not connected")
    ser.write((cmd.strip() + "\n").encode("utf-8"))


def require_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        global API_TOKEN
        if not API_TOKEN:
            return fn(*args, **kwargs)

        auth_header = request.headers.get("Authorization", "")
        supplied = request.headers.get("X-API-Key", "")

        if auth_header.startswith("Bearer "):
            supplied = auth_header[7:].strip()

        if supplied != API_TOKEN:
            return jsonify({"ok": False, "error": "unauthorized"}), 401

        return fn(*args, **kwargs)

    return wrapper


def apply_state():
    mode = state["mode"]
    if mode == "online":
        send("SCREEN:online")
    elif mode == "idle":
        send("SCREEN:idle")
    elif mode == "clock":
        send("SCREEN:clock")
        send(f"TIME:{state['line1']}")
        send(f"SUB:{state['line2']}")
    elif mode == "msg":
        send("SCREEN:msg")
        send(f"LINE1:{state['line1']}")
        send(f"LINE2:{state['line2']}")
        if state['line3']:
            send(f"LINE3:{state['line3']}")
    else:
        send("SCREEN:online")


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "serial": ser is not None,
        "state": state,
        "tokenEnabled": bool(API_TOKEN),
        "serverTime": datetime.now().isoformat(timespec="seconds"),
    })


@app.post("/online")
@require_token
def online():
    state["mode"] = "online"
    apply_state()
    return jsonify({"ok": True})


@app.post("/idle")
@require_token
def idle():
    state["mode"] = "idle"
    apply_state()
    return jsonify({"ok": True})


@app.post("/message")
@require_token
def message():
    data = request.get_json(force=True, silent=True) or {}
    state["mode"] = "msg"
    state["line1"] = str(data.get("line1", "JARVIS"))[:14]
    state["line2"] = str(data.get("line2", "Mensagem"))[:20]
    state["line3"] = str(data.get("line3", ""))[:20]
    apply_state()
    return jsonify({"ok": True, "state": state})


@app.post("/alert")
@require_token
def alert():
    data = request.get_json(force=True, silent=True) or {}
    text = str(data.get("text", "Novo alerta"))[:20]
    state["last_alert"] = text
    send(f"ALERT:{text}")
    return jsonify({"ok": True, "alert": text})


@app.post("/clock")
@require_token
def clock():
    data = request.get_json(force=True, silent=True) or {}
    hhmm = str(data.get("time", datetime.now().strftime("%H:%M")))[:10]
    subtitle = str(data.get("subtitle", "Windows 11"))[:20]
    state["mode"] = "clock"
    state["line1"] = hhmm
    state["line2"] = subtitle
    apply_state()
    return jsonify({"ok": True, "state": state})


def clock_worker():
    while True:
        if state["mode"] == "clock":
            state["line1"] = datetime.now().strftime("%H:%M")
            apply_state()
        time.sleep(15)


def main():
    global ser, API_TOKEN
    parser = argparse.ArgumentParser(description="JARVIS Arduino Display Bridge")
    parser.add_argument("--port", required=True, help="COM port, ex: COM5")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--host", default="0.0.0.0", help="Use 0.0.0.0 para aceitar rede local")
    parser.add_argument("--api-port", type=int, default=8765)
    parser.add_argument("--token", default=None, help="Token opcional para proteger a API")
    args = parser.parse_args()

    API_TOKEN = args.token or os.environ.get("JARVIS_DISPLAY_TOKEN")

    ser = serial.Serial(args.port, args.baud, timeout=1)
    time.sleep(2)
    send("SCREEN:boot")
    time.sleep(1)
    send("SCREEN:online")

    threading.Thread(target=clock_worker, daemon=True).start()

    print(f"JARVIS bridge online on http://{args.host}:{args.api_port} -> {args.port}")
    if API_TOKEN:
        print("API token protection: ENABLED")
    else:
        print("API token protection: DISABLED")

    app.run(host=args.host, port=args.api_port)


if __name__ == "__main__":
    main()
