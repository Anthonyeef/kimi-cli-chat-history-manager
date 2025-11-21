// API Response Types

export interface Message {
	role: 'user' | 'assistant' | 'tool';
	content: string | Array<{ type: string; [key: string]: any }>;
	tool_calls?: Array<any>;
	tool_call_id?: string;
	timestamp?: string | null;
}

export interface Chat {
	id: string;
	name: string;
	workspace: string;
	workspace_hash: string;
	created: string; // ISO date string
	message_count: number;
	has_subsessions: boolean;
	sub_sessions?: Array<{ id: string; name: string }>;
	file_path?: string;
}

export interface Workspace {
	name: string;
	path: string;
	hash: string;
	last_session_id: string | null;
	session_count: number;
}

export interface SearchResult {
	chat: Chat;
	match_count: number;
	matches?: Array<{
		content: string;
		role: string;
	};
}

export interface Stats {
	total_chats: number;
	total_messages: number;
	total_workspaces: number;
	date_range_start: string | null;
	date_range_end: string | null;
}

export interface ActivityData {
	activity: Array<{
		date: string; // ISO date
		count: number;
		chats: Array<{
			id: string;
			name: string;
			workspace: string;
		}>;
	}>;
}

export interface ChatFilters {
	workspace?: string;
	limit?: number;
	offset?: number;
	refresh?: boolean;
}

export interface SearchOptions {
	query: string;
	searchMessages?: boolean;
	workspace?: string;
}
