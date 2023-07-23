from fastapi import FastAPI

from app.api import api_v1
from app.config import settings

app = FastAPI(
    title=settings.project_name, openapi_url=f"{settings.api_v1_str}/openapi.json"
)

if settings.cors_origins:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

app.include_router(api_v1.router, prefix=settings.api_v1_str)
