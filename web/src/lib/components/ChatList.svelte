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
	
	function getInitials(name: string): string {
		return name.charAt(0).toUpperCase();
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
			title={chat.name}
		>
			<div class="chat-main">
				<div class="chat-title-row">
					<h3 class="chat-title">
						{escapeHtml(chat.name)}
					</h3>
					<span class="workspace-tag" title={chat.workspace}>
						{getWorkspaceName(chat.workspace)}
					</span>
				</div>
				
				<div class="chat-meta">
					<span class="message-info">
						{chat.message_count} message{chat.message_count !== 1 ? 's' : ''}
					</span>
					<span class="chat-date" title={chat.created}>
						{formatDate(chat.created)}
					</span>
					<span class="chat-id" title={chat.id}>
						{chat.id.substring(0, 8)}...
					</span>
				</div>
			</div>
			
			{#if chat.has_subsessions && chat.sub_sessions}
				<div class="chat-indicator" title="Has sub-sessions">
					<span class="indicator-dot"></span>
					<span class="indicator-text">{chat.sub_sessions.length}</span>
				</div>
			{/if}
		</div>
	{/each}
</div>

<style>
	.chat-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	
	.chat-item {
		display: flex;
		align-items: center;
		padding: 14px 16px;
		background: white;
		border: 1px solid #e1e4e8;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.2s ease;
		position: relative;
	}
	
	.chat-item:hover {
		border-color: #d0d7de;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
		transform: translateY(-1px);
	}
	
	.chat-item:active {
		transform: translateY(0);
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
	}
	
	.chat-main {
		flex: 1;
		min-width: 0; /* Allows text truncation to work */
	}
	
	.chat-title-row {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 6px;
	}
	
	.chat-title {
		font-size: 15px;
		font-weight: 500;
		color: #24292f;
		margin: 0;
		flex: 1;
		min-width: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		line-height: 1.4;
	}
	
	.workspace-tag {
		font-size: 11px;
		font-weight: 500;
		color: #57606a;
		background: #f6f8fa;
		padding: 2px 8px;
		border-radius: 12px;
		white-space: nowrap;
		border: 1px solid #d0d7de;
		flex-shrink: 0;
		max-width: 120px;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	
	.chat-meta {
		display: flex;
		align-items: center;
		gap: 12px;
		font-size: 12px;
		color: #656d76;
	}
	
	.message-info {
		font-weight: 400;
	}
	
	.chat-date {
		font-weight: 400;
	}
	
	.chat-id {
		font-family: 'SFMono-Regular', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Ubuntu Mono', monospace;
		font-size: 10px;
		color: #8c959f;
		background: #f6f8fa;
		padding: 2px 6px;
		border-radius: 4px;
		border: 1px solid #d0d7de;
		flex-shrink: 0;
	}
	
	.chat-indicator {
		display: flex;
		align-items: center;
		gap: 4px;
		margin-left: 12px;
		padding-left: 12px;
		border-left: 1px solid #e1e4e8;
	}
	
	.indicator-dot {
		width: 6px;
		height: 6px;
		background: #2da44e;
		border-radius: 50%;
	}
	
	.indicator-text {
		font-size: 11px;
		font-weight: 500;
		color: #2da44e;
	}
	
	/* Responsive adjustments */
	@media (max-width: 768px) {
		.chat-title-row {
			flex-wrap: wrap;
		}
		
		.workspace-tag {
			max-width: none;
		}
	}
	
	.chat-id {
		font-family: 'SFMono-Regular', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Ubuntu Mono', monospace;
		font-size: 10px;
		color: #8c959f;
		background: #f6f8fa;
		padding: 2px 6px;
		border-radius: 4px;
		border: 1px solid #d0d7de;
		flex-shrink: 0;
	}
</style>