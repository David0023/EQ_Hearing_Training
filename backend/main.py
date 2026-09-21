from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import init_db
import uvicorn

from api.auth import router as auth_router
from api.v1.router import router as v1_router

# Life cycle of a fastapi app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database when the application starts."""
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
@app.get("/")
def read_root():
    """Return the root endpoint response."""
    return {"Hello": "World"}

app.include_router(auth_router)
app.include_router(v1_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)