<script lang="ts">
    import type { ChatMessage } from '$lib/api/types';

    let { message, onOptionSelect }: {
        message: ChatMessage;
        onOptionSelect?: (option: string) => void;
    } = $props();

    let isAssistant = $derived(message.role === 'assistant');
</script>

<div class="flex {isAssistant ? 'justify-start' : 'justify-end'}">
    <div class="max-w-[80%] {isAssistant ? 'bg-gray-800' : 'bg-alchemy-600'} rounded-2xl px-4 py-3 space-y-2">
        <p class="text-sm leading-relaxed">{message.content}</p>

        {#if message.options && message.options.length > 0}
            <div class="flex flex-wrap gap-2 pt-1">
                {#each message.options as option}
                    <button
                        onclick={() => onOptionSelect?.(option)}
                        class="text-xs bg-gray-700 hover:bg-alchemy-600 px-3 py-1.5 rounded-full transition"
                    >
                        {option}
                    </button>
                {/each}
            </div>
        {/if}
    </div>
</div>
