<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import hljs from 'highlight.js';
	import 'highlight.js/styles/github.css';
	import type { Message } from '$lib/types';
	
	export let message: Message;
	
	const dispatch = createEventDispatcher();
	
	function formatContent(content: Message['content']): string {
		if (typeof content === 'string') {
			return content;
		}
		if (Array.isArray(content)) {
			return content.map(part => {
				if (part.type === 'think') {
					return `<div class="think-block"><strong>Thinking:</strong><br/>${escapeHtml(part.think)}</div>`;
				} else if (part.type === 'text') {
					return escapeHtml(part.text);
				}
				return '';
			}).join('\n');
		}
		return String(content);
	}
	
	function escapeHtml(text: string): string {
		const div = document.createElement('div');
		div.textContent = text;
		return div.innerHTML;
	}
	
	function enhanceCodeBlocks(html: string): string {
		// Simple code block highlighting
		return html.replace(/```(\w+)?\n([\s\S]*?)```/g, (_match, lang, code) => {
			const language = lang || 'plaintext';
			try {
				if (hljs.getLanguage(language)) {
					const highlighted = hljs.highlight(code, { language }).value;
					return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`;
				}
			} catch {
				// Fallback to plain text if highlighting fails
			}
			return `<pre><code>${escapeHtml(code)}</code></pre>`;
		});
	}
	
	function formatAndHighlight(content: string): string {
		let html = escapeHtml(content);
		// Convert markdown-style code blocks
		html = enhanceCodeBlocks(html);
		// Convert newlines to <br>
		html = html.replace(/\n/g, '<br>');
		return html;
	}
	
	function renderToolCalls(toolCalls: any[]): string {
		if (!toolCalls || toolCalls.length === 0) return '';
		
		const calls = toolCalls.map(call => {
			const name = call.function?.name || 'unknown';
			const args = call.function?.arguments || '{}';
			try {
				const parsed = JSON.parse(args);
				return `<div class="tool-call"><strong>🔧 ${name}</strong><pre>${JSON.stringify(parsed, null, 2)}</pre></div>`;
			} catch {
				return `<div class="tool-call"><strong>🔧 ${name}</strong><pre>${args}</pre></div>`;
			}
		}).join('\n');
		
		return `<div class="tool-calls">${calls}</div>`;
	}
	
	const roleClass = message.role;
	const content = message.tool_calls 
		? renderToolCalls(message.tool_calls)
		: formatAndHighlight(formatContent(message.content));
</script>

<div class="message {roleClass}">
	<div class="message-role">{message.role}</div>
	<div class="message-content">
		<!-- eslint-disable svelte/no-at-html-tags -->
		{@html content}
		<!-- eslint-enable svelte/no-at-html-tags -->
	</div>
</div>

<style>
	.message {
		margin-bottom: 20px;
		padding: 16px;
		background: white;
		border-radius: 8px;
		border-left: 4px solid #ddd;
	}
	
	.message.user {
		border-left-color: #0366d6;
		background: #f1f8ff;
	}
	
	.message.assistant {
		border-left-color: #28a745;
	}
	
	.message.tool {
		border-left-color: #ffc107;
		background: #fff8e1;
	}
	
	.message-role {
		font-size: 12px;
		font-weight: 600;
		text-transform: uppercase;
		color: #666;
		margin-bottom: 8px;
		letter-spacing: 0.5px;
	}
	
	.message-content {
		line-height: 1.6;
		color: #24292e;
	}
	
	.message-content :global(pre) {
		background: #f6f8fa;
		border: 1px solid #e1e4e8;
		border-radius: 6px;
		padding: 12px;
		overflow-x: auto;
		margin: 12px 0;
	}
	
	.message-content :global(code) {
		font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
		font-size: 13px;
	}
	
	.message-content :global(pre code) {
		background: none;
		border: none;
		padding: 0;
	}
	
	.message-content :global(.tool-calls) {
		margin-top: 12px;
	}
	
	.message-content :global(.tool-call) {
		background: #fff3cd;
		border: 1px solid #ffeaa7;
		border-radius: 6px;
		padding: 12px;
		margin-bottom: 8px;
		font-size: 13px;
	}
	
	.message-content :global(.think-block) {
		background: #e8f5e9;
		border: 1px solid #c8e6c9;
		border-radius: 6px;
		padding: 12px;
		margin: 8px 0;
		font-style: italic;
		color: #2e7d32;
	}
</style>
