import { writable, derived } from 'svelte/store';
import type { Chat, Workspace, SearchResult } from '$lib/types';
import { api } from '$lib/api/client';

// Main data stores
export const chats = writable<Chat[]>([]);
export const currentChat = writable<Chat | null>(null);
export const workspaces = writable<Workspace[]>([]);
export const searchResults = writable<SearchResult[]>([]);

// UI state stores
export const isLoading = writable(false);
export const error = writable<string | null>(null);
export const searchQuery = writable('');
export const selectedWorkspace = writable<string>('');
export const searchInMessages = writable(false);

// Derived stores for computed values
export const filteredChats = derived(
	[chats, searchResults, searchQuery],
	([$chats, $searchResults, $searchQuery]) => {
		if ($searchQuery && $searchResults.length > 0) {
			// Return chats that have search results
			const chatIds = new Set($searchResults.map(r => r.chat.id));
			return $chats.filter(chat => chatIds.has(chat.id));
		}
		return $chats;
	}
);

export const totalStats = derived(chats, ($chats) => {
	return {
		total: $chats.length,
		totalMessages: $chats.reduce((sum, chat) => sum + chat.message_count, 0),
		totalWorkspaces: new Set($chats.map(c => c.workspace)).size
	};
});

// Actions
export async function loadChats() {
	isLoading.set(true);
	error.set(null);
	try {
		const [chatsData, workspacesData] = await Promise.all([
			api.fetchChats(),
			api.fetchWorkspaces()
		]);
		chats.set(chatsData);
		workspaces.set(workspacesData);
	} catch (e) {
		error.set(e instanceof Error ? e.message : 'Failed to load chats');
	} finally {
		isLoading.set(false);
	}
}

export async function searchChats(query: string, searchMessages = false) {
	if (!query.trim()) {
		searchResults.set([]);
		return;
	}

	isLoading.set(true);
	error.set(null);
	try {
		const results = await api.search({ query, searchMessages });
		searchResults.set(results);
	} catch (e) {
		error.set(e instanceof Error ? e.message : 'Search failed');
		searchResults.set([]);
	} finally {
		isLoading.set(false);
	}
}

export async function refreshData() {
	isLoading.set(true);
	error.set(null);
	try {
		await api.refreshChats();
		await loadChats();
	} catch (e) {
		error.set(e instanceof Error ? e.message : 'Refresh failed');
	} finally {
		isLoading.set(false);
	}
}

export function selectChat(chat: Chat) {
	currentChat.set(chat);
}

export function clearSearch() {
	searchQuery.set('');
	searchResults.set([]);
}

// Auto-refresh every 5 minutes
setInterval(() => {
	refreshData();
}, 5 * 60 * 1000);
