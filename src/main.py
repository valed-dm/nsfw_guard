import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi.responses import JSONResponse
import requests


load_dotenv()
app = FastAPI()

NSFW_API_URL = os.getenv("NSFW_API_URL")
DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")

@app.post("/moderate")
async def moderate_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only .jpg, .jpeg, .png files are allowed")

    try:
        response = requests.post(
            NSFW_API_URL,
            files={"image": (file.filename, await file.read())},
            headers={"api-key": DEEPAI_API_KEY},
        )
        data = response.json()

        nsfw_score = data.get("output", {}).get("nsfw_score", 0)

        if nsfw_score > 0.7:
            return JSONResponse(status_code=200, content={"status": "REJECTED", "reason": "NSFW content"})
        else:
            return {"status": "OK"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Moderation failed: {str(e)}")
