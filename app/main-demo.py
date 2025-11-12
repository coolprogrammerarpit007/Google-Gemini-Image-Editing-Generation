import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import image_routes
from core.database import Base, engine
from core.logger import logger

app = FastAPI(title="Gemini Image API", version="2.0")

app.mount("/static", StaticFiles(directory="."), name="static")
app.include_router(image_routes.router)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database and tables initialized successfully")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=9000, reload=True)

