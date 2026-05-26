from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.link import Link
from app.models.link_tag import link_tag
from app.models.tag import Tag
from app.schemas import LinkResponse, LinkUpdate, TagResponse

router = APIRouter()


def _link_to_response(link: Link) -> LinkResponse:
    return LinkResponse(
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


@router.get("")
async def list_links(
    page: int = 1,
    page_size: int = 20,
    tag: str = "",
    source: str = "",
    status: str = "",
    search: str = "",
    db: AsyncSession = Depends(get_db),
):
    query = select(Link).options(selectinload(Link.tags)).order_by(Link.created_at.desc())

    if tag:
        query = query.join(link_tag).join(Tag).where(Tag.name == tag)
    if source:
        query = query.where(Link.source == source)
    if status:
        query = query.where(Link.status == status)

    count_q = select(Link.id)
    if tag:
        count_q = count_q.join(link_tag).join(Tag).where(Tag.name == tag)
    if source:
        count_q = count_q.where(Link.source == source)
    if status:
        count_q = count_q.where(Link.status == status)
    total_result = await db.execute(count_q)
    total = len(total_result.all())

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    links = result.scalars().unique().all()

    return {
        "items": [_link_to_response(link) for link in links],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{link_id}")
async def get_link(link_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Link).options(selectinload(Link.tags)).where(Link.id == link_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")
    return _link_to_response(link)


@router.delete("/{link_id}", status_code=204)
async def delete_link(link_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")
    await db.execute(link_tag.delete().where(link_tag.c.link_id == link_id))
    await db.delete(link)
    await db.commit()


@router.patch("/{link_id}/read-status")
async def update_read_status(link_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")
    link.is_read = 1 if body.get("is_read") else 0
    await db.commit()
    return {"id": link.id, "is_read": bool(link.is_read)}


@router.patch("/{link_id}")
async def update_link(
    link_id: int,
    body: LinkUpdate,
    db: AsyncSession = Depends(get_db),
):
    """手动更新内容"""
    result = await db.execute(
        select(Link).options(selectinload(Link.tags)).where(Link.id == link_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="链接不存在")

    link.content = body.content
    link.raw_content = body.content
    if body.title:
        link.title = body.title

    await db.commit()

    resp = _link_to_response(link)
    return resp