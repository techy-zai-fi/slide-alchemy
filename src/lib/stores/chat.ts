import { writable } from 'svelte/store';
import type { ChatMessage } from '$lib/api/types';

export const chatMessages = writable<ChatMessage[]>([]);
export const qaComplete = writable(false);
export const qaContext = writable<Record<string, string>>({});

export function addMessage(msg: ChatMessage) {
    chatMessages.update(msgs => [...msgs, msg]);
}

export function clearChat() {
    chatMessages.set([]);
    qaComplete.set(false);
    qaContext.set({});
}
