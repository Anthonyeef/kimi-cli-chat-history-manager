<script lang="ts">
	import { onMount } from 'svelte';
	import { 
		loadChats, 
		filteredChats, 
		isLoading, 
		error,
		totalStats,
		searchQuery
	} from '$lib/stores/chats';
	import ChatList from '$components/ChatList.svelte';
	import EmptyState from '$components/EmptyState.svelte';
	import { api } from '$lib/api/client';
	
	onMount(() => {
		// Chats are loaded in layout, so we just need to ensure they're loaded
		loadChats();
	});
</script>

<div class="container">
	<div class="header-section">
		<h2>Dashboard</h2>
		<p class="subtitle">Browse your Kimi conversation history</p>
	</div>
	
	{#if $totalStats}
		<div class="stats-grid">
			<div class="stat-card">
				<div class="stat-value">{$totalStats.total}</div>
				<div class="stat-label">Total Chats</div>
			</div>
			<div class="stat-card">
				<div class="stat-value">{$totalStats.totalMessages}</div>
				<div class="stat-label">Total Messages</div>
			</div>
			<div class="stat-card">
				<div class="stat-value">{$totalStats.totalWorkspaces}</div>
				<div class="stat-label">Workspaces</div>
			</div>
		</div>
	{/if}
	
	{#if $isLoading}
		<div class="loading-state">
			<EmptyState title="Loading conversations..." message="Please wait" icon="⏳" />
		</div>
	{:else if $error}
		<EmptyState 
			title="Error loading conversations" 
			message={$error} 
		/>
	{:else if $filteredChats.length === 0}
		<EmptyState 
			title="No conversations found" 
			message={$searchQuery ? 'No chats match your search criteria' : 'Try adjusting your search or filters'} 
		/>
	{:else}
		<section class="chat-section">
			<h3 class="section-title">Conversations</h3>
			<ChatList chats={$filteredChats} />
		</section>
	{/if}
</div>

<style>
	.container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 24px;
	}
	
	.header-section {
		margin-bottom: 24px;
	}
	
	h2 {
		font-size: 28px;
		font-weight: 700;
		color: #24292e;
		margin: 0 0 8px 0;
	}
	
	.subtitle {
		color: #666;
		font-size: 16px;
		margin: 0;
	}
	
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 16px;
		margin-bottom: 24px;
	}
	
	.stat-card {
		background: white;
		border: 1px solid #e1e4e8;
		border-radius: 8px;
		padding: 20px;
		text-align: center;
	}
	
	.stat-value {
		font-size: 32px;
		font-weight: 700;
		color: #0366d6;
		margin-bottom: 4px;
	}
	
	.stat-label {
		font-size: 14px;
		color: #666;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}
	
	.loading-state {
		text-align: center;
		padding: 40px;
	}
	
	.chat-section {
		margin-top: 24px;
	}
	
	.section-title {
		font-size: 20px;
		font-weight: 600;
		color: #24292e;
		margin: 0 0 16px 0;
	}
</style>
