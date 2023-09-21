from fastapi import FastAPI

from app.api import api_v1
from app.config import settings

if settings.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=str(settings.sentry_dsn),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
    )

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
