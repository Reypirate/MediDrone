import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from shared.database import init_db
from shared.tracking import RequestTrackingMiddleware
from scalar_fastapi import get_scalar_api_reference
from .router import router
from . import service


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    service.run_consumer_thread()
    yield


app = FastAPI(title="Drone Dispatch Service", lifespan=lifespan)
app.add_middleware(RequestTrackingMiddleware)


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
