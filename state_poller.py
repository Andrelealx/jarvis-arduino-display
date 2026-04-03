import argparse
import json
import os
import time
from datetime import datetime

import requests


def load_state(url, timeout):
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def post_command(base_url, token, command):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-API-Key"] = token

    cmd_type = command.get("type")

    if cmd_type == "online":
        requests.post(f"{base_url}/online", headers=headers, timeout=5).raise_for_status()
    elif cmd_type == "idle":
        requests.post(f"{base_url}/idle", headers=headers, timeout=5).raise_for_status()
    elif cmd_type == "alert":
        payload = {"text": command.get("text", "Novo alerta")}
        requests.post(f"{base_url}/alert", headers=headers, json=payload, timeout=5).raise_for_status()
    elif cmd_type == "clock":
        payload = {
            "time": command.get("time", datetime.now().strftime("%H:%M")),
            "subtitle": command.get("subtitle", "Windows 11"),
        }
        requests.post(f"{base_url}/clock", headers=headers, json=payload, timeout=5).raise_for_status()
    elif cmd_type == "message":
        payload = {
            "line1": command.get("line1", "JARVIS"),
            "line2": command.get("line2", "Mensagem"),
            "line3": command.get("line3", ""),
        }
        requests.post(f"{base_url}/message", headers=headers, json=payload, timeout=5).raise_for_status()
    else:
        raise ValueError(f"Unsupported command type: {cmd_type}")


def main():
    parser = argparse.ArgumentParser(description="JARVIS Display State Poller")
    parser.add_argument("--state-url", required=True, help="Raw JSON URL com comandos")
    parser.add_argument("--bridge-url", default="http://127.0.0.1:8765", help="URL da bridge local")
    parser.add_argument("--bridge-token", default=None, help="Token da bridge local")
    parser.add_argument("--shared-token", default=None, help="Token esperado dentro do JSON remoto")
    parser.add_argument("--interval", type=int, default=5, help="Intervalo de polling em segundos")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout HTTP em segundos")
    parser.add_argument("--cache-file", default=".poller_state.json", help="Arquivo local para deduplicar comandos")
    args = parser.parse_args()

    seen_ids = set()
    if os.path.exists(args.cache_file):
        try:
            with open(args.cache_file, "r", encoding="utf-8") as f:
                seen_ids = set(json.load(f).get("seen", []))
        except Exception:
            seen_ids = set()

    print(f"JARVIS poller ativo. Fonte: {args.state_url}")

    while True:
        try:
            data = load_state(args.state_url, args.timeout)

            remote_token = data.get("token")
            if args.shared_token and remote_token != args.shared_token:
                raise ValueError("Shared token mismatch in remote state")

            commands = data.get("commands", [])
            for command in commands:
                cmd_id = command.get("id")
                if not cmd_id or cmd_id in seen_ids:
                    continue

                post_command(args.bridge_url, args.bridge_token, command)
                seen_ids.add(cmd_id)
                print(f"[{datetime.now().isoformat(timespec='seconds')}] comando aplicado: {cmd_id} ({command.get('type')})")

                with open(args.cache_file, "w", encoding="utf-8") as f:
                    json.dump({"seen": sorted(seen_ids)}, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[{datetime.now().isoformat(timespec='seconds')}] erro no poller: {e}")

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
