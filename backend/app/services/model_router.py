from typing import AsyncIterator, Optional
from pydantic import BaseModel


class ModelConfig(BaseModel):
    provider: str
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class ModelRouter:
    def __init__(self):
        self.config: Optional[ModelConfig] = None

    def set_config(self, config: ModelConfig) -> None:
        self.config = config

    def format_messages(self, system: str, history: list[dict]) -> list[dict]:
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        return messages

    async def chat(self, system: str, history: list[dict], user_message: str) -> str:
        if not self.config:
            raise ValueError("Model not configured. Call set_config first.")
        messages = self.format_messages(system, history)
        messages.append({"role": "user", "content": user_message})
        if self.config.provider == "ollama":
            return await self._chat_ollama(messages)
        elif self.config.provider == "gemini":
            return await self._chat_gemini(messages)
        else:
            return await self._chat_openai_compatible(messages)

    async def chat_stream(self, system: str, history: list[dict], user_message: str) -> AsyncIterator[str]:
        if not self.config:
            raise ValueError("Model not configured. Call set_config first.")
        messages = self.format_messages(system, history)
        messages.append({"role": "user", "content": user_message})
        if self.config.provider == "ollama":
            async for chunk in self._stream_ollama(messages):
                yield chunk
        elif self.config.provider == "gemini":
            async for chunk in self._stream_gemini(messages):
                yield chunk
        else:
            async for chunk in self._stream_openai_compatible(messages):
                yield chunk

    async def _chat_ollama(self, messages: list[dict]) -> str:
        import ollama
        client = ollama.AsyncClient()
        response = await client.chat(model=self.config.model_name, messages=messages)
        return response.message.content

    async def _stream_ollama(self, messages: list[dict]) -> AsyncIterator[str]:
        import ollama
        client = ollama.AsyncClient()
        stream = await client.chat(model=self.config.model_name, messages=messages, stream=True)
        async for chunk in stream:
            if chunk.message.content:
                yield chunk.message.content

    async def _chat_openai_compatible(self, messages: list[dict]) -> str:
        from openai import AsyncOpenAI
        base_urls = {
            "openrouter": "https://openrouter.ai/api/v1",
            "groq": "https://api.groq.com/openai/v1",
            "openai": "https://api.openai.com/v1",
        }
        base_url = self.config.base_url or base_urls.get(self.config.provider)
        client = AsyncOpenAI(api_key=self.config.api_key, base_url=base_url)
        response = await client.chat.completions.create(model=self.config.model_name, messages=messages)
        return response.choices[0].message.content or ""

    async def _stream_openai_compatible(self, messages: list[dict]) -> AsyncIterator[str]:
        from openai import AsyncOpenAI
        base_urls = {
            "openrouter": "https://openrouter.ai/api/v1",
            "groq": "https://api.groq.com/openai/v1",
            "openai": "https://api.openai.com/v1",
        }
        base_url = self.config.base_url or base_urls.get(self.config.provider)
        client = AsyncOpenAI(api_key=self.config.api_key, base_url=base_url)
        stream = await client.chat.completions.create(model=self.config.model_name, messages=messages, stream=True)
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def _chat_gemini(self, messages: list[dict]) -> str:
        from google import genai
        client = genai.Client(api_key=self.config.api_key)
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                contents.append({"role": "user", "parts": [{"text": f"[System] {msg['content']}"}]})
            elif msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            else:
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
        response = await client.aio.models.generate_content(model=self.config.model_name, contents=contents)
        return response.text or ""

    async def _stream_gemini(self, messages: list[dict]) -> AsyncIterator[str]:
        from google import genai
        client = genai.Client(api_key=self.config.api_key)
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                contents.append({"role": "user", "parts": [{"text": f"[System] {msg['content']}"}]})
            elif msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            else:
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
        async for chunk in await client.aio.models.generate_content_stream(model=self.config.model_name, contents=contents):
            if chunk.text:
                yield chunk.text
