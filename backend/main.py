from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import init_db
import uvicorn

from api.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)