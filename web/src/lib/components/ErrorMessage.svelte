<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	
	export let title = 'Error';
	export let message: string | null = null;
	export let code: string | null = null;
	export let actionLabel: string | null = null;
	
	const dispatch = createEventDispatcher();
	
	function handleAction() {
		dispatch('action');
	}
	
	function handleCopy() {
		if (code) {
			navigator.clipboard.writeText(code);
		}
	}
</script>

<div class="error-message">
	<div class="error-icon">⚠️</div>
	<h2 class="error-title">{title}</h2>
	
	{#if message}
		<p class="error-text">{message}</p>
	{/if}
	
	{#if code}
		<div class="code-block">
			<code>{code}</code>
			<button class="copy-btn" on:click={handleCopy}>Copy</button>
		</div>
	{/if}
	
	{#if actionLabel}
		<button class="action-btn" on:click={handleAction}>
			{actionLabel}
		</button>
	{/if}
</div>

<style>
	.error-message {
		text-align: center;
		padding: 2rem;
		max-width: 500px;
		margin: 0 auto;
	}
	
	.error-icon {
		font-size: 48px;
		margin-bottom: 16px;
	}
	
	.error-title {
		font-size: 20px;
		font-weight: 600;
		color: #d73a49;
		margin: 0 0 12px 0;
	}
	
	.error-text {
		color: #666;
		margin-bottom: 20px;
		line-height: 1.5;
	}
	
	.code-block {
		background: #f6f8fa;
		border: 1px solid #e1e4e8;
		border-radius: 6px;
		padding: 12px;
		margin: 16px 0;
		position: relative;
		text-align: left;
	}
	
	.code-block code {
		font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
		font-size: 13px;
		color: #24292e;
		display: block;
		overflow-x: auto;
	}
	
	.copy-btn {
		position: absolute;
		top: 8px;
		right: 8px;
		padding: 4px 8px;
		background: white;
		border: 1px solid #ddd;
		border-radius: 4px;
		font-size: 11px;
		cursor: pointer;
	}
	
	.copy-btn:hover {
		background: #f6f8fa;
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
