from fastapi import FastAPI

from app.models import HealthCheck
from app.routers import items

app = FastAPI(
    title="DevOps Pipeline Lab API",
    description="API REST de ejemplo para laboratorio de DevOps",
    version="1.0.0",
)

app.include_router(items.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {"message": "DevOps Pipeline Lab API", "docs": "/docs"}


@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """Health check endpoint for container orchestration."""
    return HealthCheck()
