import type { Resource, Project, SlidePlan, Prompt, Feedback, PreferenceProfile, AppSettings, ChatMessage } from './types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8741';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || 'Request failed');
    }
    return res.json();
}

export const api = {
    health: () => request<{ status: string }>('/health'),

    uploadFile: async (file: File, priority = 'primary', label?: string): Promise<Resource> => {
        const form = new FormData();
        form.append('file', file);
        form.append('priority', priority);
        if (label) form.append('label', label);
        const res = await fetch(`${BASE_URL}/api/resources/upload`, { method: 'POST', body: form });
        if (!res.ok) throw new Error('Upload failed');
        return res.json();
    },
    addUrl: (type: string, source: string, priority = 'primary', label?: string) =>
        request<Resource>('/api/resources/url', {
            method: 'POST',
            body: JSON.stringify({ type, source, priority, label }),
        }),
    addText: (text: string, priority = 'primary', label?: string) =>
        request<Resource>('/api/resources/text', {
            method: 'POST',
            body: JSON.stringify({ type: 'raw_text', source: text, priority, label }),
        }),
    listResources: () => request<Resource[]>('/api/resources/'),
    deleteResource: (id: string) => request<void>(`/api/resources/${id}`, { method: 'DELETE' }),

    // Feedback
    submitFeedback: (feedback: Feedback) =>
        request<void>('/api/feedback/submit', {
            method: 'POST',
            body: JSON.stringify(feedback),
        }),
    getPreferences: () => request<PreferenceProfile>('/api/feedback/preferences'),

    // Slides
    generateSlidePlan: (projectId: string, qaContext: Record<string, string>, summaries: string[]) =>
        request<any>('/api/slides/generate-plan', {
            method: 'POST',
            body: JSON.stringify({ project_id: projectId, qa_context: qaContext, resource_summaries: summaries }),
        }),
    getSlidePlan: (projectId: string) => request<any>(`/api/slides/${projectId}`),

    // NotebookLM
    buildPrompt: (data: any) => request<any>('/api/notebooklm/build-prompt', { method: 'POST', body: JSON.stringify(data) }),
    generate: (data: any) => request<any>('/api/notebooklm/generate', { method: 'POST', body: JSON.stringify(data) }),
    getGenerationStatus: (projectId: string) => request<any>(`/api/notebooklm/status/${projectId}`),

    // Research
    searchAll: (query: string) => request<any[]>('/api/research/search', { method: 'POST', body: JSON.stringify({ query }) }),
    analyzeGaps: (texts: string[], context: Record<string, string>) =>
        request<any>('/api/research/gaps', { method: 'POST', body: JSON.stringify({ resource_texts: texts, qa_context: context }) }),

    // Settings
    getSettings: () => request<AppSettings>('/api/settings/'),
    saveSettings: (settings: AppSettings) =>
        request<void>('/api/settings/', { method: 'PUT', body: JSON.stringify(settings) }),
};
