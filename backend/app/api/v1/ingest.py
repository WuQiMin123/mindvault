import hashlib

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.link import Link
from app.models.link_tag import link_tag
from app.models.tag import Tag
from app.schemas import TextCreate

router = APIRouter()


async def _ensure_tag(db: AsyncSession, name: str) -> Tag:
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        await db.flush()
    return tag


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