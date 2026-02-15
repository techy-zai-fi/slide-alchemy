import asyncio
from typing import Optional
from pydantic import BaseModel

from ..models.resource import ParsedContent


class ResearchResult(BaseModel):
    source: str
    title: str
    snippet: str
    url: str
    source_type: str


class ResearchEngine:
    def __init__(self, serper_api_key: Optional[str] = None, reddit_client_id: Optional[str] = None, reddit_secret: Optional[str] = None):
        self.serper_api_key = serper_api_key
        self.reddit_client_id = reddit_client_id
        self.reddit_secret = reddit_secret

    async def analyze_gaps(self, resources: list[ParsedContent], qa_context: dict) -> list[str]:
        all_text = " ".join(r.text[:500] for r in resources)
        topic_keywords = set()
        sections = qa_context.get("sections", "").split(",")
        for section in sections:
            topic_keywords.update(section.strip().lower().split())
        key_message = qa_context.get("key_message", "")
        topic_keywords.update(key_message.lower().split())
        gap_queries = []
        for keyword_group in self._cluster_keywords(list(topic_keywords)):
            if keyword_group.lower() not in all_text.lower():
                gap_queries.append(keyword_group)
        return gap_queries[:5]

    async def search_web(self, query: str) -> list[ResearchResult]:
        if not self.serper_api_key:
            return []
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post("https://google.serper.dev/search",
                headers={"X-API-KEY": self.serper_api_key, "Content-Type": "application/json"},
                json={"q": query, "num": 5})
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [ResearchResult(source="google", title=item.get("title", ""), snippet=item.get("snippet", ""),
                url=item.get("link", ""), source_type="web") for item in data.get("organic", [])[:5]]

    async def search_academic(self, query: str) -> list[ResearchResult]:
        try:
            import arxiv
            client = arxiv.Client()
            search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
            return [ResearchResult(source="arxiv", title=paper.title, snippet=paper.summary[:300],
                url=paper.entry_id, source_type="academic") for paper in client.results(search)]
        except Exception:
            return []

    async def search_youtube(self, query: str) -> list[ResearchResult]:
        if not self.serper_api_key:
            return []
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post("https://google.serper.dev/videos",
                headers={"X-API-KEY": self.serper_api_key, "Content-Type": "application/json"},
                json={"q": query, "num": 3})
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [ResearchResult(source="youtube", title=item.get("title", ""), snippet=item.get("snippet", ""),
                url=item.get("link", ""), source_type="youtube") for item in data.get("videos", [])[:3]]

    async def search_reddit(self, query: str) -> list[ResearchResult]:
        if not self.reddit_client_id:
            return []
        try:
            import praw
            reddit = praw.Reddit(client_id=self.reddit_client_id, client_secret=self.reddit_secret, user_agent="SlideAlchemy/0.1")
            return [ResearchResult(source="reddit", title=sub.title, snippet=(sub.selftext or "")[:300],
                url=f"https://reddit.com{sub.permalink}", source_type="reddit")
                for sub in reddit.subreddit("all").search(query, limit=3)]
        except Exception:
            return []

    async def search_all(self, query: str) -> list[ResearchResult]:
        tasks = [self.search_web(query), self.search_academic(query), self.search_youtube(query), self.search_reddit(query)]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        all_results = []
        for result in results_lists:
            if isinstance(result, list):
                all_results.extend(result)
        return all_results

    def _cluster_keywords(self, keywords: list[str]) -> list[str]:
        filtered = [k for k in keywords if len(k) > 3]
        if not filtered:
            return keywords
        clusters = []
        for i in range(0, len(filtered), 2):
            chunk = filtered[i:i+2]
            clusters.append(" ".join(chunk))
        return clusters
