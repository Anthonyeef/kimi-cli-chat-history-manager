<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	
	export let title = 'Nothing here';
	export let message: string | null = null;
	export let icon = '🤷';
	export let actionLabel: string | null = null;
	
	const dispatch = createEventDispatcher();
	
	function handleAction() {
		dispatch('action');
	}
</script>

<div class="empty-state">
	<div class="icon">{icon}</div>
	<h3 class="title">{title}</h3>
	
	{#if message}
		<p class="message">{message}</p>
	{/if}
	
	{#if actionLabel}
		<button class="action-btn" on:click={handleAction}>
			{actionLabel}
		</button>
	{/if}
</div>

<style>
	.empty-state {
		text-align: center;
		padding: 3rem 2rem;
		color: #666;
	}
	
	.icon {
		font-size: 48px;
		margin-bottom: 16px;
		opacity: 0.7;
	}
	
	.title {
		font-size: 18px;
		font-weight: 600;
		color: #444;
		margin: 0 0 8px 0;
	}
	
	.message {
		font-size: 14px;
		margin-bottom: 20px;
		max-width: 400px;
		margin-left: auto;
		margin-right: auto;
		line-height: 1.5;
	}
	
	.action-btn {
		padding: 10px 20px;
		background: #0366d6;
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s;
	}
	
	.action-btn:hover {
		background: #0256c7;
	}
</style>
