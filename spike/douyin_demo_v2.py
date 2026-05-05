"""
抖音内容提取 Demo v2 — Playwright 方式

管线: Playwright 打开抖音页面 → 提取视频信息(标题+简介) + 触发下载
"""
import asyncio, sys, os, re, json
from playwright.async_api import async_playwright

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "douyin_videos")


async def main():
    if len(sys.argv) < 2:
        url = input("粘贴抖音链接: ").strip()
    else:
        url = sys.argv[1]

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  抖音内容提取 Demo (Playwright)")
    print(f"  链接: {url[:60]}")
    print(f"  保存目录: {DOWNLOAD_DIR}")
    print(f"{'='*60}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=False,  # 有界面模式，看反爬验证
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/125.0.0.0 Safari/537.36"),
            viewport={"width": 1280, "height": 720},
            locale="zh-CN",
        )
        page = await context.new_page()
        await page.add_init_script(
            'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'
        )

        print(f"\n==> 正在打开抖音页面...")
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(5000)

        print(f"  当前URL: {page.url}")
        title = await page.title()
        print(f"  页面标题: {title}")

        # 尝试从页面提取视频信息（内嵌 JSON）
        info = await page.evaluate("""
            () => {
                // 找 #RENDER_DATA 或 __INITIAL_STATE__
                for (const id of ['RENDER_DATA', '__INITIAL_STATE__']) {
                    const el = document.getElementById(id);
                    if (el) return { source: id, data: el.textContent.slice(0, 50000) };
                }
                // 找 script 中的 window.__INITIAL_STATE__
                const scripts = document.querySelectorAll('script');
                for (const s of scripts) {
                    const m = s.textContent.match(/window\\.__INITIAL_STATE__\\s*=\\s*(\\{[\\s\\S]*?\\});/);
                    if (m) return { source: 'script', data: m[1].slice(0, 50000) };
                }
                return { source: 'none', data: '' };
            }
        """)

        if info and info["data"]:
            print(f"\n  找到内嵌数据: {info['source']}")
            try:
                raw = json.loads(info["data"])
                # 尝试多种路径找到视频描述
                desc = ""
                if info["source"] == "RENDER_DATA":
                    raw = json.loads(raw) if isinstance(raw, str) else raw
                    desc = (raw.get("aweme", {}) or raw.get("video", {}) or {}).get("desc", "")
                else:
                    desc = (raw.get("aweme", {}) or raw.get("videoInfo", {}) or {}).get("desc", "")
                print(f"  简介: {desc[:300] if desc else '(空)'}")
            except json.JSONDecodeError as e:
                print(f"  JSON 解析失败: {e}")
                # 直接输出原始数据前 500 字符看看结构
                print(f"  原始数据前500字: {info['data'][:500]}")
        else:
            print(f"\n  页面内无内嵌数据，提取页面文本")
            body = await page.evaluate("document.body.innerText")
            print(f"  页面文本: {body[:500]}")

        # 截图查看
        screenshot_path = os.path.join(DOWNLOAD_DIR, "douyin_page.png")
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"\n  截图保存: {screenshot_path}")

        input("\n按回车键关闭浏览器...")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
