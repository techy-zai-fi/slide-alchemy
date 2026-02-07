export type ResourceType =
    | 'pdf' | 'docx' | 'pptx' | 'txt' | 'markdown'
    | 'image' | 'youtube' | 'web_url' | 'google_drive' | 'raw_text' | 'research';

export interface ParsedContent {
    text: string;
    sections: { title: string; content: string }[];
    metadata: Record<string, unknown>;
}

export interface Resource {
    id: string;
    type: ResourceType;
    source: string;
    label: string | null;
    priority: 'primary' | 'supplementary';
    parsed: ParsedContent | null;
    status: 'pending' | 'parsing' | 'parsed' | 'error';
    error: string | null;
}

export interface Project {
    id: string;
    name: string;
    model_provider: string;
    model_name: string;
    created_at: string;
    updated_at: string;
    status: string;
    resource_ids: string[];
    slide_plan: Record<string, unknown> | null;
    prompt_text: string | null;
    variant_count: number;
}

export interface Slide {
    id: string;
    order: number;
    title: string;
    key_points: string[];
    supporting_data: string[];
    source_refs: string[];
    visual_direction: string;
    speaker_notes: string;
}

export interface SlidePlan {
    project_id: string;
    slides: Slide[];
    total_slides: number;
    estimated_duration_min: number | null;
}

export interface VisualDirective {
    theme_name: string;
    color_palette: string[];
    typography: string;
    layout_style: string;
    data_viz_style: string;
    image_guidance: string;
}

export interface PromptVariant {
    variant_number: number;
    variant_description: string;
    visual_directive: VisualDirective;
    full_prompt: string;
}

export interface Prompt {
    project_id: string;
    variants: PromptVariant[];
    raw_text: string;
}

export interface SlideRating {
    slide_id: string;
    thumbs_up: boolean;
    comment: string | null;
}

export interface Feedback {
    project_id: string;
    variant_number: number;
    overall_rating: number;
    tags: string[];
    slide_ratings: SlideRating[];
}

export interface PreferenceProfile {
    preferred_styles: Record<string, number>;
    preferred_tones: Record<string, number>;
    favorite_palettes: string[][];
    bullet_density: string;
    chart_preferences: string[];
    avg_slide_count: number | null;
    total_presentations: number;
}

export interface ChatMessage {
    role: 'assistant' | 'user';
    content: string;
    options?: string[];
    type?: 'question' | 'answer' | 'info';
}

export interface AppSettings {
    active_provider: string;
    providers: Record<string, {
        provider: string;
        api_key: string | null;
        base_url: string | null;
        model_name: string;
        is_configured: boolean;
    }>;
    notebooklm_cookie: string | null;
    serper_api_key: string | null;
}
