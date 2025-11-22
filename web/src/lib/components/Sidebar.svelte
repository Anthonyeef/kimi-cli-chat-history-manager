<script lang="ts">
	import { onMount } from 'svelte';
	import { 
		workspaces, 
		selectedWorkspace, 
		searchQuery, 
		searchInMessages,
		isLoading,
		searchChats,
		loadChats,
		refreshData,
		clearSearch
	} from '$lib/stores/chats';
	import Heatmap from '$components/Heatmap.svelte';
	
	let searchInput = '';
	let searching = false;
	
	function handleSearch() {
		const query = searchInput.trim();
		searchQuery.set(query);
		
		if (query) {
			searching = true;
			searchChats(query, $searchInMessages);
		} else {
			clearSearch();
			searching = false;
		}
	}
	
	function handleWorkspaceChange(event: Event) {
		const select = event.target as HTMLSelectElement;
		selectedWorkspace.set(select.value);
		loadChats(); // Reload with filter
	}
	
	function handleRefresh() {
		refreshData();
	}
	
	// Debounce search input
	let searchTimeout: NodeJS.Timeout;
	function handleSearchInput() {
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(handleSearch, 300);
	}
</script>

<div class="sidebar">
	<div class="search-section">
		<div class="search-box">
			<input 
				type="text" 
				placeholder="Search conversations..."
				bind:value={searchInput}
				on:input={handleSearchInput}
				class="search-input"
			/>
			{#if searching || $isLoading}
				<span class="search-indicator">🔍</span>
			{/if}
		</div>
		
		<label class="checkbox-label">
			<input 
				type="checkbox" 
				bind:checked={$searchInMessages}
				on:change={handleSearch}
			/>
			<span>Search in messages</span>
		</label>
	</div>
	
	<div class="filters-section">
		<label class="filter-label">Workspace</label>
		<select 
			value={$selectedWorkspace} 
			on:change={handleWorkspaceChange}
			class="workspace-select"
		>
			<option value="">All Workspaces</option>
			{#each $workspaces as workspace}
				<option value={workspace.path}>{workspace.name}</option>
			{/each}
		</select>
	</div>
	
	<div class="heatmap-section">
		<Heatmap />
	</div>
	
	<div class="actions-section">
		<button on:click={handleRefresh} class="refresh-btn" disabled={$isLoading}>
			{#if $isLoading}
				<span class="spinner"></span>
			{:else}
				🔄
			{/if}
			Refresh
		</button>
	</div>
</div>

<style>
	.sidebar {
		width: 300px;
		background: #f6f8fa;
		border-right: 1px solid #e1e4e8;
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 20px;
		height: 100%;
		overflow-y: auto;
		overflow-x: hidden;
		scrollbar-gutter: stable;
	}
	
	/* Custom scrollbar styling to minimize overlap */
	.sidebar::-webkit-scrollbar {
		width: 8px;
	}
	
	.sidebar::-webkit-scrollbar-track {
		background: transparent;
	}
	
	.sidebar::-webkit-scrollbar-thumb {
		background: #d1d5db;
		border-radius: 4px;
		border: 2px solid #f6f8fa;
	}
	
	.sidebar::-webkit-scrollbar-thumb:hover {
		background: #9ca3af;
	}
	
	.search-section {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}
	
	.search-box {
		position: relative;
	}
	
	.search-input {
		width: 100%;
		padding: 10px 35px 10px 12px;
		border: 1px solid #ddd;
		border-radius: 6px;
		font-size: 14px;
	}
	
	.search-input:focus {
		outline: none;
		border-color: #0366d6;
		box-shadow: 0 0 0 3px rgba(3, 102, 214, 0.1);
	}
	
	.search-indicator {
		position: absolute;
		right: 10px;
		top: 50%;
		transform: translateY(-50%);
		font-size: 14px;
	}
	
	.checkbox-label {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 13px;
		color: #666;
		cursor: pointer;
	}
	
	.filters-section {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	
	.filter-label {
		font-size: 12px;
		font-weight: 600;
		color: #666;
		text-transform: uppercase;
	}
	
	.workspace-select {
		padding: 8px 12px;
		border: 1px solid #ddd;
		border-radius: 6px;
		font-size: 14px;
		background: white;
	}
	
	.heatmap-section {
		margin-top: auto;
		padding-top: 20px;
		padding-right: 0;
		border-top: 1px solid #e1e4e8;
		overflow: visible;
	}
	
	.actions-section {
		margin-top: 0;
	}
	
	.refresh-btn {
		width: 100%;
		padding: 10px 16px;
		background: #0366d6;
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		transition: background-color 0.2s;
	}
	
	.refresh-btn:hover:not(:disabled) {
		background: #0256c7;
	}
	
	.refresh-btn:disabled {
		background: #ccc;
		cursor: not-allowed;
	}
	
	.spinner {
		width: 14px;
		height: 14px;
		border: 2px solid white;
		border-top-color: transparent;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}
	
	@keyframes spin {
		100% { transform: rotate(360deg); }
	}
</style>