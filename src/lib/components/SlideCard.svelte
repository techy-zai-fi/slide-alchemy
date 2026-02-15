<script lang="ts">
    import type { Slide } from '$lib/api/types';

    let { slide, onEdit, onDelete }: {
        slide: Slide;
        onEdit: (slide: Slide) => void;
        onDelete: (id: string) => void;
    } = $props();

    let editing = $state(false);
    let editTitle = $state(slide.title);
    let editPoints = $state(slide.key_points.join('\n'));

    function save() {
        onEdit({
            ...slide,
            title: editTitle,
            key_points: editPoints.split('\n').filter(p => p.trim()),
        });
        editing = false;
    }
</script>

<div class="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3 group">
    <div class="flex items-start justify-between">
        <div class="flex items-center gap-3">
            <span class="text-xs bg-gray-800 px-2 py-1 rounded text-gray-400 font-mono">
                {slide.order + 1}
            </span>
            {#if editing}
                <input type="text" bind:value={editTitle}
                    class="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-sm font-semibold focus:border-alchemy-500 focus:outline-none" />
            {:else}
                <h3 class="font-semibold">{slide.title}</h3>
            {/if}
        </div>
        <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition">
            <button onclick={() => { editing = !editing; if (!editing) save(); }}
                class="text-xs bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded transition">
                {editing ? 'Save' : 'Edit'}
            </button>
            <button onclick={() => onDelete(slide.id)}
                class="text-xs bg-gray-800 hover:bg-red-900 text-red-400 px-2 py-1 rounded transition">Delete</button>
        </div>
    </div>

    {#if editing}
        <textarea bind:value={editPoints} rows="4" placeholder="One key point per line..."
            class="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm focus:border-alchemy-500 focus:outline-none resize-none"></textarea>
    {:else}
        <ul class="text-sm text-gray-300 space-y-1">
            {#each slide.key_points as point}
                <li class="flex items-start gap-2">
                    <span class="text-alchemy-500 mt-0.5">-</span>
                    <span>{point}</span>
                </li>
            {/each}
        </ul>
    {/if}

    {#if slide.supporting_data.length > 0}
        <div class="flex gap-1 flex-wrap">
            {#each slide.supporting_data as data}
                <span class="text-xs bg-gray-800 px-2 py-0.5 rounded text-gray-400">{data}</span>
            {/each}
        </div>
    {/if}

    {#if slide.visual_direction}
        <p class="text-xs text-gray-500 italic">{slide.visual_direction}</p>
    {/if}
</div>
