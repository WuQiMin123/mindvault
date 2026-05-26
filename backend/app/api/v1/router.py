from fastapi import APIRouter

from app.api.v1 import export, ingest, links, search, tags

api_router = APIRouter()
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(links.router, prefix="/links", tags=["links"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
