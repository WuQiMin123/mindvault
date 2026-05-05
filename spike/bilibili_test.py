"""
可行性验证: B站字幕提取 v2
"""

import httpx
import json
import sys
import re
import asyncio

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Origin": "https://www.bilibili.com",
}


def extract_bvid(url: str) -> str:
    patterns = [r"BV\w+"]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(0)
    raise ValueError(f"无法提取 BV 号: {url}")


async def get_subtitle(url: str) -> dict:
    bvid = extract_bvid(url)
    print(f"  BV号: {bvid}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: 取视频信息
        info_resp = await client.get(
            f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",
            headers=BROWSER_HEADERS,
        )
        if info_resp.status_code != 200:
            return {"status": "error", "step": "view_api", "http": info_resp.status_code}
        info = info_resp.json()
        if info["code"] != 0:
            return {"status": "error", "step": "view_api", "biz_code": info["code"], "msg": info.get("message", "")}

        cid = info["data"]["cid"]
        title = info["data"]["title"]
        print(f"  标题: {title}")
        print(f"  CID: {cid}")

        # Step 2: 取字幕
        sub_resp = await client.get(
            f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}",
            headers=BROWSER_HEADERS,
        )
        sub_data = sub_resp.json()
        subtitles = sub_data.get("data", {}).get("subtitle", {}).get("subtitles", [])
        print(f"  字幕数量: {len(subtitles)}")

        if not subtitles:
            # Fallback: 尝试 AI 生成字幕
            ai_sub = sub_data.get("data", {}).get("subtitle", {}).get("ai_subtitle")
            if ai_sub:
                return {"status": "success_ai", "title": title, "text": ai_sub.get("text", "")[:500]}
            return {"status": "no_subtitle", "title": title}

        sub_url = subtitles[0]["subtitle_url"]
        if sub_url.startswith("//"):
            sub_url = "https:" + sub_url

        text_resp = await client.get(sub_url, headers=BROWSER_HEADERS)
        text_data = text_resp.json()
        body = text_data.get("body", [])
        full_text = " ".join(item["content"] for item in body)

        return {
            "status": "success",
            "title": title,
            "char_count": len(full_text),
            "preview": full_text[:300],
        }


async def main():
    # 从 B站热门精选找一些 BV 号
    test_urls = [
        # BV号来源: B站热门视频 (2025年热点)
        ("科技①", "BV1GJ411x7Ht"),      # 测试用热门视频
        ("科技②", "BV1zQ4y1d7dG"),
        ("硬核", "BV1uT4y1P7CX"),
        ("科普", "BV1L94y1a7pS"),
    ]

    results = {}
    for name, bvid in test_urls:
        print(f"\n{'='*50}")
        print(f"测试: {name}")
        url = f"https://www.bilibili.com/video/{bvid}"
        result = await get_subtitle(url)
        results[name] = result
        print(f"{'='*50}")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"\n\n汇总:")
    ok = sum(1 for r in results.values() if r.get("status", "").startswith("success"))
    no = sum(1 for r in results.values() if r.get("status") == "no_subtitle")
    err = sum(1 for r in results.values() if r.get("status") == "error")
    print(f" 成功: {ok}  无字幕: {no}  出错: {err}")


if __name__ == "__main__":
    asyncio.run(main())
