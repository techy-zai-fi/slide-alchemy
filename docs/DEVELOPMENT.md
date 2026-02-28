# Development Guide

This guide covers setting up a development environment, running tests, extending SlideAlchemy, and building for production.

## Development Environment Setup

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/AshutoshBuilds/slide-alchemy.git
cd slide-alchemy

# Frontend dependencies
npm install

# Backend dependencies
cd backend
python3.12 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Install Rust (for Tauri)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

### 3. Running in Development

**Option A: Full Tauri stack**

```bash
npm run tauri dev
```

This starts both the Vite dev server (port 1420) and the Tauri window. However, you need to start the Python backend separately:

```bash
cd backend
source .venv/bin/activate
python -m app.main --port 8741
```

**Option B: Frontend + Backend separately**

```bash
# Terminal 1: Backend
cd backend && source .venv/bin/activate
python -m app.main --port 8741

# Terminal 2: Frontend (Vite dev server)
npm run dev

# Then open http://localhost:1420 in your browser
```

**Option C: Use the dev script**

```bash
./scripts/dev.sh
```

### 4. Verify Everything Works

1. Check backend health: `curl http://localhost:8741/health`
2. Open the frontend and verify "Backend connected" shows in green on the dashboard
3. Try uploading a text file or pasting a URL on the Resources page

## Running Tests

### Backend Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

Run a specific test file:

```bash
pytest tests/test_prompt_engine.py
pytest tests/test_resource_parser.py -v
```

Run with coverage:

```bash
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

### Existing Test Files

| Test File | Tests |
|-----------|-------|
| `test_resource_parser.py` | Raw text, markdown, and TXT file parsing |
| `test_model_router.py` | Model configuration, message formatting |
| `test_qa_engine.py` | Question flow, answer recording, context building |
| `test_prompt_engine.py` | Prompt assembly, theme selection, variant generation |
| `test_feedback_service.py` | Feedback storage, preference updates, pattern storage |

### Frontend Tests

The project does not yet include a frontend test framework. To add one:

```bash
npm install -D vitest @testing-library/svelte
```

## Adding New Model Providers

The model router at `backend/app/services/model_router.py` dispatches LLM calls based on the `provider` field. To add a new provider:

### 1. Add the Provider Enum

In `backend/app/models/settings.py`:

```python
class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    OPENAI = "openai"
    GEMINI = "gemini"
    MY_PROVIDER = "my_provider"   # Add here
```

### 2. Implement Chat Methods

In `backend/app/services/model_router.py`, add two methods:

```python
async def _chat_my_provider(self, messages: list[dict]) -> str:
    # Import the provider's SDK
    # Create a client with self.config.api_key and self.config.base_url
    # Send messages and return the response text
    pass

async def _stream_my_provider(self, messages: list[dict]) -> AsyncIterator[str]:
    # Same setup, but yield chunks as they arrive
    pass
```

### 3. Update the Router Dispatch

In the `chat()` and `chat_stream()` methods, add your provider to the dispatch logic:

```python
async def chat(self, system: str, history: list[dict], user_message: str) -> str:
    # ...existing code...
    elif self.config.provider == "my_provider":
        return await self._chat_my_provider(messages)
```

If your provider uses the OpenAI-compatible API format, you can skip implementing custom methods entirely. Just add its base URL to the `base_urls` dict in `_chat_openai_compatible()`:

```python
base_urls = {
    "openrouter": "https://openrouter.ai/api/v1",
    "groq": "https://api.groq.com/openai/v1",
    "openai": "https://api.openai.com/v1",
    "my_provider": "https://api.myprovider.com/v1",  # Add here
}
```

### 4. Add the Dependency

Add the provider's Python SDK to `backend/requirements.txt`.

### 5. Test

Add tests in `backend/tests/test_model_router.py` for the new provider's message formatting and error handling.

## Adding New Resource Parsers

The resource parser at `backend/app/services/resource_parser.py` handles document ingestion. To add a new resource type:

### 1. Add the Resource Type

In `backend/app/models/resource.py`:

```python
class ResourceType(str, Enum):
    # ...existing types...
    CSV = "csv"   # Add here
