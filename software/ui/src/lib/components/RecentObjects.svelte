<script lang="ts">
	import { getMachineContext } from '$lib/machines/context';
	import type { KnownObjectData } from '$lib/api/events';

	const ctx = getMachineContext();

	const objects = $derived(ctx.machine?.recentObjects ?? []);

	let expanded_id = $state<string | null>(null);

	function toggleExpand(uuid: string) {
		expanded_id = expanded_id === uuid ? null : uuid;
	}

	function statusColor(status: KnownObjectData['status']): string {
		switch (status) {
			case 'created':
				return 'bg-gray-500';
			case 'classifying':
				return 'bg-yellow-500';
			case 'classified':
				return 'bg-blue-500';
			case 'distributing':
				return 'bg-orange-500';
			case 'distributed':
				return 'bg-green-500';
			default:
				return 'bg-gray-500';
		}
	}

	function formatBin(bin: [unknown, unknown, unknown] | null | undefined): string {
		if (!bin) return '-';
		return `L${bin[0]}:S${bin[1]}:B${bin[2]}`;
	}
</script>

<div
	class="dark:border-border-dark dark:bg-surface-dark flex h-full flex-col border border-border bg-surface"
>
	<div
		class="dark:bg-surface-dark dark:text-text-dark dark:border-border-dark border-b border-border px-2 py-1 text-sm font-medium text-text"
	>
		Recent Objects
	</div>
	<div class="flex-1 overflow-y-auto">
		{#if objects.length === 0}
			<div class="dark:text-text-muted-dark p-3 text-center text-sm text-text-muted">
				No objects yet
			</div>
		{:else}
			<div class="flex flex-col gap-1 p-1">
				{#each objects as obj (obj.uuid)}
					{@const is_expanded = expanded_id === obj.uuid}
					<button
						type="button"
						onclick={() => toggleExpand(obj.uuid)}
						class="dark:border-border-dark dark:bg-bg-dark dark:hover:bg-surface-dark w-full border border-border bg-bg p-2 text-left transition-colors hover:bg-surface"
					>
						<div class="flex gap-2">
							{#if obj.thumbnail}
								<img
									src={`data:image/jpeg;base64,${obj.thumbnail}`}
									alt="piece"
									class="h-12 w-12 flex-shrink-0 object-cover"
								/>
							{:else}
								<div
									class="dark:bg-surface-dark dark:text-text-muted-dark flex h-12 w-12 flex-shrink-0 items-center justify-center bg-surface text-xs text-text-muted"
								>
									?
								</div>
							{/if}
							<div class="flex min-w-0 flex-1 flex-col text-xs">
								<div class="flex items-center gap-1">
									<span class={`h-2 w-2 rounded-full ${statusColor(obj.status)}`}></span>
									<span class="dark:text-text-dark truncate font-mono text-text">
										{obj.part_id ?? obj.uuid.slice(0, 8)}
									</span>
								</div>
								<div class="dark:text-text-muted-dark text-text-muted">
									{obj.status}
									{#if obj.confidence != null}
										({(obj.confidence * 100).toFixed(0)}%)
									{/if}
								</div>
								<div class="dark:text-text-muted-dark text-text-muted">
									{obj.category_id ?? '-'} → {formatBin(obj.destination_bin)}
								</div>
							</div>
						</div>

						{#if is_expanded && (obj.top_image || obj.bottom_image)}
							<div class="dark:border-border-dark mt-2 flex gap-2 border-t border-border pt-2">
								{#if obj.top_image}
									<div class="flex-1">
										<div class="dark:text-text-muted-dark mb-1 text-xs text-text-muted">Top</div>
										<img
											src={`data:image/jpeg;base64,${obj.top_image}`}
											alt="top view"
											class="w-full"
										/>
									</div>
								{/if}
								{#if obj.bottom_image}
									<div class="flex-1">
										<div class="dark:text-text-muted-dark mb-1 text-xs text-text-muted">Bottom</div>
										<img
											src={`data:image/jpeg;base64,${obj.bottom_image}`}
											alt="bottom view"
											class="w-full"
										/>
									</div>
								{/if}
							</div>
						{/if}
					</button>
				{/each}
			</div>
		{/if}
	</div>
</div>
