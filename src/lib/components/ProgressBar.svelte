<script lang="ts">
    let { progress, label }: { progress: number; label?: string } = $props();
</script>

<div class="space-y-1">
    {#if label}
        <div class="flex justify-between text-xs text-gray-400">
            <span>{label}</span>
            <span>{Math.round(progress)}%</span>
        </div>
    {/if}
    <div class="w-full bg-gray-800 rounded-full h-2">
        <div
            class="bg-alchemy-500 h-2 rounded-full transition-all duration-500"
            style="width: {progress}%"
        ></div>
    </div>
</div>
