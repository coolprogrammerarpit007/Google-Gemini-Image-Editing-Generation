
import os
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.image_schema import ImageRequest, ImageEditRequest
from services.gemini_service import generate_image, edit_image, GeminiServiceError
from core.database import get_db
from models.image_log import ImageLog
from utils.response_utils import success_response, error_response
from utils.error_utils import log_error
from core.config import settings

router = APIRouter(prefix="/api", tags=["Image"])
os.makedirs("generated_images", exist_ok=True)

@router.post("/generate-image")
async def generate_image_endpoint(payload: ImageRequest, db: AsyncSession = Depends(get_db)):
    try:
        path = await generate_image(payload.prompt)
        db.add(ImageLog(prompt=payload.prompt, image_path=path, type="generate"))
        await db.commit()
        full_url = f"{settings.SERVER_HOST}/static/{path}"
        return success_response("Image generated successfully", full_url)
    except GeminiServiceError as e:
        await log_error(db, "generate_image", e.error_type, e.message, payload.prompt)
        return error_response(e.message, 400)
    except Exception as e:
        await log_error(db, "generate_image", "UnknownError", str(e), payload.prompt)
        return error_response("Internal server error", 500)

@router.post("/edit-image")
async def edit_image_endpoint(payload: ImageEditRequest, db: AsyncSession = Depends(get_db)):
    try:
        path = await edit_image(payload.prompt, payload.base64_image)
        db.add(ImageLog(prompt=payload.prompt, image_path=path, type="edit"))
        await db.commit()
        full_url = f"{settings.SERVER_HOST}/static/{path}"
        return success_response("Image edited successfully", full_url)
    except GeminiServiceError as e:
        await log_error(db, "edit_image", e.error_type, e.message, payload.prompt)
        return error_response(e.message, 400)
    except Exception as e:
        await log_error(db, "edit_image", "UnknownError", str(e), payload.prompt)
        return error_response("Internal server error", 500)

