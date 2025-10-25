import asyncio
import os
import signal
import json
import websockets
from websockets.server import serve

WS_PORT = int(os.getenv("WS_PORT", "8765"))

# Store connected clients
connected_clients = set()

async def handle_client(websocket, path):
    """Handle a WebSocket client connection."""
    print(f"Client connected from {websocket.remote_address}")
    connected_clients.add(websocket)
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "ORDER":
                    payload = data.get("payload", "")
                    print(f"Received order: {payload}")

                    # Send order response
                    response = {
                        "type": "FOOD",
                        "payload": f"FOOD: {payload}",
                        "timestamp": asyncio.get_event_loop().time()
                    }
                    await websocket.send(json.dumps(response))
                    
            except json.JSONDecodeError:
                print(f"Invalid JSON received: {message}")
            except Exception as e:
                print(f"Error processing message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} disconnected")
    except Exception as e:
        print(f"Error handling client {websocket.remote_address}: {e}")
    finally:
        connected_clients.discard(websocket)

async def order_food_server(stop_event: asyncio.Event):
    """Start the WebSocket server for food order communication."""
    print(f"Starting WebSocket server on port {WS_PORT}")
    
    async with serve(handle_client, "localhost", WS_PORT):
        print(f"WebSocket server running on ws://localhost:{WS_PORT}")
        await stop_event.wait()  # Wait until stop event is set

async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _stop(*_):
        print("Shutdown requested")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop)
        except NotImplementedError:
            # Signal handlers are not implemented on Windows for asyncio
            pass


    await order_food_server(stop_event)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted. Exiting.")