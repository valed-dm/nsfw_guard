from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi.responses import JSONResponse
import requests


app = FastAPI()

DEEPAI_API_KEY = "bbfef540-7331-4a29-bc05-9e2b21b006d9"
NSFW_API_URL = "https://api.deepai.org/api/nsfw-detector"

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
