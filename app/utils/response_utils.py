from fastapi.responses import JSONResponse

def success_response(message: str, image_url: str = None):
    return JSONResponse(
        status_code=200,
        content={
            "status": True,
            "message": message,
            "image_url": image_url,
        },
    )

def error_response(message: str, code: int = 500):
    return JSONResponse(
        status_code=code,
        content={
            "status": False,
            "message": message,
        },
    )
