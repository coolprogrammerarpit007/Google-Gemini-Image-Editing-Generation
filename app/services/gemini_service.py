import io
import base64
from PIL import Image
from google import genai
from core.config import settings

client = genai.Client(api_key=settings.GOOGLE_API_KEY)

async def generate_image(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image = Image.open(io.BytesIO(part.inline_data.data))
            output_path = f"generated_images/generated_{abs(hash(prompt))}.png"
            image.save(output_path)
            return output_path
    raise ValueError("No image returned from Gemini API")


async def edit_image(prompt: str, base64_image: str) -> str:
    image_data = base64.b64decode(base64_image.split(",")[-1])
    input_image = Image.open(io.BytesIO(image_data))

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, input_image],
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            edited_img = Image.open(io.BytesIO(part.inline_data.data))
            output_path = f"generated_images/edited_{abs(hash(prompt))}.png"
            edited_img.save(output_path)
            return output_path
    raise ValueError("No edited image returned from Gemini API")
