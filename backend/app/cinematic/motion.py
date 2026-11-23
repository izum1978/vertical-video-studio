"""Модуль 2.5D кинематографичного движения камеры (100% бесплатно через FFmpeg).

Оживляет статичные кадры 9:16 (1080x1920) движениями камеры:
- push_in (наезд на объект)
- pull_out (отъезд, раскрытие масштаба)
- pan_left / pan_right (горизонтальный пролёт)
- tilt_up / tilt_down (вертикальное панорамирование)
- handheld_drift (органичное дыхание камеры)

Добавляет аналоговое плёночное зерно (35mm film grain), виньетку и кинематографичный цветокор.
"""
import math
import subprocess
from pathlib import Path
from typing import Optional

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


def build_camera_filter(
    camera_move: str,
    duration: float,
    fps: int = 30,
    width: int = 1080,
    height: int = 1920,
) -> str:
    """Генерирует FFmpeg filtergraph для заданного движения камеры."""
    total_frames = max(1, int(duration * fps))

    # Базовое масштабирование с запасом для панорам
    pre_scale = f"scale={int(width * 1.25)}:{int(height * 1.25)}"

    if camera_move == "push_in":
        # Плавный наезд от 1.0 до 1.18
        zoom_step = 0.18 / total_frames
        zoom_expr = f"min(pzoom+{zoom_step:.6f},1.18)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
        zp = f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s={width}x{height}:fps={fps}"

    elif camera_move == "pull_out":
        # Отъезд от 1.18 до 1.01
        zoom_step = 0.17 / total_frames
        zoom_expr = f"max(1.18-on*{zoom_step:.6f},1.01)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
        zp = f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s={width}x{height}:fps={fps}"

    elif camera_move == "pan_right":
        # Пролёт слева направо при zoom=1.15
        zp = (
            f"zoompan=z='1.15':x='(on/{total_frames})*(iw-iw/zoom)':"
            f"y='ih/2-(ih/zoom/2)':d={total_frames}:s={width}x{height}:fps={fps}"
        )

    elif camera_move == "pan_left":
        # Пролёт справа налево при zoom=1.15
        zp = (
            f"zoompan=z='1.15':x='(1-(on/{total_frames}))*(iw-iw/zoom)':"
            f"y='ih/2-(ih/zoom/2)':d={total_frames}:s={width}x{height}:fps={fps}"
        )

    elif camera_move == "tilt_up":
        # Панорама снизу вверх (раскрытие высоты)
        zp = (
            f"zoompan=z='1.15':x='iw/2-(iw/zoom/2)':"
            f"y='(1-(on/{total_frames}))*(ih-ih/zoom)':d={total_frames}:s={width}x{height}:fps={fps}"
        )

    elif camera_move == "tilt_down":
        # Панорама сверху вниз (спуск в темноту)
        zp = (
            f"zoompan=z='1.15':x='iw/2-(iw/zoom/2)':"
            f"y='(on/{total_frames})*(ih-ih/zoom)':d={total_frames}:s={width}x{height}:fps={fps}"
        )

    else:  # handheld_drift / default
        # Тонкое органичное покачивание камеры
        zp = (
            f"zoompan=z='1.08+0.03*sin(on/25)':"
            f"x='(iw/2-(iw/zoom/2))+sin(on/18)*18':"
            f"y='(ih/2-(ih/zoom/2))+cos(on/22)*18':"
            f"d={total_frames}:s={width}x{height}:fps={fps}"
        )

    # Кинематографичный грейдинг: плёночное зерно (живой кадр), виньетка, контраст теней
    post_fx = (
        "noise=alls=8:allf=t+u,"
        "vignette=PI/4,"
        "eq=contrast=1.12:saturation=1.04:brightness=-0.01"
    )

    return f"{pre_scale},{zp},{post_fx}"


def animate_cinematic_shot(
    image_path: Path,
    duration: float,
    camera_move: str = "push_in",
    out_path: Optional[Path] = None,
    fps: int = 30,
    width: int = 1080,
    height: int = 1920,
) -> Path:
    """Оживляет статичное изображение в кинематографичный MP4-видеоролик заданной длительности."""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Файл изображения не найден: {image_path}")

    if out_path is None:
        out_path = image_path.with_suffix(".mp4")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    filter_graph = build_camera_filter(
        camera_move=camera_move,
        duration=duration,
        fps=fps,
        width=width,
        height=height,
    )

    cmd = [
        FFMPEG_BIN, "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-vf", filter_graph,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(out_path),
    ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg ошибка при анимации кадра: {res.stderr}")

    return out_path


if __name__ == "__main__":
    test_img = Path("output/test_art/test_shot_1.jpg")
    if test_img.exists():
        print("Тестирование движений камеры...")
        for move in ["push_in", "pan_right", "handheld_drift"]:
            out = Path(f"output/test_art/motion_{move}.mp4")
            print(f"-> Анимация {move} (2.5 сек)...")
            animate_cinematic_shot(test_img, duration=2.5, camera_move=move, out_path=out)
            print(f"   Готово: {out} ({out.stat().st_size // 1024} KB)")

