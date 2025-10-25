Simple asyncio MQTT ping-pong backend

Requirements:
- Python 3.8+
- Install dependencies: pip install -r requirements.txt

Usage:
- Set MQTT_BROKER env var if broker is not localhost.
- Run: python main.py

Behavior:
- Subscribes to topic `osensa/ping`.
- When a message arrives it publishes `pong:<payload>` to `osensa/pong`.
- Reconnects on failure and supports Ctrl+C to exit.
