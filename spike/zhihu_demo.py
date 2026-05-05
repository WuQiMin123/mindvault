"""
知乎文章提取 Demo — 手动输 cookie
"""
import asyncio, sys, os, tempfile
from playwright.async_api import async_playwright

async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else input("粘贴知乎链接: ").strip()

    d_c0 = input("d_c0: ").strip()
    z_c0 = input("z_c0: ").strip()
    _xsrf = input("_xsrf: ").strip()

    cookies = []
    if d_c0: cookies.append({"name": "d_c0", "value": d_c0, "domain": ".zhihu.com", "path": "/"})
    if z_c0: cookies.append({"name": "z_c0", "value": z_c0, "domain": ".zhihu.com", "path": "/"})
    if _xsrf: cookies.append({"name": "_xsrf", "value": _xsrf, "domain": ".zhihu.com", "path": "/"})

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context()
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()
        await page.add_init_script(
            'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'
        )

        print(f"\n打开: {url[:50]}...")
        await page.goto(url, timeout=30000)
        await page.wait_for_timeout(5000)

        title = await page.title()
        print(f"标题: {title}")

        text = await page.evaluate("""
            () => {
                const sel = '.Post-RichText,.RichText,article,.AnswerCard';
                for (const s of sel.split(',')) {
                    const el = document.querySelector(s);
                    if (el && el.innerText.length > 200) return el.innerText;
                }
                return document.body.innerText;
            }
        """)
        print(f"正文: {len(text)} 字")
        if len(text) > 200:
            print(f"\n{'━'*40}")
            print(text[:800])
            print(f"\n{'━'*40}")
        else:
            print(f"内容: {text[:200]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
