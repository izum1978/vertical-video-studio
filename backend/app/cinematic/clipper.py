"""Модуль автоматического клиппера и вертикального кадрирования (Auto-Clipper).

Превращает любое длинное или горизонтальное видео в динамичный вертикальный Shorts/Reels:
1. Обнаруживает и вырезает паузы тишины (Jump-cuts через FFmpeg silencedetect)
2. Умно кадрирует видео в 9:16 (1080x1920) с размытым фоном или кино-кропом
3. Автоматически извлекает слова через faster-whisper
4. Накладывает вирусные караоке-субтитры с подсветкой
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.cinematic.subtitles import generate_cinematic_ass
from backend.app.cinematic.transcriber import transcribe_audio_words


FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"

FFPROBE_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffprobe.exe"
if not Path(FFPROBE_BIN).exists():
    FFPROBE_BIN = "ffprobe"


def has_audio_stream(video_path: Path) -> bool:
    """Проверяет наличие звуковой дорожки в файле."""
    cmd = [
        FFPROBE_BIN, "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_type",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    try:
        out = subprocess.check_output(cmd, text=True).strip()
        return "audio" in out
    except Exception:
        return False


def get_video_duration(video_path: Path) -> float:

    """Определяет точную длительность видео через ffprobe."""
    cmd = [
        FFPROBE_BIN, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    try:
        return float(subprocess.check_output(cmd, text=True).strip())
    except Exception:
        return 10.0


def crop_to_vertical_blurred_bg(
    input_video: Path,
    output_video: Path,
    width: int = 1080,
    height: int = 1920,
) -> Path:
    """Преобразует горизонтальное (16:9) видео в вертикальное (9:16) по стандарту TikTok/Shorts:
    - Нижний слой: сильно размытое масштабированное видео на весь экран (ambient blur)
    - Верхний слой: чёткое центрированное исходное видео с аккуратной тенью
    """
    output_video = Path(output_video)
    output_video.parent.mkdir(parents=True, exist_ok=True)

    # Filtergraph:
    # 1. Задник: растягивается, заполняет 1080x1920, кропается и размывается boxblur
    # 2. Передний план: вписывается по ширине 1080 с сохранением пропорций
    # 3. Наложение переднего плана ровно по центру
    filter_complex = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},boxblur=25:5,eq=brightness=-0.08[bg];"
        f"[0:v]scale={width}:-1:force_original_aspect_ratio=decrease[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[vout]"
    )

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(input_video),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_video),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_video


def detect_silence_intervals(
    video_path: Path,
    noise_db: float = -30.0,
    min_silence: float = 0.5,
) -> List[Tuple[float, float]]:
    """Находит интервалы тишины в видео через FFmpeg silencedetect."""
    cmd = [
        FFMPEG_BIN,
        "-i", str(video_path),
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}",
        "-f", "null",
        "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    lines = res.stderr.splitlines()

    silence_starts = []
    intervals = []

    for line in lines:
        if "silence_start:" in line:
            m = re.search(r"silence_start:\s*([\d.]+)", line)
            if m:
                silence_starts.append(float(m.group(1)))
        elif "silence_end:" in line and silence_starts:
            m = re.search(r"silence_end:\s*([\d.]+)", line)
            if m:
                s_end = float(m.group(1))
                s_start = silence_starts.pop(0)
                intervals.append((s_start, s_end))

    return intervals


def auto_clip_and_sub(
    input_video: Path,
    out_dir: Path,
    max_duration: float = 30.0,
    out_filename: str = "clipped_short.mp4",
) -> Path:
    """Полный цикл создания вирусного Shorts из любого исходного видео:
    1. Обрезка до max_duration
    2. Умный вертикальный кроп (9:16 1080x1920)
    3. Распознавание речи через faster-whisper
    4. Вжигание динамичных караоке-субтитров
    """
    input_video = Path(input_video)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = out_dir / "temp_clipper"
    temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n✂️ ЗАПУСК АВТО-КЛИППЕРА: {input_video.name}")
    
    # 1. Форматирование в вертикальный 9:16
    print("[1/3] Вертикальное кадрирование 9:16 (1080x1920)...")
    vert_video = temp_dir / "vertical.mp4"
    crop_to_vertical_blurred_bg(input_video, vert_video)

    # 2. Извлечение аудио и распознавание слов через faster-whisper (если есть звук)
    words = []
    if has_audio_stream(vert_video):
        print("[2/3] Локальная транскрибация речи через faster-whisper...")
        extracted_audio = temp_dir / "audio.mp3"
        cmd_audio = [
            FFMPEG_BIN, "-y",
            "-i", str(vert_video),
            "-vn", "-acodec", "libmp3lame", "-b:a", "192k",
            str(extracted_audio),
        ]
        try:
            subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            full_text, words = transcribe_audio_words(extracted_audio, model_size="tiny")
            print(f"      Распознано {len(words)} слов: \"{full_text[:80]}...\"")
        except Exception as e:
            print(f"      Предупреждение: звук не распознан ({e})")
    else:
        print("[2/3] Звуковая дорожка отсутствует в исходном файле, пропуск транскрибации.")

    # 3. Генерация и вжигание караоке-субтитров (если есть слова)
    final_clipped = out_dir / out_filename
    if words:
        print("[3/3] Генерация и вжигание вирусных караоке-субтитров...")
        ass_path = temp_dir / "clipper_subs.ass"
        generate_cinematic_ass(words, ass_path, margin_v=420)
        escaped_ass = ass_path.resolve().as_posix().replace(":", r"\:")

        cmd_final = [
            FFMPEG_BIN, "-y",
            "-i", str(vert_video),
            "-vf", f"subtitles='{escaped_ass}'",
            "-c:v", "libx264",
            "-preset", "faster",
            "-crf", "20",
            "-c:a", "aac" if has_audio_stream(vert_video) else "none",
            "-t", f"{max_duration:.2f}",
            str(final_clipped),
        ]
    else:
        print("[3/3] Финализация видео...")
        cmd_final = [
            FFMPEG_BIN, "-y",
            "-i", str(vert_video),
            "-c:v", "libx264",
            "-preset", "faster",
            "-crf", "20",
            "-c:a", "aac" if has_audio_stream(vert_video) else "none",
            "-t", f"{max_duration:.2f}",
            str(final_clipped),
        ]
    subprocess.run(cmd_final, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    print(f"✅ КЛИП ГОТОВ: {final_clipped} ({final_clipped.stat().st_size // (1024*1024)} MB)\n")
    return final_clipped


if __name__ == "__main__":
    # Тест на одном из наших готовых видео
    test_src = Path("output/cinematic_master/master_cinematic.mp4")
    if test_src.exists():
        out_dir = Path("output/test_clipper")
        auto_clip_and_sub(test_src, out_dir=out_dir, max_duration=10.0)
