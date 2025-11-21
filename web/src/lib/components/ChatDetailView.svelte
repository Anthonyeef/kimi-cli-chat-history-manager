<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { formatDistanceToNow, parseISO } from 'date-fns';
	import type { Chat, Message } from '$lib/types';
	import MessageComponent from './Message.svelte';
	
	export let chat: Chat | null = null;
	export let messages: Message[] = [];
	
	const dispatch = createEventDispatcher();
	
	function handleBack() {
		dispatch('back');
	}
	
	function formatDate(dateString: string | null): string {
		if (!dateString) return 'Unknown';
		try {
			const date = parseISO(dateString);
			return formatDistanceToNow(date, { addSuffix: true });
		} catch {
			return dateString;
		}
	}
	
	function handleCopySessionId() {
		if (chat?.id) {
			navigator.clipboard.writeText(chat.id);
		}
	}
	
	function handleExport() {
		if (!chat || messages.length === 0) return;
		
		const content = messages.map(msg => {
			const role = msg.role.toUpperCase();
			const content = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content, null, 2);
			return `## ${role}\n\n${content}\n`;
		}).join('\n');
		
		const markdown = `# ${chat.name}\n\n${content}`;
		const blob = new Blob([markdown], { type: 'text/markdown' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `${chat.name}.md`;
		a.click();
		URL.revokeObjectURL(url);
	}
</script>

<div class="chat-detail">
	<header class="detail-header">
		<button class="back-btn" on:click={handleBack}>
			← Back to list
		</button>
		
		{#if chat}
			<div class="chat-info">
				<h1 class="chat-title">{chat.name}</h1>
				<div class="chat-meta">
					<span>Created {formatDate(chat.created)}</span>
					<span>•</span>
					<span>{chat.message_count} messages</span>
				</div>
			</div>
			
			<div class="actions">
				<button class="action-btn" on:click={handleCopySessionId} title="Copy Session ID">
					📋 Copy ID
				</button>
				<button class="action-btn primary" on:click={handleExport}>
					💾 Export Markdown
				</button>
			</div>
		{/if}
	</header>
	
	<div class="messages-container">
		{#if messages.length === 0}
			<div class="empty-state">
				<p>No messages in this conversation.</p>
			</div>
		{:else}
			{#each messages as message}
				<MessageComponent {message} />
			{/each}
		{/if}
	</div>
</div>

<style>
	.chat-detail {
		height: 100%;
		display: flex;
		flex-direction: column;
	}
	
	.detail-header {
		flex-shrink: 0;
		padding: 20px;
		border-bottom: 1px solid #e1e4e8;
		background: white;
	}
	
	.back-btn {
		background: none;
		border: none;
		color: #0366d6;
		cursor: pointer;
		font-size: 14px;
		padding: 8px 12px;
		margin-bottom: 16px;
		border-radius: 6px;
		transition: background-color 0.2s;
	}
	
	.back-btn:hover {
		background-color: #f6f8fa;
	}
	
	.chat-info {
		margin-bottom: 16px;
	}
	
	.chat-title {
		font-size: 24px;
		font-weight: 600;
		color: #24292e;
		margin: 0 0 8px 0;
	}
	
	.chat-meta {
		color: #666;
		font-size: 14px;
		display: flex;
		gap: 8px;
		align-items: center;
	}
	
	.actions {
		display: flex;
		gap: 12px;
	}
	
	.action-btn {
		padding: 8px 16px;
		border: 1px solid #ddd;
		background: white;
		border-radius: 6px;
		font-size: 14px;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.action-btn:hover {
		background: #f6f8fa;
		border-color: #0366d6;
	}
	
	.action-btn.primary {
		background: #0366d6;
		color: white;
		border-color: #0366d6;
	}
	
	.action-btn.primary:hover {
		background: #0256c7;
	}
	
	.messages-container {
		flex: 1;
		overflow-y: auto;
		padding: 20px;
		background: #f6f8fa;
	}
	
	.empty-state {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 200px;
		color: #666;
		font-style: italic;
	}
</style>
