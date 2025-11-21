<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { chats, currentChat, isLoading, error } from '$lib/stores/chats';
	import ChatDetailView from '$components/ChatDetailView.svelte';
	import EmptyState from '$components/EmptyState.svelte';
	import { goto } from '$app/navigation';
	
	let messages = [];
	let chat: import('$lib/types').Chat | undefined;
	
	const chatId = $page.params.id;
	
	onMount(async () => {
		isLoading.set(true);
		error.set(null);
		
		try {
			// Find chat in store or fetch if not loaded
			chat = $chats.find(c => c.id === chatId);
			
			if (!chat && $chats.length > 0) {
				error.set('Chat not found');
				return;
			}
			
			if (chat) {
				currentChat.set(chat);
			}
			
			// Always fetch messages
			messages = await api.fetchChatDetail(chatId);
		} catch (e) {
			error.set(e instanceof Error ? e.message : 'Failed to load chat');
		} finally {
			isLoading.set(false);
		}
	});
	
	function handleBack() {
		goto('/');
	}
</script>

{#if $isLoading}
	<div class="container">
		<p>Loading conversation...</p>
	</div>
{:else if $error}
	<EmptyState 
		title="Error loading chat" 
		message={$error}
		on:action={handleBack}
		actionLabel="Back to list"
	/>
{:else if messages.length > 0}
	<ChatDetailView chat={chat || $currentChat} {messages} on:back={handleBack} />
{:else}
	<EmptyState 
		title="No messages found" 
		message="This conversation appears to be empty" 
		on:action={handleBack}
		actionLabel="Back to list"
	/>
{/if}

<style>
	.container {
		padding: 2rem;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
	}
</style>
