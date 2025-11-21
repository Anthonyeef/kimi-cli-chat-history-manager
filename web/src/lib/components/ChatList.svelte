<script lang="ts">
	import { goto } from '$app/navigation';
	import { selectChat } from '$lib/stores/chats';
	import type { Chat } from '$lib/types';
	import { formatDistanceToNow, parseISO } from 'date-fns';
	
	export let chats: Chat[] = [];
	
	function formatDate(dateString: string): string {
		try {
			const date = parseISO(dateString);
			return formatDistanceToNow(date, { addSuffix: true });
		} catch {
			return dateString;
		}
	}
	
	function getWorkspaceName(workspace: string): string {
		return workspace.split('/').pop() || workspace;
	}
	
	function handleChatClick(chat: Chat) {
		selectChat(chat);
		goto(`/chat/${chat.id}`);
	}
	
	function escapeHtml(text: string): string {
		const div = document.createElement('div');
		div.textContent = text;
		return div.innerHTML;
	}
</script>

<div class="chat-list">
	{#each chats as chat}
		<div 
			class="chat-item" 
			on:click={() => handleChatClick(chat)}
			role="button"
			tabindex="0"
			on:keypress={(e) => e.key === 'Enter' && handleChatClick(chat)}
		>
			<div class="chat-header">
				<div class="chat-title" title={chat.name}>
					{escapeHtml(chat.name)}
				</div>
				<div class="chat-date">
					{formatDate(chat.created)}
				</div>
			</div>
			
			<div class="chat-meta">
				<span class="workspace-tag" title={chat.workspace}>
					{getWorkspaceName(chat.workspace)}
				</span>
				<span class="message-count">
					{chat.message_count} messages
				</span>
				{#if chat.has_subsessions && chat.sub_sessions}
					<span class="sub-sessions">
						{chat.sub_sessions.length} sub-sessions
					</span>
				{/if}
			</div>
			
			{#if chat.has_subsessions}
				<div class="session-info">
					Session ID: <span class="session-id">{chat.id}</span>
				</div>
			{/if}
		</div>
	{/each}
</div>

<style>
	.chat-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}
	
	.chat-item {
		padding: 16px;
		background: white;
		border: 1px solid #e1e4e8;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s;
	}
	
	.chat-item:hover {
		border-color: #0366d6;
		box-shadow: 0 2px 8px rgba(3, 102, 214, 0.1);
		transform: translateY(-1px);
	}
	
	.chat-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 8px;
	}
	
	.chat-title {
		font-weight: 600;
		color: #24292e;
		flex: 1;
		margin-right: 12px;
		word-break: break-word;
	}
	
	.chat-date {
		font-size: 12px;
		color: #666;
		white-space: nowrap;
	}
	
	.chat-meta {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		font-size: 12px;
	}
	
	.workspace-tag {
		background: #e1f5fe;
		color: #0277bd;
		padding: 2px 8px;
		border-radius: 12px;
		font-weight: 500;
	}
	
	.message-count {
		color: #666;
	}
	
	.sub-sessions {
		color: #28a745;
		background: #d4edda;
		padding: 2px 8px;
		border-radius: 12px;
	}
	
	.session-info {
		margin-top: 8px;
		font-size: 11px;
		color: #888;
		font-family: monospace;
	}
	
	.session-id {
		font-weight: 500;
	}
</style>
