from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi.util import get_remote_address
from slowapi import Limiter
from schemas.image_schema import ImageRequest, ImageEditRequest
from services.gemini_service import generate_image, edit_image, GeminiServiceError
from core.database import get_db
from models.image_log import ImageLog
from utils.response_utils import success_response, error_response
from utils.error_utils import log_error
from core.config import settings

router = APIRouter(prefix="/api", tags=["Image"])

# ✅ Get limiter instance from app
limiter = Limiter(key_func=get_remote_address)

@router.post("/generate-image")
@limiter.limit("5/minute")  # 👈 Limit this route to 5 requests per minute per IP

# ****************** Handle urls of Multiple Images ******************
# async def generate_image_endpoint(payload: ImageRequest, request: Request, db: AsyncSession = Depends(get_db)):
#     try:
#         path = await generate_image(payload.prompt)
#         db.add(ImageLog(prompt=payload.prompt, image_path=path, type="generate"))
#         await db.commit()
#         full_url = f"{settings.SERVER_HOST}/static/{path}"
#         return success_response("Image generated successfully", full_url)
#     except GeminiServiceError as e:
#         await log_error(db, "generate_image", e.error_type, e.message, payload.prompt)
#         return error_response(e.message, 400)
#     except Exception as e:
#         await log_error(db, "generate_image", "UnknownError", str(e), payload.prompt)
#         return error_response("Internal server error", 500)


async def generate_image_endpoint(payload: ImageRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handles both single and multi-image prompts (like "10 images of good morning").
    Automatically detects count, generates concurrently, logs results, and returns URLs.
    """
    try:
        # Generate one or more images based on the prompt
        image_paths = await generate_image(payload.prompt)  # returns list of paths
        logger_msg = f"Generated {len(image_paths)} image(s) for prompt: {payload.prompt}"
        print(logger_msg)

        # Store all generated images in the database
        for path in image_paths:
            db.add(ImageLog(prompt=payload.prompt, image_path=path, type="generate"))
        await db.commit()

        # Build full accessible URLs
        image_urls = [f"{settings.SERVER_HOST}/static/{path}" for path in image_paths]

        # Dynamic message depending on count
        msg = "Image generated successfully" if len(image_urls) == 1 else f"{len(image_urls)} images generated successfully"
        return success_response(msg, image_urls)

    except GeminiServiceError as e:
        await log_error(db, "generate_image", e.error_type, e.message, payload.prompt)
        return error_response(e.message, 400)

    except Exception as e:
        await log_error(db, "generate_image", "UnknownError", str(e), payload.prompt)
        return error_response("Internal server error", 500)


@router.post("/edit-image")
@limiter.limit("3/minute")  # 👈 Limit this route to 3 requests per minute per IP
async def edit_image_endpoint(payload: ImageEditRequest, request: Request, db: AsyncSession = Depends(get_db)):
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