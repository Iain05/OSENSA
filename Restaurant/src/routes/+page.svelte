<script lang="ts">
	import { onMount } from 'svelte';
	import mqtt from 'mqtt';
	
	type MessageType = 'info' | 'success' | 'sent' | 'warning' | 'error';
	
	interface Message {
		text: string;
		type: MessageType;
		timestamp: string;
	}
	
	let client: mqtt.MqttClient | null = null;
	let connected: boolean = false;
	let messages: Message[] = [];
	let pingCount: number = 0;


	onMount(() => {
		client = mqtt.connect('ws://localhost:9001');

		client.on('connect', () => {
			connected = true;
			addMessage('Connected to MQTT broker', 'success');
			// subscribe to all topics so we receive messages from the broker
			client?.subscribe('#', (err) => {
				if (err) {
					addMessage('Failed to subscribe to topics', 'error');
				} else {
					addMessage('Subscribed to all topics', 'info');
				}
			});
		});

		// callback for incoming messages
		client.on('message', (topic: string, message: Buffer) => {
			const payload = message.toString();
			// Example handling: increment pingCount for PING messages
			if (topic === 'PING') {
				pingCount += 1;
				addMessage(`Ping received (${pingCount})`, 'info');
			} else if (topic === 'FOOD') {
				addMessage(`Received: FOOD: ${payload}`, 'success');
			} else {
				addMessage(`Received: ${topic}: ${payload}`, 'info');
			}
		});

		client.on('close', () => {
			connected = false;
			addMessage('Disconnected from MQTT broker', 'warning');
		});

		client.on('error', (err: Error) => {
			addMessage(`MQTT error: ${err.message}`, 'error');
		});
	})

	function sendOrder() {
		console.log('Sending order...');
		if (client && connected) {
			client.publish('ORDER', 'Pizza');
		}
	}

	function addMessage(text: string, type: MessageType): void {
		const timestamp = new Date().toLocaleTimeString();
		messages = [...messages, { text, type, timestamp }];
		// Keep only last 20 messages
		if (messages.length > 20) {
			messages = messages.slice(-20);
		}
	}
</script>

<div class="container">
	<h1>WebSocket Food Order</h1>
	
	<div class="status">
		<span class="status-indicator" class:connected class:disconnected={!connected}></span>
		<span>{connected ? 'Connected' : 'Disconnected'}</span>
	</div>

	<div class="controls">
		<button on:click={sendOrder} disabled={!connected} class="order-button">
			Send Order
		</button>
	</div>
    <div class="messages">
        <h3>Messages</h3>
        <div class="message-list">
            {#each messages as message}
                <div class="message {message.type}">
                    <span class="timestamp">[{message.timestamp}]</span>
                    <span class="text">{message.text}</span>
                </div>
            {/each}
        </div>
    </div>
</div>