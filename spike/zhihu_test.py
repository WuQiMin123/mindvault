"""
可行性验证: 知乎文章提取
测试 httpx + BeautifulSoup 能否稳定获取知乎文章内容
"""

import httpx
import json
import asyncio
from bs4 import BeautifulSoup


async def extract_zhihu(url: str) -> dict:
    """提取知乎文章内容"""
    print(f"  URL: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)

        if resp.status_code != 200:
            return {
                "status": "error",
                "step": "http_get",
                "detail": f"HTTP {resp.status_code}",
            }

        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # 方法1: meta 标签取标题
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]

        # 方法2: h1 取标题
        if not title:
            h1 = soup.find("h1", class_="Post-Title")
            if h1:
                title = h1.get_text(strip=True)

        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)

        # 提取正文
        # 方法1: article 标签
        content = ""
        article = soup.find("article")
        if article:
            content = article.get_text(strip=True)

        # 方法2: .Post-RichText
        if not content or len(content) < 50:
            richtext = soup.find("div", class_="Post-RichText")
            if richtext:
                content = richtext.get_text(strip=True)

        # 方法3: .ContentItem
        if not content or len(content) < 50:
            content_item = soup.find("div", class_="ContentItem")
            if content_item:
                content = content_item.get_text(strip=True)

        # 方法4: 所有 p 标签
        if not content or len(content) < 50:
            paragraphs = soup.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        # 检查反爬
        if "验证中心" in html or "zhuanlan.zhihu.com/p/anon" in url:
            return {
                "status": "blocked",
                "title": title or "未知",
                "detail": "触发了知乎验证/反爬",
            }

        return {
            "status": "success" if len(content) > 100 else "empty",
            "title": title or "未知标题",
            "content_length": len(content),
            "method_found": "article" if article else "richtext" if content else "paragraphs",
            "preview": content[:300] if content else "无内容",
        }


async def main():
    test_urls = [
        ("技术文章", "https://zhuanlan.zhihu.com/p/2016598051163218226"),
        ("另一个试试", "https://zhuanlan.zhihu.com/p/68019738215"),
    ]

    for name, url in test_urls:
        print(f"\n{'='*60}")
        print(f"测试: {name}")
        print(f"{'='*60}")
        result = await extract_zhihu(url)
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
