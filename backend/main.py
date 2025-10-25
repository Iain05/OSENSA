import asyncio
import os
import signal
from aiomqtt import Client, MqttError

BROKER = os.getenv("MQTT_BROKER", "localhost")
PING_TOPIC = "osensa/ping"
PONG_TOPIC = "osensa/pong"

async def ping_pong(stop_event: asyncio.Event):
    """Connect to broker, subscribe to PING_TOPIC and reply to PONG_TOPIC with a simple "pong:<payload>"."""
    reconnect_delay = 1
    while not stop_event.is_set():
        try:
            async with Client(BROKER) as client:
                reconnect_delay = 1
                async with client.unfiltered_messages() as messages:
                    await client.subscribe(PING_TOPIC)
                    async for message in messages:
                        payload = message.payload.decode(errors="ignore")
                        print(f"Received ping on {message.topic}: {payload}")
                        await client.publish(PONG_TOPIC, f"pong:{payload}")
                        if stop_event.is_set():
                            break
        except MqttError as e:
            print(f"MQTT error: {e}. Reconnecting in {reconnect_delay}s...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 30)

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
            # add_signal_handler may not be implemented on some platforms
            pass

    await ping_pong(stop_event)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted. Exiting.")