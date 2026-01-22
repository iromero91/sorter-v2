<script lang="ts">
	import { onMount } from 'svelte';
	import { getMachinesContext, getMachineContext } from '$lib/machines/context';
	import CameraFeed from '$lib/components/CameraFeed.svelte';
	import RecentObjects from '$lib/components/RecentObjects.svelte';
	import BinLayout from '$lib/components/BinLayout.svelte';
	import SettingsModal from '$lib/components/SettingsModal.svelte';
	import MachineDropdown from '$lib/components/MachineDropdown.svelte';
	import { Settings } from 'lucide-svelte';

	const manager = getMachinesContext();
	const machine = getMachineContext();

	let settings_open = $state(false);

	onMount(() => {
		manager.connect('ws://localhost:8000/ws');
	});
</script>

<div class="dark:bg-bg-dark min-h-screen bg-bg p-6">
	<div class="mb-4 flex items-center justify-between">
		<h1 class="dark:text-text-dark text-2xl font-bold text-text">Sorter</h1>
		<div class="flex items-center gap-2">
			<MachineDropdown />
			<button
				onclick={() => (settings_open = true)}
				class="dark:text-text-dark dark:hover:bg-surface-dark p-2 text-text transition-colors hover:bg-surface"
				title="Settings"
			>
				<Settings size={24} />
			</button>
		</div>
	</div>

	{#if machine.machine}
		<div class="grid grid-cols-[2fr_1fr_1fr] gap-3">
			<div class="row-span-2">
				<CameraFeed camera="feeder" />
			</div>
			<div>
				<CameraFeed camera="classification_top" />
			</div>
			<div class="row-span-2">
				<RecentObjects />
			</div>
			<div>
				<CameraFeed camera="classification_bottom" />
			</div>
		</div>

		<div class="mt-3">
			<BinLayout />
		</div>
	{:else}
		<div class="dark:text-text-muted-dark py-12 text-center text-text-muted">
			No machine selected. Connect to a machine in Settings.
		</div>
	{/if}
</div>

<SettingsModal bind:open={settings_open} />
