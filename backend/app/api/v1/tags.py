from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.link import Link
from app.models.link_tag import link_tag
from app.models.tag import Tag
from app.schemas import LinkResponse, TagCreate, TagResponse, TagSummaryResponse, TagUpdate

router = APIRouter()


@router.get("")
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            Tag.id,
            Tag.name,
            Tag.color,
            func.count(link_tag.c.link_id).label("link_count"),
        )
        .outerjoin(link_tag, Tag.id == link_tag.c.tag_id)
        .group_by(Tag.id)
        .order_by(Tag.name)
    )
    rows = result.all()
    return [
        TagResponse(id=row.id, name=row.name, color=row.color, link_count=row.link_count)
        for row in rows
    ]


@router.post("", status_code=201)
async def create_tag(body: TagCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Tag).where(Tag.name == body.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="标签已存在")
    tag = Tag(name=body.name, color=body.color)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return TagResponse(id=tag.id, name=tag.name, color=tag.color)


@router.put("/{tag_id}")
async def update_tag(tag_id: int, body: TagUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    if body.name is not None:
        tag.name = body.name
    if body.color is not None:
        tag.color = body.color
    await db.commit()
    await db.refresh(tag)
    return TagResponse(id=tag.id, name=tag.name, color=tag.color)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    await db.execute(link_tag.delete().where(link_tag.c.tag_id == tag_id))
    await db.delete(tag)
    await db.commit()


@router.put("/links/{link_id}/tags")
async def update_link_tags(link_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    tag_ids = body.get("tag_ids", [])
    await db.execute(link_tag.delete().where(link_tag.c.link_id == link_id))
    for tid in tag_ids:
        await db.execute(link_tag.insert().values(link_id=link_id, tag_id=tid))
    await db.commit()
    return {"tag_ids": tag_ids}


@router.get("/{tag_id}/summary")
async def tag_summary(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    result = await db.execute(
        select(Link)
        .options(selectinload(Link.tags))
        .join(link_tag)
        .where(link_tag.c.tag_id == tag_id)
        .order_by(Link.created_at.desc())
    )
    links = result.scalars().unique().all()

    summaries = [link.summary for link in links if link.summary]
    aggregate = " | ".join(summaries) if summaries else "暂无内容"

    return TagSummaryResponse(
        tag=TagResponse(id=tag.id, name=tag.name, color=tag.color, link_count=len(links)),
        links=[
            LinkResponse(
                id=link.id,
                url=link.url,
                title=link.title,
                content=link.content,
                raw_content=link.raw_content,
                source=link.source,
                summary=link.summary,
                tags=[TagResponse(id=t.id, name=t.name, color=t.color) for t in link.tags],
                status=link.status,
                error=link.error,
                is_read=link.is_read,
                created_at=str(link.created_at),
                updated_at=str(link.updated_at),
            )
            for link in links
        ],
        aggregate_summary=aggregate,
    )
