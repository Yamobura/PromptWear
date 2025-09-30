import os
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
DEFAULT_NEG = "(low quality, worst quality:1.3), negative_hand-neg, ((hard light))"

class GenerateBody(BaseModel):
    # core prompt
    prompt: str
    negative_prompt: Optional[str] = DEFAULT_NEG

    # sampler (use Karras variant in the name; don’t send separate scheduler)
    steps: int = 30
    sampler_name: str = "DPM++ 2M SDE Karras"
    cfg_scale: float = 7.0

    # seed/size
    seed: Optional[int] = None
    width: int = 512
    height: int = 640

    # hires fix
    enable_hr: bool = True
    denoising_strength: float = 0.35
    hr_scale: float = 2.0
    hr_upscaler: str = "8xNMKDSuperscale_150000G"
    hr_second_pass_steps: int = 10
    hr_sampler_name: Optional[str] = None  # omit if None

    # Forge expects a list, not None
    hr_additional_modules: Optional[List[str]] = ["Use same choices"]

    # build a clean A1111/Forge payload
    def to_sd_payload(self) -> dict:
        p = {
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "steps": self.steps,
            "sampler_name": self.sampler_name,
            "cfg_scale": self.cfg_scale,
            "seed": self.seed if self.seed is not None else -1,
            "width": self.width,
            "height": self.height,
            "send_images": True,
            "save_images": False,
        }
        if self.enable_hr:
            p.update({
                "enable_hr": True,
                "denoising_strength": self.denoising_strength,
                "hr_scale": self.hr_scale,
                "hr_upscaler": self.hr_upscaler,
                "hr_second_pass_steps": self.hr_second_pass_steps,
                # IMPORTANT: always send a list here for Forge
                "hr_additional_modules": self.hr_additional_modules or ["Use same choices"],
            })
            if self.hr_sampler_name:
                p["hr_sampler_name"] = self.hr_sampler_name  # only include if set
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
