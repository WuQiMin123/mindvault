"""
知乎文章提取 Demo v2 — Playwright 隐身模式
"""
import asyncio, sys
from playwright.async_api import async_playwright

ZH_URL = "https://zhuanlan.zhihu.com/p/2016598051163218226"

async def main():
    async with async_playwright() as p:
        # 用 Edge 启动，有界面模式看效果
        browser = await p.chromium.launch(
            channel="msedge",
            headless=False,  # 有界面模式
        )

        context = await browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/125.0.0.0 Safari/537.36"),
            viewport={"width": 1280, "height": 720},
            locale="zh-CN",
        )
        page = await context.new_page()

        # 监听所有响应
        responses = []
        page.on("response", lambda r: responses.append(r))

        print(f"正在打开知乎文章...")
        await page.goto(ZH_URL, timeout=60000)

        # 等页面完全加载
        await page.wait_for_timeout(5000)

        # 看当前 URL 是否变了（可能会重定向到验证页）
        print(f"当前URL: {page.url}")
        print(f"页面标题: {await page.title()}")

        # 截屏看看
        await page.screenshot(path="/tmp/zhihu_result.png", full_page=True)
        print("已保存截图: /tmp/zhihu_result.png")

        # 检查页面文本
        body_text = await page.evaluate("document.body.innerText")
        print(f"\n页面文本 ({len(body_text)} 字):")
        print(body_text[:500])

        input("\n按回车键关闭浏览器...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
