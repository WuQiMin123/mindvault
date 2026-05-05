"""B站内容提取 — 字幕 API + 简介回退"""

import re

import httpx

from app.services.crawler.base import Crawler

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


class BilibiliCrawler(Crawler):
    async def extract(self, url: str, client: httpx.AsyncClient) -> dict:
        bvid = self._extract_bvid(url)
        if not bvid:
            return {"title": "", "content": None, "raw_content": None}

        headers = {"User-Agent": UA, "Referer": "https://www.bilibili.com/"}

        # 1. 获取视频信息
        r = await client.get(
            f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",
            headers=headers,
        )
        if r.status_code != 200:
            return {"title": "", "content": None}
        data = r.json().get("data", {})
        title = data.get("title", "")
        desc = data.get("desc", "")
        aid, cid = data.get("aid"), data.get("cid")

        if not aid or not cid:
            return {"title": title, "content": None}

        # 2. 获取字幕
        sr = await client.get(
            f"https://api.bilibili.com/x/player/v2?aid={aid}&cid={cid}",
            headers=headers,
        )
        sd = sr.json()
        subs = sd.get("data", {}).get("subtitle", {}).get("subtitles", [])

        full_text = ""
        if subs:
            for s in subs:
                if s.get("lan") in ("zh-CN", "ai-zh"):
                    sub_url = s.get("subtitle_url", "")
                    if len(sub_url) > 5:
                        if sub_url.startswith("//"):
                            sub_url = "https:" + sub_url
                        tr = await client.get(sub_url)
                        if tr.status_code == 200:
                            body = tr.json().get("body", [])
                            texts = [item["content"] for item in body]
                            full_text = " ".join(texts)
                            break

        content = full_text or desc or None
        return {"title": title, "content": content, "raw_content": content}

    def _extract_bvid(self, url: str) -> str | None:
        m = re.search(r"BV\w+", url)
        return m.group(0) if m else None
