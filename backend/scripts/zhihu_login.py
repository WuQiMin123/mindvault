"""知乎 Cookie 导出工具

运行方式:
    python scripts/zhihu_login.py

会打开一个浏览器窗口，请手动登录知乎，完成后 Cookie 自动保存到 data/zhihu_cookies.json
"""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

COOKIE_PATH = Path(__file__).resolve().parent.parent / "data" / "zhihu_cookies.json"


def main():
    print("=" * 60)
    print("知乎 Cookie 导出工具")
    print("=" * 60)
    print("即将打开浏览器窗口…")
    print("请手动登录知乎（扫码或账号密码）")
    print("登录成功后按 Enter 键保存 Cookie\n")
    input("按 Enter 继续…")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="zh-CN",
        )
        page = context.new_page()
        page.add_init_script(
            'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'
        )

        page.goto("https://www.zhihu.com/signin", timeout=60000)
        print("\n请在浏览器中完成登录，然后回到此终端…")
        input("登录完成后按 Enter 保存 Cookie…")

        cookies = context.cookies()
        COOKIE_PATH.write_text(json.dumps(cookies, ensure_ascii=False, indent=2))
        print(f"✅ Cookie 已保存 ({len(cookies)} 条) → {COOKIE_PATH}")

        # 验证登录态
        page.goto("https://www.zhihu.com/", timeout=30000)
        page.wait_for_timeout(3000)
        title = page.title()
        if "知乎" in title:
            print("✅ 登录验证成功")
        else:
            print("⚠️  页面标题异常，登录可能未生效")

        browser.close()


if __name__ == "__main__":
    main()
