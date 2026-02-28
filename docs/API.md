# API Reference

The SlideAlchemy backend exposes a REST API on `http://127.0.0.1:{port}` (default port: 8741). All endpoints accept and return JSON unless otherwise noted.

## Health

### `GET /health`

Health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

**Example:**

```bash
curl http://localhost:8741/health
```

---

## Resources

Endpoints for uploading, ingesting, and managing source materials.

### `POST /api/resources/upload`

Upload a file resource. Uses multipart form data.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | The file to upload |
| `priority` | string | No | `"primary"` (default) or `"supplementary"` |
| `label` | string | No | Display label (defaults to filename) |

**Supported file types:** `.pdf`, `.docx`, `.pptx`, `.txt`, `.md`, `.png`, `.jpg`, `.jpeg`, `.webp`

**Response:** `Resource` object

```json
{
  "id": "a1b2c3d4-...",
  "type": "pdf",
  "source": "/Users/.../.slide-alchemy/uploads/a1b2c3d4.pdf",
  "label": "report.pdf",
  "priority": "primary",
  "parsed": {
    "text": "Full extracted text...",
    "sections": [{"title": "Page 1", "content": "..."}],
    "metadata": {"type": "pdf", "page_count": 12, "char_count": 45000}
  },
  "status": "parsed",
  "error": null
}
```

**Example:**

```bash
curl -X POST http://localhost:8741/api/resources/upload \
  -F "file=@report.pdf" \
  -F "priority=primary" \
  -F "label=Q4 Report"
```

### `POST /api/resources/url`

Add a URL-based resource (web page or YouTube video).

**Request body:**

```json
{
  "type": "web_url",
  "source": "https://example.com/article",
  "label": "Example Article",
  "priority": "primary"
}
```

For YouTube:

```json
{
  "type": "youtube",
  "source": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "label": "YouTube Video",
  "priority": "supplementary"
}
```

**Response:** `Resource` object (same schema as upload)

**Example:**

```bash
curl -X POST http://localhost:8741/api/resources/url \
  -H "Content-Type: application/json" \
  -d '{"type": "web_url", "source": "https://example.com", "priority": "primary"}'
```

### `POST /api/resources/text`

Add raw text as a resource.

**Request body:**

```json
{
  "type": "raw_text",
  "source": "These are my notes about the quarterly results...",
  "label": "Meeting Notes",
  "priority": "primary"
}
```

**Response:** `Resource` object

**Example:**

```bash
curl -X POST http://localhost:8741/api/resources/text \
  -H "Content-Type: application/json" \
  -d '{"type": "raw_text", "source": "My raw notes here", "label": "Notes"}'
```

### `GET /api/resources/`

List all resources.

**Response:** Array of `Resource` objects

```bash
curl http://localhost:8741/api/resources/
```

### `GET /api/resources/{resource_id}`

Get a single resource by ID.

**Response:** `Resource` object

```bash
curl http://localhost:8741/api/resources/a1b2c3d4-...
```

### `DELETE /api/resources/{resource_id}`

Delete a resource.

**Response:**

```json
{"deleted": true}
```

```bash
curl -X DELETE http://localhost:8741/api/resources/a1b2c3d4-...
```

---

## Chat & Q/A

Endpoints for configuring the AI model and running the Q&A interview.

### `POST /api/chat/configure`

Configure the active AI model provider.

**Request body:**

