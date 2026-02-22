<script>
    import '../app.css';
    let { children } = $props();

    const navItems = [
        { href: '/', label: 'Dashboard' },
        { href: '/upload', label: 'Resources' },
        { href: '/qa', label: 'Q&A' },
        { href: '/planner', label: 'Planner' },
        { href: '/prompt', label: 'Generate' },
        { href: '/settings', label: 'Settings' },
    ];
</script>

<div class="min-h-screen bg-gray-950 text-white">
    <nav class="border-b border-gray-800 px-6 py-3">
        <div class="flex items-center justify-between max-w-7xl mx-auto">
            <a href="/" class="text-xl font-bold text-alchemy-500">SlideAlchemy</a>
            <div class="flex gap-1">
                {#each navItems as item}
                    <a
                        href={item.href}
                        class="px-3 py-1.5 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition"
                    >
                        {item.label}
                    </a>
                {/each}
            </div>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-6 py-8">
        {@render children()}
    </main>
</div>
