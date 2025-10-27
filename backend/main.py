from paho.mqtt import client as mqtt
import asyncio
import json
import random

from logger import info, error, mqtt as mqtt_log, order as order_log, debug

# global event loop reference so paho callbacks (which run in another thread) can schedule coroutines
EVENT_LOOP = None

CLIENT_ID = "food_order_server"
PORT = 9001
BROKER = "mosquitto"
TOPIC = "ORDER"

decoder = json.JSONDecoder()

async def handle_order(client, payload):
    """Asynchronous order handler that simulates food preparation and delivery.
    If the order is invalid, an error message is logged and no delivery is made.
    Otherwise, wait a random time between 3 and 10 seconds to simulate preparation,
    then publish a delivery message to the FOOD topic.

    Parameters
    ----------
    client : mqtt.Client
        The MQTT client instance to publish delivery messages.
    payload : str
        The JSON-encoded order payload containing 'food' and 'table' fields.
    
    Returns
    -------
    None
    """
    try:
        order = decoder.decode(payload)
    except json.JSONDecodeError:
        error(f"Invalid order received: {payload}")
        return
    food = order.get("food")
    table = order.get("table")
    if not food or not table:
        error(f"Invalid order received: {payload}")
        return
    if not isinstance(table, int):
        error(f"Invalid order received (table must be int): {payload}")
        return
    if not isinstance(food, str) or food.strip() == "":
        error(f"Invalid order received (food must be non-empty string): {payload}")
        return

    order_log(f"Order received: {food} for table {table}")
    wait_time = random.uniform(3, 10)
    order_log(f"Preparing {food} for table {table} (will take {wait_time:.1f}s)")

    await asyncio.sleep(wait_time)

    client.publish("FOOD", json.dumps({"food": food, "table": table}))
    order_log(f"Delivered {food} to table {table}")


def on_connect(client, userdata, flags, rc, properties=None):
    mqtt_log(f"Connected to {BROKER}:{PORT} (rc={rc})")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    """
    Callback function to handle incoming MQTT messages. Decodes the message payload
    and schedules the order handling coroutine.
    Parameters
    ----------
    client : mqtt.Client
        The MQTT client instance.
    userdata : any
        The private user data as set in Client() or userdata_set().
    msg : mqtt.MQTTMessage
        The MQTT message instance containing topic and payload.
    """
    try:
        payload = msg.payload.decode('utf-8')
    except Exception:
        error(f"Failed to decode message payload: {msg.payload}")
        return
    mqtt_log(f"Received -> topic: {msg.topic} | payload: {payload}")

    try:
        if EVENT_LOOP is None:
            asyncio.run(handle_order(client, payload))
        else:
            asyncio.run_coroutine_threadsafe(handle_order(client, payload), EVENT_LOOP)
    except Exception as e:
        error(f"Failed to schedule order handling: {e}")


def on_disconnect(client, userdata, rc):
    mqtt_log(f"Disconnected (rc={rc})")


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    mqtt_log(f"Subscribed (mid={mid}) granted_qos={granted_qos}")


# def on_log(client, userdata, level, buf):
    # print(f"MQTT log: {buf}")


async def main():
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
        error(f"Failed to connect to broker: {e}")
        return

    # save the running asyncio loop so callbacks from paho (other thread) can schedule coroutines
    global EVENT_LOOP
    EVENT_LOOP = asyncio.get_running_loop()

    client.loop_start()

    info("MQTT backend running — listening for messages. Press Ctrl+C to exit.")

    try:
        # run forever until interrupted
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        info("Shutting down MQTT backend...")
    finally:
        client.loop_stop()
        try:
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
