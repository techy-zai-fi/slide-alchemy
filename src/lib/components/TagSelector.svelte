<script lang="ts">
    let { selected, onChange }: { selected: string[]; onChange: (tags: string[]) => void } = $props();

    const tags = ['colors', 'layout', 'content depth', 'flow', 'data viz', 'speaker notes'];

    function toggle(tag: string) {
        const next = selected.includes(tag)
            ? selected.filter(t => t !== tag)
            : [...selected, tag];
        onChange(next);
    }
</script>

<div class="flex flex-wrap gap-2">
    {#each tags as tag}
        <button
            onclick={() => toggle(tag)}
            class="text-xs px-3 py-1.5 rounded-full transition
                {selected.includes(tag) ? 'bg-alchemy-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}"
        >
            {tag}
        </button>
    {/each}
</div>
