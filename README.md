<p align="center">
  <h1 align="center">SlideAlchemy</h1>
  <p align="center">
    Transform raw resources into visually stunning presentations using AI and NotebookLM
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/svelte-5-FF3E00?style=flat-square&logo=svelte&logoColor=white" alt="Svelte 5">
  <img src="https://img.shields.io/badge/tauri-2.0-FFC131?style=flat-square&logo=tauri&logoColor=white" alt="Tauri 2.0">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License MIT">
</p>

---

SlideAlchemy is a desktop application that takes your documents, URLs, videos, and notes, runs them through an AI-powered pipeline, and produces polished presentation decks via Google NotebookLM. It combines a Svelte 5 frontend, a FastAPI backend, and a Tauri 2.0 shell into a single installable app for macOS, Windows, and Linux.

## Features

- **Multi-format resource ingestion** -- Upload PDFs, DOCX, PPTX, TXT, Markdown, images (with OCR), YouTube videos (transcript extraction), and web URLs (content extraction)
- **AI-powered research** -- Automatically identifies knowledge gaps in your resources and fills them from the web (Serper/Google), academic papers (arXiv), YouTube, and Reddit
- **Interactive Q&A interview** -- A 12-question guided interview refines your target audience, presentation goals, visual style, tone, slide count, time limit, and call to action
- **Intelligent slide planning** -- AI generates a detailed slide-by-slide plan with key points, supporting data, visual direction, and speaker notes for each slide
- **Ultra-detailed prompt engine** -- Assembles a 7-section mega-prompt with role definition, context, resource summaries, slide plan, visual directives, quality rules, and learned user preferences
- **4 visual theme presets** -- Corporate Blue, Dark & Modern, Minimal & Clean, Vibrant & Creative, each with full color palettes, typography, layout styles, and data visualization guidance
- **1-4 variant generation** -- Generate up to 4 visual variants of your presentation in a single run, each with a different theme treatment
- **NotebookLM integration** -- Creates notebooks, adds sources, sends the crafted prompt, generates slide decks, and downloads the resulting PPTX files
- **Positive reinforcement learning** -- Rate your presentations with 1-5 stars and per-slide thumbs up/down feedback; the system builds a preference profile that improves future prompts
- **Success pattern database** -- High-rated presentations have their prompt fragments stored in a SQLite database for reuse in future sessions
- **Encrypted local storage** -- All settings and API keys are encrypted at rest using Fernet symmetric encryption derived from machine identity
- **5 model providers** -- Ollama (local), OpenRouter, Groq, OpenAI, and Google Gemini with streaming support across all providers

## Architecture Overview

```
+-------------------------------------------------------------+
|                    Tauri 2.0 Desktop Shell                   |
|  +---------------------------+  +-------------------------+  |
|  |    Svelte 5 Frontend      |  |   FastAPI Backend       |  |
|  |                           |  |   (Python sidecar)      |  |
|  |  Dashboard (/*)           |  |                         |  |
|  |  Upload    (/upload)      |  |   /api/resources        |  |
|  |  Q&A       (/qa)       <---->   /api/chat              |  |
|  |  Planner   (/planner)     |  |   /api/slides           |  |
|  |  Generate  (/prompt)      |  |   /api/research         |  |
|  |  Settings  (/settings)    |  |   /api/notebooklm       |  |
|  |                           |  |   /api/feedback         |  |
|  |  SvelteKit + TailwindCSS  |  |   /api/settings         |  |
|  +---------------------------+  +-------------------------+  |
|         Port 1420 (dev)              Port 8741 (dynamic)     |
+-------------------------------------------------------------+
                                            |
                                            v
                                   Google NotebookLM
                                   (via notebooklm-py)
```

## Screenshots

> Screenshots will be added after the first release build.

## Installation

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Frontend build toolchain |
| Python | 3.12+ | Backend runtime |
| Rust | latest stable | Tauri desktop shell |
| Ollama | latest (optional) | Local AI models |

### macOS

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Node.js (via Homebrew)
brew install node

# Install Python 3.12+
brew install python@3.12

# Install Ollama (optional, for local models)
brew install ollama

# Clone and install
git clone https://github.com/AshutoshBuilds/slide-alchemy.git
cd slide-alchemy

# Frontend dependencies
npm install

# Backend dependencies
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

### Windows

```powershell
# Install Rust from https://rustup.rs
# Install Node.js from https://nodejs.org (LTS)
# Install Python 3.12+ from https://python.org

# Install Ollama (optional) from https://ollama.ai

git clone https://github.com/AshutoshBuilds/slide-alchemy.git
cd slide-alchemy

npm install

cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### Linux (Ubuntu/Debian)

```bash
# System dependencies for Tauri
sudo apt update
sudo apt install -y libwebkit2gtk-4.1-dev build-essential curl wget \
    libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

