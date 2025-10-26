<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let tableNumber: number;
	export let connected = false;

	let input = '';
	let items: string[] = [];

	const dispatch = createEventDispatcher();

	export function addItem(food: string) {
		items = [...items, food];
	}

	function placeOrder() {
        if (!input) return;
		dispatch('placeOrder', { table: tableNumber, food: input });
		input = '';
	}
</script>

<div class="table-component">
	<h4>Table {tableNumber}</h4>
	<input type="text" bind:value={input} placeholder="Food item" maxlength="50" />
	<button on:click={placeOrder} disabled={!connected}>Place Order</button>

	<div class="received">
		<h5>Received</h5>
		{#if items.length > 0}
			<ul class="received-list">
				{#each items as item}
					<li>{item}</li>
				{/each}
			</ul>
		{:else}
			<div class="no-items">—</div>
		{/if}
	</div>
</div>

<style>
	.table-component { padding: 0.25rem; }
	.table-component h4 { margin: 0 0 0.5rem 0; }
	.table-component input { width: 100%; box-sizing: border-box; padding: 0.25rem; margin-bottom: 0.5rem; }
	.table-component button { width: 100%; }
	.received { margin-top: 0.5rem; }
	.received-list { list-style: none; padding: 0; margin: 0; max-height: 8rem; overflow: auto; }
	.received-list li { background: #f7f7f7; margin: 0 0 0.25rem 0; padding: 0.25rem; border-radius: 4px; font-size: 0.9rem; }
	.no-items { color: #888; font-size: 0.9rem; }
</style>
