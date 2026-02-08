<script lang="ts">
    import type { ChatMessage } from '$lib/api/types';
    import ChatMessageComponent from '$lib/components/ChatMessage.svelte';

    let messages = $state<ChatMessage[]>([]);
    let userInput = $state('');
    let projectId = $state('current');
    let qaComplete = $state(false);
    let currentQuestion = $state<any>(null);
    let loading = $state(false);

    async function startQA() {
        loading = true;
        try {
            const res = await fetch('http://localhost:8741/api/chat/qa/start?project_id=' + projectId, { method: 'POST' });
            const data = await res.json();
            currentQuestion = data.question;
            if (currentQuestion) {
                messages = [...messages, {
                    role: 'assistant', content: currentQuestion.text,
                    options: currentQuestion.options, type: 'question',
                }];
            }
        } catch (err) { console.error('Failed to start Q&A:', err); }
        loading = false;
    }

    async function submitAnswer(answer: string) {
        messages = [...messages, { role: 'user', content: answer, type: 'answer' }];
        userInput = '';
        loading = true;
        try {
            const res = await fetch('http://localhost:8741/api/chat/qa/answer', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_id: projectId, answer }),
            });
            const data = await res.json();
            if (data.complete) {
                qaComplete = true;
                messages = [...messages, {
                    role: 'assistant',
                    content: 'All questions answered! Your presentation context is ready. Head to the Slide Planner to review.',
                    type: 'info',
                }];
            } else if (data.question) {
                currentQuestion = data.question;
                messages = [...messages, {
                    role: 'assistant', content: data.question.text,
                    options: data.question.options, type: 'question',
                }];
            }
        } catch (err) { console.error('Failed to submit answer:', err); }
        loading = false;
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey && userInput.trim()) {
            e.preventDefault();
            submitAnswer(userInput.trim());
        }
    }

    $effect(() => { startQA(); });
</script>

<div class="flex flex-col h-[calc(100vh-120px)]">
    <div class="flex items-center justify-between mb-4">
        <h1 class="text-2xl font-bold">Presentation Q&A</h1>
        {#if currentQuestion}
            <span class="text-sm text-gray-400">
                Question {currentQuestion.question_number} of {currentQuestion.total_questions}
            </span>
        {/if}
    </div>

    {#if currentQuestion}
        <div class="w-full bg-gray-800 rounded-full h-1.5 mb-4">
            <div class="bg-alchemy-500 h-1.5 rounded-full transition-all duration-300"
                style="width: {(currentQuestion.question_number / currentQuestion.total_questions) * 100}%"></div>
        </div>
    {/if}

    <div class="flex-1 overflow-y-auto space-y-4 pb-4">
        {#each messages as message}
            <ChatMessageComponent {message} onOptionSelect={submitAnswer} />
        {/each}
        {#if loading}
            <div class="flex justify-start">
                <div class="bg-gray-800 rounded-2xl px-4 py-3">
                    <div class="flex gap-1">
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    </div>
                </div>
            </div>
        {/if}
    </div>

    {#if !qaComplete}
        <div class="flex gap-2 pt-4 border-t border-gray-800">
            <input type="text" bind:value={userInput} onkeydown={handleKeydown}
                placeholder="Type your answer or click an option above..."
                class="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm focus:border-alchemy-500 focus:outline-none" />
            <button onclick={() => userInput.trim() && submitAnswer(userInput.trim())}
                class="bg-alchemy-600 hover:bg-alchemy-700 px-6 py-3 rounded-lg text-sm font-medium transition">Send</button>
        </div>
    {:else}
        <div class="pt-4 border-t border-gray-800">
            <a href="/planner" class="block text-center bg-alchemy-600 hover:bg-alchemy-700 px-6 py-3 rounded-lg font-medium transition">
                Continue to Slide Planner →
            </a>
        </div>
    {/if}
</div>
