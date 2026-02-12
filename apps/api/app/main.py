from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth_router,
    users_router,
    artists_router,
    events_router,
    search_router,
)

app = FastAPI(
    title="Artist Event Aggregator API",
    description="RAG-based artist event search and calendar API",
    version="0.1.0",
)

# CORS 설정 (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(artists_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Artist Event Aggregator API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
