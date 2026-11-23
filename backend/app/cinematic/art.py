"""Модуль генерации кинематографичного арта (100% бесплатно).

Генерирует высокодетализированные 9:16 (1080x1920) кадры в стиле тёмного реализма
(35mm film still, Kodak Vision3, туман, низкоугловой свет, кинематографичные тени)
без платных API-ключей с дисковым кэшированием и оффлайн-фоллбеком.
"""
import hashlib
import os
import random
import time
import urllib.parse
from pathlib import Path
from typing import Optional

import httpx

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = WORKSPACE_ROOT / "work" / "art_cache"
OFFLINE_FALLBACK_DIR = WORKSPACE_ROOT / "backend" / "assets" / "ai_horror"

CINEMATIC_PREFIX = (
    "35mm film still, cinematic dark realism, atmospheric mystery thriller, "
    "volumetric fog, Kodak Vision3 500T, deep shadows, "
    "subtle rim lighting, realistic film grain, masterwork, 8k photorealistic: "
)

CINEMATIC_SUFFIX = (
    ", sharp focus, award winning cinematography, "
    "no cartoon, no anime, no 3D render, no drawing, no oversaturation, no bright neon, no watermark"
)


def _get_cache_path(prompt: str, seed: int) -> Path:
    """Генерирует детерминированный путь к кэшированному изображению."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = f"{prompt}_{seed}".encode("utf-8")
    hash_str = hashlib.sha256(key).hexdigest()[:16]
    return CACHE_DIR / f"art_{hash_str}.jpg"


def _get_offline_fallback() -> Path:
    """Возвращает один из существующих качественных оффлайн-ассетов при сбое сети."""
    candidates = []
    if OFFLINE_FALLBACK_DIR.exists():
        candidates.extend(list(OFFLINE_FALLBACK_DIR.glob("*.jpg")) + list(OFFLINE_FALLBACK_DIR.glob("*.png")))
    
    for root_img in ["kyiv_alert_scene.jpg", "kyiv_shelter_scene.jpg"]:
        p = WORKSPACE_ROOT / root_img
        if p.exists():
            candidates.append(p)

    if candidates:
        return random.choice(candidates)
    raise FileNotFoundError("Нет доступных фоллбек-изображений.")


def generate_cinematic_image(
    prompt: str,
    out_path: Optional[Path] = None,
    seed: Optional[int] = None,
    width: int = 576,
    height: int = 1024,
    timeout: float = 30.0,
    upscale_4k: bool = False,
) -> Path:
    """Генерирует вертикальный кинематографичный кадр через бесплатный Pollinations API.
    
    Если изображение уже было сгенерировано для этого промпта, берёт из кэша.
    При сетевых сбоях/лимитах переключается на встроенный оффлайн-банк кадров.
    При upscale_4k=True увеличивает разрешение до 4K через Real-ESRGAN.
    """
    if seed is None:
        seed = random.randint(1000, 9999999)

    full_prompt = f"{CINEMATIC_PREFIX}{prompt.strip()}{CINEMATIC_SUFFIX}"
    cache_path = _get_cache_path(full_prompt, seed)

    if cache_path.exists() and cache_path.stat().st_size > 5000:
        if out_path:
            out_path = Path(out_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(cache_path.read_bytes())
            target = out_path
        else:
            target = cache_path
        if upscale_4k:
            from backend.app.cinematic.upscaler import upscale_image_4k
            target = upscale_image_4k(target, out_path=out_path, scale=4)
        return target

    encoded_prompt = urllib.parse.quote(full_prompt)
    client_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }

    # Варианты бесплатных запросов к Pollinations
    urls_to_try = [
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}",
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=turbo&nologo=true",
    ]

    for url in urls_to_try:
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True, headers=client_headers) as client:
                resp = client.get(url)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    cache_path.write_bytes(resp.content)
                    target = out_path if out_path else cache_path
                    target = Path(target)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(resp.content)
                    if upscale_4k:
                        from backend.app.cinematic.upscaler import upscale_image_4k
                        target = upscale_image_4k(target, out_path=out_path, scale=4)
                    return target
        except Exception:
            continue

    # Если API недоступно или выдало лимит, переключаемся на оффлайн банк
    fallback_src = _get_offline_fallback()
    target = out_path if out_path else cache_path
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(fallback_src.read_bytes())
    if upscale_4k:
        from backend.app.cinematic.upscaler import upscale_image_4k
        target = upscale_image_4k(target, out_path=out_path, scale=4)
    return target


if __name__ == "__main__":
    test_dir = WORKSPACE_ROOT / "output" / "test_art"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_out = test_dir / "test_shot_2.jpg"

    test_prompt = "vintage car dashboard night radio dial glowing in dark forest"
    res = generate_cinematic_image(test_prompt, out_path=test_out, seed=123)
    print(f"Готово: {res} ({res.stat().st_size // 1024} KB)")
