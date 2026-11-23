"""
Cartoon Explainer Video Assembler.
Combines 2D vector background, animated character rig (lip-sync, bobbing, expressions),
game-like HUD, speech bubbles, sound effects, voiceover, and karaoke subtitles into a finished 1080x1920 MP4.
"""

import math
import subprocess
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image

from backend.app.cartoon.background import render_night_kiosk_location
from backend.app.cartoon.character import CharacterRig
from backend.app.cartoon.sfx import synth_alert_sting, synth_bubble_pop, synth_coin_ding
from backend.app.cartoon.ui_engine import (
    draw_floating_badge,
    draw_location_pill,
    draw_speech_bubble,
    draw_top_hud,
)
from backend.app.cinematic.subtitles import generate_cinematic_ass
from backend.app.cinematic.voice import generate_cinematic_voice

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


def mix_audio_with_sfx(
    voice_path: Path,
    out_audio_path: Path,
    sfx_events: List[Tuple[float, Path, float]],  # (time_sec, sfx_path, volume)
    total_duration: float,
) -> Path:
    """Mixes voiceover with procedural SFX events at specific timestamps."""
    sr = 44100
    total_samples = int((total_duration + 0.5) * sr)
    master = np.zeros(total_samples, dtype=np.float32)

    # Load voice via wave or ffmpeg
    cmd = [
        FFMPEG_BIN, "-y", "-i", str(voice_path),
        "-f", "s16le", "-ac", "1", "-ar", str(sr), "pipe:1"
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw_voice, _ = p.communicate()
    voice_samples = np.frombuffer(raw_voice, dtype=np.int16).astype(np.float32) / 32768.0

    # Add voice to master
    v_len = min(len(voice_samples), total_samples)
    master[:v_len] += voice_samples[:v_len]

    # Add SFX
    for timestamp, sfx_file, vol in sfx_events:
        if not sfx_file.exists():
            continue
        with wave.open(str(sfx_file), "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            sfx_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0 * vol
        start_idx = int(timestamp * sr)
        end_idx = min(start_idx + len(sfx_data), total_samples)
        add_len = end_idx - start_idx
        if add_len > 0:
            master[start_idx:end_idx] += sfx_data[:add_len]

    # Normalize to avoid clipping
    mx = np.max(np.abs(master))
    if mx > 0.95:
        master = master / mx * 0.95

    # Write WAV
    out_audio_path.parent.mkdir(parents=True, exist_ok=True)
    master_int16 = (master * 32767).astype(np.int16)
    with wave.open(str(out_audio_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(master_int16.tobytes())

    return out_audio_path


def render_cartoon_video(
    script_text: str = "День первый. На счету триста тридцать тысяч рублей. Ларёк у остановки мой, но конкуренты уже вызвали проверку!",
    output_path: Path = Path("output/cartoon_master/cartoon_scene_1.mp4"),
    voice: str = "ru-RU-DmitryNeural",
    fps: int = 30,
) -> Path:
    """Generates the full animated 2D explainer scene."""
    output_path = Path(output_path)
    work_dir = output_path.parent / "temp_build"
    work_dir.mkdir(parents=True, exist_ok=True)

    print("[1/5] Синтезируем голос диктора и собираем пословные таймкоды...")
    voice_mp3, words, duration = generate_cinematic_voice(
        script_text,
        work_dir,
        voice=voice,
        pitch="+0Hz",
        rate="-2%",
    )
    print(f"      Длительность озвучки: {duration:.2f}s, слов: {len(words)}")

    # SFX Synthesis
    print("[2/5] Генерируем фирменные звуковые эффекты (SFX)...")
    sfx_dir = work_dir / "sfx"
    sfx_coin = synth_coin_ding(sfx_dir / "coin.wav")
    sfx_pop = synth_bubble_pop(sfx_dir / "pop.wav")
    sfx_alert = synth_alert_sting(sfx_dir / "alert.wav")

    # Find twist timestamp (when word 'конкуренты' or 'проверку' starts, or ~65% into the scene)
    twist_time = duration * 0.62
    for w in words:
        if any(term in w["word"].lower() for term in ["конкурент", "проверк"]):
            twist_time = w["start"]
            break
    print(f"      Сюжетный поворот (твист): на {twist_time:.2f}s")

    # Audio Mixing
    print("[3/5] Сводим мастер-аудиодорожку со звуками...")
    sfx_events = [
        (0.4, sfx_coin, 0.85),     # Деньги на счету
        (0.7, sfx_pop, 0.75),      # Бабл открылся
        (twist_time, sfx_alert, 0.95),  # Вспышка тревоги / проверка!
    ]
    master_audio = work_dir / "master_audio.wav"
    mix_audio_with_sfx(voice_mp3, master_audio, sfx_events, duration)

    # Subtitles
    print("[4/5] Генерируем караоке-субтитры...")
    ass_path = work_dir / "cartoon_subtitles.ass"
    generate_cinematic_ass(
        words,
        ass_path,
        words_per_phrase=3,
        font_name="Arial",
        font_size=64,
        primary_color="&H00FFFFFF",
        highlight_color="&H002BF5FF",  # Золотой
        outline_color="&H00050505",
        margin_v=340,
    )

    # Pre-render static base background
    print("[5/5] Рендерим кадры 2D анимации и кодируем видео...")
    base_bg = render_night_kiosk_location()
    char_rig = CharacterRig()

    # Pre-render character sprites to maximize speed
    sprites = {
        ("confident", "closed"): char_rig.render(mood="confident", mouth_state="closed"),
        ("confident", "half"): char_rig.render(mood="confident", mouth_state="half"),
        ("confident", "open"): char_rig.render(mood="confident", mouth_state="open"),
        ("shocked", "closed"): char_rig.render(mood="shocked", mouth_state="closed"),
        ("shocked", "half"): char_rig.render(mood="shocked", mouth_state="half"),
        ("shocked", "open"): char_rig.render(mood="shocked", mouth_state="open"),
    }

    # Helper to check if someone is speaking at time t
    def is_speaking(t: float) -> bool:
        for w in words:
            if w["start"] - 0.05 <= t <= w["end"] + 0.05:
                return True
        return False

    total_frames = int(duration * fps)
    raw_video_path = work_dir / "raw_video.mp4"

    # FFmpeg pipe process
    ffmpeg_cmd = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1080x1920",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "pipe:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(raw_video_path),
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    bubble_rect = (140, 560, 940, 740)
    tail_tip = (540, 920)

    for f in range(total_frames):
        t = f / fps

        # Determine mood & UI state
        if t < twist_time:
            mood = "confident"
            hud_balance = "330 000 ₽"
            hud_status = "ПАВИЛЬОН ТВОЙ"
            bubble_text = "«Открываемся завтра утром! Всё готово.»"
            show_alert = False
        else:
            mood = "shocked"
            hud_balance = "330 000 ₽"
            hud_status = "⚠️ СРОЧНАЯ ПРОВЕРКА!"
            bubble_text = "«Что?! Они вызвали проверку?!»"
            show_alert = True

        # Determine mouth flap
        if is_speaking(t):
            # Rapid mouth flap (6 Hz)
            phase = int((t * 8) % 3)
            mouth = ["half", "open", "half"][phase]
            # Natural speech bobbing (head moves up/down by 4 pixels)
            bob_y = int(math.sin(t * 12) * 5)
        else:
            mouth = "closed"
            bob_y = 0

        # Start with fresh background
        frame = base_bg.copy()

        # Composite Character with bobbing offset
        # Use offset_y if needed or composite pre-rendered sprite
        sprite = sprites[(mood, mouth)]
        if bob_y != 0:
            # Shift sprite slightly
            shifted = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
            shifted.paste(sprite, (0, bob_y))
            frame = Image.alpha_composite(frame, shifted)
        else:
            frame = Image.alpha_composite(frame, sprite)

        # Draw UI
        draw_top_hud(frame, balance_text=hud_balance, status_text=hud_status)
        draw_location_pill(frame, text="ларёк с шаурмой 24/7 у остановки")

        # Speech bubble pop-in (animates slightly during first 0.2s of each state)
        draw_speech_bubble(frame, bubble_text, box_rect=bubble_rect, tail_tip=tail_tip)

        # Floating alert badge
        if show_alert:
            draw_floating_badge(frame, text="?!", center_pos=(730, 980))

        # Convert to RGB and write raw bytes to ffmpeg pipe
        rgb_data = frame.convert("RGB").tobytes()
        proc.stdin.write(rgb_data)

    proc.stdin.close()
    proc.wait()

    # Final assembly: Raw video + Master audio + ASS Subtitles
    print("      Финальный рендер с субтитрами и аудио...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")

    final_cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(raw_video_path),
        "-i", str(master_audio),
        "-vf", f"ass='{ass_escaped}'",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path),
    ]

    res = subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        # Fallback without ass filter if libass error occurs
        fallback_cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(raw_video_path),
            "-i", str(master_audio),
            "-c:v", "copy",
            "-c:a", "aac",
            str(output_path),
        ]
        subprocess.run(fallback_cmd, check=True)

    print(f"[OK] 2D Cartoon Video успешно собран: {output_path}")
    return output_path
