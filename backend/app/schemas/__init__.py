from pydantic import BaseModel


class LinkCreate(BaseModel):
    url: str
    tags: list[str] = []


class LinkBookmark(BaseModel):
    url: str


class TextCreate(BaseModel):
    title: str
    content: str
    url: str = ""
    tags: list[str] = []


class TagResponse(BaseModel):
    id: int
    name: str
    color: str | None = None
    link_count: int = 0


class LinkResponse(BaseModel):
    id: int
    url: str | None = None
    title: str
    content: str | None = None
    raw_content: str | None = None
    source: str
    summary: str | None = None
    tags: list[TagResponse] = []
    status: str
    error: str | None = None
    is_read: int = 0
    created_at: str
    updated_at: str


class LinkListResponse(BaseModel):
    items: list[LinkResponse]
    total: int
    page: int
    page_size: int


class TagCreate(BaseModel):
    name: str
    color: str | None = None


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TagSummaryResponse(BaseModel):
    tag: TagResponse
    links: list[LinkResponse]
    aggregate_summary: str


class SearchResponse(BaseModel):
    items: list[LinkResponse]
    total: int
    page: int
    page_size: int


class MessageResponse(BaseModel):
    id: int
    status: str
    message: str


class LinkUpdate(BaseModel):
    content: str
    title: str | None = None
