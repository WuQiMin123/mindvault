"""后台任务：抓取内容 → AI 摘要 → 自动打标签"""

import logging

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.link import Link
from app.models.link_tag import link_tag
from app.models.tag import Tag
from app.services.crawler.bilibili import BilibiliCrawler
from app.services.crawler.zhihu import ZhihuCrawler
from app.services.processor import Processor

logger = logging.getLogger(__name__)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

_crawlers = {
    "bilibili": BilibiliCrawler(),
    "zhihu": ZhihuCrawler(),
}

_processor = Processor()


async def ensure_tag(db: AsyncSession, name: str) -> Tag:
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        await db.flush()
    return tag


async def process_link(link_id: int) -> None:
    """处理单个链接：抓取 → 摘要 → 标签"""
    async with async_session() as db:
        result = await db.execute(select(Link).where(Link.id == link_id))
        link = result.scalar_one_or_none()
        if not link:
            logger.warning("[link_id=%d] 链接不存在，跳过处理", link_id)
            return

        if link.status != "pending":
            logger.info("[link_id=%d] 跳过非 pending 状态: %s", link_id, link.status)
            return

        logger.info(
            "[link_id=%d] 开始处理 | source=%s | url=%s",
            link_id, link.source, link.url,
        )

        # --- 抓取内容（仅当尚无内容时） ---
        if not link.content:
            crawler = _crawlers.get(link.source)
            if crawler is None:
                logger.info("[link_id=%d] 无对应爬虫: %s", link_id, link.source)
                link.status = "no_content"
                await db.commit()
                return

            try:
                if link.source == "bilibili":
                    async with httpx.AsyncClient() as client:
                        result = await crawler.extract(link.url, client)
                else:
                    result = await crawler.extract(link.url)
            except Exception as e:
                logger.error("[link_id=%d] 抓取失败: %s", link_id, e)
                link.status = "no_content"
                link.error = f"抓取失败: {e}"
                fail_tag = await ensure_tag(db, "未成功")
                await db.execute(link_tag.insert().values(link_id=link.id, tag_id=fail_tag.id))
                await db.commit()
                return

            title = result.get("title", "")
            content = result.get("content")

            if not content:
                logger.info("[link_id=%d] 内容提取为空 | title=%s", link_id, title)
                link.status = "no_content"
                link.error = "内容提取失败"
                fail_tag = await ensure_tag(db, "未成功")
                await db.execute(link_tag.insert().values(link_id=link.id, tag_id=fail_tag.id))
                await db.commit()
                return

            # --- 更新基本信息 ---
            if title:
                link.title = title
            link.content = content
            link.raw_content = result.get("raw_content", content)
            logger.info("[link_id=%d] 内容提取成功 | content_len=%d", link_id, len(content))
        else:
            logger.info("[link_id=%d] 已有内容，跳过抓取 | content_len=%d", link_id, len(link.content))

        # --- AI 摘要 ---
        try:
            summary = await _processor.generate_summary(content)
            link.summary = summary
            logger.info("[link_id=%d] AI 摘要生成完成 | summary_len=%d", link_id, len(summary))
        except Exception as e:
            logger.error("[link_id=%d] AI 摘要失败: %s", link_id, e)

        # --- AI 标签 ---
        try:
            tag_names = await _processor.suggest_tags(content)
            if tag_names:
                link.tags_ai = ",".join(tag_names)
                for tag_name in tag_names:
                    tag = await ensure_tag(db, tag_name)
                    await db.execute(link_tag.insert().values(link_id=link.id, tag_id=tag.id))
                logger.info(
                    "[link_id=%d] AI 标签生成完成 | tags=%s", link_id, tag_names,
                )
        except Exception as e:
            logger.error("[link_id=%d] AI 打标签失败: %s", link_id, e)

        link.status = "completed"
        await db.commit()
        logger.info("[link_id=%d] 处理完成 | status=completed", link_id)
