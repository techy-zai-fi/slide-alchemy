<script lang="ts">
    import type { Slide } from '$lib/api/types';
    import SlideCard from '$lib/components/SlideCard.svelte';

    let slides = $state<Slide[]>([]);
    let loading = $state(true);
    let projectId = $state('current');

    async function loadPlan() {
        loading = true;
        try {
            const res = await fetch(`http://localhost:8741/api/slides/${projectId}`);
            if (res.ok) {
                const plan = await res.json();
                slides = plan.slides;
            }
        } catch {}
        loading = false;
    }

    async function generatePlan() {
        loading = true;
        try {
            const ctxRes = await fetch(`http://localhost:8741/api/chat/qa/context?project_id=${projectId}`, { method: 'POST' });
            const qaContext = await ctxRes.json();
            const resRes = await fetch('http://localhost:8741/api/resources/');
            const resources = await resRes.json();
            const summaries = resources.filter((r: any) => r.parsed).map((r: any) => r.parsed.text.slice(0, 500));
            const planRes = await fetch('http://localhost:8741/api/slides/generate-plan', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_id: projectId, qa_context: qaContext, resource_summaries: summaries }),
            });
            const plan = await planRes.json();
            slides = plan.slides;
        } catch (err) { console.error('Failed to generate plan:', err); }
        loading = false;
    }

    function handleEdit(updated: Slide) {
        slides = slides.map(s => s.id === updated.id ? updated : s);
        fetch(`http://localhost:8741/api/slides/${projectId}/slide/${updated.id}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: updated.title, key_points: updated.key_points }),
        });
    }

    function handleDelete(id: string) {
        slides = slides.filter(s => s.id !== id);
        fetch(`http://localhost:8741/api/slides/${projectId}/slide/${id}`, { method: 'DELETE' });
    }

    $effect(() => { loadPlan(); });
</script>

<div class="space-y-6">
    <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">Slide Planner</h1>
        <div class="flex gap-2">
            <button onclick={generatePlan}
                class="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg text-sm transition">
                {slides.length > 0 ? 'Regenerate' : 'Generate'} Plan
            </button>
            <a href="/prompt" class="bg-alchemy-600 hover:bg-alchemy-700 px-4 py-2 rounded-lg text-sm font-medium transition">
                Continue to Prompt →
            </a>
        </div>
    </div>

    {#if loading}
        <div class="text-center py-12 text-alchemy-500 animate-pulse">Generating slide plan...</div>
    {:else if slides.length === 0}
        <div class="text-center py-12 text-gray-500">
            <p class="text-lg">No slide plan yet</p>
            <p class="text-sm mt-2">Click "Generate Plan" to create one from your Q&A answers and resources</p>
        </div>
    {:else}
        <p class="text-sm text-gray-400">{slides.length} slides - Drag to reorder, click to edit</p>
        <div class="space-y-3">
            {#each slides.sort((a, b) => a.order - b.order) as slide (slide.id)}
                <SlideCard {slide} onEdit={handleEdit} onDelete={handleDelete} />
            {/each}
        </div>
    {/if}
</div>
