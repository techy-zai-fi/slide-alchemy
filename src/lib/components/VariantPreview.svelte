<script lang="ts">
    let { variant, selected, onSelect }: {
        variant: { variant_number: number; variant_description: string; pptx_path?: string };
        selected: boolean;
        onSelect: (num: number) => void;
    } = $props();
</script>

<button
    onclick={() => onSelect(variant.variant_number)}
    class="border rounded-xl p-4 text-left transition
        {selected ? 'border-alchemy-500 bg-alchemy-500/10' : 'border-gray-800 bg-gray-900 hover:border-gray-600'}"
>
    <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-semibold">Variant {variant.variant_number}</span>
        {#if selected}
            <span class="text-xs bg-alchemy-600 px-2 py-0.5 rounded">Selected</span>
        {/if}
    </div>
    <p class="text-xs text-gray-400">{variant.variant_description}</p>

    <!-- Placeholder for PPTX thumbnail -->
    <div class="mt-3 bg-gray-800 rounded-lg aspect-video flex items-center justify-center">
        {#if variant.pptx_path}
            <span class="text-xs text-green-400">Generated</span>
        {:else}
            <span class="text-xs text-gray-500">Pending</span>
        {/if}
    </div>
</button>
