from typing import Optional
from pathlib import Path
from ..utils.config import DATA_DIR


class NotebookLMBridge:
    def __init__(self, cookie: Optional[str] = None):
        self.cookie = cookie
        self.client = None

    async def initialize(self):
        if not self.cookie:
            raise ValueError("NotebookLM cookie not configured. Set it in Settings.")

        from notebooklm import NotebookLM
        self.client = NotebookLM(cookie=self.cookie)

    async def create_notebook(self, title: str) -> str:
        if not self.client:
            await self.initialize()

        notebook = self.client.create_notebook(title=title)
        return notebook.id

    async def add_sources(self, notebook_id: str, sources: list[dict]) -> list[str]:
        if not self.client:
            await self.initialize()

        notebook = self.client.get_notebook(notebook_id)
        source_ids = []

        for source in sources:
            source_type = source.get("type", "text")
            content = source.get("content", "")

            if source_type == "url":
                result = notebook.add_source(url=content)
            elif source_type == "youtube":
                result = notebook.add_source(youtube_url=content)
            elif source_type == "text":
                result = notebook.add_source(text=content)
            else:
                result = notebook.add_source(text=content)

            source_ids.append(str(result.id) if hasattr(result, 'id') else "added")

        return source_ids

    async def generate_slides(self, notebook_id: str, prompt: str) -> dict:
        if not self.client:
            await self.initialize()

        notebook = self.client.get_notebook(notebook_id)

        # Use the chat to send our ultra-detailed prompt
        response = notebook.chat(prompt)

        # Generate slide deck
        deck = notebook.generate_slide_deck()

        return {
            "notebook_id": notebook_id,
            "chat_response": str(response),
            "deck_id": str(deck.id) if hasattr(deck, 'id') else "generated",
        }

    async def download_pptx(self, notebook_id: str, output_dir: Optional[str] = None) -> str:
        if not self.client:
            await self.initialize()

        download_dir = Path(output_dir) if output_dir else DATA_DIR / "downloads"
        download_dir.mkdir(parents=True, exist_ok=True)

        notebook = self.client.get_notebook(notebook_id)
        deck = notebook.get_slide_deck()

        output_path = download_dir / f"{notebook_id}_slides.pptx"
        deck.download(str(output_path))

        return str(output_path)

    async def generate_variant(self, title: str, sources: list[dict], prompt: str, variant_num: int) -> dict:
        """Full pipeline: create notebook, add sources, generate slides, download."""
        notebook_id = await self.create_notebook(f"{title} - Variant {variant_num}")
        await self.add_sources(notebook_id, sources)
        result = await self.generate_slides(notebook_id, prompt)

        output_path = await self.download_pptx(notebook_id)
        result["pptx_path"] = output_path
        result["variant_number"] = variant_num
        return result
