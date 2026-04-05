<script lang="ts">
    import PromptEditor from '$lib/components/PromptEditor.svelte';
    import VariantPreview from '$lib/components/VariantPreview.svelte';
    import ProgressBar from '$lib/components/ProgressBar.svelte';

    const API = import.meta.env.VITE_API_URL || 'http://localhost:8741';

    let projectId = $state('current');
    let variantCount = $state(1);
    let prompt = $state<any>(null);
    let variants = $state<any[]>([]);
    let selectedVariant = $state(1);
    let generating = $state(false);
    let progress = $state(0);
    let results = $state<any[]>([]);

    async function buildPrompt() {
        try {
            // Get Q&A context
            const ctxRes = await fetch(`${API}/api/chat/qa/context?project_id=${projectId}`, {
                method: 'POST',
            });
            const qaContext = await ctxRes.json();

            // Get slides
            const slidesRes = await fetch(`${API}/api/slides/${projectId}`);
            const plan = await slidesRes.json();

            // Get resources
            const resRes = await fetch(`${API}/api/resources/`);
            const resources = await resRes.json();
            const summaries = resources
                .filter((r: any) => r.parsed)
                .map((r: any) => r.parsed.text.slice(0, 500));

            const promptRes = await fetch(`${API}/api/notebooklm/build-prompt`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: projectId,
                    qa_context: qaContext,
                    slides: plan.slides,
                    resource_summaries: summaries,
                    variant_count: variantCount,
                }),
            });
            prompt = await promptRes.json();
            variants = prompt.variants || [];
        } catch (err) {
            console.error('Failed to build prompt:', err);
        }
    }

    async function generate() {
        if (!prompt) return;
        generating = true;
        progress = 0;

        try {
            const resources = await fetch(`${API}/api/resources/`).then(r => r.json());
            const sources = resources.map((r: any) => ({
                type: r.type === 'web_url' || r.type === 'youtube' ? 'url' : 'text',
                content: r.type === 'web_url' || r.type === 'youtube' ? r.source : r.parsed?.text?.slice(0, 5000) || '',
            }));

            const res = await fetch(`${API}/api/notebooklm/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: projectId,
                    title: 'SlideAlchemy Presentation',
                    sources,
                    prompts: variants.map((v: any) => ({
                        variant_number: v.variant_number,
                        full_prompt: v.full_prompt,
                    })),
                }),
            });
            const data = await res.json();
            results = data.results || [];
            progress = 100;
        } catch (err) {
            console.error('Generation failed:', err);
        }
        generating = false;
    }

    function updatePrompt(newText: string) {
        if (prompt && variants.length > 0) {
            const idx = variants.findIndex((v: any) => v.variant_number === selectedVariant);
            if (idx >= 0) {
                variants[idx].full_prompt = newText;
            }
        }
    }

    $effect(() => { buildPrompt(); });
</script>

<div class="space-y-6">
    <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">Prompt & Variants</h1>
        <button
            onclick={generate}
            disabled={generating || !prompt}
            class="bg-alchemy-600 hover:bg-alchemy-700 disabled:opacity-50 px-6 py-2 rounded-lg font-medium transition"
        >
            {generating ? 'Generating...' : 'Generate Presentation'}
        </button>
    </div>

    <!-- Variant Count -->
    <div class="flex items-center gap-4">
        <span class="text-sm text-gray-400">Number of variants:</span>
        {#each [1, 2, 3, 4] as count}
            <button
                onclick={() => { variantCount = count; buildPrompt(); }}
                class="w-8 h-8 rounded-lg text-sm transition
                    {variantCount === count ? 'bg-alchemy-600' : 'bg-gray-800 hover:bg-gray-700'}"
            >
                {count}
            </button>
        {/each}
    </div>

    <!-- Variant Selection -->
    {#if variants.length > 1}
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            {#each variants as variant}
                <VariantPreview
                    {variant}
                    selected={selectedVariant === variant.variant_number}
                    onSelect={(n) => selectedVariant = n}
                />
            {/each}
        </div>
    {/if}

    <!-- Prompt Editor -->
    {#if variants.length > 0}
        {@const currentVariant = variants.find((v: any) => v.variant_number === selectedVariant)}
        {#if currentVariant}
            <PromptEditor
                value={currentVariant.full_prompt}
                onUpdate={updatePrompt}
            />
        {/if}
    {/if}

    <!-- Generation Progress -->
    {#if generating}
        <ProgressBar {progress} label="Generating presentations..." />
    {/if}

    <!-- Results -->
    {#if results.length > 0}
        <div class="space-y-3">
            <h2 class="text-lg font-semibold">Generated Presentations</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {#each results as result}
                    <div class="bg-gray-900 border border-gray-800 rounded-xl p-4">
                        <h3 class="font-medium">Variant {result.variant_number}</h3>
                        {#if result.pptx_path}
                            <a
                                href={`${API}/api/notebooklm/download/${result.pptx_path.split('/').pop()}`}
                                class="inline-block mt-2 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm transition"
                                download
                            >
                                Download .pptx
                            </a>
                        {:else if result.error}
                            <p class="text-red-400 text-sm mt-1">{result.error}</p>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>
    {/if}
</div>
