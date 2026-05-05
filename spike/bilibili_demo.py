"""
B站内容提取 Demo — AI字幕 + 简介回退
用法: python bilibili_demo.py "https://www.bilibili.com/video/BVxxxxxx"
"""
import httpx, asyncio, sys, re, os

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/125.0.0.0 Safari/537.36")

def extract_bvid(text: str) -> str:
    m = re.search(r"BV\w+", text)
    if not m: raise ValueError(f"找不到BV号: {text}")
    return m.group(0)

def clean(s: str) -> str:
    return s.strip().replace(" ", "").replace("\n", "").replace("\r", "")

async def main():
    if len(sys.argv) < 2:
        url = input("粘贴B站视频链接或BV号: ").strip()
    else:
        url = sys.argv[1]
    bvid = extract_bvid(url)

    sessdata = clean(os.environ.get("BILI_SESSDATA", ""))
    if not sessdata:
        sessdata = clean(input("请输入 SESSDATA (留空则无登录态): "))

    print(f"\n{'='*60}")
    print(f"  B站内容提取 Demo")
    print(f"  BV号: {bvid}")
    print(f"  登录态: {'有' if sessdata else '无'}")
    print(f"{'='*60}")

    cookie_val = f"SESSDATA={sessdata}" if sessdata else ""

    async with httpx.AsyncClient(timeout=30.0) as c:
        headers = {"User-Agent": UA, "Referer": "https://www.bilibili.com/"}
        if cookie_val: headers["Cookie"] = cookie_val

        # 1. 视频信息
        r = await c.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=headers)
        if r.status_code != 200: return print(f"  ❌ HTTP {r.status_code}")
        info = r.json()
        if info["code"] != 0: return print(f"  ❌ API错误: {info}")
        data = info["data"]
        aid, cid, title, desc = data["aid"], data["cid"], data["title"], data.get("desc", "")
        print(f"\n▶ 视频信息")
        print(f"  标题: {title}")
        print(f"  简介: {desc[:100] if desc else '(空)'}")

        # 2. 字幕
        sr = await c.get(f"https://api.bilibili.com/x/player/v2?aid={aid}&cid={cid}", headers=headers)
        sd = sr.json()
        subs = sd.get("data", {}).get("subtitle", {}).get("subtitles", [])

        full_text = ""
        if subs:
            target = subs[0]
            sub_url = target.get("subtitle_url", "")
            if len(sub_url) > 5:
                if sub_url.startswith("//"): sub_url = "https:" + sub_url
                tr = await c.get(sub_url)
                if tr.status_code == 200:
                    body = tr.json().get("body", [])
                    if body:
                        print(f"\n▶ 字幕: {len(body)} 条")
                        for item in body[:12]:
                            t = int(item.get("from", 0))
                            m, s = divmod(t, 60)
                            print(f"  [{m:02d}:{s:02d}] {item['content']}")
                        if len(body) > 12: print(f"  ... 还有 {len(body)-12} 条")
                        full_text = " ".join(item["content"] for item in body)

        if not full_text:
            full_text = desc
            print(f"\n▶ 无字幕，使用简介 ({len(desc)} 字)")

        # 3. 汇总
        print(f"\n{'='*60}")
        print(f"  结果: {title}")
        print(f"  内容长度: {len(full_text)} 字")
        if len(full_text) >= 2000:   print(f"  质量: ★★★★★ (字幕完整)")
        elif len(full_text) >= 200:  print(f"  质量: ★★★☆☆ (内容简要)")
        else:                        print(f"  质量: ★☆☆☆☆ (仅标题)")
        print(f"{'='*60}")
        if full_text:
            print(f"\n{full_text}")

if __name__ == "__main__":
    asyncio.run(main())
