from sqlalchemy import Column, ForeignKey, Integer, Table

from app.database import Base

link_tag = Table(
    "link_tag",
    Base.metadata,
    Column("link_id", Integer, ForeignKey("links.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
