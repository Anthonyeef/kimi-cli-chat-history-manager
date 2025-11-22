<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { format, parseISO, subWeeks } from 'date-fns';
	import type { ActivityData } from '$lib/types';
	
	let activity: ActivityData | null = null;
	let loading = false;
	let error: string | null = null;
	let heatmapElement: HTMLDivElement;
	let resizeObserver: ResizeObserver;
	let hoveredDay: { date: string; count: number; chats: any[] } | null = null;
	let tooltipPosition = { x: 0, y: 0 };
	let containerWidth = 0; // Reactive variable to force recalculation
	
	// Size constants (in pixels)
	const DAY_SIZE = 11; // 10px square + 1px gap
	const WEEK_GAP = 2;
	const WEEKDAY_LABELS_WIDTH = 16; // Width for M/W/F labels (reduced from 26px)
	const MIN_WEEKS = 16; // Show at least 16 weeks (4 months)
	const MAX_WEEKS = 52; // Maximum weeks to show
	
	onMount(async () => {
		loading = true;
		try {
			activity = await api.fetchActivity(365);
			
			// Set up ResizeObserver to track container size
			if (heatmapElement && typeof ResizeObserver !== 'undefined') {
				resizeObserver = new ResizeObserver(() => {
					// Force re-render by updating reactive variable
					containerWidth = heatmapElement.offsetWidth;
				});
				resizeObserver.observe(heatmapElement);
				// Initial measurement after a small delay to ensure sidebar is rendered
				setTimeout(() => {
					containerWidth = heatmapElement.offsetWidth;
				}, 100);
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load activity';
		} finally {
			loading = false;
		}
		
		return () => {
			if (resizeObserver) {
				resizeObserver.disconnect();
			}
		};
	});
	
	// Calculate how many weeks can fit in the available width
	// Using containerWidth to make it reactive
	$: weekCount = (() => {
		if (!heatmapElement || (containerWidth === 0 && heatmapElement.offsetWidth === 0)) {
			return MIN_WEEKS;
		}
		
		const currentWidth = containerWidth || heatmapElement.offsetWidth;
		
		// Account for container padding (20px on each side = 40px total)
		const containerPadding = 40;
		const availableContainerWidth = currentWidth - containerPadding;
		
		// Check if parent sidebar has scrollbar by finding the sidebar element
		let scrollbarWidth = 0;
		try {
			const sidebar = heatmapElement.closest('.sidebar');
			if (sidebar && sidebar.scrollHeight > sidebar.clientHeight) {
				// Scrollbar is present, account for it (custom scrollbar is 8px wide)
				// But scrollbar-gutter: stable reserves space, so we might not need this
				// However, we'll use a small buffer just in case
				scrollbarWidth = 0; // scrollbar-gutter handles it, but we keep the check for fallback
			}
		} catch (e) {
			// If we can't find sidebar, assume no scrollbar
		}
		
		// Available width = container width - weekday labels - scrollbar buffer - margin
		// Use WEEKDAY_LABELS_WIDTH + margin-right (6px) for weekday labels
		// scrollbar-gutter: stable should reserve space, but we add a small buffer for fallback
		const weekdayLabelsTotal = WEEKDAY_LABELS_WIDTH + 6; // width + margin-right (reduced from 8px)
		const scrollbarBuffer = 2; // Small buffer for scrollbar-gutter fallback
		const availableWidth = availableContainerWidth - weekdayLabelsTotal - scrollbarWidth - scrollbarBuffer;
		
		// Each day is 10px wide, so each week column is 10px wide
		// Plus WEEK_GAP (2px) between week columns (but not after the last week)
		const dayWidth = 10; // Each day square is 10px wide
		const weekColumnWidth = dayWidth; // Each week column is 10px wide (7 days stacked vertically)
		const gapBetweenWeeks = WEEK_GAP; // 2px gap between week columns
		
		// Calculate: availableWidth = (weekCount * weekColumnWidth) + ((weekCount - 1) * gapBetweenWeeks)
		// Solving for weekCount: weekCount = (availableWidth + gapBetweenWeeks) / (weekColumnWidth + gapBetweenWeeks)
		const weeksFromWidth = Math.floor((availableWidth + gapBetweenWeeks) / (weekColumnWidth + gapBetweenWeeks));
		
		// Ensure we show at least MIN_WEEKS but not more than what fits
		const calculated = Math.min(MAX_WEEKS, Math.max(MIN_WEEKS, Math.max(0, weeksFromWidth)));
		return calculated;
	})();
	
	function getWeekCount(): number {
		return weekCount;
	}
	
	// Get the weeks data based on available width
	function getWeeksData() {
		if (!activity) return [];
		
		const weekCount = getWeekCount();
		const endDate = new Date();
		const weeksData = [];
		
		for (let week = 0; week < weekCount; week++) {
			const weekStart = subWeeks(endDate, weekCount - week - 1);
			const weekData = [];
			
			for (let dayOfWeek = 0; dayOfWeek < 7; dayOfWeek++) {
				const date = new Date(weekStart);
				date.setDate(date.getDate() - (6 - dayOfWeek));
				
				const dateStr = format(date, 'yyyy-MM-dd');
				const dayData = activity.activity.find(d => d.date === dateStr);
				
				weekData.push({
					date: dateStr,
					count: dayData?.count || 0,
					chats: dayData?.chats || []
				});
			}
			
			weeksData.push({
				weekStart,
				days: weekData
			});
		}
		
		return weeksData;
	}
	
	// Get month labels for the top of the heatmap
	function getMonthLabels() {
		const weeksData = getWeeksData();
		if (weeksData.length === 0) return [];
		
		const monthLabels: Array<{ month: string; weekIndex: number }> = [];
		let lastMonth = '';
		
		weeksData.forEach((week, index) => {
			const month = format(week.weekStart, 'MMM');
			if (month !== lastMonth) {
				monthLabels.push({ month, weekIndex: index });
				lastMonth = month;
			}
		});
		
		return monthLabels;
	}
	
	function getLevel(count: number): number {
		if (count === 0) return 0;
		if (count <= 2) return 1;
		if (count <= 5) return 2;
		if (count <= 10) return 3;
		return 4;
	}
	
	function handleDayHover(event: MouseEvent, day: { date: string; count: number; chats: any[] }) {
		hoveredDay = day;
		tooltipPosition = { x: event.clientX, y: event.clientY };
	}
	
	function handleDayLeave() {
		hoveredDay = null;
	}
	
	function getTotalConversations(): number {
		if (!activity) return 0;
		return activity.activity.reduce((sum, day) => sum + day.count, 0);
	}
	
	function formatDate(dateString: string): string {
		return format(parseISO(dateString), 'MMM dd, yyyy');
	}
</script>

<div bind:this={heatmapElement} class="heatmap-container">
	<div class="header">
		<h3 class="heatmap-title">Activity</h3>
		{#if activity && !loading}
			<div class="summary">
				<span class="summary-value">{getTotalConversations()}</span>
				<span class="summary-label">conversations in the last year</span>
			</div>
		{/if}
	</div>
	
	{#if loading}
		<div class="loading">Loading activity...</div>
	{:else if error}
		<div class="error">Unable to load activity data</div>
	{:else if activity}
		<div class="heatmap-wrapper">
			<div class="month-labels">
				{#each getMonthLabels() as label}
					<div 
						class="month-label" 
						style="left: {label.weekIndex * (10 + WEEK_GAP) + WEEKDAY_LABELS_WIDTH}px"
					>
						{label.month}
					</div>
				{/each}
			</div>
			
			<div class="heatmap">
				<div class="weekday-labels">
					<span>M</span>
					<span>W</span>
					<span>F</span>
				</div>
				
				<div class="calendar">
					{#each getWeeksData() as week}
						<div class="week">
							{#each week.days as day}
								<div 
									class="day level-{getLevel(day.count)}"
									on:mouseenter={(e) => handleDayHover(e, day)}
									on:mouseleave={handleDayLeave}
									on:mousemove={(e) => tooltipPosition = { x: e.clientX, y: e.clientY }}
									role="button"
									tabindex="0"
								/>
							{/each}
						</div>
					{/each}
				</div>
			</div>
			
			{#if hoveredDay}
				<div 
					class="tooltip"
					style="left: {tooltipPosition.x}px; top: {tooltipPosition.y}px"
				>
					<div class="tooltip-date">{formatDate(hoveredDay.date)}</div>
					<div class="tooltip-count">
						{hoveredDay.count === 0 
							? 'No conversations' 
							: `${hoveredDay.count} conversation${hoveredDay.count !== 1 ? 's' : ''}`
						}
					</div>
				</div>
			{/if}
		</div>
		
		<div class="footer">
			<div class="legend">
				<span class="legend-label">Less</span>
				<div class="legend-items">
					<div class="day level-0"></div>
					<div class="day level-1"></div>
					<div class="day level-2"></div>
					<div class="day level-3"></div>
					<div class="day level-4"></div>
				</div>
				<span class="legend-label">More</span>
			</div>
		</div>
	{/if}
</div>

<style>
	.heatmap-container {
		background: white;
		border-radius: 12px;
		border: 1px solid #e1e4e8;
		padding: 20px;
		margin-bottom: 20px;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
		overflow: visible;
	}
	
	.header {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		margin-bottom: 16px;
		gap: 16px;
		flex-wrap: wrap;
	}
	
	.heatmap-title {
		font-size: 16px;
		font-weight: 600;
		margin: 0;
		color: #24292f;
		flex-shrink: 0;
	}
	
	.summary {
		display: flex;
		align-items: baseline;
		gap: 6px;
		flex-wrap: wrap;
		min-width: 0;
	}
	
	.summary-value {
		font-size: 20px;
		font-weight: 700;
		color: #0969da;
	}
	
	.summary-label {
		font-size: 13px;
		color: #656d76;
	}
	
	.loading, .error {
		text-align: center;
		padding: 40px 20px;
		color: #656d76;
		font-size: 14px;
	}
	
	.error {
		color: #cf222e;
	}
	
	.heatmap-wrapper {
		position: relative;
		margin-bottom: 16px;
		width: 100%;
		max-width: 100%;
		overflow: visible;
	}
	
	.month-labels {
		position: relative;
		height: 14px;
		margin-bottom: 2px;
		margin-left: 16px; /* WEEKDAY_LABELS_WIDTH */
		overflow: hidden;
		width: calc(100% - 16px);
	}
	
	.month-label {
		position: absolute;
		font-size: 11px;
		color: #656d76;
		font-weight: 400;
		transform: translateX(-50%);
		white-space: nowrap;
		line-height: 1;
		padding: 0;
		margin: 0;
	}
	
	.heatmap {
		display: flex;
		gap: 2px;
		align-items: flex-end;
		width: 100%;
		max-width: 100%;
		min-height: 100px;
		position: relative;
		overflow: visible;
		margin-top: 0;
	}
	
	.weekday-labels {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		height: 77px; /* 7 days * 11px */
		margin-right: 6px;
		font-size: 11px;
		color: #656d76;
		flex-shrink: 0;
		width: 16px; /* WEEKDAY_LABELS_WIDTH - reduced for M/W/F labels */
	}
	
	.weekday-labels span {
		height: 11px;
		display: flex;
		align-items: center;
		justify-content: flex-start;
		font-weight: 400;
		line-height: 1;
		padding: 0;
		margin: 0;
	}
	
	.calendar {
		display: flex;
		gap: 2px;
		flex: 1;
		min-width: 0;
		max-width: 100%;
		overflow: visible;
		justify-content: flex-start;
		padding-bottom: 2px;
		padding-right: 0;
	}
	
	.week {
		display: flex;
		flex-direction: column;
		gap: 1px;
		flex-shrink: 0;
	}
	
	.day {
		width: 10px;
		height: 10px;
		border-radius: 2px;
		background: #ebedf0;
		cursor: pointer;
		flex-shrink: 0;
		transition: all 0.15s ease;
		position: relative;
	}
	
	.day:hover {
		outline: 2px solid #0969da;
		outline-offset: -2px;
		transform: scale(1.1);
		z-index: 10;
	}
	
	.day.level-0 { background: #ebedf0; }
	.day.level-1 { background: #9be9a8; }
	.day.level-2 { background: #40c463; }
	.day.level-3 { background: #30a14e; }
	.day.level-4 { background: #216e39; }
	
	.tooltip {
		position: fixed;
		background: #24292f;
		color: white;
		padding: 8px 12px;
		border-radius: 6px;
		font-size: 12px;
		pointer-events: none;
		z-index: 1000;
		transform: translate(-50%, -100%);
		margin-top: -8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		white-space: nowrap;
	}
	
	.tooltip::after {
		content: '';
		position: absolute;
		bottom: -4px;
		left: 50%;
		transform: translateX(-50%);
		width: 0;
		height: 0;
		border-left: 4px solid transparent;
		border-right: 4px solid transparent;
		border-top: 4px solid #24292f;
	}
	
	.tooltip-date {
		font-weight: 600;
		margin-bottom: 2px;
	}
	
	.tooltip-count {
		color: #b1bac4;
		font-size: 11px;
	}
	
	.footer {
		display: flex;
		justify-content: flex-end;
		align-items: center;
		margin-top: 12px;
		padding-top: 12px;
		border-top: 1px solid #f1f3f5;
	}
	
	.legend {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 11px;
		color: #656d76;
	}
	
	.legend-label {
		font-weight: 400;
	}
	
	.legend-items {
		display: flex;
		gap: 1px;
	}
	
	/* Responsive adjustments */
	@media (max-width: 768px) {
		.heatmap-container {
			padding: 16px;
		}
		
		.header {
			flex-direction: column;
			align-items: flex-start;
			gap: 12px;
		}
		
		.summary {
			flex-direction: column;
			align-items: flex-start;
			gap: 4px;
		}
		
		.month-labels {
			display: none; /* Hide month labels on small screens */
		}
		
		.footer {
			justify-content: flex-start;
		}
	}
	
	/* Ensure summary text doesn't get cut off on narrow containers */
	@media (max-width: 400px) {
		.summary-label {
			font-size: 12px;
		}
		
		.summary-value {
			font-size: 18px;
		}
	}
</style>