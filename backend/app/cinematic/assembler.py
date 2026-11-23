"""Модуль финального монтажа кинематографичного видео (100% бесплатно через FFmpeg).

Объединяет все компоненты в единый готовый шедевр:
1. Синхронизирует кадры со словами диктора с точностью до миллисекунды
2. Анимирует каждый кадр через 2.5D камеру (push_in, pan, tilt) с плёночным зерном 35mm
3. Накладывает звуковые эффекты (SFX: удар, сердцебиение, райзер, вуш) точно на смены сцен
4. Подмешивает атмосферный низкочастотный кинематографичный саундтрек-эмбиент
5. Вжигает динамичные вирусные караоке-субтитры с золотой подсветкой через libass
"""
import json
import math
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.app.cinematic.art import generate_cinematic_image
from backend.app.cinematic.motion import animate_cinematic_shot
from backend.app.cinematic.portrait import animate_character_portrait
from backend.app.cinematic.sfx import ensure_sfx_library, get_scene_sfx_events
from backend.app.cinematic.story import CinematicStory, CURATED_STORIES
from backend.app.cinematic.subtitles import generate_cinematic_ass
from backend.app.cinematic.voice import generate_cinematic_voice

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
SFX_DIR = WORKSPACE_ROOT / "backend" / "assets" / "sfx"


