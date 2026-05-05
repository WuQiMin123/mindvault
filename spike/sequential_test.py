"""全平台串行测试"""
import httpx, json, asyncio
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


async def test_bilibili():
    print("=== B站 ===")
    h = {**{"User-Agent": UA}, "Referer": "https://www.bilibili.com/"}
    async with httpx.AsyncClient(timeout=30.0) as c:
        # 热门API取有效视频
        r = await c.get("https://api.bilibili.com/x/web-interface/popular", headers=h)
        d = r.json()
        if d["code"] != 0:
            return print(f"  API error: {d}")
        for v in d["data"]["list"][:3]:
            bvid = v["bvid"]
            vr = await c.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=h)
            vd = vr.json()["data"]
            desc = vd.get("desc", "")
            print(f"  {bvid}")
            print(f"    标题: {vd['title'][:50]}")
            print(f"    简介长度: {len(desc)}")
            print(f"    简介: {desc[:150]}")
            print(f"    时长: {vd['duration']}s")
        print(f"  字幕结论: AI字幕API不提供, 标题+简介作为内容")


async def test_zhihu():
    print("\n=== 知乎 ===")
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as c:
        r = await c.get("https://zhuanlan.zhihu.com/p/2016598051163218226",
                        headers={"User-Agent": UA})
        print(f"  HTTP: {r.status_code}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            t = soup.find("title")
            print(f"  标题: {t.get_text()[:80] if t else 'N/A'}")
            body = soup.find("body")
            text = body.get_text(strip=True) if body else ""
            print(f"  正文长度: {len(text)}")
            print(f"  正文: {text[:200]}")
        else:
            print(f"  响应: {r.text[:200]}")
        print(f"  结论: 知乎有反爬, 需要验证方案")


async def test_general():
    print("\n=== 通用网页 ===")
    async with httpx.AsyncClient(timeout=15.0) as c:
        for name, url in [("百度", "https://www.baidu.com"), ("B站", "https://www.bilibili.com")]:
            r = await c.get(url, headers={"User-Agent": UA})
            soup = BeautifulSoup(r.text, "html.parser")
            t = soup.find("title")
            ps = soup.find_all("p")
            text = " ".join(p.get_text(strip=True) for p in ps if p.get_text(strip=True))
            print(f"  {name}: {r.status_code} | 标题: {t.get_text()[:40] if t else 'N/A'} | 段落: {len(text)}字")
        print(f"  结论: 通用网页抓取可行")

asyncio.run(test_bilibili())
asyncio.run(test_zhihu())
asyncio.run(test_general())
