# Architecture

This document describes the system architecture of SlideAlchemy, covering the desktop shell, frontend, backend, data flows, and security model.

## System Architecture Overview

SlideAlchemy is a three-layer desktop application:

```
+------------------------------------------------------------------+
|                        User's Desktop                             |
|                                                                   |
|  +------------------------------------------------------------+  |
|  |                   Tauri 2.0 Shell (Rust)                    |  |
|  |                                                              |  |
|  |  - Spawns Python backend as a sidecar process                |  |
|  |  - Picks an unused port dynamically (default fallback: 8741) |  |
|  |  - Manages application lifecycle                             |  |
|  |  - Provides get_backend_port command to frontend             |  |
|  |                                                              |  |
|  |  +------------------------+  +----------------------------+  |  |
|  |  |   WebView (Frontend)   |  |   Sidecar (Backend)        |  |  |
|  |  |                        |  |                            |  |  |
|  |  |   Svelte 5 SPA         |  |   FastAPI + Uvicorn        |  |  |
|  |  |   SvelteKit (static)   |  |   Python 3.12+             |  |  |
|  |  |   TailwindCSS 4        |  |   Runs on 127.0.0.1:port   |  |  |
|  |  |                        |  |                            |  |  |
|  |  |   Routes:              |  |   Routers:                 |  |  |
|  |  |   / (Dashboard)        |  |   /api/resources           |  |  |
|  |  |   /upload              |  |   /api/chat                |  |  |
|  |  |   /qa                  |  |   /api/slides              |  |  |
|  |  |   /planner             |  |   /api/research            |  |  |
|  |  |   /prompt              |  |   /api/notebooklm          |  |  |
|  |  |   /settings            |  |   /api/feedback            |  |  |
|  |  |                        |  |   /api/settings            |  |  |
|  |  +----------+-------------+  +-------------+--------------+  |  |
|  |             |          HTTP (localhost)     |                  |  |
|  |             +------------------------------+                  |  |
|  +------------------------------------------------------------+  |
|                                |                                  |
+--------------------------------|----------------------------------+
                                 |
                    External Services (Internet)
                    +----------------------------+
                    | Google NotebookLM          |
                    | Ollama (localhost)          |
                    | OpenRouter API             |
                    | Groq API                   |
                    | OpenAI API                 |
                    | Google Gemini API           |
                    | Serper.dev (search)         |
                    | arXiv API                  |
                    | Reddit API                 |
                    +----------------------------+
```

## Frontend Architecture

The frontend is a Svelte 5 single-page application built with SvelteKit in static adapter mode. It compiles to a static bundle that Tauri serves from disk in production.

### Routes

| Route | Page | Purpose |
|-------|------|---------|
| `/` | `+page.svelte` | Dashboard -- project creation, workflow step cards, backend health check |
| `/upload` | `upload/+page.svelte` | Resource management -- file upload, URL/YouTube/text input, resource list |
| `/qa` | `qa/+page.svelte` | Q&A interview -- chat-based 12-question flow with choice and freetext inputs |
| `/planner` | `planner/+page.svelte` | Slide planner -- AI-generated slide plan with drag-to-reorder, inline editing |
| `/prompt` | `prompt/+page.svelte` | Prompt review and generation -- variant count selection, prompt editing, NotebookLM trigger |
| `/settings` | `settings/+page.svelte` | Settings -- provider configuration, API keys, NotebookLM cookie, research keys |

### Layout

`+layout.svelte` provides the app shell: a top navigation bar with links to all routes, and a content area rendered by `{@render children()}` (Svelte 5 snippet syntax).

### Components

| Component | Purpose |
|-----------|---------|
| `ResourceCard` | Displays a single resource with type icon, label, status badge, and delete action |
| `ChatMessage` | Renders a single message bubble in the Q&A chat interface (user or assistant) |
| `StarRating` | Interactive 1-5 star rating input for feedback |
| `TagSelector` | Multi-select tag input for categorizing feedback |
| `ProgressBar` | Shows generation progress with variant count and completion status |
| `VariantPreview` | Side-by-side preview of generated presentation variants |
| `PromptEditor` | Editable text area for reviewing and modifying the generated mega-prompt |
| `SlideCard` | Card view of a single slide in the planner with inline editing of all fields |

