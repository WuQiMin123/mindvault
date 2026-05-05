"""
B站内容提取 demo v2 — 修复字幕URL为空的问题
"""
import httpx, asyncio, json, sys, re, os

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/125.0.0.0 Safari/537.36")

async def main():
    bvid = sys.argv[1] if len(sys.argv) > 1 else "BV1BM9fB8Eds"
    sessdata = os.environ.get("BILI_SESSDATA", "")
    proxy = os.environ.get("https_proxy", "") or os.environ.get("http_proxy", "")

    print(f"BV号: {bvid}")
    print(f"登录态: {'有' if sessdata else '无'}")
    print(f"代理: {proxy or '无'}")

    cookie_val = f"SESSDATA={sessdata}" if sessdata else ""

    async with httpx.AsyncClient(timeout=30.0) as c:
        headers = {
            "User-Agent": UA,
            "Referer": "https://www.bilibili.com/",
        }
        if cookie_val:
            headers["Cookie"] = cookie_val

        # Step 1: 获取视频信息
        r = await c.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=headers)
        data = r.json()["data"]
        aid, cid = data["aid"], data["cid"]
        title = data["title"]
        desc = data.get("desc", "")
        print(f"标题: {title}")
        print(f"AID: {aid}, CID: {cid}")

        # Step 2: 获取字幕列表
        sr = await c.get(f"https://api.bilibili.com/x/player/v2?aid={aid}&cid={cid}", headers=headers)
        sd = sr.json()
        subs = sd.get("data", {}).get("subtitle", {}).get("subtitles", [])
        ai_sub = sd.get("data", {}).get("subtitle", {}).get("ai_subtitle")

        print(f"手动字幕: {len(subs)} 条")
        for s in subs:
            lan = s.get("lan", "?")
            url = s.get("subtitle_url", "N/A")
            print(f"  {lan}: {url[:60]}...")

        # 尝试下载字幕
        full_text = ""
        if subs:
            # 尝试 zh-CN 或 ai-zh
            for s in subs:
                if s.get("lan") in ("zh-CN", "ai-zh") and len(s.get("subtitle_url", "")) > 3:
                    target = s
                    break
            else:
                target = subs[0]

            sub_url = target.get("subtitle_url", "")
            if len(sub_url) < 5:
                print("字幕URL无效，跳过")
            else:
                if sub_url.startswith("//"):
                    sub_url = "https:" + sub_url
                print(f"下载字幕: {sub_url[:80]}...")

                # 重要: 不要传 Cookie 头，否则 httpx 的 cookie 处理会出问题
                tr = await c.get(sub_url)
                if tr.status_code == 200:
                    body = tr.json().get("body", [])
                    texts = [item["content"] for item in body]
                    full_text = " ".join(texts)
                    print(f"字幕条目: {len(body)}")
                    print(f"字幕长度: {len(full_text)} 字")
                else:
                    print(f"下载失败: HTTP {tr.status_code}")

        if not full_text and ai_sub and ai_sub.get("text"):
            full_text = ai_sub["text"]
            print(f"使用AI字幕: {len(full_text)} 字")

        if not full_text:
            full_text = desc
            print(f"使用简介回退: {len(full_text)} 字")

        print(f"\n=== 结果 ===")
        print(f"内容长度: {len(full_text)}")
        if len(full_text) > 200:
            print(f"预览: {full_text[:200]}")
        else:
            print(f"全文: {full_text}")

        quality = "良好" if len(full_text) >= 2000 else "中等" if len(full_text) >= 500 else "差"
        print(f"质量: {quality}")

if __name__ == "__main__":
    asyncio.run(main())
