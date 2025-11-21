<script lang="ts">
	import { goto } from '$app/navigation';
	import { currentChat } from '$lib/stores/chats';
	
	function goHome() {
		goto('/');
	}
</script>

<header class="header">
	<div class="header-left">
		<button class="logo" on:click={goHome}>
			<span class="logo-icon">🤖</span>
			<span class="logo-text">Kimi Chat History</span>
		</button>
		{#if $currentChat}
			<span class="separator">›</span>
			<span class="current-chat">{$currentChat.name}</span>
		{/if}
	</div>
</header>

<style>
	.header {
		height: 60px;
		background: #24292e;
		color: white;
		display: flex;
		align-items: center;
		padding: 0 20px;
		border-bottom: 1px solid #444;
		flex-shrink: 0;
	}
	
	.header-left {
		display: flex;
		align-items: center;
		gap: 10px;
	}
	
	.logo {
		display: flex;
		align-items: center;
		gap: 8px;
		background: none;
		border: none;
		color: white;
		font-size: 18px;
		font-weight: 600;
		cursor: pointer;
		padding: 8px 12px;
		border-radius: 6px;
		transition: background-color 0.2s;
	}
	
	.logo:hover {
		background-color: rgba(255, 255, 255, 0.1);
	}
	
	.logo-icon {
		font-size: 20px;
	}
	
	.separator {
		color: #888;
		font-size: 20px;
	}
	
	.current-chat {
		font-size: 14px;
		color: #ccc;
		max-width: 400px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
</style>
