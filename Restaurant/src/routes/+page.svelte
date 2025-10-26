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

	// inputs for 4 tables (indexed 0..3, displayed as tables 1..4)
	let orderInputs: string[] = ['', '', '', ''];

	
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
			if (topic === 'FOOD') {
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
			client.publish('ORDER', JSON.stringify({ food: 'Pizza', table: 1 }));
		}
	}

	// send an order for a specific table (tableIndex 0..3)
	function sendTableOrder(tableIndex: number) {
		const table = tableIndex + 1;
		const food = orderInputs[tableIndex] || 'Unknown';
		if (client && connected) {
			client.publish('ORDER', JSON.stringify({ food, table }));
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

	<div class="tables">
		{#each [0,1,2,3] as i}
			<div class="table">
				<h4>Table {i + 1}</h4>
				<input type="text" bind:value={orderInputs[i]} placeholder="Food item" />
				<button on:click={() => sendTableOrder(i)} disabled={!connected}>Place Order</button>
			</div>
		{/each}
	</div>

    <div class="messages">
        <h3>Messages</h3>
        <div class="message-list">
            {#each [...messages].reverse() as message}
                <div class="message {message.type}">
                    <span class="timestamp">[{message.timestamp}]</span>
                    <span class="text">{message.text}</span>
                </div>
            {/each}
        </div>
    </div>
</div>

<style>
	.container { padding: 1rem; font-family: system-ui, sans-serif; }
	.tables { display: flex; gap: 1rem; margin: 1rem 0; }
	.table { border: 1px solid #ccc; padding: 0.5rem; width: 12rem; border-radius: 6px; }
	.table h4 { margin: 0 0 0.5rem 0; }
	.table input { width: 100%; box-sizing: border-box; padding: 0.25rem; margin-bottom: 0.5rem; }
	.table button { width: 100%; }
</style>