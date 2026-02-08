<script lang="ts">
    let activeProvider = $state('ollama');
    let ollamaModel = $state('gemma4');
    let openrouterKey = $state('');
    let openrouterModel = $state('');
    let groqKey = $state('');
    let groqModel = $state('');
    let openaiKey = $state('');
    let openaiModel = $state('gpt-4o');
    let geminiKey = $state('');
    let geminiModel = $state('gemini-2.0-flash');
    let notebooklmCookie = $state('');
    let serperKey = $state('');
    let saved = $state(false);

    async function saveSettings() {
        const configs: Record<string, any> = {
            ollama: { provider: 'ollama', model_name: ollamaModel },
            openrouter: { provider: 'openrouter', model_name: openrouterModel, api_key: openrouterKey },
            groq: { provider: 'groq', model_name: groqModel, api_key: groqKey },
            openai: { provider: 'openai', model_name: openaiModel, api_key: openaiKey },
            gemini: { provider: 'gemini', model_name: geminiModel, api_key: geminiKey },
        };
        await fetch('http://localhost:8741/api/chat/configure', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(configs[activeProvider]),
        });
        saved = true;
        setTimeout(() => saved = false, 2000);
    }
</script>

<div class="max-w-2xl space-y-8">
    <h1 class="text-2xl font-bold">Settings</h1>

    <section class="space-y-4">
        <h2 class="text-lg font-semibold">AI Model</h2>
        <div class="grid grid-cols-5 gap-2">
            {#each ['ollama', 'openrouter', 'groq', 'openai', 'gemini'] as provider}
                <button onclick={() => activeProvider = provider}
                    class="px-3 py-2 rounded-lg text-sm capitalize transition
                        {activeProvider === provider ? 'bg-alchemy-600' : 'bg-gray-800 hover:bg-gray-700'}">
                    {provider}
                </button>
            {/each}
        </div>

        {#if activeProvider === 'ollama'}
            <input type="text" bind:value={ollamaModel} placeholder="Model name (e.g., gemma4)"
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
        {:else if activeProvider === 'openrouter'}
            <input type="password" bind:value={openrouterKey} placeholder="OpenRouter API Key"
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
            <input type="text" bind:value={openrouterModel} placeholder="Model (e.g., meta-llama/llama-3-70b)"
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
        {:else if activeProvider === 'groq'}
            <input type="password" bind:value={groqKey} placeholder="Groq API Key"
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
            <input type="text" bind:value={groqModel} placeholder="Model (e.g., llama3-70b-8192)"
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
        {:else if activeProvider === 'openai'}
            <input type="password" bind:value={openaiKey} placeholder="OpenAI API Key"
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
            <input type="text" bind:value={openaiModel} placeholder="Model (e.g., gpt-4o)"
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
        {:else if activeProvider === 'gemini'}
            <input type="password" bind:value={geminiKey} placeholder="Gemini API Key"
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
            <input type="text" bind:value={geminiModel} placeholder="Model (e.g., gemini-2.0-flash)"
                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
        {/if}
    </section>

    <section class="space-y-4">
        <h2 class="text-lg font-semibold">NotebookLM</h2>
        <textarea bind:value={notebooklmCookie} placeholder="Paste your NotebookLM cookie here..." rows="3"
            class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none resize-none"></textarea>
    </section>

    <section class="space-y-4">
        <h2 class="text-lg font-semibold">Research APIs</h2>
        <input type="password" bind:value={serperKey} placeholder="Serper API Key (for web search)"
            class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none" />
    </section>

    <button onclick={saveSettings} class="bg-alchemy-600 hover:bg-alchemy-700 px-6 py-2 rounded-lg font-medium transition">
        Save Settings
    </button>

    {#if saved}
        <span class="text-green-400 text-sm ml-3">Saved!</span>
    {/if}
</div>