```json
{
  "provider": "ollama",
  "model_name": "gemma3:4b",
  "api_key": null,
  "base_url": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | string | Yes | One of: `ollama`, `openrouter`, `groq`, `openai`, `gemini` |
| `model_name` | string | Yes | Model identifier for the provider |
| `api_key` | string | No | API key (required for cloud providers) |
| `base_url` | string | No | Custom base URL (overrides provider default) |

**Response:**

```json
{"status": "configured", "provider": "ollama", "model": "gemma3:4b"}
```

**Example:**

```bash
curl -X POST http://localhost:8741/api/chat/configure \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq", "model_name": "llama-3.1-70b-versatile", "api_key": "gsk_..."}'
```

### `POST /api/chat/qa/start`

Start a new Q&A interview session.

**Query parameter:** `project_id` (string)

**Response:**

```json
{
  "question": {
    "key": "audience",
    "text": "Who is your target audience for this presentation?",
    "options": ["Business executives", "Technical team", "Students/Academia", "General public", "Investors/Stakeholders"],
    "type": "choice",
    "question_number": 1,
    "total_questions": 12
  },
  "state": {
    "current_question_index": 0,
    "answers": {},
    "is_complete": false,
    "skipped_keys": []
  }
}
```

**Example:**

```bash
curl -X POST "http://localhost:8741/api/chat/qa/start?project_id=my-project"
```

### `POST /api/chat/qa/answer`

Submit an answer to the current Q&A question.

**Request body:**

```json
{
  "project_id": "my-project",
  "answer": "Business executives"
}
```

**Response (not complete):**

```json
{
  "complete": false,
  "question": {
    "key": "goal",
    "text": "What's the primary goal of this presentation?",
    "options": ["Inform/Educate", "Persuade/Convince", "Teach/Train", "Pitch/Sell", "Report/Update"],
    "type": "choice",
    "question_number": 2,
    "total_questions": 12
  },
  "state": { "current_question_index": 1, "answers": {"audience": "Business executives"}, "is_complete": false }
}
```

**Response (complete after question 12):**

```json
{
  "complete": true,
  "context": {
    "audience": "Business executives",
    "goal": "Inform/Educate",
    "tone": "Formal & Professional",
    "slide_count": "10-20 (Standard)",
    "key_message": "Q4 results exceeded all targets",
    "visual_style": "Corporate & Professional",
    "must_include": "Revenue chart, customer growth data",
    "time_limit": "15 minutes",
    "sections": "Introduction, Q4 Highlights, Revenue, Growth, Roadmap, Q&A",
    "data_viz": "Yes, lots of data viz",
    "speaker_notes": "Yes, detailed notes",
    "call_to_action": "Approve Q1 budget"
  },
  "state": { "current_question_index": 12, "answers": {...}, "is_complete": true }
}
```

### `POST /api/chat/qa/context`

Retrieve the built context from a completed Q&A session.

**Query parameter:** `project_id` (string)

**Response:** Context dict (same as the `context` field in the complete answer response)

```bash
curl -X POST "http://localhost:8741/api/chat/qa/context?project_id=my-project"
```

### `POST /api/chat/message`

Send a free-form chat message to the configured AI model.

**Request body:**

```json
{
  "project_id": "my-project",
  "message": "What makes a good opening slide?"
}
```

**Response:**

```json
{
  "response": "A good opening slide should..."
}
```

### `POST /api/chat/message/stream`

Send a chat message with streaming response (Server-Sent Events).

**Request body:** Same as `/api/chat/message`

**Response:** `text/event-stream`

```
data: A good
data:  opening
data:  slide should...
data: [DONE]
```

**Example:**

```bash
curl -N -X POST http://localhost:8741/api/chat/message/stream \
  -H "Content-Type: application/json" \
  -d '{"project_id": "test", "message": "Hello"}'
