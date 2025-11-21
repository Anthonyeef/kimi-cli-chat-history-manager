<script lang="ts">
	export let message = 'Loading...';
	export let size: 'small' | 'medium' | 'large' = 'medium';
	
	const sizeClasses = {
		small: 'spinner-small',
		medium: 'spinner-medium',
		large: 'spinner-large'
	};
</script>

<div class="loading">
	<div class="spinner {sizeClasses[size]}"></div>
	{#if message}
		<span class="message">{message}</span>
	{/if}
</div>

<style>
	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 12px;
		padding: 2rem;
		color: #666;
	}
	
	.spinner {
		border: 3px solid #f3f3f3;
		border-top: 3px solid #0366d6;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}
	
	.spinner-small {
		width: 16px;
		height: 16px;
		border-width: 2px;
	}
	
	.spinner-medium {
		width: 24px;
		height: 24px;
		border-width: 3px;
	}
	
	.spinner-large {
		width: 40px;
		height: 40px;
		border-width: 4px;
	}
	
	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
	
	.message {
		font-size: 14px;
	}
</style>
