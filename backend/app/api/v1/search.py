from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.link import Link
from app.models.link_tag import link_tag
from app.schemas import LinkResponse, SearchResponse, TagResponse

router = APIRouter()


@router.get("")
async def search(
    q: str = "",
    tag_ids: str = "",
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    query = select(Link).options(selectinload(Link.tags)).order_by(Link.created_at.desc())

    if q:
        like = f"%{q}%"
        query = query.where(
            or_(Link.title.ilike(like), Link.content.ilike(like), Link.summary.ilike(like))
        )

    if tag_ids:
        tid_list = [int(x) for x in tag_ids.split(",") if x.strip().isdigit()]
        for tid in tid_list:
            subq = select(link_tag.c.link_id).where(link_tag.c.tag_id == tid)
            query = query.where(Link.id.in_(subq))

    # Count without selectinload to avoid cartesian product
    count_q = select(Link.id)
    if q:
        count_q = count_q.where(
            or_(
                Link.title.ilike(f"%{q}%"),
                Link.content.ilike(f"%{q}%"),
                Link.summary.ilike(f"%{q}%"),
            )
        )
    if tag_ids:
        tid_list = [int(x) for x in tag_ids.split(",") if x.strip().isdigit()]
        for tid in tid_list:
            subq = select(link_tag.c.link_id).where(link_tag.c.tag_id == tid)
            count_q = count_q.where(Link.id.in_(subq))
    count_result = await db.execute(count_q)
    total = len(count_result.all())

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    links = result.scalars().unique().all()

    return SearchResponse(
        items=[
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
        total=total,
        page=page,
        page_size=page_size,
    )
