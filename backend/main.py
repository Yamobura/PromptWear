import os
import requests
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SD_URL = os.getenv("SD_URL", "http://127.0.0.1:7860")
DEFAULT_NEG = "(low quality, worst quality:1.3), negative_hand-neg, ((hard light))"

class GenerateBody(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = DEFAULT_NEG
    seed: Optional[int] = None
    steps: int = 30
    sampler_name: str = "DPM++ 2M SDE"
    cfg_scale: float = 7.0
    width: int = 512
    height: int = 640

def sd_txt2img(payload: dict) -> List[str]:
    try:
        r = requests.post(f"{SD_URL}/sdapi/v1/txt2img", json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        images = data.get("images", [])
        if not images:
            raise HTTPException(status_code=500, detail="Stable Diffusion returned no images.")
        return images
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"SD API error: {e}")

@app.post("/generate")
def generate(body: GenerateBody):
    images = sd_txt2img(body.dict())
    return {"prompt": body.prompt, "images": images}
