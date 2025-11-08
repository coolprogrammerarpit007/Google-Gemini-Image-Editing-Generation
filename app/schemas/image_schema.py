from pydantic import BaseModel

class ImageRequest(BaseModel):
    prompt: str

class ImageEditRequest(BaseModel):
    prompt: str
    base64_image: str

class ImageResponse(BaseModel):
    status: bool
    message: str
    image_url: str | None = None