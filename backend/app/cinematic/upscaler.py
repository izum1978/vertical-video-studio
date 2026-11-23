"""Модуль локального нейросетевого апскейлинга и денойзинга артов до 4K (Real-ESRGAN).

Использует нативную Vulkan-модель Real-ESRGAN x4plus с аппаратным ускорением
на видеокарте NVIDIA GeForce RTX 4050 / Vulkan GPU:
- Увеличение разрешения в 4 раза (до 2304x4096 / 4K UHD)
- Удаление JPEG-артефактов и пикселизации
- Сверхчёткие микротекстуры (кожа, туман, металл, листва, свет)
- Мгновенная скорость работы (~2 секунды на кадр)
- 100% бесплатно, оффлайн, без сторонних API
"""
import hashlib
import os
import subprocess
from pathlib import Path
from typing import Optional

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
REALESRGAN_DIR = WORKSPACE_ROOT / "backend" / "app" / "cinematic" / "realesrgan"
REALESRGAN_BIN = REALESRGAN_DIR / "realesrgan-ncnn-vulkan.exe"

CACHE_DIR = WORKSPACE_ROOT / "work" / "upscale_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


def _get_cache_key(image_path: Path, scale: int, model_name: str) -> str:
    h = hashlib.md5()
    h.update(str(image_path.resolve()).encode("utf-8"))
    if image_path.exists():
        h.update(str(image_path.stat().st_mtime).encode("utf-8"))
        h.update(str(image_path.stat().st_size).encode("utf-8"))
    h.update(f"{scale}_{model_name}".encode("utf-8"))
    return h.hexdigest()[:16]


def upscale_image_4k(
    image_path: Path,
    out_path: Optional[Path] = None,
    scale: int = 4,
    model_name: str = "realesrgan-x4plus",
    gpu_id: int = 1,
) -> Path:
    """Апскейлит изображение через Real-ESRGAN x4plus на GPU до разрешения 4K.
    
    Args:
        image_path: Путь к исходному изображению
        out_path: Путь для сохранения 4K результата
        scale: Коэффициент увеличения (2 или 4)
        model_name: 'realesrgan-x4plus' (фотореализм) или 'realesrgan-x4plus-anime'
        gpu_id: Индекс GPU (1 для дискретной NVIDIA RTX, 0 для встроенной)
    
    Returns:
        Path к сохранённому 4K изображению
    """
    image_path = Path(image_path).resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Файл для апскейла не найден: {image_path}")

    cache_key = _get_cache_key(image_path, scale, model_name)
    cached_file = CACHE_DIR / f"upscale_{cache_key}.jpg"

    if out_path is None:
        out_path = image_path.parent / f"{image_path.stem}_4k.jpg"
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Проверка дискового кэша
    if cached_file.exists() and cached_file.stat().st_size > 5000:
        if cached_file != out_path:
            import shutil
            shutil.copy2(cached_file, out_path)
        return out_path

    # Проверка наличия бинарника Real-ESRGAN
    if not REALESRGAN_BIN.exists():
        print(f"⚠️ Real-ESRGAN бинарник не найден по пути {REALESRGAN_BIN}, используется FFmpeg Lanczos...")
        return _fallback_ffmpeg_upscale(image_path, out_path, scale)

    # Запуск нативного Vulkan апскейлера на RTX GPU
    cmd = [
        str(REALESRGAN_BIN),
        "-i", str(image_path),
        "-o", str(cached_file),
        "-n", model_name,
        "-s", str(scale),
        "-g", str(gpu_id),
    ]

    res = subprocess.run(
        cmd,
        cwd=str(REALESRGAN_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if res.returncode != 0 or not cached_file.exists() or cached_file.stat().st_size < 1000:
        # Fallback на GPU 0 или автоопределение
        cmd_auto = [
            str(REALESRGAN_BIN),
            "-i", str(image_path),
            "-o", str(cached_file),
            "-n", model_name,
            "-s", str(scale),
        ]
        res_auto = subprocess.run(
            cmd_auto,
            cwd=str(REALESRGAN_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if res_auto.returncode != 0 or not cached_file.exists():
            print(f"⚠️ Real-ESRGAN ошибка ({res_auto.stderr[-150:] if res_auto.stderr else 'unknown'}), fallback на FFmpeg...")
            return _fallback_ffmpeg_upscale(image_path, out_path, scale)

    if cached_file != out_path:
        import shutil
        shutil.copy2(cached_file, out_path)

    return out_path


def _fallback_ffmpeg_upscale(image_path: Path, out_path: Path, scale: int = 4) -> Path:
    """Запасной высококачественный апскейл через фильтр Lanczos в FFmpeg."""
    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(image_path),
        "-vf", f"scale=iw*{scale}:ih*{scale}:flags=lanczos,unsharp=5:5:0.8:3:3:0.4",
        "-q:v", "2",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path


if __name__ == "__main__":
    import time
    test_src = REALESRGAN_DIR / "input.jpg"
    if test_src.exists():
        t0 = time.time()
        res = upscale_image_4k(test_src, scale=4)
        print(f"Тестовый апскейл успешен: {res} ({time.time()-t0:.2f} сек, размер: {res.stat().st_size} байт)")
