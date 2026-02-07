import type { Resource, Project, SlidePlan, Prompt, Feedback, PreferenceProfile, AppSettings, ChatMessage } from './types';

const BASE_URL = 'http://localhost:8741';

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
};
