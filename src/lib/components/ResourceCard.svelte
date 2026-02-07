<script lang="ts">
    import type { Resource } from '$lib/api/types';

    let { resource, onDelete }: { resource: Resource; onDelete: (id: string) => void } = $props();

    const typeIcons: Record<string, string> = {
        pdf: '📄', docx: '📝', pptx: '📊', txt: '📃', markdown: '📋',
        image: '🖼️', youtube: '🎬', web_url: '🌐', raw_text: '✏️', research: '🔍',
    };

    const statusColors: Record<string, string> = {
        pending: 'text-yellow-400',
        parsing: 'text-blue-400',
        parsed: 'text-green-400',
        error: 'text-red-400',
    };

    let preview = $derived(
        resource.parsed?.text
            ? resource.parsed.text.slice(0, 200) + (resource.parsed.text.length > 200 ? '...' : '')
            : 'Parsing...'
    );
</script>

<div class="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3">
    <div class="flex items-start justify-between">
        <div class="flex items-center gap-2">
            <span class="text-xl">{typeIcons[resource.type] || '📎'}</span>
            <div>
                <h3 class="font-medium text-sm">{resource.label || resource.source}</h3>
                <span class="text-xs {statusColors[resource.status]}">{resource.status}</span>
                <span class="text-xs text-gray-500 ml-2">{resource.priority}</span>
            </div>
        </div>
        <button
            onclick={() => onDelete(resource.id)}
            class="text-gray-500 hover:text-red-400 text-sm transition"
        >
            ✕
        </button>
    </div>

    {#if resource.parsed}
        <p class="text-xs text-gray-400 leading-relaxed">{preview}</p>
        {#if resource.parsed.metadata}
            <div class="flex gap-2 flex-wrap">
                {#each Object.entries(resource.parsed.metadata).filter(([k]) => k !== 'type') as [key, val]}
                    <span class="text-xs bg-gray-800 px-2 py-0.5 rounded text-gray-400">
                        {key}: {val}
                    </span>
                {/each}
            </div>
        {/if}
    {/if}

    {#if resource.error}
        <p class="text-xs text-red-400">{resource.error}</p>
    {/if}
</div>
