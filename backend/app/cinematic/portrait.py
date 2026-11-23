"""Модуль оживления лиц и персонажей через LivePortrait (100% бесплатно и локально).

Превращает статичные портреты персонажей в живых говорящих героев:
- Натуральные движения глаз, моргание
- Микромимика и дыхание
- Артикуляция губ при речи
- Кинематографичное кадрирование 9:16 (1080x1920) с плёночным зерном и цветокором
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
LIVEPORTRAIT_DIR = WORKSPACE_ROOT / "backend" / "app" / "cinematic" / "liveportrait"
CACHE_DIR = WORKSPACE_ROOT / "work" / "portrait_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"

PYTHON_BIN = sys.executable

PRESETS = {
    "talking": LIVEPORTRAIT_DIR / "assets" / "examples" / "driving" / "d8.pkl",
    "reaction": LIVEPORTRAIT_DIR / "assets" / "examples" / "driving" / "d11.mp4",
    "subtle": LIVEPORTRAIT_DIR / "assets" / "examples" / "driving" / "d2.pkl",
}


def _get_cache_key(image_path: Path, preset: str, duration: float, framing: str) -> str:
    h = hashlib.md5()
    h.update(str(image_path.resolve()).encode("utf-8"))
    if image_path.exists():
        h.update(str(image_path.stat().st_mtime).encode("utf-8"))
    h.update(f"{preset}_{duration:.2f}_{framing}".encode("utf-8"))
    return h.hexdigest()[:16]


def animate_character_portrait(
    image_path: Path,
    duration: float,
    preset: str = "talking",
    out_path: Optional[Path] = None,
    fps: int = 30,
    width: int = 1080,
    height: int = 1920,
    framing: str = "close_up",
) -> Path:
    """Анимирует статичный портрет персонажа через LivePortrait и форматирует в 9:16.
    
    Args:
        image_path: Путь к исходному фото/арту персонажа
        duration: Требуемая длительность в секундах
        preset: 'talking' (живая речь), 'reaction' (реакция), 'subtle' (микромимика)
        out_path: Выходной файл
        fps: Частота кадров (по умолчанию 30)
        width: Ширина кадра (1080)
        height: Высота кадра (1920)
        framing: 'close_up' (кинематографичный крупный план) или 'ambient_blur' (размытый фон)
    """
    image_path = Path(image_path).resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Файл портрета не найден: {image_path}")

    if out_path is None:
        out_path = CACHE_DIR / f"portrait_{image_path.stem}_{preset}_{duration:.1f}s.mp4"
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cache_key = _get_cache_key(image_path, preset, duration, framing)
    cached_final = CACHE_DIR / f"lp_{cache_key}.mp4"
    if cached_final.exists() and cached_final.stat().st_size > 1024:
        # Копируем или возвращаем кэш
        if cached_final != out_path:
            import shutil
            shutil.copy2(cached_final, out_path)
        return out_path

    # Выбор файла движений
    dri_path = PRESETS.get(preset, PRESETS["talking"])
    if not dri_path.exists():
        # Fallback to d2.pkl if d8.pkl is missing
        dri_path = LIVEPORTRAIT_DIR / "assets" / "examples" / "driving" / "d2.pkl"

    # Оптимизация скорости: генерируем до 45 выразительных кадров,
    # а FFmpeg бесшовно зацикливает их на точную длительность сцены (-stream_loop -1)
    total_frames = min(max(15, int(duration * 20)), 45)

    raw_out = CACHE_DIR / f"raw_{cache_key}.mp4"

    # Запуск LivePortrait runner
    cmd = [
        PYTHON_BIN, "run.py",
        "--src_image", str(image_path),
        "--dri_video", str(dri_path),
        "--cfg", "configs/onnx_infer.yaml",
        "--paste_back",
        "--max_frames", str(total_frames),
        "--output_path", str(raw_out),
    ]

    env = os.environ.copy()
    ffmpeg_dir = str(Path(FFMPEG_BIN).parent)
    env["PATH"] = f"{ffmpeg_dir};{env.get('PATH', '')}"

    res = subprocess.run(
        cmd,
        cwd=str(LIVEPORTRAIT_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if res.returncode != 0 or not raw_out.exists():
        # Если LivePortrait не распознал лицо или возникла ошибка, делаем элегантный fallback
        # на кинематографичное 2.5D дыхание камеры handheld_drift
        print(f"⚠️ LivePortrait fallback на 2.5D движение для {image_path.name}: {res.stderr[-200:] if res.stderr else 'unknown'}")
        from backend.app.cinematic.motion import animate_cinematic_shot
        return animate_cinematic_shot(
            image_path=image_path,
            duration=duration,
            camera_move="handheld_drift",
            out_path=out_path,
            fps=fps,
            width=width,
            height=height,
        )

    # Постобработка FFmpeg: вертикальное кадрирование 9:16 + плёночное зерно 35mm + виньетка
    if framing == "ambient_blur":
        vf = (
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},boxblur=25:5[bg];"
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,"
            f"noise=alls=8:allf=t+u,vignette=PI/4,eq=contrast=1.12:saturation=1.04:brightness=-0.01"
        )
    else:  # close_up
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"noise=alls=8:allf=t+u,vignette=PI/4,eq=contrast=1.12:saturation=1.04:brightness=-0.01"
        )

    cmd_post = [
        FFMPEG_BIN, "-y",
        "-stream_loop", "-1",
        "-i", str(raw_out),
        "-vf", vf,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(cached_final),
    ]

    res_post = subprocess.run(cmd_post, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res_post.returncode != 0:
        raise RuntimeError(f"FFmpeg ошибка при кадрировании портрета: {res_post.stderr}")

    if cached_final != out_path:
        import shutil
        shutil.copy2(cached_final, out_path)

    return out_path
