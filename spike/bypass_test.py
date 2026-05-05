"""
尝试绕过知乎403 + 验证B站其他方案
"""
import httpx, asyncio, json
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/125.0.0.0 Safari/537.36")


async def zhihu_bypass():
    print("=== 知乎绕过方案测试 ===")
    url = "https://zhuanlan.zhihu.com/p/2016598051163218226"
    async with httpx.AsyncClient(timeout=30.0) as c:

        # 方案1: 不同User-Agent + 额外头
        print("\n方案1: 浏览器全套头部")
        r1 = await c.get(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        })
        print(f"  HTTP {r1.status_code} | len={len(r1.text)}")

        # 方案2: 先访问首页拿cookie, 再用cookie访问文章
        print("\n方案2: Cookie预热")
        await c.get("https://www.zhihu.com", headers={"User-Agent": UA})
        cookies = dict(c.cookies)
        r2 = await c.get(url, headers={"User-Agent": UA, "Cookie": "; ".join(f"{k}={v}" for k,v in cookies.items())})
        print(f"  HTTP {r2.status_code} | len={len(r2.text)} | cookies: {len(cookies)}")

        # 方案3: 尝试textise.iitty (第三方)
        print("\n方案3: 第三方代理 textise.iitty")
        try:
            r3 = await c.get(f"https://r.jina.ai/http://zhuanlan.zhihu.com/p/2016598051163218226", timeout=10)
            print(f"  HTTP {r3.status_code} | len={len(r3.text)}")
            if r3.status_code == 200:
                print(f"  内容预览: {r3.text[:300]}")
        except Exception as e:
            print(f"  失败: {e}")

        # 方案4: 尝试textise (textise dot iitty)
        print("\n方案4: Mozilla readability 方案说明")
        print("  Playwright + Readability 可绕过反爬, 但需要安装浏览器")
        print("  这是推荐的知乎方案")


async def bilibili_alternatives():
    print("\n=== B站替代方案 ===")
    bh = {**{"User-Agent": UA}, "Referer": "https://www.bilibili.com/"}

    async with httpx.AsyncClient(timeout=30.0) as c:
        # 获取有效视频
        r = await c.get("https://api.bilibili.com/x/web-interface/popular", headers=bh)
        v = r.json()["data"]["list"][0]
        bvid = v["bvid"]
        print(f"视频: {bvid} {v['title']}")

        # 方案1: 取视频的description - 已验证可行
        vr = await c.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=bh)
        d = vr.json()["data"]
        print(f"方案1 标题+简介: 标题({len(d['title'])}字) + 简介({len(d.get('desc',''))}字)")

        # 方案2: 尝试取AI字幕 (可能需sessdata)
        # 实际上B站AI字幕生成需要登录态 + 前端触发
        # 这里只做文档记录
        print(f"方案2 AI字幕: 需要登录态 + 前端POST触发, 不可行")

        # 方案3: 取视频标签作为内容补充
        print(f"方案3 标签补充: B站视频无公开标签API, 只能从description提取")


async def main():
    await zhihu_bypass()
    await bilibili_alternatives()

    print(f"\n\n{'='*50}")
    print("最终结论")
    print(f"{'='*50}")
    print(json.dumps({
        "bilibili": {
            "status": "partial",
            "available": ["title", "description"],
            "unavailable": ["subtitle", "transcript", "AI_subtitle"],
            "recommendation": "使用标题+简介作为内容, 坦白告知用户无法获取字幕",
        },
        "zhihu": {
            "status": "blocked",
            "available": [],
            "recommendation": "使用Playwright浏览器自动化进行抓取, 或使用第三方代理服务",
        },
        "general_fallback": {
            "status": "partial",
            "available": ["static HTML pages"],
            "unavailable": ["JS-rendered pages"],
            "recommendation": "用BeautifulSoup + readability-lite提取, JS渲染用Playwright兜底",
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
