<script lang="ts">
	import { onMount } from 'svelte';
	import mqtt from 'mqtt';
	import Table from '$lib/Table.svelte';
	
	type MessageType = 'info' | 'success' | 'sent' | 'warning' | 'error';
	
	interface Message {
		text: string;
		type: MessageType;
		timestamp: string;
	}
	
	let client: mqtt.MqttClient | null = null;
	let connected: boolean = false;
	let messages: Message[] = [];
	let tableRefs: Array<any> = [];
	const tables = [1, 2, 3, 4];

	
	onMount(() => {
		client = mqtt.connect('ws://localhost:9001');

		client.on('connect', () => {
			connected = true;
			addMessage('Connected to MQTT broker', 'success');
			client?.subscribe('#', (err) => {
				if (err) {
					addMessage('Failed to subscribe to topics', 'error');
				} else {
					addMessage('Subscribed to all topics', 'info');
				}
			});
		});

		client.on('message', (topic: string, message: Buffer) => {
			const payload = message.toString();
			console.log(message);
			if (topic === 'FOOD') {
				try {
					const data = JSON.parse(payload);
					const table = Number(data.table);
					const foodName = String(data.food);

					// bad table number
					if (Number.isNaN(table) || table < 1 || table > tables.length) {
						addMessage(`Received FOOD for unknown table: ${payload}`, 'warning');
						return;
					}

					const ref = tableRefs[table - 1];
					ref.addItem(foodName);
					addMessage(`Received FOOD for table ${table}: ${foodName}`, 'success');

				} catch (e) {
					addMessage(`Bad FOOD payload: ${payload}`, 'error');
				}
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
	});

	function handlePlaceOrder(event: CustomEvent<{ table: number; food: string }>) {
		const { table, food } = event.detail;
		if (client && connected) {
			client.publish('ORDER', JSON.stringify({ food, table }));
			addMessage(`Sent ORDER for table ${table}: ${food}`, 'sent');
		} else {
			addMessage(`Cannot send ORDER, not connected`, 'warning');
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
	<h1>The Mosquitto Diner</h1>

	<p>Welcome to the Mosquitto Diner! Once an order is placed it will take between 3 and 10 seconds to be prepared and sent back to the customer.</p>
	
	<div class="status">
		<span class="status-indicator" class:connected class:disconnected={!connected}></span>
		<span>{connected ? 'Connected' : 'Disconnected'}</span>
	</div>

	<div class="tables">
		{#each tables as table}
			<div class="table">
				<Table tableNumber={table} bind:this={tableRefs[table - 1]} on:placeOrder={handlePlaceOrder} {connected} />
			</div>
		{/each}
	</div>

    <div class="messages">
        <h3>Debug Messages</h3>
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
	.table { border: 1px solid #ccc; padding: 0.5rem; width: 14rem; border-radius: 6px; }
	.received { margin-top: 0.5rem; }
	.received-list { list-style: none; padding: 0; margin: 0; max-height: 8rem; overflow: auto; }
	.no-items { color: #888; font-size: 0.9rem; }
</style>