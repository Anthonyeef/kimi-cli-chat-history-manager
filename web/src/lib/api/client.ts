import type { Chat, Message, Workspace, SearchResult, Stats, ActivityData, ChatFilters, SearchOptions } from '$lib/types';

export class API {
	private baseUrl: string;

	constructor() {
		// Use relative URL - works in both dev (proxy) and production
		this.baseUrl = '/api';
	}

	private async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
		const url = `${this.baseUrl}${endpoint}`;
		const response = await fetch(url, {
			...options,
			headers: {
				'Accept': 'application/json',
				...options.headers
			}
		});

		if (!response.ok) {
			throw new Error(`HTTP ${response.status}: ${response.statusText}`);
		}

		return response.json();
	}

	async fetchHealth(): Promise<{ status: string; service: string }> {
		return this.fetch('/v1/health');
	}

	async fetchChats(filters: ChatFilters = {}): Promise<Chat[]> {
		const params = new URLSearchParams();
		if (filters.workspace) params.append('workspace', filters.workspace);
		if (filters.limit) params.append('limit', filters.limit.toString());
		if (filters.offset) params.append('offset', filters.offset.toString());
		if (filters.refresh) params.append('refresh', 'true');

		return this.fetch(`/v1/chats?${params}`);
	}

	async fetchChatDetail(chatId: string): Promise<Message[]> {
		return this.fetch(`/v1/chats/${chatId}`);
	}

	async fetchWorkspaces(): Promise<Workspace[]> {
		return this.fetch('/v1/workspaces');
	}

	async search(options: SearchOptions): Promise<SearchResult[]> {
		const params = new URLSearchParams();
		params.append('q', options.query);
		params.append('search_messages', (options.searchMessages ?? false).toString());
		if (options.workspace) params.append('workspace', options.workspace);

		return this.fetch(`/v1/search?${params}`);
	}

	async refreshChats(): Promise<{ status: string; message: string }> {
		return this.fetch('/v1/refresh', { method: 'POST' });
	}

	async fetchStats(): Promise<Stats> {
		return this.fetch('/v1/stats');
	}

	async fetchActivity(days: number = 365): Promise<ActivityData> {
		return this.fetch(`/v1/activity?days=${days}`);
	}
}

export const api = new API();
