<script lang="ts">
    let { value, onChange }: { value: number; onChange: (v: number) => void } = $props();
    let hovered = $state(0);
</script>

<div class="flex gap-1">
    {#each [1, 2, 3, 4, 5] as star}
        <button
            onclick={() => onChange(star)}
            onmouseenter={() => hovered = star}
            onmouseleave={() => hovered = 0}
            class="text-2xl transition {(hovered || value) >= star ? 'text-yellow-400' : 'text-gray-600'}"
        >
            *
        </button>
    {/each}
</div>
