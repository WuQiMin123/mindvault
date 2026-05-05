import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_ingest_text():
    resp = client.post(
        "/api/v1/ingest/text",
        json={
            "title": "测试文章",
            "content": "这是一篇测试文章的内容",
            "tags": ["测试"],
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "测试文章"
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_bookmark():
    resp = client.post(
        "/api/v1/ingest/bookmark",
        json={
            "url": "https://example.com/test",
        },
    )
    assert resp.status_code == 201
    assert "待处理" in resp.json()["message"]


@pytest.mark.asyncio
async def test_list_links():
    # Create one first
    client.post(
        "/api/v1/ingest/text",
        json={
            "title": "文章1",
            "content": "内容1",
        },
    )
    resp = client.get("/api/v1/links")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0


@pytest.mark.asyncio
async def test_list_tags():
    resp = client.get("/api/v1/tags")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_search():
    resp = client.get("/api/v1/search?q=test")
    assert resp.status_code == 200
