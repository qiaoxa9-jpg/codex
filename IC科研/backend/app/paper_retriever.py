import asyncio
from urllib.parse import quote

import httpx

from .config import Settings
from .schemas import PaperResult


class PaperRetriever:
    FIELDS = "title,abstract,authors,year,venue,url,externalIds,citationCount,openAccessPdf"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(self, query: str, limit: int = 8) -> tuple[list[PaperResult], dict[str, str]]:
        semantic_task = self._semantic_scholar(query, limit)
        crossref_task = self._crossref(query, limit)
        semantic, crossref = await asyncio.gather(semantic_task, crossref_task)
        provider_status = {
            "semantic_scholar": semantic[1],
            "crossref": crossref[1],
        }
        merged: list[PaperResult] = []
        seen: set[str] = set()
        for paper in [*semantic[0], *crossref[0]]:
            key = (paper.doi or paper.title).lower().strip()
            if key not in seen:
                seen.add(key)
                merged.append(paper)
        return merged[:limit], provider_status

    async def _semantic_scholar(
        self, query: str, limit: int
    ) -> tuple[list[PaperResult], str]:
        headers = {"User-Agent": "ICResearchCopilot/0.1"}
        if self.settings.semantic_scholar_api_key:
            headers["x-api-key"] = self.settings.semantic_scholar_api_key
        params = {"query": query, "limit": min(limit, 100), "fields": self.FIELDS}
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
            results = []
            for item in response.json().get("data", []):
                external_ids = item.get("externalIds") or {}
                open_pdf = item.get("openAccessPdf") or {}
                url = item.get("url") or open_pdf.get("url")
                if not url:
                    continue
                results.append(
                    PaperResult(
                        paper_id=item["paperId"],
                        title=item.get("title") or "Untitled",
                        abstract=item.get("abstract"),
                        authors=[author.get("name", "") for author in item.get("authors", [])],
                        year=item.get("year"),
                        venue=item.get("venue") or None,
                        doi=external_ids.get("DOI"),
                        citation_count=item.get("citationCount") or 0,
                        url=url,
                        source="Semantic Scholar",
                        open_access=bool(open_pdf.get("url")),
                    )
                )
            return results, "ok"
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            return [], f"unavailable: {type(exc).__name__}"

    async def _crossref(self, query: str, limit: int) -> tuple[list[PaperResult], str]:
        params: dict[str, str | int] = {
            "query": query,
            "rows": min(limit, 100),
            "select": "DOI,title,abstract,author,published,container-title,is-referenced-by-count,URL,link",
        }
        if self.settings.crossref_mailto:
            params["mailto"] = self.settings.crossref_mailto
        headers = {"User-Agent": "ICResearchCopilot/0.1 (mailto:unset)"}
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.get(
                    "https://api.crossref.org/v1/works", params=params, headers=headers
                )
                response.raise_for_status()
            results = []
            for item in response.json().get("message", {}).get("items", []):
                title = (item.get("title") or ["Untitled"])[0]
                doi = item.get("DOI")
                url = item.get("URL") or (f"https://doi.org/{quote(doi)}" if doi else None)
                if not url:
                    continue
                date_parts = (item.get("published") or {}).get("date-parts") or [[]]
                year = date_parts[0][0] if date_parts and date_parts[0] else None
                authors = [
                    " ".join(filter(None, [author.get("given"), author.get("family")]))
                    for author in item.get("author", [])
                ]
                links = item.get("link") or []
                results.append(
                    PaperResult(
                        paper_id=doi or title,
                        title=title,
                        abstract=item.get("abstract"),
                        authors=authors,
                        year=year,
                        venue=(item.get("container-title") or [None])[0],
                        doi=doi,
                        citation_count=item.get("is-referenced-by-count") or 0,
                        url=url,
                        source="Crossref",
                        open_access=any(link.get("content-version") == "vor" for link in links),
                    )
                )
            return results, "ok"
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            return [], f"unavailable: {type(exc).__name__}"

    async def detail(self, source: str, paper_id: str) -> PaperResult | None:
        if source == "Semantic Scholar":
            headers = {"User-Agent": "ICResearchCopilot/0.1"}
            if self.settings.semantic_scholar_api_key:
                headers["x-api-key"] = self.settings.semantic_scholar_api_key
            try:
                async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                    response = await client.get(
                        f"https://api.semanticscholar.org/graph/v1/paper/{quote(paper_id, safe='')}",
                        params={"fields": self.FIELDS},
                        headers=headers,
                    )
                    response.raise_for_status()
                item = response.json()
                external_ids = item.get("externalIds") or {}
                open_pdf = item.get("openAccessPdf") or {}
                return PaperResult(
                    paper_id=item["paperId"],
                    title=item.get("title") or "Untitled",
                    abstract=item.get("abstract"),
                    authors=[author.get("name", "") for author in item.get("authors", [])],
                    year=item.get("year"),
                    venue=item.get("venue") or None,
                    doi=external_ids.get("DOI"),
                    citation_count=item.get("citationCount") or 0,
                    url=item.get("url") or open_pdf.get("url"),
                    source=source,
                    open_access=bool(open_pdf.get("url")),
                )
            except (httpx.HTTPError, ValueError, KeyError):
                return None
        if source == "Crossref":
            try:
                async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                    response = await client.get(
                        f"https://api.crossref.org/v1/works/{quote(paper_id, safe='')}",
                        headers={"User-Agent": "ICResearchCopilot/0.1"},
                    )
                    response.raise_for_status()
                item = response.json().get("message", {})
                date_parts = (item.get("published") or {}).get("date-parts") or [[]]
                return PaperResult(
                    paper_id=item.get("DOI") or paper_id,
                    title=(item.get("title") or ["Untitled"])[0],
                    abstract=item.get("abstract"),
                    authors=[
                        " ".join(filter(None, [author.get("given"), author.get("family")]))
                        for author in item.get("author", [])
                    ],
                    year=date_parts[0][0] if date_parts and date_parts[0] else None,
                    venue=(item.get("container-title") or [None])[0],
                    doi=item.get("DOI"),
                    citation_count=item.get("is-referenced-by-count") or 0,
                    url=item.get("URL") or f"https://doi.org/{quote(paper_id)}",
                    source=source,
                    open_access=False,
                )
            except (httpx.HTTPError, ValueError, KeyError):
                return None
        return None

