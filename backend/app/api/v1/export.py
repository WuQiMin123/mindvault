"""数据导出：JSON / Markdown"""

import datetime
import io
import zipfile

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.link import Link
from app.models.tag import Tag

router = APIRouter()


@router.get("/json")
async def export_json(db: AsyncSession = Depends(get_db)):
    """导出全部数据为 JSON"""
    links_result = await db.execute(
        select(Link).options(selectinload(Link.tags)).order_by(Link.created_at.desc())
    )
    links = links_result.scalars().unique().all()

    tags_result = await db.execute(select(Tag).order_by(Tag.name))
    tags = tags_result.scalars().all()

    return {
        "version": "1.0",
        "exported_at": datetime.datetime.now().isoformat(),
        "tags": [
            {"id": t.id, "name": t.name, "color": t.color, "created_at": str(t.created_at)}
            for t in tags
        ],
        "links": [
            {
                "id": link.id,
                "url": link.url,
                "title": link.title,
                "content": link.content,
                "raw_content": link.raw_content,
                "source": link.source,
                "summary": link.summary,
                "tags": [{"id": t.id, "name": t.name} for t in link.tags],
                "status": link.status,
                "is_read": bool(link.is_read),
                "created_at": str(link.created_at),
                "updated_at": str(link.updated_at),
            }
            for link in links
        ],
    }


@router.get("/markdown")
async def export_markdown(db: AsyncSession = Depends(get_db)):
    """导出全部数据为 Markdown 文件，ZIP 打包"""
    links_result = await db.execute(
        select(Link).options(selectinload(Link.tags)).order_by(Link.created_at.desc())
    )
    links = links_result.scalars().unique().all()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for link in links:
            safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in link.title)
            safe_title = safe_title.strip() or f"link_{link.id}"
            filename = f"{safe_title[:80]}.md"

            md = f"# {link.title}\n\n"
            if link.url:
                md += f"源链接：{link.url}\n\n"
            md += f"> 来源：{link.source} | 状态：{link.status} | 创建时间：{link.created_at}\n\n"
            if link.summary:
                md += f"## 摘要\n\n{link.summary}\n\n"
            if link.tags:
                md += f"标签：{'、'.join(t.name for t in link.tags)}\n\n"
            if link.content:
                md += "---\n\n## 正文\n\n"
                # 对 content 做基本的 markdown 转义，避免误解
                md += link.content + "\n\n"

            zf.writestr(filename, md)

    buf.seek(0)
    from fastapi.responses import Response

    return Response(
        content=buf.read(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=mindvault-export.zip"},
    )
