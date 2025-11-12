import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routes import image_routes
from core.database import Base, engine
from core.logger import logger

# Initialize app
app = FastAPI(title="Gemini Image API", version="2.0")

# ✅ Create limiter (example: max 10 calls per minute per IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter

# ✅ Register handler for rate-limit errors
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ✅ Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# ✅ Include routers
app.include_router(image_routes.router)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database and tables initialized successfully")

# ✅ Example of global middleware logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    return response

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=9000, reload=True)

