from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, donation, refurbishment, part, recipient


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    from app.init_db import init_db
    init_db()
    yield


app = FastAPI(
    title="自行车翻新捐赠平台 API",
    description="城市旧自行车回收翻新捐赠公益平台",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(donation.router)
app.include_router(refurbishment.router)
app.include_router(part.router)
app.include_router(recipient.router)


@app.get("/")
def root():
    return {
        "message": "自行车翻新捐赠平台 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