### Stores

The `src/lib/stores/chat.ts` module provides Svelte writable stores for Q&A state:

- `chatMessages` -- Array of `ChatMessage` objects (questions and answers)
- `qaComplete` -- Boolean flag indicating the interview is finished
- `qaContext` -- The final context dict produced by the Q&A engine
- `addMessage()` -- Helper to append a message
- `clearChat()` -- Resets all chat state

### API Client

`src/lib/api/client.ts` is a typed HTTP client wrapping all backend endpoints. It uses `fetch()` against `http://localhost:8741` (the default backend port). All methods return typed promises matching the interfaces in `types.ts`.

The client covers:
- Health check
- Resource upload (multipart), URL addition, text addition, listing, deletion
- Feedback submission, preference retrieval
- Slide plan generation and retrieval
- NotebookLM prompt building, generation, status polling
- Research search and gap analysis
- Settings get/save

## Backend Architecture

The backend is a FastAPI application running on Uvicorn. In production, it is compiled into a standalone binary via PyInstaller and spawned by Tauri as a sidecar process.

### Entry Point

`backend/app/main.py` creates the FastAPI app with:
- CORS middleware (allow all origins for localhost communication)
- Lifespan handler that ensures the data directory exists on startup
- 7 routers registered under `/api/` prefixes
- A `/health` endpoint at the root

The app accepts `--port` and `--host` CLI arguments for the sidecar to configure.

### Router Layer

Each router handles one domain of the API:

| Router | Prefix | Responsibility |
|--------|--------|---------------|
| `resources` | `/api/resources` | File upload, URL ingestion, text input, listing, deletion |
| `chat` | `/api/chat` | Model configuration, Q&A start/answer/context, free chat, streaming |
| `settings` | `/api/settings` | CRUD for application settings, provider config, active provider |
| `research` | `/api/research` | Multi-source search, gap analysis |
| `slides` | `/api/slides` | Slide plan generation, retrieval, individual slide CRUD, reordering |
| `notebooklm` | `/api/notebooklm` | Prompt building, NotebookLM generation, status tracking, file download |
| `feedback` | `/api/feedback` | Feedback submission, preference profile, success patterns |

### Service Layer

Services contain the business logic, separated from HTTP concerns:

| Service | File | Responsibility |
|---------|------|---------------|
| `ResourceParser` | `resource_parser.py` | Parses 10 resource types into a unified `ParsedContent` model with text, sections, and metadata |
| `ModelRouter` | `model_router.py` | Routes LLM requests to 5 providers (Ollama, OpenRouter, Groq, OpenAI, Gemini) with both sync and streaming modes |
| `QAEngine` | `qa_engine.py` | Manages the 12-question interview flow with state tracking, answer recording, and context building |
| `ResearchEngine` | `research_engine.py` | Searches web, academic, YouTube, and Reddit sources; analyzes resource gaps via keyword clustering |
| `PromptEngine` | `prompt_engine.py` | Builds the 7-section mega-prompt with 4 theme presets and variant generation |
| `NotebookLMBridge` | `notebooklm_bridge.py` | Wraps notebooklm-py to create notebooks, add sources, send prompts, generate decks, download PPTX |
| `FeedbackService` | `feedback_service.py` | Stores feedback as JSON files, updates preference profiles, manages SQLite success patterns DB |

### Model Layer

Pydantic models define the data structures:

| Model | File | Key Classes |
|-------|------|-------------|
| Resource | `resource.py` | `ResourceType` (11 enum values), `ParsedContent`, `Resource`, `ResourceCreate` |
| Settings | `settings.py` | `ModelProvider` (5 enum values), `ProviderConfig`, `AppSettings` |
| Slide | `slide.py` | `Slide`, `SlideUpdate`, `SlidePlan` |
| Prompt | `prompt.py` | `VisualDirective`, `PromptVariant`, `Prompt` |
| Feedback | `feedback.py` | `SlideRating`, `Feedback`, `PreferenceProfile` |

