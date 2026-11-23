"""
Локальный сервис быстрой генерации изображений на базе SDXL-Lightning / SD-Turbo.
Запускается на GPU (NVIDIA RTX 4050 6GB) в режиме FP16 с CPU offload / xformers / sliced attention.
"""
import io
import os
import time
import torch
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from PIL import Image

pipe = None
MODEL_TYPE = os.getenv("AI_MODEL_TYPE", "sd_turbo")  # "sd_turbo" или "sdxl_lightning"


def load_pipeline():
    global pipe
    if pipe is not None:
        return pipe

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    print(f"[AI-ENGINE] Загрузка модели {MODEL_TYPE} на {device} ({dtype})...")
    
    if MODEL_TYPE == "sd_turbo":
        from diffusers import AutoPipelineForText2Image
        pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sd-turbo",
            torch_dtype=dtype,
            variant="fp16" if device == "cuda" else None,
        )
    elif MODEL_TYPE == "sdxl_lightning":
        from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
        from huggingface_hub import hf_hub_download
        base = "stabilityai/stable-diffusion-xl-base-1.0"
        repo = "ByteDance/SDXL-Lightning"
        ckpt = "sdxl_lightning_4step_unet.safetensors"
        
        unet = UNet2DConditionModel.from_config(base, subfolder="unet").to(device, dtype)
        unet.load_state_dict(torch.load(hf_hub_download(repo, ckpt), map_location=device))
        pipe = StableDiffusionXLPipeline.from_pretrained(base, unet=unet, torch_dtype=dtype, variant="fp16")
        pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")

    if device == "cuda":
        pipe = pipe.to("cuda")
        if hasattr(pipe, "enable_attention_slicing"):
            pipe.enable_attention_slicing()
        if hasattr(pipe, "enable_vae_slicing"):
            pipe.enable_vae_slicing()
        if hasattr(pipe, "enable_vae_tiling"):
            pipe.enable_vae_tiling()
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except Exception:
            pass

    print("[AI-ENGINE] Модель успешно загружена в память!")
    return pipe


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Фоновая ленивая загрузка
    try:
        load_pipeline()
    except Exception as e:
        print(f"[AI-ENGINE ВНИМАНИЕ] Не удалось предзагрузить модель: {e}")
    yield


app = FastAPI(title="Local AI Scene Generation Engine", lifespan=lifespan)


class GenerateRequest(BaseModel):
    prompt: str
    width: int = 512
    height: int = 912
    steps: int = 1
    guidance_scale: float = 0.0


class VideoGenerateRequest(BaseModel):
    prompt: str
    motion: str = "zoom_in"
    action_type: str = "cinematic"
    motion_bucket: int = 140
    duration: float = 4.0
    fps: int = 60


@app.get("/health")
def health():
    cuda_ok = torch.cuda.is_available()
    vram_free = 0
    if cuda_ok:
        vram_free = torch.cuda.mem_get_info()[0] / (1024 ** 3)
    return {
        "status": "ready" if pipe is not None else "loading",
        "device": "cuda" if cuda_ok else "cpu",
        "vram_free_gb": round(vram_free, 2),
        "model": MODEL_TYPE,
        "capabilities": ["text2img", "video_diffusion", "motion_retiming"],
    }


@app.post("/generate_video")
def generate_video(req: VideoGenerateRequest):
    """Генерация полноценного динамического видеоролика 9:16 (60 FPS) по сценарию."""
    import tempfile
    from ai_engine.video_engine import VideoGenerationEngine

    t0 = time.time()
    try:
        eng = VideoGenerationEngine()
        temp_out = Path(tempfile.mktemp(suffix=".mp4"))
        eng.generate_scene_video(
            prompt=req.prompt,
            motion=req.motion,
            action_type=req.action_type,
            duration=req.duration,
            out_path=temp_out,
            motion_bucket=req.motion_bucket,
        )
        if not temp_out.exists() or temp_out.stat().st_size < 1000:
            raise HTTPException(500, "Видеофайл не был создан")
        data = temp_out.read_bytes()
        try:
            temp_out.unlink()
        except Exception:
            pass
        print(f"[AI-ENGINE] Видео {len(data)} байт отдано за {time.time() - t0:.2f} сек.")
        return Response(content=data, media_type="video/mp4")
    except Exception as e:
        print(f"[AI-ENGINE ERROR] {e}")
        raise HTTPException(500, f"Ошибка генерации видео: {e}")


@app.post("/generate")
def generate(req: GenerateRequest):
    p = load_pipeline()
    if p is None:
        raise HTTPException(500, "Пайплайн модели не инициализирован")

    t0 = time.time()
    try:
        # Для SD-Turbo шаг 1 и guidance_scale 0.0 дают чистый результат за 0.3 секунды
        steps = req.steps if MODEL_TYPE != "sd_turbo" else 1
        guidance = req.guidance_scale if MODEL_TYPE != "sd_turbo" else 0.0
        
        # Разрешение для вертикального формата 9:16
        w = req.width
        h = req.height
        
        # Выравнивание до кратности 8
        w = (w // 8) * 8
        h = (h // 8) * 8

        with torch.inference_mode():
            res = p(
                prompt=req.prompt,
                width=w,
                height=h,
                num_inference_steps=steps,
                guidance_scale=guidance,
            )
            image: Image.Image = res.images[0]

        # Масштабируем до эталонного 1080x1920
        if image.size != (1080, 1920):
            image = image.resize((1080, 1920), Image.Resampling.LANCZOS)

        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=95)
        dt = time.time() - t0
        print(f"[AI-ENGINE] Кадр 1080x1920 сгенерирован за {dt:.2f} сек. Промпт: {req.prompt[:60]}...")
        return Response(content=buf.getvalue(), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(500, f"Ошибка инференса: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8189)
