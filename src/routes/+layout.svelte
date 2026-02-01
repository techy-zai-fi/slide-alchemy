<script>
    import '../app.css';
    let { children } = $props();
</script>

<div class="min-h-screen bg-gray-950 text-white">
    <nav class="border-b border-gray-800 px-6 py-4">
        <div class="flex items-center justify-between max-w-7xl mx-auto">
            <a href="/" class="text-xl font-bold text-alchemy-500">SlideAlchemy</a>
            <div class="flex gap-4 text-sm text-gray-400">
                <a href="/" class="hover:text-white transition">Dashboard</a>
                <a href="/settings" class="hover:text-white transition">Settings</a>
            </div>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-6 py-8">
        {@render children()}
    </main>
</div>
