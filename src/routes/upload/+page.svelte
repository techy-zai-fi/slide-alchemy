<script lang="ts">
    import { api } from '$lib/api/client';
    import type { Resource } from '$lib/api/types';
    import ResourceCard from '$lib/components/ResourceCard.svelte';

    let resources = $state<Resource[]>([]);
    let urlInput = $state('');
    let textInput = $state('');
    let dragOver = $state(false);
    let loading = $state(false);

    async function handleFileDrop(e: DragEvent) {
        e.preventDefault();
        dragOver = false;
        const files = e.dataTransfer?.files;
        if (!files) return;
        for (const file of files) {
            await uploadFile(file);
        }
    }

    async function handleFileSelect(e: Event) {
        const input = e.target as HTMLInputElement;
        const files = input.files;
        if (!files) return;
        for (const file of files) {
            await uploadFile(file);
        }
    }

    async function uploadFile(file: File) {
        loading = true;
        try {
            const resource = await api.uploadFile(file);
            resources = [...resources, resource];
        } catch (err) {
            console.error('Upload failed:', err);
        }
        loading = false;
    }

    async function addUrl() {
        if (!urlInput.trim()) return;
        loading = true;
        const type = urlInput.includes('youtube.com') || urlInput.includes('youtu.be')
            ? 'youtube' : 'web_url';
        try {
            const resource = await api.addUrl(type, urlInput);
            resources = [...resources, resource];
            urlInput = '';
        } catch (err) {
            console.error('URL add failed:', err);
        }
        loading = false;
    }

    async function addText() {
        if (!textInput.trim()) return;
        loading = true;
        try {
            const resource = await api.addText(textInput);
            resources = [...resources, resource];
            textInput = '';
        } catch (err) {
            console.error('Text add failed:', err);
        }
        loading = false;
    }

    async function deleteResource(id: string) {
        await api.deleteResource(id);
        resources = resources.filter(r => r.id !== id);
    }
</script>

<div class="space-y-6">
    <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">Add Resources</h1>
        <a href="/qa" class="bg-alchemy-600 hover:bg-alchemy-700 px-4 py-2 rounded-lg text-sm font-medium transition">
            Continue to Q&A →
        </a>
    </div>

    <div
        class="border-2 border-dashed rounded-xl p-12 text-center transition
            {dragOver ? 'border-alchemy-500 bg-alchemy-500/10' : 'border-gray-700 hover:border-gray-600'}"
        ondragover={(e) => { e.preventDefault(); dragOver = true; }}
        ondragleave={() => dragOver = false}
        ondrop={handleFileDrop}
        role="button"
        tabindex="0"
    >
        <p class="text-gray-400 text-lg">Drop files here</p>
        <p class="text-gray-500 text-sm mt-1">PDF, DOCX, PPTX, TXT, MD, Images</p>
        <label class="inline-block mt-4 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg cursor-pointer text-sm transition">
            Browse Files
            <input type="file" multiple class="hidden" onchange={handleFileSelect} />
        </label>
    </div>

    <div class="flex gap-2">
        <input
            type="text"
            bind:value={urlInput}
            placeholder="Paste a URL (web page, YouTube, arXiv...)"
            class="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:border-alchemy-500 focus:outline-none"
        />
        <button onclick={addUrl} class="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg text-sm transition">
            Add URL
        </button>
    </div>

    <div class="space-y-2">
        <textarea
            bind:value={textInput}
            placeholder="Paste raw notes, bullet points, or outline..."
            rows="4"
            class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm focus:border-alchemy-500 focus:outline-none resize-none"
        ></textarea>
        <button onclick={addText} class="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg text-sm transition">
            Add Text
        </button>
    </div>

    {#if loading}
        <div class="text-center text-alchemy-500 text-sm animate-pulse">Processing...</div>
    {/if}

    {#if resources.length > 0}
        <div>
            <h2 class="text-lg font-semibold mb-3">Resources ({resources.length})</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {#each resources as resource (resource.id)}
                    <ResourceCard {resource} onDelete={deleteResource} />
                {/each}
            </div>
        </div>
    {/if}
</div>
