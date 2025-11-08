import os, time, base64
import requests
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SD_URL = os.getenv("SD_URL", "http://127.0.0.1:7860")
SAVE_DIR = r"C:\Users\user\Documents\lidia\lidia\thesis\PromptWear\Result images"
os.makedirs(SAVE_DIR, exist_ok=True)

class GenerateBody(BaseModel):
    # core prompt
    prompt: str

    # build a clean A1111/Forge payload
    def to_sd_payload(self) -> dict:
        p = {
            "prompt": self.prompt,
            "batch_size": 1,
            "steps": 30,
            "seed": -1,
            "distilled_cfg_scale": 3.5,
            "cfg_scale": 1,
            "width": 896,
            "height": 1152,
            "sampler_name": "Euler",
            "scheduler": "Simple"
            }
        return p

def sd_txt2img(payload: dict) -> List[str]:
    try:
        r = requests.post(f"{SD_URL}/sdapi/v1/txt2img", json=payload, timeout=180)
        if r.status_code >= 400:
            # surface Forge/A1111 error message (OOM, bad upscaler, etc.)
            raise HTTPException(status_code=502, detail=f"SD API error {r.status_code}: {r.text}")
        data = r.json()
        images = data.get("images", [])
        if not images:
            raise HTTPException(status_code=500, detail="Stable Diffusion returned no images.")
        return images
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"SD API request failed: {e}")

@app.post("/generate")
def generate(body: GenerateBody):
    payload = body.to_sd_payload()
    images = sd_txt2img(payload)
    return {"prompt": body.prompt, "images": images}

@app.get("/progress")
def get_progress():
    try:
        r = requests.get(f"{SD_URL}/sdapi/v1/progress?skip_current_image=false", timeout=10)
        if r.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"SD API error {r.status_code}: {r.text}")
        data = r.json()
        return {
            "progress": round(data.get("progress", 0) * 100, 2),
            "eta_relative": data.get("eta_relative", 0),
            "sampling_step": data.get("state", {}).get("sampling_step", 0),
            "sampling_steps": data.get("state", {}).get("sampling_steps", 0),
            "current_image": data.get("current_image"),  # optional: base64 preview
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"SD progress API request failed: {e}")



class SaveBody(BaseModel):
    image_base64: str           # just the raw base64, no data URL prefix
    filename: Optional[str] = None  # optional custom name

@app.post("/save_image")
def save_image(body: SaveBody):
    # pick a filename
    name = body.filename or f"design_{int(time.time())}.png"
    # sanitize just in case
    name = name.replace("\\", "_").replace("/", "_")
    path = os.path.join(SAVE_DIR, name)

    try:
        img_bytes = base64.b64decode(body.image_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image: {e}")

    try:
        with open(path, "wb") as f:
            f.write(img_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    return {"ok": True, "saved_path": path, "filename": name}
