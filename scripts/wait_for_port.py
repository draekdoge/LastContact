#!/usr/bin/env python3
"""Ожидание TCP-порта (для migrate до alembic без netcat в образе)."""
import socket
import sys
import time

if len(sys.argv) < 3:
    print("usage: wait_for_port.py HOST PORT [timeout_sec]", file=sys.stderr)
    sys.exit(2)

host = sys.argv[1]
port = int(sys.argv[2])
timeout_sec = float(sys.argv[3]) if len(sys.argv) > 3 else 120.0

deadline = time.monotonic() + timeout_sec
while time.monotonic() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            pass
        sys.exit(0)
    except OSError:
        time.sleep(0.5)

sys.exit(1)