### Utils

| Module | Purpose |
|--------|---------|
| `config.py` | Defines data directory paths (`~/.slide-alchemy/`), settings encryption/decryption, project data I/O |
| `encryption.py` | Fernet symmetric encryption using a key derived from machine identity (hostname + architecture) |

## Data Flow Diagrams

### Resource Ingestion Flow

```
User uploads file / pastes URL / enters text
         |
         v
    Router (resources.py)
    - Validates file type
    - Saves file to ~/.slide-alchemy/uploads/
    - Creates Resource model
         |
         v
    ResourceParser.parse()
    - Dispatches to type-specific parser
    - PDF: PyPDF2 page extraction
    - DOCX: python-docx paragraph/heading extraction
    - PPTX: python-pptx shape text extraction
    - YouTube: youtube-transcript-api transcript download
    - Web URL: trafilatura content extraction
    - Image: Pillow + pytesseract OCR
    - TXT/Markdown/Raw: built-in text processing
         |
         v
    ParsedContent
    - text: full extracted text
    - sections: [{title, content}] structural breakdown
    - metadata: type-specific info (page count, word count, etc.)
         |
         v
    Stored in-memory as Resource with status="parsed"
```

### Q&A Interview Flow

```
Frontend starts Q&A session
         |
         v
    POST /api/chat/qa/start
    - Creates QAState (index=0, answers={})
    - Returns first question with options
         |
         v
    User selects answer or types freetext
         |
         v
    POST /api/chat/qa/answer
    - Records answer in QAState
    - Advances question index
    - If index < 12: returns next question
    - If index >= 12: marks complete, builds context
         |
         v
    QAEngine.build_context()
    - Extracts all 12 answers into a context dict
    - Keys: audience, goal, tone, slide_count, key_message,
            visual_style, must_include, time_limit, sections,
            data_viz, speaker_notes, call_to_action
         |
         v
    Context dict used by Slide Planner and Prompt Engine
```

### Prompt Generation Flow

```
Frontend requests prompt build
         |
         v
    POST /api/notebooklm/build-prompt
    - Receives: qa_context, slides, resource_summaries, variant_count
         |
         v
    PromptEngine.build_prompt()
         |
         +-- _build_role_section()
         |   "World-class presentation designer..." role definition
         |
         +-- _build_context_section(qa_context)
         |   Audience, goal, tone, time limit, slide count, etc.
         |
         +-- _build_resources_section(summaries)
         |   Numbered source summaries (max 1000 chars each)
         |
         +-- _build_slide_plan_section(slide_plan)
         |   Slide-by-slide: title, key points, data, visuals, notes
         |
         +-- generate_visual_directives(style_hint, count)
         |   Matches user style preference to theme presets
         |   Returns 1-4 VisualDirective objects
         |
         +-- _build_quality_rules(qa_context)
         |   10 quality rules (bullet limits, source refs, etc.)
         |
         +-- _build_preferences_section(preferences)
         |   Learned user preferences from past feedback
         |
         v
    For each directive (variant):
         |
         +-- _build_variant_instruction()
         +-- _assemble_prompt() -- joins all 7 sections
         |
         v
    Prompt object with N PromptVariant objects
    Each variant has: variant_number, theme name, visual directive, full prompt text
```

### NotebookLM Generation Flow

```
Frontend triggers generation
         |
         v
    POST /api/notebooklm/generate
    - Receives: project_id, title, sources, prompts (variant list)
         |
         v
    For each variant prompt:
         |
         v
    NotebookLMBridge.generate_variant()
         |
         +-- create_notebook(title + variant number)
         |   Creates a new NotebookLM notebook
         |
         +-- add_sources(notebook_id, sources)
         |   Adds text, URL, or YouTube sources to the notebook
         |
         +-- generate_slides(notebook_id, prompt)
         |   Sends the mega-prompt via notebook.chat()
         |   Calls notebook.generate_slide_deck()
         |
         +-- download_pptx(notebook_id)
         |   Downloads the generated PPTX to ~/.slide-alchemy/downloads/
         |
         v
    Result: {notebook_id, chat_response, deck_id, pptx_path, variant_number}
         |
         v
    Generation status updated in real-time
    Frontend polls GET /api/notebooklm/status/{project_id}
```

