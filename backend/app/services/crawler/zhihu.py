"""知乎内容提取 — Playwright + Cookie 持久化"""

import asyncio
import json
import logging
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

from app.services.crawler.base import Crawler

logger = logging.getLogger(__name__)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

COOKIE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "zhihu_cookies.json"


class ZhihuCrawler(Crawler):
    async def extract(self, url: str, client=None) -> dict:  # noqa: ARG002
        try:
            return await asyncio.to_thread(self._do_extract_sync, url)
        except Exception as e:
            logger.error("知乎抓取异常: %s", e)
            return {"title": "", "content": None}

    def _load_cookies(self, context) -> None:
        if not COOKIE_PATH.exists():
            logger.info("未找到知乎 Cookie 文件，将以无登录态抓取: %s", COOKIE_PATH)
            return
        try:
            cookies = json.loads(COOKIE_PATH.read_text())
            context.add_cookies(cookies)
            logger.info("已加载 %d 条知乎 Cookie", len(cookies))
        except Exception as e:
            logger.warning("加载 Cookie 失败: %s", e)

    def _do_extract_sync(self, url: str) -> dict:
        with sync_playwright() as p:
            # playwright-stealth 注入反检测脚本
            Stealth(
                navigator_languages_override=("zh-CN", "zh"),
                navigator_platform_override="Win32",
            ).hook_playwright_context(p)

            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context(
                user_agent=UA,
                viewport={"width": 1280, "height": 720},
                locale="zh-CN",
            )

            self._load_cookies(context)

            page = context.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_timeout(8000)

            title = page.title()

            text = page.evaluate(
                """
                () => {
                    const sel = '.Post-RichText,.RichText,article,.AnswerCard';
                    for (const s of sel.split(',')) {
                        const el = document.querySelector(s);
                        if (el && el.innerText.length > 200) return el.innerText;
                    }
                    return document.body.innerText;
                }
            """
            )

            browser.close()

            if len(text) < 200:
                return {"title": title, "content": None}

            return {"title": title, "content": text, "raw_content": text}
