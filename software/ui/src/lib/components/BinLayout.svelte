<script lang="ts">
	import { getMachineContext } from '$lib/machines/context';

	const ctx = getMachineContext();

	const layout = $derived(ctx.machine?.layout ?? null);

	function sizeClass(size: string): string {
		switch (size) {
			case 'small':
				return 'w-6 h-6';
			case 'medium':
				return 'w-8 h-8';
			case 'big':
				return 'w-10 h-10';
			default:
				return 'w-6 h-6';
		}
	}

	function categoryColor(category_id: string | null | undefined): string {
		if (!category_id) return 'bg-gray-700';
		const hash = category_id.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
		const hue = hash % 360;
		return `hsl(${hue}, 60%, 45%)`;
	}
</script>

<div class="dark:border-border-dark dark:bg-surface-dark border border-border bg-surface p-3">
	<div class="dark:text-text-dark mb-2 text-sm font-medium text-text">Bin Layout</div>
	{#if !layout}
		<div class="dark:text-text-muted-dark text-sm text-text-muted">No layout data</div>
	{:else}
		<div class="flex flex-col gap-4">
			{#each layout.layers as layer, layer_idx}
				<div class="dark:border-border-dark border border-border p-2">
					<div class="dark:text-text-muted-dark mb-2 text-xs text-text-muted">
						Layer {layer_idx}
					</div>
					<div class="flex flex-wrap gap-2">
						{#each layer.sections as section, section_idx}
							<div class="flex flex-col gap-1">
								<div class="dark:text-text-muted-dark text-center text-xs text-text-muted">
									S{section_idx}
								</div>
								<div class="flex gap-1">
									{#each section as bin, bin_idx}
										<div
											class="{sizeClass(bin.size)} flex items-center justify-center rounded text-xs"
											style="background-color: {categoryColor(bin.category_id)}"
											title={bin.category_id ?? 'unassigned'}
										>
											{bin_idx}
										</div>
									{/each}
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
