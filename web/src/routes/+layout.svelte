<script lang="ts">
	import { onMount } from 'svelte';
	import { loadChats } from '$lib/stores/chats';
	import { api } from '$lib/api/client';
	import Header from '$components/Header.svelte';
	import Sidebar from '$components/Sidebar.svelte';
	import Loading from '$components/Loading.svelte';
	import ErrorMessage from '$components/ErrorMessage.svelte';
	import '../app.css';
	
	let apiAvailable = false;
	let checkingApi = true;
	
	onMount(async () => {
		try {
			await api.fetchHealth();
			apiAvailable = true;
			await loadChats();
		} catch (e) {
			console.error('API not available:', e);
		} finally {
			checkingApi = false;
		}
	});
</script>

{#if checkingApi}
	<Loading message="Connecting to API..." />
{:else if !apiAvailable}
	<div class="error-container">
		<ErrorMessage 
			title="⚠️ API Server Not Running"
			message="Please start the API server first:"
			code="cd server && python3 -m uvicorn app:app --port 8001 --reload"
			on:action={() => window.location.reload()}
			actionLabel="Retry"
		/>
	</div>
{:else}
	<div class="app">
		<Header />
		<div class="main">
			<Sidebar />
			<main class="content">
				<slot />
			</main>
		</div>
	</div>
{/if}

<style>
	.app {
		height: 100vh;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}
	
	.main {
		display: flex;
		flex: 1;
		overflow: hidden;
	}
	
	.content {
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
	}
	
	.error-container {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100vh;
		padding: 2rem;
	}
</style>
