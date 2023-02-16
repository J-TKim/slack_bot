from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from api.api_v1.api import api_router
from core.config import settings

app = FastAPI(
    title="slackBot", openapi_url="/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
