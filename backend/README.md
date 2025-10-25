Simple asyncio WebSocket ping-pong backend

Requirements:
- Python 3.8+
- Install dependencies: pip install -r requirements.txt

Usage:
- Set WS_PORT env var if you want to use a different port (default: 8765).
- Run: python main.py

Behavior:
- Starts a WebSocket server on localhost:8765
- Accepts JSON messages with type "ping" and payload
- Responds with JSON messages containing "pong:<payload>"
- Supports Ctrl+C to exit gracefully
