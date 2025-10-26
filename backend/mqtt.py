from paho.mqtt import client as mqtt
import asyncio
import json

CLIENT_ID = "food_order_server"
PORT = 9001
BROKER = "localhost"
TOPIC = "ORDER"

decoder = json.JSONDecoder()

def handle_order(client, payload):
    order = decoder.decode(payload)
    food = order.get("food")
    table = order.get("table")
    if not food or not table:
        print(f"Invalid order received: {payload}")
        return
    print(f"Order received: {food} for table {table}")
    client.publish("FOOD", json.dumps({"food": food, "table": table}))

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected to {BROKER}:{PORT} (rc={rc})")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
    except Exception:
        # fallback to raw representation
        payload = repr(msg.payload)
    print(f"Received -> topic: {msg.topic} | payload: {payload}")
    if msg.topic == TOPIC:
        handle_order(client, payload)


def on_disconnect(client, userdata, rc):
    print(f"Disconnected (rc={rc})")


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print(f"Subscribed (mid={mid}) granted_qos={granted_qos}")


# def on_log(client, userdata, level, buf):
    # print(f"MQTT log: {buf}")


async def main():
    # use an explicit client id and a widely-compatible protocol
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=True, transport="websockets")
    client.enable_logger()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    # client.on_log = on_log

    # connect and start network loop in background thread
    try:
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as e:
        print(f"Failed to connect to broker: {e}")
        return

    client.loop_start()

    print("MQTT backend running — listening for messages. Press Ctrl+C to exit.")

    try:
        # run forever until interrupted
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("Shutting down MQTT backend...")
    finally:
        client.loop_stop()
        try:
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
