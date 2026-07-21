from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.routers import jobs, tailor, profile, notifications, resume
from app.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler_task = asyncio.create_task(start_scheduler())
    yield
    scheduler_task.cancel()


app = FastAPI(
    title="HireForge AI API",
    description="AI-powered job hunting and resume tailoring backend",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(tailor.router, prefix="/api/tailor", tags=["Tailor"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(resume.router)

@app.get("/")
async def root():
    return {"status": "HireForge AI backend is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
