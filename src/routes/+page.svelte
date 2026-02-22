<script lang="ts">
    import { api } from '$lib/api/client';

    let projects = $state<any[]>([]);
    let newName = $state('');
    let showNew = $state(false);
    let backendOk = $state(false);

    async function checkBackend() {
        try {
            await api.health();
            backendOk = true;
        } catch {
            backendOk = false;
        }
    }

    async function createProject() {
        if (!newName.trim()) return;
        // For now, just navigate to upload — project state is managed in-memory
        window.location.href = '/upload';
    }

    $effect(() => { checkBackend(); });
</script>

<div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-3xl font-bold">SlideAlchemy</h1>
            <p class="text-gray-400 mt-1">Transform your resources into stunning presentations</p>
        </div>
        <div class="flex items-center gap-3">
            <span class="text-xs {backendOk ? 'text-green-400' : 'text-red-400'}">
                {backendOk ? 'Backend connected' : 'Backend offline'}
            </span>
            <button
                onclick={() => showNew = true}
                class="bg-alchemy-600 hover:bg-alchemy-700 px-6 py-2.5 rounded-lg font-medium transition"
            >
                + New Presentation
            </button>
        </div>
    </div>

    <!-- New Project Modal -->
    {#if showNew}
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
            <h2 class="text-lg font-semibold">New Presentation</h2>
            <input
                type="text"
                bind:value={newName}
                placeholder="Presentation name..."
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none"
            />
            <div class="flex gap-2">
                <button onclick={createProject}
                    class="bg-alchemy-600 hover:bg-alchemy-700 px-4 py-2 rounded-lg text-sm transition">
                    Create & Start
                </button>
                <button onclick={() => showNew = false}
                    class="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg text-sm transition">
                    Cancel
                </button>
            </div>
        </div>
    {/if}

    <!-- Workflow Steps -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        {#each [
            { step: '1', title: 'Add Resources', desc: 'Upload docs, URLs, videos, notes', href: '/upload', color: 'from-blue-500/20' },
            { step: '2', title: 'Q&A Interview', desc: 'AI refines your presentation goals', href: '/qa', color: 'from-purple-500/20' },
            { step: '3', title: 'Plan Slides', desc: 'Review and edit slide content', href: '/planner', color: 'from-pink-500/20' },
            { step: '4', title: 'Generate', desc: 'Create variants via NotebookLM', href: '/prompt', color: 'from-green-500/20' },
        ] as item}
            <a href={item.href}
                class="bg-gradient-to-br {item.color} to-transparent bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-600 transition group">
                <span class="text-xs text-gray-500">Step {item.step}</span>
                <h3 class="font-semibold mt-1 group-hover:text-alchemy-400 transition">{item.title}</h3>
                <p class="text-sm text-gray-400 mt-1">{item.desc}</p>
            </a>
        {/each}
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <a href="/settings" class="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-600 transition">
            <h3 class="font-semibold">Settings</h3>
            <p class="text-sm text-gray-400 mt-1">Configure AI models, API keys, NotebookLM auth</p>
        </a>
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <h3 class="font-semibold">Your Style Profile</h3>
            <p class="text-sm text-gray-400 mt-1">Built from your feedback — improves with every presentation</p>
        </div>
    </div>
</div>