def _generate_ambient_drone(duration: float, out_path: Path) -> Path:
    """Генерирует глубокий кинематографичный суб-басовый эмбиент без авторских прав."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    expr = (
        "0.20*sin(46*2*PI*t) + 0.12*sin(69*2*PI*t) + "
        "0.05*sin(138*2*PI*t) + 0.02*sin(276*2*PI*t)*(1+0.35*sin(0.3*2*PI*t))"
    )
    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "lavfi",
        "-i", f"aevalsrc=exprs='{expr}':s=44100",
        "-af", "lowpass=f=320,volume=-16dB",
        "-t", f"{duration:.3f}",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path


def _calculate_scene_timings(
    story: CinematicStory,
    words: List[Dict],
    total_voice_duration: float,
) -> List[Tuple[float, float]]:
    """Вычисляет точные интервалы (start, duration) для каждой сцены на основе таймкодов слов."""
    num_scenes = len(story.scenes)
    if not words or num_scenes == 0:
        equal_dur = total_voice_duration / max(1, num_scenes)
        return [(i * equal_dur, equal_dur) for i in range(num_scenes)]

    # Ищем стартовые таймкоды для каждой сцены по совпадению первого слова
    starts = [0.0]
    word_idx = 0

    for s_idx in range(1, num_scenes):
        scene_first_word = story.scenes[s_idx].text_ru.split()[0].lower().strip(".,!?:;\"'«»")
        found_time = None
        for w_i in range(word_idx, len(words)):
            w_clean = words[w_i]["word"].lower().strip(".,!?:;\"'«»")
            if w_clean.startswith(scene_first_word[:3]):  # сопоставление по корню
                found_time = words[w_i]["start"]
                word_idx = w_i + 1
                break
        if found_time is not None and found_time > starts[-1]:
            starts.append(found_time)
        else:
            # Если не нашли, интерполируем равномерно
            approx = starts[-1] + (total_voice_duration - starts[-1]) / (num_scenes - s_idx + 1)
            starts.append(round(approx, 2))

    # Вычисляем длительность каждого плана (последнему даём буфер на клиффхэнгер)
    timings = []
    for i in range(num_scenes):
        s_start = starts[i]
        if i < num_scenes - 1:
            s_dur = max(1.5, starts[i + 1] - s_start)
        else:
            s_dur = max(2.0, (total_voice_duration - s_start) + 0.8)
        timings.append((s_start, s_dur))

    return timings


def _mix_master_soundtrack(
    voice_mp3: Path,
    drone_mp3: Path,
    sfx_events: List[Tuple[float, str]],  # [(timestamp, sfx_name)]
    total_duration: float,
    out_mixed_audio: Path,
) -> Path:
    """Сводит голос, фоновый эмбиент и звуковые эффекты в единый дорожный микс."""
    inputs = [
        "-i", str(voice_mp3),
        "-i", str(drone_mp3),
    ]

    filter_chains = [
        "[0:a]volume=1.0[voice]",
        "[1:a]volume=0.45[drone]",
    ]
    mix_labels = ["[voice]", "[drone]"]

    sfx_input_idx = 2
    for event in sfx_events:
        if len(event) == 3:
            ts_sec, sfx_name, vol = event
        else:
            ts_sec, sfx_name = event
            vol = 0.70
        sfx_file = SFX_DIR / f"{sfx_name}.wav"
        if not sfx_file.exists():
            sfx_file = SFX_DIR / "whoosh.wav"
        if sfx_file.exists():
            inputs.extend(["-i", str(sfx_file)])
            delay_ms = max(0, int(ts_sec * 1000))
            label = f"[sfx_{sfx_input_idx}]"
            filter_chains.append(f"[{sfx_input_idx}:a]adelay={delay_ms}|{delay_ms},volume={vol:.2f}{label}")
            mix_labels.append(label)
            sfx_input_idx += 1

    total_inputs = len(mix_labels)
    filter_chains.append(
        f"{''.join(mix_labels)}amix=inputs={total_inputs}:duration=first:dropout_transition=2[aout]"
    )

    full_filter = ";".join(filter_chains)
    cmd = [
        FFMPEG_BIN, "-y",
        *inputs,
        "-filter_complex", full_filter,
        "-map", "[aout]",
        "-t", f"{total_duration:.3f}",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(out_mixed_audio),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_mixed_audio


def assemble_cinematic_video(
    story: CinematicStory,
    out_dir: Path,
    out_filename: str = "master_cinematic.mp4",
    upscale_4k: bool = False,
) -> Path:
    """Полный цикл создания кинематографичного видеоролика:
    
    1. Синтез голоса + таймкоды
    2. Генерация арта через Flux
    3. Анимация 2.5D движения камеры
    4. Склейка видеоряда
    5. Саунд-дизайн и мастеринг
    6. Вжигание караоке-субтитров
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = out_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=======================================================")
    print(f"🎬 ЗАПУСК КИНЕМАТОГРАФИЧНОГО ПАЙПЛАЙНА: {story.title}")
    print(f"=======================================================")

    # Гарантируем наличие процедурной библиотеки SFX
    ensure_sfx_library()

    # 1. Синтез голоса и пословных таймкодов
    print("[1/5] Озвучка диктора + извлечение пословных таймкодов...")
    full_text = story.full_voiceover_text
    voice_mp3, words, total_voice_dur = generate_cinematic_voice(
        text=full_text,
        out_dir=temp_dir,
    )
    print(f"      Готово: {voice_mp3.name} ({total_voice_dur:.2f} сек, {len(words)} слов)")

    # 2. Расчёт таймингов сцен
    timings = _calculate_scene_timings(story, words, total_voice_dur)
    total_video_dur = timings[-1][0] + timings[-1][1]
    sfx_events = get_scene_sfx_events(story.scenes, timings)

    # 3. Генерация арта и анимация планов
    print(f"[2/5] Генерация 35mm арта и 2.5D движений камеры ({len(story.scenes)} сцен)...")
    clip_paths = []

    for idx, (scene, (s_start, s_dur)) in enumerate(zip(story.scenes, timings), start=1):
        print(f"      План {idx}: {scene.camera_move} ({s_dur:.2f}с) | Промпт: {scene.art_prompt[:45]}...")
        
        # Арт
        art_img = temp_dir / f"art_scene_{idx}.jpg"
        is_char = getattr(scene, "is_character", False)
        generate_cinematic_image(
            prompt=scene.art_prompt,
            out_path=art_img,
            seed=100 + idx * 7,
            upscale_4k=upscale_4k and not is_char,
        )

        # Анимация: либо LivePortrait персонаж, либо 2.5D камера
        clip_mp4 = temp_dir / f"clip_scene_{idx}.mp4"
        if getattr(scene, "is_character", False):
            preset = getattr(scene, "portrait_preset", "talking")
            print(f"      🎭 Оживление лица персонажа через LivePortrait [{preset}]...")
            animate_character_portrait(
                image_path=art_img,
                duration=s_dur,
                preset=preset,
                out_path=clip_mp4,
            )
        else:
            animate_cinematic_shot(
                image_path=art_img,
                duration=s_dur,
                camera_move=scene.camera_move,
                out_path=clip_mp4,
            )
        clip_paths.append(clip_mp4)

    # 4. Склейка видеоряда
    print("[3/5] Монтаж видеоряда...")
    concat_list_file = temp_dir / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve().as_posix()}'\n")

    merged_video = temp_dir / "merged_video.mp4"
    cmd_concat = [
        FFMPEG_BIN, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(merged_video),
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. Саундтрек и саунд-дизайн
    print("[4/5] Саунд-дизайн: подмешивание низкого эмбиента и SFX...")
    drone_mp3 = temp_dir / "ambient_drone.mp3"
    _generate_ambient_drone(total_video_dur, drone_mp3)

    master_audio = temp_dir / "master_soundtrack.mp3"
    _mix_master_soundtrack(
        voice_mp3=voice_mp3,
        drone_mp3=drone_mp3,
        sfx_events=sfx_events,
        total_duration=total_video_dur,
        out_mixed_audio=master_audio,
    )

    # 6. Субтитры и финальный экспорт
    print("[5/5] Вжигание караоке-субтитров и финализация...")
    subtitles_ass = temp_dir / "subtitles.ass"
    generate_cinematic_ass(words, subtitles_ass)

    final_mp4 = out_dir / out_filename
    # Для фильтра subtitles в FFmpeg на Windows путь форматируется без конфликтов
    escaped_ass_path = subtitles_ass.resolve().as_posix().replace(":", r"\:")
    sub_filter = f"subtitles='{escaped_ass_path}'"

    cmd_final = [
        FFMPEG_BIN, "-y",
        "-i", str(merged_video),
        "-i", str(master_audio),
        "-vf", sub_filter,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(final_mp4),
    ]
    res = subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg ошибка финального рендера: {res.stderr}")

    file_size_mb = final_mp4.stat().st_size / (1024 * 1024)
    print(f"\n✅ ГОТОВО! Мастер-видео создано:")
    print(f"   Файл: {final_mp4}")
    print(f"   Размер: {file_size_mb:.2f} MB")
    print(f"   Длительность: {total_video_dur:.2f} сек")
    print(f"=======================================================\n")

    return final_mp4


if __name__ == "__main__":
    test_story = CURATED_STORIES[0]  # "Случай на ночной трассе"
    out_dir = WORKSPACE_ROOT / "output" / "cinematic_master"
    assemble_cinematic_video(test_story, out_dir=out_dir)

