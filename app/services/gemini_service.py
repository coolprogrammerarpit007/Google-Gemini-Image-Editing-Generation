import io
import re
import base64
import asyncio
from PIL import Image, UnidentifiedImageError
from google import genai
from google.api_core import exceptions as google_exceptions
from core.config import settings
from core.logger import logger

client = genai.Client(api_key=settings.GOOGLE_API_KEY)

class GeminiServiceError(Exception):
    def __init__(self, message: str, error_type: str = "GeneralError"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


# ✅ Reusable retry-safe Gemini API call
async def safe_api_call(func, *args, retries=3, delay=1, **kwargs):
    """Retry wrapper for Gemini API calls"""
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except google_exceptions.ServiceUnavailable:
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise GeminiServiceError("Gemini API service unavailable", "ServiceUnavailable")


# ✅ Helper: Extract number of images from prompt
def extract_image_count(prompt: str) -> int:
    """
    Detects if user prompt asks for multiple images like '10 images of cats'
    and returns count (defaults to 1 if not found)
    """
    match = re.search(r"(\d+)\s*(?:images?|photos?|pictures?)", prompt.lower())
    if match:
        count = int(match.group(1))
        return min(max(count, 1), 10)  # limit between 1 and 10 for safety
    return 1


# ✅ Core single-image generator
async def _generate_single_image(prompt: str, index: int = None) -> str:
    """Generate a single image safely from Gemini"""
    try:
        response = await safe_api_call(
            client.models.generate_content,
            model="gemini-2.5-flash-image",
            contents=[prompt]
        )

        if not response or not response.candidates:
            raise GeminiServiceError("No response from Gemini API", "EmptyResponse")

        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image = Image.open(io.BytesIO(part.inline_data.data))
                filename_suffix = f"_{index}" if index is not None else ""
                output_path = f"generated_images/generated_{abs(hash(prompt))}{filename_suffix}.png"
                image.save(output_path)
                return output_path

        raise GeminiServiceError("Gemini API did not return image data", "NoImageData")

    except google_exceptions.PermissionDenied:
        raise GeminiServiceError("Gemini API key invalid or missing permission", "PermissionDenied")
    except google_exceptions.ResourceExhausted:
        raise GeminiServiceError("Gemini API quota or credits exhausted", "ResourceExhausted")
    except UnidentifiedImageError:
        raise GeminiServiceError("Invalid image data returned from Gemini API", "InvalidImage")
    except Exception as e:
        logger.error(f"Gemini single image error: {e}")
        raise GeminiServiceError(str(e), "UnknownError")


# ✅ Main function — handles both single and multi-image prompts
async def generate_image(prompt: str):
    try:
        if not prompt.strip():
            raise GeminiServiceError("Prompt cannot be empty", "ValidationError")

        # detect if prompt asks for multiple images
        image_count = extract_image_count(prompt)
        logger.info(f"Detected image count: {image_count} for prompt: '{prompt}'")

        # Generate multiple images asynchronously if requested
        if image_count > 1:
            # Slightly modify prompt for better diversity
            tasks = [
                _generate_single_image(f"{prompt} (version {i+1})", index=i+1)
                for i in range(image_count)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            output_paths = []
            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    logger.error(f"Image {i+1} failed: {res}")
                else:
                    output_paths.append(res)

            if not output_paths:
                raise GeminiServiceError("No images generated successfully", "EmptyResponse")

            return output_paths  # list of image paths

        # Otherwise, single image generation
        single_path = await _generate_single_image(prompt)
        return [single_path]

    except GeminiServiceError:
        raise
    except Exception as e:
        logger.error(f"Gemini multi-image error: {e}")
        raise GeminiServiceError(str(e), "UnknownError")


# ✅ Image editing (unchanged, except for naming consistency)
async def edit_image(prompt: str, base64_image: str) -> str:
    try:
        if not prompt.strip():
            raise GeminiServiceError("Prompt cannot be empty", "ValidationError")
        if not base64_image:
            raise GeminiServiceError("Base64 image required", "InvalidInput")

        try:
            image_data = base64.b64decode(base64_image.split(",")[-1])
            input_image = Image.open(io.BytesIO(image_data))
        except Exception:
            raise GeminiServiceError("Invalid base64 image data", "InvalidInput")

        response = await safe_api_call(
            client.models.generate_content,
            model="gemini-2.5-flash-image",
            contents=[prompt, input_image]
        )

        if not response or not response.candidates:
            raise GeminiServiceError("No response from Gemini API", "EmptyResponse")

        for part in response.candidates[0].content.parts:
            if part.inline_data:
                edited_img = Image.open(io.BytesIO(part.inline_data.data))
                output_path = f"generated_images/edited_{abs(hash(prompt))}.png"
                edited_img.save(output_path)
                return output_path

        raise GeminiServiceError("Gemini API did not return edited image", "NoImageData")

    except google_exceptions.ResourceExhausted:
        raise GeminiServiceError("Gemini API quota or credits exhausted", "ResourceExhausted")
    except google_exceptions.PermissionDenied:
        raise GeminiServiceError("Invalid Gemini API key", "PermissionDenied")
    except Exception as e:
        logger.error(f"Edit error: {e}")
        raise GeminiServiceError(str(e), "UnknownError")