```

---

## Settings

Endpoints for managing application configuration.

### `GET /api/settings/`

Get current application settings.

**Response:**

```json
{
  "active_provider": "ollama",
  "providers": {
    "ollama": {
      "provider": "ollama",
      "api_key": null,
      "base_url": null,
      "model_name": "gemma3:4b",
      "is_configured": true
    }
  },
  "notebooklm_cookie": "...",
  "serper_api_key": "...",
  "reddit_client_id": null,
  "reddit_client_secret": null,
  "data_dir": "~/.slide-alchemy"
}
```

### `PUT /api/settings/`

Replace all settings.

**Request body:** Full `AppSettings` object

**Response:** `{"status": "saved"}`

### `PUT /api/settings/provider/{provider}`

Update a single provider's configuration.

**Path parameter:** `provider` (e.g., `ollama`, `openrouter`, `groq`, `openai`, `gemini`)

**Request body:**

```json
{
  "provider": "groq",
  "api_key": "gsk_...",
  "base_url": null,
  "model_name": "llama-3.1-70b-versatile",
  "is_configured": true
}
```

**Response:** `{"status": "saved", "provider": "groq"}`

### `PUT /api/settings/active-provider`

Set the active model provider.

**Query parameter:** `provider` (string)

**Response:** `{"status": "active_provider_set", "provider": "groq"}`

```bash
curl -X PUT "http://localhost:8741/api/settings/active-provider?provider=groq"
```

---

## Research

Endpoints for searching external sources and analyzing knowledge gaps.

### `POST /api/research/search`

Search all configured sources (web, academic, YouTube, Reddit).

**Request body:**

```json
{
  "query": "machine learning presentation best practices"
}
```

**Response:** Array of `ResearchResult` objects

```json
[
  {
    "source": "google",
    "title": "How to Present ML Results",
    "snippet": "When presenting machine learning results to stakeholders...",
    "url": "https://example.com/article",
    "source_type": "web"
  },
  {
    "source": "arxiv",
    "title": "A Survey of Presentation Techniques for Data Science",
    "snippet": "This paper surveys...",
    "url": "https://arxiv.org/abs/2301.12345",
    "source_type": "academic"
  }
]
```

### `POST /api/research/gaps`

Analyze uploaded resources for knowledge gaps and suggest research queries.

**Request body:**

```json
{
  "resource_texts": ["Full text of resource 1...", "Full text of resource 2..."],
  "qa_context": {
    "sections": "Introduction, Market Analysis, Competition",
    "key_message": "Our product leads the market"
  }
}
```

**Response:**

```json
{
  "gaps": ["market analysis competition", "product leads differentiation"]
}
```

### `POST /api/research/web`

Search web only (via Serper).

**Request/Response:** Same structure as `/api/research/search`, but only returns web results.

### `POST /api/research/academic`

Search academic papers only (via arXiv).

**Request/Response:** Same structure as `/api/research/search`, but only returns academic results.

---

## Slides

Endpoints for generating and managing the slide plan.

### `POST /api/slides/generate-plan`

Generate an AI-powered slide plan.

**Request body:**

```json
{
  "project_id": "my-project",
  "qa_context": {
    "audience": "Business executives",
    "goal": "Inform/Educate",
    "tone": "Formal & Professional",
    "slide_count": "10-20 (Standard)",
    "key_message": "Q4 exceeded targets",
    "visual_style": "Corporate & Professional",
    "sections": "Intro, Revenue, Growth, Roadmap",
    "must_include": "Revenue chart",
    "time_limit": "15 minutes"
  },
  "resource_summaries": ["Summary of resource 1...", "Summary of resource 2..."]
}
```

**Response:** `SlidePlan` object

```json
{
  "project_id": "my-project",
  "slides": [
    {
      "id": "uuid-...",
      "order": 0,
      "title": "Q4 Results: Exceeding Expectations",
      "key_points": ["Revenue up 23% YoY", "Customer base grew 15%"],
      "supporting_data": ["$4.2M revenue", "1,200 new customers"],
      "source_refs": [],
      "visual_direction": "Hero number with trend line chart",
      "speaker_notes": "Open with the headline number to grab attention..."
    }
  ],
  "total_slides": 10,
  "estimated_duration_min": null
}
```

### `GET /api/slides/{project_id}`

Get the slide plan for a project.

**Response:** `SlidePlan` object

### `PUT /api/slides/{project_id}/slide/{slide_id}`

Update a single slide's content.

**Request body:** (all fields optional)

```json
{
  "title": "Updated Title",
  "key_points": ["New point 1", "New point 2"],
  "supporting_data": ["New data"],
  "visual_direction": "Full-bleed image with text overlay",
  "speaker_notes": "Updated notes",
  "order": 3
}
```

**Response:** `{"updated": true}`

### `POST /api/slides/{project_id}/slide`

Add a new slide to the plan.

**Request body:** Full `Slide` object

**Response:** `{"added": true, "slide_id": "uuid-..."}`

### `DELETE /api/slides/{project_id}/slide/{slide_id}`

Delete a slide from the plan.

**Response:** `{"deleted": true}`

### `PUT /api/slides/{project_id}/reorder`

Reorder slides by providing an ordered list of slide IDs.

**Request body:** Array of slide ID strings

```json
["slide-id-3", "slide-id-1", "slide-id-2"]
```

**Response:** `{"reordered": true}`

---

## NotebookLM

Endpoints for building prompts, generating presentations, and downloading results.

### `POST /api/notebooklm/build-prompt`

Build the mega-prompt from Q&A context, slide plan, and resources.

**Request body:**

```json
{
  "project_id": "my-project",
  "qa_context": { "audience": "...", "goal": "...", ... },
  "slides": [
    { "order": 0, "title": "Intro", "key_points": ["..."], ... }
  ],
  "resource_summaries": ["Summary 1", "Summary 2"],
  "variant_count": 2
}
```

**Response:** Full `Prompt` object with variants

```json
{
  "project_id": "my-project",
  "role_section": "You are a world-class presentation designer...",
  "context_section": "[PRESENTATION CONTEXT]\n- Target Audience: ...",
  "resources_summary": "[RESOURCES SUMMARY]\nSource 1: ...",
  "slide_plan_section": "[SLIDE-BY-SLIDE PLAN]\n--- Slide 1: ...",
  "quality_rules": "[QUALITY RULES]\n1. Maximum 4 bullet points...",
  "user_preferences_section": "",
  "variants": [
    {
      "variant_number": 1,
      "variant_description": "Corporate Blue",
      "visual_directive": {
        "theme_name": "Corporate Blue",
        "color_palette": ["#1a365d", "#2b6cb0", "#4299e1", "#e2e8f0", "#ffffff"],
        "typography": "Inter for headings, Source Sans Pro for body",
        "layout_style": "grid with ample whitespace",
        "data_viz_style": "clean bar and line charts with blue gradient",
        "image_guidance": "professional stock photography, abstract geometric patterns"
      },
      "full_prompt": "[ROLE]\nYou are a world-class...\n\n[PRESENTATION CONTEXT]\n..."
    }
  ],
  "raw_text": "..."
}
```

### `POST /api/notebooklm/generate`

Generate presentations via NotebookLM. This is the main generation endpoint.

**Request body:**

```json
{
  "project_id": "my-project",
  "title": "Q4 Business Review",
  "sources": [
    {"type": "text", "content": "Full resource text..."},
    {"type": "url", "content": "https://example.com"},
    {"type": "youtube", "content": "https://youtube.com/watch?v=..."}
  ],
  "prompts": [
    {"variant_number": 1, "full_prompt": "The full mega-prompt text..."},
    {"variant_number": 2, "full_prompt": "Second variant prompt..."}
  ]
}
```

**Response:**

```json
{
  "results": [
    {
      "notebook_id": "abc123",
      "chat_response": "I'll create a presentation with...",
      "deck_id": "generated",
      "pptx_path": "/Users/.../.slide-alchemy/downloads/abc123_slides.pptx",
      "variant_number": 1
    },
    {
      "notebook_id": "def456",
      "chat_response": "Creating variant 2...",
      "deck_id": "generated",
      "pptx_path": "/Users/.../.slide-alchemy/downloads/def456_slides.pptx",
      "variant_number": 2
    }
  ]
}
```

### `GET /api/notebooklm/status/{project_id}`

Poll generation status.

**Response:**

```json
{
  "status": "generating",
  "total_variants": 2,
  "completed": 1,
  "results": [
    { "notebook_id": "abc123", "variant_number": 1, "pptx_path": "..." }
  ]
}
```

Status values: `"not_started"`, `"generating"`, `"done"`

### `GET /api/notebooklm/download/{filename}`

Download a generated PPTX file.

**Response:** Binary file download (`application/vnd.openxmlformats-officedocument.presentationml.presentation`)

```bash
curl -O http://localhost:8741/api/notebooklm/download/abc123_slides.pptx
```

---

## Feedback

Endpoints for submitting presentation feedback and retrieving learned preferences.

### `POST /api/feedback/submit`

Submit feedback for a generated presentation variant.

**Request body:**

```json
{
  "project_id": "my-project",
  "variant_number": 1,
  "overall_rating": 4,
  "tags": ["clean design", "good flow", "needs more data"],
  "slide_ratings": [
    {"slide_id": "uuid-1", "thumbs_up": true, "comment": null},
    {"slide_id": "uuid-2", "thumbs_up": false, "comment": "Too much text"}
  ]
}
```

**Response:** `{"status": "saved"}`

If `overall_rating >= 4`, the prompt fragment and tags are also stored in the success patterns database.

### `GET /api/feedback/preferences`

Get the learned preference profile.

**Response:**

```json
{
  "preferred_styles": {"clean design": 0.82, "dark theme": 0.65},
  "preferred_tones": {"professional": 0.9},
  "favorite_palettes": [["#1a365d", "#2b6cb0", "#4299e1", "#e2e8f0", "#ffffff"]],
  "bullet_density": "medium",
  "chart_preferences": [],
  "avg_slide_count": 15.0,
  "total_presentations": 5,
  "last_updated": "2025-01-15T10:30:00"
}
```

### `GET /api/feedback/patterns`

Get top success patterns from high-rated presentations.

**Query parameter:** `limit` (int, default: 10)

**Response:**

```json
[
  {
    "prompt_fragment": "Tags: clean design, good flow",
    "rating": 5,
    "tags": ["clean design", "good flow"],
    "created_at": "2025-01-15T10:30:00"
  }
]
```

### `GET /api/feedback/{project_id}`

Get all feedback entries for a project.

**Response:** Array of `Feedback` objects

```bash
curl http://localhost:8741/api/feedback/my-project
```
