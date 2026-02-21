<script lang="ts">
    let { value, onUpdate }: { value: string; onUpdate: (val: string) => void } = $props();
    let editing = $state(false);
    let editValue = $state(value);

    function save() {
        onUpdate(editValue);
        editing = false;
    }

    $effect(() => { editValue = value; });
</script>

<div class="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
    <div class="flex items-center justify-between px-4 py-2 border-b border-gray-800">
        <span class="text-sm text-gray-400">Generated Prompt</span>
        <button
            onclick={() => { if (editing) save(); else editing = true; }}
            class="text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1 rounded transition"
        >
            {editing ? 'Save' : 'Edit'}
        </button>
    </div>
    {#if editing}
        <textarea
            bind:value={editValue}
            rows="20"
            class="w-full bg-gray-950 px-4 py-3 text-sm font-mono text-gray-300 focus:outline-none resize-none"
        ></textarea>
    {:else}
        <pre class="px-4 py-3 text-sm font-mono text-gray-300 overflow-x-auto max-h-96 overflow-y-auto whitespace-pre-wrap">{value}</pre>
    {/if}
</div>
