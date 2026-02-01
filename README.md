# SlideAlchemy

AI-powered presentation builder that transforms your resources into visually stunning slide decks using NotebookLM.

## Features

- Upload any resource: PDFs, documents, URLs, YouTube videos, images, raw notes
- AI-powered research fills knowledge gaps from web, academic, news, YouTube, Reddit, X
- Interactive Q&A refines your presentation goals, audience, and visual style
- Ultra-detailed prompt engine crafts perfect instructions for NotebookLM
- Generate 1-4 visual variants of your presentation
- Positive reinforcement learning improves outputs over time

## Tech Stack

- **Desktop Shell:** Tauri 2.0
- **Frontend:** Svelte 5 + TailwindCSS 4
- **Backend:** FastAPI (Python 3.12)
- **AI:** Ollama (Gemma 4), OpenRouter, Groq, OpenAI, Google Gemini
- **Slides:** Google NotebookLM via notebooklm-py

## Getting Started

### Prerequisites
- Node.js 20+
- Python 3.12+
- Rust (for Tauri)
- Ollama (optional, for local models)

### Install

```bash
# Frontend
npm install

# Backend
cd backend
pip install -r requirements.txt

# Run dev
npm run tauri dev
```

## License

MIT
