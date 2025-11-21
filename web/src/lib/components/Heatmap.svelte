<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { format, parseISO, subDays, startOfWeek } from 'date-fns';
	import type { ActivityData } from '$lib/types';
	
	let activity: ActivityData | null = null;
	let loading = false;
	let error: string | null = null;
	
	onMount(async () => {
		loading = true;
		try {
			activity = await api.fetchActivity(60); // Last 60 days
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load activity';
		} finally {
			loading = false;
		}
	});
	
	function getWeeksData() {
		if (!activity) return [];
		
		const weeks = [];
		const endDate = new Date();
		const startDate = subDays(endDate, 60);
		
		// Generate all dates in range
		const dates = [];
		for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
			dates.push(new Date(d));
		}
		
		// Group by weeks
		const weeksData = [];
		for (let i = 0; i < dates.length; i += 7) {
			const week = dates.slice(i, i + 7).map(date => {
				const dateStr = format(date, 'yyyy-MM-dd');
				const dayData = activity.activity.find(d => d.date === dateStr);
				return {
					date: dateStr,
					count: dayData?.count || 0,
					chats: dayData?.chats || []
				};
			});
			weeksData.push(week);
		}
		
		return weeksData;
	}
	
	function getLevel(count: number): number {
		if (count === 0) return 0;
		if (count <= 2) return 1;
		if (count <= 5) return 2;
		if (count <= 10) return 3;
		return 4;
	}
	
	function getTooltip(week: any[], dayIndex: number): string {
		const day = week[dayIndex];
		const date = format(parseISO(day.date), 'MMM dd, yyyy');
		if (day.count === 0) {
			return `${date}: No conversations`;
		}
		return `${date}: ${day.count} conversation${day.count !== 1 ? 's' : ''}`;
	}
</script>

<div class="heatmap-container">
	<h3 class="heatmap-title">Activity (Last 60 days)</h3>
	
	{#if loading}
		<div class="loading">Loading activity...</div>
	{:else if error}
		<div class="error">Unable to load activity data</div>
	{:else if activity}
		<div class="heatmap">
			<div class="weekday-labels">
				<span>Mon</span>
				<span>Wed</span>
				<span>Fri</span>
			</div>
			
			<div class="calendar">
				{#each getWeeksData() as week}
					<div class="week">
						{#each week as day, dayIndex}
							<div 
								class="day level-{getLevel(day.count)}"
								title={getTooltip(week, dayIndex)}
							/>
						{/each}
					</div>
				{/each}
			</div>
		</div>
		
		<div class="legend">
			<span>Less</span>
			<div class="legend-items">
				<div class="day level-0"></div>
				<div class="day level-1"></div>
				<div class="day level-2"></div>
				<div class="day level-3"></div>
				<div class="day level-4"></div>
			</div>
			<span>More</span>
		</div>
	{/if}
</div>

<style>
	.heatmap-container {
		background: white;
		border: 1px solid #e1e4e8;
		border-radius: 8px;
		padding: 20px;
		margin-bottom: 20px;
	}
	
	.heatmap-title {
		font-size: 16px;
		font-weight: 600;
		margin: 0 0 16px 0;
		color: #24292e;
	}
	
	.loading, .error {
		text-align: center;
		padding: 40px;
		color: #666;
	}
	
	.error {
		color: #d73a49;
	}
	
	.heatmap {
		display: flex;
		gap: 4px;
		align-items: flex-end;
	}
	
	.weekday-labels {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		height: 84px; /* 7 days * 12px */
		margin-right: 8px;
		font-size: 10px;
		color: #666;
	}
	
	.weekday-labels span {
		height: 12px;
		display: flex;
		align-items: center;
	}
	
	.calendar {
		display: flex;
		gap: 2px;
	}
	
	.week {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	
	.day {
		width: 10px;
		height: 10px;
		border-radius: 2px;
		background: #ebedf0;
		cursor: pointer;
	}
	
	.day:hover {
		stroke: #0366d6;
		stroke-width: 1px;
	}
	
	.day.level-0 { background: #ebedf0; }
	.day.level-1 { background: #9be9a8; }
	.day.level-2 { background: #40c463; }
	.day.level-3 { background: #30a14e; }
	.day.level-4 { background: #216e39; }
	
	.legend {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 8px;
		margin-top: 12px;
		font-size: 11px;
		color: #666;
	}
	
	.legend-items {
		display: flex;
		gap: 2px;
	}
</style>
