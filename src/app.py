from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import health, configs
from utils.logging_utils import setup_logging, get_logger

setup_logging()
logger = get_logger()

app = FastAPI(
    title="Configuration Management API",
    description="Lightweight configuration management for microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(configs.router, prefix="/configs", tags=["configurations"])


@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Configuration Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
