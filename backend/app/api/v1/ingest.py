import hashlib

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.link import Link
from app.models.link_tag import link_tag
from app.models.tag import Tag
from app.schemas import LinkBookmark, LinkCreate, TextCreate
from app.services.task_runner import process_link

router = APIRouter()


async def _ensure_tag(db: AsyncSession, name: str) -> Tag:
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        await db.flush()
    return tag


@router.post("/link", status_code=202)
async def ingest_link(
    body: LinkCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    link = Link(
        url=body.url,
        title=body.url,
        source=_detect_source(body.url),
        status="pending",
    )
    db.add(link)
    await db.flush()

    if body.tags:
        for tag_name in body.tags:
            tag = await _ensure_tag(db, tag_name)
            await db.execute(link_tag.insert().values(link_id=link.id, tag_id=tag.id))

    await db.commit()

    background_tasks.add_task(process_link, link.id)
    return {"id": link.id, "status": "pending", "message": "内容正在抓取处理"}


@router.post("/bookmark", status_code=201)
async def bookmark_link(body: LinkBookmark, db: AsyncSession = Depends(get_db)):
    link = Link(
        url=body.url,
        title=body.url,
        source=_detect_source(body.url),
        status="completed",
    )
    db.add(link)
    await db.flush()

    tag = await _ensure_tag(db, "待处理")
    await db.execute(link_tag.insert().values(link_id=link.id, tag_id=tag.id))
    await db.commit()

    return {"id": link.id, "status": "completed", "message": "链接已暂存到「待处理」标签"}


@router.post("/text", status_code=201)
async def ingest_text(body: TextCreate, db: AsyncSession = Depends(get_db)):
    content_hash = hashlib.md5(body.content.encode()).hexdigest()
    link = Link(
        url=body.url or None,
        title=body.title,
        content=body.content,
        raw_content=body.content,
        source="manual",
        content_hash=content_hash,
        status="completed",
    )
    db.add(link)
    await db.flush()

    if body.tags:
        for tag_name in body.tags:
            tag = await _ensure_tag(db, tag_name)
            await db.execute(link_tag.insert().values(link_id=link.id, tag_id=tag.id))

    await db.commit()
    return {"id": link.id, "title": body.title, "status": "completed"}


@router.post("/check")
async def check_link(url: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.url == url))
    existing = result.scalar_one_or_none()
    if existing:
        return {"exists": True, "link_id": existing.id, "title": existing.title}
    return {"exists": False}


def _detect_source(url: str) -> str:
    url = url.lower()
    if "bilibili.com" in url:
        return "bilibili"
    if "zhihu.com" in url:
        return "zhihu"
    if "douyin.com" in url:
        return "douyin"
    return "web"
