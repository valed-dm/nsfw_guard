from contextlib import asynccontextmanager
import os
from typing import AsyncIterator

from aiohttp import ClientSession
from aiohttp import FormData
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile

from src.models import ModerationResponse


load_dotenv()

NSFW_API_URL = os.getenv("NSFW_API_URL")
DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.aiohttp_session = ClientSession()
    yield
    await app.state.aiohttp_session.close()


app = FastAPI(lifespan=lifespan)
router = APIRouter()

@router.post("/moderate", response_model=ModerationResponse)
async def moderate_image(file: UploadFile = File(...)) -> ModerationResponse:
    """
    Moderate an uploaded image using the DeepAI NSFW detector.
    Returns 'OK' if safe, otherwise 'REJECTED'.
    """
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only .jpg, .jpeg, .png files are allowed")

    try:
        image_bytes = await file.read()

        form = FormData()
        form.add_field(
            name="image",
            value=image_bytes,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
        )

        async with app.state.aiohttp_session.post(
            NSFW_API_URL,
            data=form,
            headers={"api-key": DEEPAI_API_KEY},
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise HTTPException(status_code=resp.status, detail=f"API error: {text}")
            data = await resp.json()

        nsfw_score = data.get("output", {}).get("nsfw_score", 0)
        if nsfw_score > 0.7:
            return ModerationResponse(status="REJECTED", reason="NSFW content")
        return ModerationResponse(status="OK")

    except Exception as e:
        import traceback
        traceback.print_exc()  # Logs full stack trace to console
        raise HTTPException(status_code=500, detail=f"Moderation failed: {str(e)}")


app.include_router(router)