### Feedback Loop Flow

```
User rates a generated variant
         |
         v
    POST /api/feedback/submit
    - Receives: project_id, variant_number, overall_rating (1-5),
                tags, slide_ratings [{slide_id, thumbs_up, comment}]
         |
         v
    FeedbackService.submit_feedback()
         |
         +-- Save feedback JSON to ~/.slide-alchemy/feedbacks/
         |
         +-- _update_preferences()
         |   - Loads existing PreferenceProfile
         |   - For each tag: exponential moving average update
         |     new_weight = current * 0.7 + (rating/5.0) * 0.3
         |   - Increments total_presentations counter
         |   - Saves updated profile to preferences.json
         |
         +-- If rating >= 4: store_success_pattern()
             - Inserts prompt fragment + rating + tags into
               SQLite success_patterns table
         |
         v
    On next prompt generation:
    - PromptEngine reads PreferenceProfile
    - Injects preferred styles, tones, palettes, bullet density
      into the [USER PREFERENCES] section of the mega-prompt
    - QAEngine suggests defaults based on high-confidence preferences
```

## Tauri Integration

### Sidecar Spawning

The Tauri Rust code in `src-tauri/src/lib.rs` handles backend lifecycle:

1. **Port allocation**: Uses `portpicker::pick_unused_port()` to find an available port, falling back to `8741`
2. **Sidecar spawn**: Uses the `tauri-plugin-shell` to spawn the `slide-alchemy-backend` binary as a sidecar process with `--port` and `--host` arguments
3. **State management**: Stores the port in a `Mutex<BackendState>` managed by Tauri's state system
4. **Frontend communication**: Exposes a `get_backend_port` Tauri command so the frontend can discover the port at runtime

### Build Configuration

`tauri.conf.json` defines:

- **Window**: 1280x800, resizable, titled "SlideAlchemy"
- **External binary**: `binaries/slide-alchemy-backend` (PyInstaller-built sidecar)
- **Bundle targets**: All platforms (DMG, NSIS, AppImage, DEB)
- **Build commands**: `npm run build` for frontend, `npm run dev` for development

### Production Binary

For production builds, the Python backend is compiled into a standalone binary using PyInstaller (`backend/build.py`). This binary includes all Python dependencies and the uvicorn server. Tauri bundles it as an external sidecar, so end users do not need Python installed.

## Security Model

### Encryption at Rest

All application settings (API keys, cookies, provider configurations) are encrypted using Fernet symmetric encryption before writing to disk:

- **Key derivation**: A SHA-256 hash of `{hostname}-{machine_architecture}-slide-alchemy` produces the encryption key
- **Storage**: Encrypted settings are stored in `~/.slide-alchemy/config.enc`
- **On read**: The key is re-derived from the current machine identity and used to decrypt

This means settings are tied to the specific machine and cannot be read if the config file is copied to a different computer.

### Local-Only Communication

- The backend binds exclusively to `127.0.0.1` -- it is never exposed to the network
- CORS is configured to allow all origins, but since the backend only listens on localhost, this only permits communication from the local webview
- No data is sent to external services except explicit user-initiated actions (LLM queries, NotebookLM generation, research searches)

### Data Storage

All data is stored locally in `~/.slide-alchemy/`:

```
~/.slide-alchemy/
├── config.enc          # Encrypted settings (API keys, cookies)
├── preferences.json    # User preference profile (no sensitive data)
├── patterns.db         # SQLite success patterns database
├── projects/           # Project data (JSON files)
├── uploads/            # Uploaded resource files
├── downloads/          # Generated PPTX files
└── feedbacks/          # Feedback JSON files
```