```

### 2. Implement the Parser Method

In `backend/app/services/resource_parser.py`:

```python
async def parse_csv(self, file_path: str) -> ParsedContent:
    import csv
    rows = []
    with open(file_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Convert to text representation
    full_text = "\n".join(str(row) for row in rows)

    return ParsedContent(
        text=full_text,
        sections=[{"title": f"Row {i+1}", "content": str(row)} for i, row in enumerate(rows[:50])],
        metadata={"type": "csv", "row_count": len(rows), "columns": list(rows[0].keys()) if rows else []},
    )
```

### 3. Register the Parser

Add it to the dispatch dict in the `parse()` method:

```python
async_parsers = {
    # ...existing parsers...
    ResourceType.CSV: self.parse_csv,
}
```

### 4. Update the Upload Router

In `backend/app/routers/resources.py`, add the file extension mapping:

```python
type_map = {
    # ...existing mappings...
    ".csv": ResourceType.CSV,
}
```

### 5. Test

Add a test in `backend/tests/test_resource_parser.py`:

```python
def test_parse_csv():
    parser = ResourceParser()
    # Create a temp CSV file and test parsing
```

## Adding New Research Sources

The research engine at `backend/app/services/research_engine.py` searches multiple sources. To add a new one:

### 1. Implement the Search Method

```python
async def search_my_source(self, query: str) -> list[ResearchResult]:
    # Call the API
    # Return ResearchResult objects with source, title, snippet, url, source_type
    pass
```

### 2. Add to `search_all()`

```python
async def search_all(self, query: str) -> list[ResearchResult]:
    tasks = [
        self.search_web(query),
        self.search_academic(query),
        self.search_youtube(query),
        self.search_reddit(query),
        self.search_my_source(query),   # Add here
    ]
    # ...rest of the method
```

### 3. Add a Dedicated Endpoint (Optional)

In `backend/app/routers/research.py`:

```python
@router.post("/my-source", response_model=list[ResearchResult])
async def search_my_source(req: ResearchRequest):
    engine = ResearchEngine(...)
    return await engine.search_my_source(req.query)
```

### 4. Add API Key Configuration (If Needed)

In `backend/app/models/settings.py`, add the key field to `AppSettings`:

```python
class AppSettings(BaseModel):
    # ...existing fields...
    my_source_api_key: Optional[str] = None
```

## PyInstaller Build Process

The backend is packaged into a standalone binary using PyInstaller so that end users do not need Python installed.

### How It Works

`backend/build.py` runs PyInstaller with these key options:

- `--onefile`: Produces a single executable binary
- `--hidden-import`: Explicitly includes modules that PyInstaller cannot detect through static analysis (uvicorn internals, router modules)
- `--collect-all notebooklm`: Bundles all files from the notebooklm package

### Building

```bash
cd backend
source .venv/bin/activate
pip install pyinstaller
python build.py
```

Output: `backend/dist/slide-alchemy-backend` (or `.exe` on Windows)

### Troubleshooting Build Issues

**Missing module errors at runtime**: Add `--hidden-import module.name` to the PyInstaller command in `build.py`.

**Large binary size**: The binary includes the entire Python runtime and all dependencies. Typical size is 80-150 MB. To reduce:
- Remove unused dependencies from `requirements.txt`
- Use `--exclude-module` for packages not needed at runtime

**Sidecar naming**: Tauri requires platform-specific binary names. After building, rename the binary:

| Platform | Binary Name |
|----------|-------------|
| macOS (ARM) | `slide-alchemy-backend-aarch64-apple-darwin` |
| macOS (Intel) | `slide-alchemy-backend-x86_64-apple-darwin` |
| Linux (x64) | `slide-alchemy-backend-x86_64-unknown-linux-gnu` |
| Windows (x64) | `slide-alchemy-backend-x86_64-pc-windows-msvc.exe` |

Place the renamed binary in `src-tauri/binaries/`.

## Tauri Build Process

### Development Build

```bash
npm run tauri dev
```

This starts Vite in dev mode and opens a Tauri window pointing to `http://localhost:1420`. Hot module replacement works for the frontend.

### Production Build

```bash
npm run tauri build
```

This:
1. Runs `npm run build` to compile the Svelte frontend into static files in `build/`
2. Compiles the Rust Tauri shell
3. Bundles the frontend, the Rust binary, and the Python sidecar into a platform installer

### Build Configuration

`src-tauri/tauri.conf.json` controls the build:

- `build.frontendDist`: `"../build"` -- location of compiled frontend
- `build.beforeBuildCommand`: `"npm run build"` -- runs before Tauri build
- `bundle.externalBin`: `["binaries/slide-alchemy-backend"]` -- the Python sidecar binary
- `bundle.targets`: `"all"` -- builds DMG, NSIS installer, AppImage, and DEB

### Full Production Build Script

```bash
# 1. Build Python backend binary
cd backend
source .venv/bin/activate
pip install pyinstaller
python build.py

# 2. Copy to Tauri binaries (adjust for your platform)
cp dist/slide-alchemy-backend ../src-tauri/binaries/slide-alchemy-backend-aarch64-apple-darwin

# 3. Build Tauri app
cd ..
npm run tauri build
```

Or use:

```bash
./scripts/build-all.sh
```

## Code Style Guidelines

### Python (Backend)

- **Models**: Use Pydantic `BaseModel` for all data structures. Use `Field` for defaults and validation.
- **Services**: Business logic lives in service classes (`backend/app/services/`). Each service is a class with methods, not standalone functions.
- **Routers**: HTTP endpoint handlers in `backend/app/routers/`. Keep them thin -- validate input, call service, return result.
- **Type hints**: Use type hints everywhere. Use `Optional[T]` for nullable fields, `list[T]` and `dict[K, V]` for collections (Python 3.12+ syntax).
- **Async**: All router handlers and service methods that perform I/O should be `async`.
- **Naming**: snake_case for functions and variables, PascalCase for classes, UPPER_CASE for module-level constants.

### TypeScript (Frontend)

- **Svelte 5 runes**: Use `$state`, `$derived`, `$effect`, and `$props` instead of Svelte 4 stores and reactive declarations.
- **Types**: Define all interfaces in `src/lib/api/types.ts`. Use them in the API client and component props.
- **API client**: All backend calls go through `src/lib/api/client.ts`. Never call `fetch()` directly from components.
- **Components**: Keep components focused. One file, one concern. Put reusable UI in `src/lib/components/`.
- **Stores**: Use `src/lib/stores/` for shared state that spans multiple routes.
- **CSS**: Use TailwindCSS utility classes. The custom `alchemy` color is defined in `tailwind.config.js`.

### Rust (Tauri Shell)

- The Tauri layer should remain minimal. Its only job is spawning the sidecar and providing the port to the frontend.
- Use `tauri::State` for shared state between commands.
- Keep the Cargo dependency list small.
