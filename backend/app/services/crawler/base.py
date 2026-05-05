from abc import ABC, abstractmethod

import httpx


class Crawler(ABC):
    """Base class for platform-specific content crawlers."""

    @abstractmethod
    async def extract(self, url: str, client: httpx.AsyncClient) -> dict:
        """Extract title and content from the given URL.

        Returns:
            dict with keys: title, content (cleaned text), raw_content (optional)
            If extraction fails, content should be None.
        """
        ...


def detect_source(url: str) -> str:
    url = url.lower()
    if "bilibili.com" in url:
        return "bilibili"
    if "zhihu.com" in url or "zhuanlan.zhihu.com" in url:
        return "zhihu"
    if "douyin.com" in url:
        return "douyin"
    return "web"