# Install Node.js 20+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Python 3.12+
sudo apt install -y python3.12 python3.12-venv

# Clone and install
git clone https://github.com/AshutoshBuilds/slide-alchemy.git
cd slide-alchemy
npm install

cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

## Configuration

All settings are stored encrypted in `~/.slide-alchemy/config.enc`. Configure them through the Settings page in the app, or before first launch by running the backend manually.

### AI Model Providers

SlideAlchemy supports 5 model providers. You need at least one configured to use the Q&A interview and slide planning features.

| Provider | API Key Required | Base URL | Recommended Models |
|----------|-----------------|----------|--------------------|
| **Ollama** | No (local) | `http://localhost:11434` | `gemma3:4b`, `llama3.1:8b`, `mistral` |
| **OpenRouter** | Yes | `https://openrouter.ai/api/v1` | `google/gemma-3-27b-it`, `anthropic/claude-sonnet-4` |
| **Groq** | Yes | `https://api.groq.com/openai/v1` | `llama-3.1-70b-versatile`, `mixtral-8x7b-32768` |
| **OpenAI** | Yes | `https://api.openai.com/v1` | `gpt-4o`, `gpt-4o-mini` |
| **Google Gemini** | Yes | Native SDK | `gemini-2.5-flash`, `gemini-2.5-pro` |

#### Ollama Setup (Local, Free)

```bash
# Install and start Ollama
ollama serve

# Pull a model
ollama pull gemma3:4b
```

No API key needed. SlideAlchemy detects Ollama automatically on localhost.

#### Cloud Provider Keys

