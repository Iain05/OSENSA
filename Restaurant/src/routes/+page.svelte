<script lang="ts">
	import { onMount } from 'svelte';
	
	type MessageType = 'info' | 'success' | 'sent' | 'warning' | 'error';
	
	interface Message {
		text: string;
		type: MessageType;
		timestamp: string;
	}
	
	let websocket: WebSocket | null = null;
	let connected: boolean = false;
	let messages: Message[] = [];
	let pingCount: number = 0;

	onMount(() => {
		connectWebSocket();
		return () => {
			if (websocket) {
				websocket.close();
			}
		};
	});

	function connectWebSocket() {
		try {
			websocket = new WebSocket('ws://localhost:8765');
			
			websocket.onopen = () => {
				connected = true;
				addMessage('Connected to server', 'info');
			};
			
			websocket.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);
					if (data.type === 'FOOD') {
						addMessage(`Received: ${data.payload}`, 'success');
					}
				} catch (error) {
					const errorMessage = error instanceof Error ? error.message : 'Unknown error';
					addMessage(`Error parsing message: ${errorMessage}`, 'error');
				}
			};
			
			websocket.onclose = () => {
				connected = false;
				addMessage('Disconnected from server', 'warning');
			};
			
			websocket.onerror = (error) => {
				addMessage('WebSocket error occurred', 'error');
				console.error('WebSocket error:', error);
			};
		} catch (error) {
			const errorMessage = error instanceof Error ? error.message : 'Unknown error';
			addMessage(`Connection error: ${errorMessage}`, 'error');
		}
	}

	function sendOrder() {
		if (websocket && connected) {
			pingCount++;
			const message = {
				type: 'ORDER',
				payload: `Order ${pingCount}`
			};
			websocket.send(JSON.stringify(message));
			addMessage(`Sent: ORDER: "${message.payload}"`, 'sent');
		} else {
			addMessage('Not connected to server', 'error');
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