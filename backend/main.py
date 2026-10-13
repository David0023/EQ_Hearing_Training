from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.database import init_db
import uvicorn

from core.config import settings
from auth.router import router as auth_router
from api.v1.router import router as v1_router

# Life cycle of a fastapi app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database when the application starts."""
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return RedirectResponse("/docs")

app.include_router(auth_router)
app.include_router(v1_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