1. **OpenRouter**: Get an API key at [openrouter.ai/keys](https://openrouter.ai/keys)
2. **Groq**: Get an API key at [console.groq.com](https://console.groq.com)
3. **OpenAI**: Get an API key at [platform.openai.com](https://platform.openai.com/api-keys)
4. **Google Gemini**: Get an API key at [aistudio.google.com](https://aistudio.google.com/apikey)

### NotebookLM Cookie

SlideAlchemy uses `notebooklm-py` to interact with Google NotebookLM. You need to provide your browser cookie for authentication:

1. Open [notebooklm.google.com](https://notebooklm.google.com) in your browser
2. Open DevTools (F12) and go to the Network tab
3. Refresh the page and find any request to `notebooklm.google.com`
4. Copy the full `Cookie` header value
5. Paste it in SlideAlchemy Settings under "NotebookLM Cookie"

### Serper API (Research)

The research engine uses [Serper.dev](https://serper.dev) for web and YouTube search:

1. Sign up at [serper.dev](https://serper.dev) (free tier: 2,500 searches/month)
2. Copy your API key
3. Paste it in SlideAlchemy Settings under "Serper API Key"

### Reddit API (Optional Research)

For Reddit research results, create a Reddit app:

1. Go to [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
2. Create a "script" type application
3. Copy the Client ID and Client Secret into Settings

## Usage Walkthrough

SlideAlchemy follows an 8-step workflow from raw resources to finished presentation:

### Step 1: Create a New Presentation

Click **"+ New Presentation"** on the dashboard. Give it a name and click "Create & Start."

### Step 2: Upload Resources

Navigate to the **Resources** page. Add your source materials:

- **File upload**: Drag and drop PDFs, DOCX, PPTX, TXT, Markdown, or images
- **URL**: Paste any web URL for automatic content extraction via Trafilatura
- **YouTube**: Paste a YouTube URL for automatic transcript extraction
- **Raw text**: Paste notes, bullet points, or any text directly

Each resource is parsed immediately and its content extracted for downstream use.

### Step 3: AI Research (Optional)

On the Resources page, SlideAlchemy can analyze your uploaded content for knowledge gaps. The research engine searches across:

- Google web results (via Serper)
- Academic papers (arXiv)
- YouTube videos (via Serper video search)
- Reddit discussions (via PRAW)

Results are added as supplementary resources.

### Step 4: Q&A Interview

Navigate to the **Q&A** page. The AI walks you through 12 targeted questions:

1. Target audience
2. Primary goal (inform, persuade, teach, pitch, report)
3. Tone and voice
4. Slide count target
5. Core message (free text)
6. Visual style preference
7. Must-include content (free text)
8. Presentation duration
9. Main sections/topics (free text)
10. Data visualization needs
11. Speaker notes preference
12. Call to action (free text)

For returning users, the system suggests defaults based on your preference profile.

### Step 5: Plan Slides

Navigate to the **Planner** page. The AI generates a slide-by-slide plan based on your Q&A answers and resource content. Each slide includes:

- A compelling title
- 2-4 key points
- Supporting data, stats, or quotes
- Visual direction notes
- Speaker notes for the presenter

You can edit, reorder, add, or delete slides before proceeding.

### Step 6: Generate Prompts

On the **Generate** page, the prompt engine assembles the mega-prompt. Choose how many visual variants (1-4) you want. Each variant gets a different theme preset applied. Review and optionally edit the generated prompts.

### Step 7: Generate via NotebookLM

Click **Generate**. For each variant, SlideAlchemy:

1. Creates a new NotebookLM notebook
2. Adds your resources as sources
3. Sends the crafted prompt via chat
4. Triggers slide deck generation
5. Downloads the resulting PPTX file

Progress is tracked in real-time.

### Step 8: Review and Feedback

After generation completes, review each variant. Provide feedback:

- **Overall rating**: 1-5 stars
- **Per-slide rating**: Thumbs up/down on individual slides
- **Tags**: Label what worked (e.g., "good visuals", "clear flow")

Your feedback updates your preference profile and stores success patterns for future use.

## Supported Resource Types

| Type | Extension / Format | Parser | Details |
|------|-------------------|--------|---------|
| PDF | `.pdf` | PyPDF2 | Full text extraction, page-by-page sections |
| Word Document | `.docx` | python-docx | Paragraph and heading extraction |
| PowerPoint | `.pptx` | python-pptx | Text extraction from all shapes on all slides |
| Plain Text | `.txt` | Built-in | Direct text ingestion |
| Markdown | `.md` | Built-in | Section extraction via heading detection, markup stripped |
| Image | `.png`, `.jpg`, `.jpeg`, `.webp` | Pillow + Tesseract OCR | Optical character recognition |
| YouTube | URL | youtube-transcript-api | Automatic transcript download |
| Web URL | Any URL | Trafilatura | Content extraction with boilerplate removal |
| Raw Text | Pasted text | Built-in | Direct ingestion, word/char count metadata |

## Build Instructions

### Development Mode

Run the full stack in development mode with hot reload:

```bash
# Terminal 1: Start the backend
cd backend
source .venv/bin/activate
python -m app.main --port 8741

# Terminal 2: Start the Tauri dev shell (includes frontend)
npm run tauri dev
```

Or use the dev script:

```bash
./scripts/dev.sh
```

### Production Build

#### 1. Build the Python Backend Binary

```bash
cd backend
source .venv/bin/activate
pip install pyinstaller
python build.py
```

This produces a standalone binary at `backend/dist/slide-alchemy-backend` (or `.exe` on Windows).

#### 2. Copy Binary to Tauri Sidecar Location

```bash
# macOS (Apple Silicon)
cp backend/dist/slide-alchemy-backend src-tauri/binaries/slide-alchemy-backend-aarch64-apple-darwin

# macOS (Intel)
cp backend/dist/slide-alchemy-backend src-tauri/binaries/slide-alchemy-backend-x86_64-apple-darwin

# Linux
cp backend/dist/slide-alchemy-backend src-tauri/binaries/slide-alchemy-backend-x86_64-unknown-linux-gnu

# Windows
cp backend/dist/slide-alchemy-backend.exe src-tauri/binaries/slide-alchemy-backend-x86_64-pc-windows-msvc.exe
```

#### 3. Build the Tauri App

```bash
npm run tauri build
```

Output locations:
- **macOS**: `src-tauri/target/release/bundle/dmg/SlideAlchemy_0.1.0_aarch64.dmg`
- **Windows**: `src-tauri/target/release/bundle/nsis/SlideAlchemy_0.1.0_x64-setup.exe`
- **Linux**: `src-tauri/target/release/bundle/appimage/SlideAlchemy_0.1.0_amd64.AppImage`

## Project Structure

```
slide-alchemy/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point, router registration
│   │   ├── routers/
│   │   │   ├── resources.py    # File upload, URL/text ingestion endpoints
│   │   │   ├── chat.py         # Model config, Q&A flow, chat endpoints
│   │   │   ├── settings.py     # App settings CRUD
│   │   │   ├── research.py     # Web/academic/YouTube/Reddit search
│   │   │   ├── slides.py       # Slide plan generation and editing
│   │   │   ├── notebooklm.py   # Prompt building and NotebookLM generation
│   │   │   └── feedback.py     # Feedback submission and preference retrieval
│   │   ├── services/
│   │   │   ├── resource_parser.py    # Multi-format document parsing
│   │   │   ├── model_router.py       # Multi-provider LLM routing
│   │   │   ├── qa_engine.py          # 12-question interview engine
│   │   │   ├── research_engine.py    # Multi-source research with gap analysis
│   │   │   ├── prompt_engine.py      # 7-section mega-prompt builder
│   │   │   ├── notebooklm_bridge.py  # NotebookLM API wrapper
│   │   │   └── feedback_service.py   # Feedback storage and preference learning
│   │   ├── models/
│   │   │   ├── resource.py     # Resource, ParsedContent, ResourceType
│   │   │   ├── settings.py     # AppSettings, ProviderConfig, ModelProvider
│   │   │   ├── slide.py        # Slide, SlidePlan, SlideUpdate
│   │   │   ├── prompt.py       # Prompt, PromptVariant, VisualDirective
│   │   │   ├── feedback.py     # Feedback, SlideRating, PreferenceProfile
│   │   │   └── project.py      # Project model
│   │   └── utils/
│   │       ├── config.py       # Data dir management, settings I/O
│   │       └── encryption.py   # Fernet encryption for settings at rest
│   ├── tests/                  # pytest test suite
│   ├── build.py                # PyInstaller build script
│   └── requirements.txt        # Python dependencies
├── src/                        # Svelte 5 frontend
│   ├── routes/
│   │   ├── +layout.svelte      # App shell with navigation
│   │   ├── +page.svelte        # Dashboard with workflow steps
│   │   ├── upload/+page.svelte # Resource upload interface
│   │   ├── qa/+page.svelte     # Q&A interview chat interface
│   │   ├── planner/+page.svelte# Slide plan editor
│   │   ├── prompt/+page.svelte # Prompt review and generation trigger
│   │   └── settings/+page.svelte# Settings configuration
│   └── lib/
│       ├── api/
│       │   ├── client.ts       # Typed HTTP client for all API endpoints
│       │   └── types.ts        # TypeScript interfaces matching backend models
│       ├── stores/
│       │   └── chat.ts         # Svelte stores for Q&A state
│       └── components/
│           ├── ResourceCard.svelte   # Resource display card
│           ├── ChatMessage.svelte    # Chat bubble component
│           ├── StarRating.svelte     # 1-5 star rating input
│           ├── TagSelector.svelte    # Multi-tag selector
│           ├── ProgressBar.svelte    # Generation progress indicator
│           ├── VariantPreview.svelte # Side-by-side variant comparison
│           ├── PromptEditor.svelte   # Prompt text editor
│           └── SlideCard.svelte      # Slide plan card with editing
├── src-tauri/                  # Tauri 2.0 desktop shell
│   ├── src/
│   │   ├── lib.rs              # Sidecar spawning, port allocation, commands
│   │   └── main.rs             # Entry point
│   ├── Cargo.toml              # Rust dependencies
│   └── tauri.conf.json         # Tauri config (window, sidecar, bundle)
├── scripts/
│   ├── dev.sh                  # Development launch script
│   └── build-all.sh            # Full production build script
├── package.json                # Node.js dependencies and scripts
├── svelte.config.js            # SvelteKit configuration
├── vite.config.ts              # Vite build configuration
└── tailwind.config.js          # TailwindCSS 4 configuration
```

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Desktop Shell | Tauri | 2.0 |
| Frontend Framework | Svelte | 5.0 |
| Frontend Tooling | SvelteKit | 2.0 |
| CSS Framework | TailwindCSS | 4.0 |
| Build Tool | Vite | 6.0 |
| Backend Framework | FastAPI | 0.115 |
| Backend Runtime | Python | 3.12+ |
| ASGI Server | Uvicorn | 0.34 |
| NotebookLM Client | notebooklm-py | 0.3.4 |
| Local AI | Ollama | 0.4.7 (Python client) |
| OpenAI-compatible | openai (Python) | 1.63 |
| Google AI | google-genai | 1.5 |
| PDF Parsing | PyPDF2 | 3.0 |
| DOCX Parsing | python-docx | 1.1 |
| PPTX Parsing | python-pptx | 1.0 |
| YouTube Transcripts | youtube-transcript-api | 0.6 |
| Web Scraping | Trafilatura | 2.0 |
| Academic Search | arxiv (Python) | 2.1 |
| Reddit API | PRAW | 7.8 |
| OCR | Pillow + pytesseract | 11.1 / 0.3 |
| Encryption | cryptography (Fernet) | 44.0 |
| HTTP Client | httpx | 0.28 |
| Rust Port Picker | portpicker | 0.1 |

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Follow existing code patterns -- Pydantic models for data, service classes for business logic, routers for HTTP endpoints
4. Add tests for new services in `backend/tests/`
5. Ensure `pytest` passes: `cd backend && pytest`
6. Submit a pull request with a clear description of the change

For detailed development guidance, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## License

MIT
