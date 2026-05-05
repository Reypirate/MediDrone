import os
from fastapi import FastAPI
from sqlmodel import SQLModel
from shared.database import engine
from shared.tracking import RequestTrackingMiddleware
from scalar_fastapi import get_scalar_api_reference
from .router import router

app = FastAPI(title="Order Service")
app.add_middleware(RequestTrackingMiddleware)


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 5002))
    uvicorn.run(app, host="0.0.0.0", port=port)
