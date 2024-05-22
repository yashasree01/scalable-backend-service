from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from .api.routes import router
from .utils import request_logging_middleware, get_logger
from .models import HealthResponse


start_time = time.time()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Scalable Backend Service starting up...")
    yield
    logger.info("Scalable Backend Service shutting down...")


app = FastAPI(
    title="Scalable Backend Service",
    description="High-concurrency backend service with async request handling",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(request_logging_middleware)

app.include_router(router)


@app.get("/", tags=["root"])
async def root():
    return {
        "name": "Scalable Backend Service",
        "version": "1.0.0",
        "description": "High-concurrency backend with async processing"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0",
        uptime_seconds=time.time() - start_time
    )
