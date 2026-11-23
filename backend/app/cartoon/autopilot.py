"""
Autopilot Engine v2: Multi-Location, High-Motion Viral 2D Explainer Generator.
Upgrades:
- True Multi-Location Storytelling: every chapter switches to a unique 2D location
  (Bank Vault -> Dealership -> Red Crash Report -> Rainy Bus Stop, etc.)
- Crisp Whip-Pan horizontal transitions + Whoosh SFX between every scene
- Kinetic Character Motion: spring pop-up entrances, natural eye blinking, expressive
  tilt/sway while speaking, lip-sync mouth flaps, and hand gestures/props
- Animated Particles & Visual FX: falling cash banknotes, slanted rain, flashing police
  sirens, anime shock speedlines, and slamming red rubber stamps ("ТОТАЛ!", "ОТКАЗАНО!")
- Continuous Camera Motion: smooth Ken Burns zoom drift in every scene + shock camera shake
- Exact Sentence-Synced Chapter Timing (never out of sync with Silero voiceover!)
"""

import math
import subprocess
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image

from backend.app.cartoon.background import (
    render_bank_vault_location,
    render_crash_report_location,
    render_dealership_location,
    render_night_kiosk_location,
    render_office_location,
    render_rainy_bus_stop_location,
)
from backend.app.cartoon.camera import CameraController
from backend.app.cartoon.character import CharacterRig
from backend.app.cartoon.crypto_scene import (
    render_trader_room,
    synth_coin_ding,
    synth_drip_drop,
    synth_liquidation_boom,
    synth_phone_vibrate,
)
from backend.app.cartoon.effects import (
    apply_whip_transition,
    draw_animated_stamp,
    draw_impact_speedlines,
    draw_money_rain,
    draw_rain,
    draw_siren_flash,
    ease_out_back,
)
from backend.app.cartoon.f5_voice import is_f5_available, synthesize_f5_script
from backend.app.cartoon.sfx import synth_whoosh
from backend.app.cartoon.silero_voice import synthesize_silero_script
from backend.app.cartoon.ui_engine import (
    draw_floating_badge,
    draw_location_pill,
    draw_speech_bubble,
    draw_top_hud,
)
from backend.app.cinematic.subtitles import generate_cinematic_ass

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


# ---------------------------------------------------------------------------
# 1. MULTI-LOCATION SCENE RENDERER REGISTRY
# ---------------------------------------------------------------------------

def get_location_image(loc_name: str) -> Image.Image:
    """Returns 1080x1920 2D vector background for the requested scene location."""
    if loc_name == "bank_vault":
        return render_bank_vault_location()
    elif loc_name == "dealership":
        return render_dealership_location(is_scam=False)
    elif loc_name == "dealership_scam":
        return render_dealership_location(is_scam=True)
    elif loc_name == "crash_report":
        return render_crash_report_location()
    elif loc_name == "rainy_bus_stop":
        return render_rainy_bus_stop_location()
    elif loc_name == "office":
        return render_office_location(is_climax=False)
    elif loc_name == "office_climax":
        return render_office_location(is_climax=True)
    elif loc_name == "trader_green":
        return render_trader_room(stage="green")
    elif loc_name == "trader_crash":
        return render_trader_room(stage="crash")
    else:
        return render_night_kiosk_location()


# ---------------------------------------------------------------------------
# 2. MULTI-LOCATION SCRIPTWRITER & DIRECTOR
# ---------------------------------------------------------------------------

def plan_story_for_topic(topic: str) -> Dict:
    """Creates a high-retention 4-location story plan tailored to the topic."""
    t_lower = topic.lower()

    if any(k in t_lower for k in ["авто", "машин", "дилер", "перекуп", "бмв", "мерс"]):
        return {
            "title": "Как меня кинул автодилер",
            "outfit": "casual",
            "outfit_color": (37, 99, 235),  # Royal blue hoodie
            "hair_style": "undercut",
            "chapters": [
                {
                    "location": "bank_vault",
                    "sentences": [
                        "Я копил пять лет и наконец собрал почти два миллиона рублей.",
                        "Мечта вот-вот сбудется!",
                    ],
                    "mood": "smug",
                    "gesture": "holding_money",
                    "hud_balance": "1 850 000 ₽",
                    "hud_status": "ЦЕЛЬ: МАШИНА МЕЧТЫ",
                    "loc_pill": "БАНКОВСКАЯ ЯЧЕЙКА • 5 ЛЕТ ТРУДА",
                    "bubble": "«Наконец-то забираю свою ласточку!»",
                    "sfx": "coin",
                    "effect": "money",
                    "zoom_start": 1.00,
                    "zoom_end": 1.07,
                    "shake": False,
                    "entrance": "up",
                },
                {
                    "location": "dealership",
                    "sentences": [
                        "Пришёл в элитный автосалон. Менеджер клялся, что на ней ездил дедушка в аптеку.",
                        "Отдаю деньги, и тут внезапно звонит знакомый автоподборщик!",
                    ],
                    "mood": "alert",
                    "gesture": "holding_phone",
                    "hud_balance": "0 ₽ (ОПЛАЧЕНО)",
                    "hud_status": "СРОЧНЫЙ ЗВОНОК!",
                    "hud_theme": "alert",
                    "loc_pill": "АВТОСАЛОН ПРЕМИУМ • 14:15",
                    "bubble": "«Алло, брат, стой! Не подписывай!»",
                    "sfx": "phone",
                    "effect": None,
                    "zoom_start": 1.02,
                    "zoom_end": 1.10,
                    "shake": False,
                    "entrance": "right",
                },
                {
                    "location": "crash_report",
                    "sentences": [
                        "Он пробил вин-номер, а там... Тотальное ДТП и скручено двести тысяч пробега!",
                        "Машина буквально сварена из двух разных половин!",
                    ],
                    "mood": "shocked",
                    "gesture": "hands_on_head",
                    "hud_balance": "-1 850 000 ₽",
                    "hud_status": "ТОТАЛЬНЫЙ РАСПИЛ!",
                    "hud_theme": "danger",
                    "loc_pill": "ОТЧЁТ ПО VIN: КРИТИЧЕСКИЙ ТОТАЛ",
                    "bubble": "«ЭТО ЖЕ РАСПИЛ ИЗ ДВУХ ЧАСТЕЙ?!»",
                    "sfx": "boom",
                    "effect": "sirens_impact",
                    "stamp": "ТОТАЛ!",
                    "zoom_start": 1.16,
                    "zoom_end": 1.22,
                    "shake": True,
                    "entrance": "up",
                },
                {
                    "location": "rainy_bus_stop",
                    "sentences": [
                        "Менеджер тут же испарился, а телефон заблокирован.",
                        "Теперь я жду сорок второй автобус под дождём. Проверяйте тачки до покупки!",
                    ],
                    "mood": "devastated",
                    "gesture": "relax",
                    "hud_balance": "42 ₽ НА ПРОЕЗД",
                    "hud_status": "ПРОВЕРЯЙ VIN!",
                    "hud_theme": "muted",
                    "loc_pill": "ОСТАНОВКА • 22:40 • ДОЖДЬ",
                    "bubble": "«Зато пешком ходить полезно...»",
                    "sfx": "drip",
                    "effect": "rain",
                    "zoom_start": 1.05,
                    "zoom_end": 1.00,
                    "shake": False,
                    "entrance": "left",
                },
            ],
        }

    elif any(k in t_lower for k in ["зарплат", "начальник", "повышен", "босс", "офис", "работ"]):
        return {
            "title": "Парень пришёл просить прибавку к зарплате",
            "outfit": "suit",
            "outfit_color": (30, 41, 59),
            "hair_style": "undercut",
            "chapters": [
                {
                    "location": "bank_vault",
                    "sentences": [
                        "Я отпахал три года без отпуска и перевыполнил план на двести процентов.",
                        "Сегодня иду к боссу за заслуженной прибавкой!",
                    ],
                    "mood": "smug",
                    "gesture": "holding_money",
                    "hud_balance": "ОКЛАД: 60 000 ₽",
                    "hud_status": "ЦЕЛЬ: +50 000 ₽",
                    "loc_pill": "МЕЧТЫ О ПРЕМИИ • 16:00",
                    "bubble": "«Я точно заслужил эту прибавку!»",
                    "sfx": "coin",
                    "effect": "money",
                    "zoom_start": 1.00,
                    "zoom_end": 1.07,
                    "shake": False,
                    "entrance": "up",
                },
                {
                    "location": "office",
                    "sentences": [
                        "Захожу в кабинет. Босс долго смотрит в мой отчёт и тяжело вздыхает.",
                    ],
                    "mood": "alert",
                    "gesture": "pointing",
                    "hud_balance": "ОЖИДАНИЕ...",
                    "hud_status": "⚠️ ПЕРЕГОВОРЫ",
                    "loc_pill": "КАБИНЕТ ГЕНЕРАЛЬНОГО • 16:30",
                    "bubble": "«В компании сейчас непростые времена...»",
                    "sfx": "phone",
                    "effect": None,
                    "zoom_start": 1.02,
                    "zoom_end": 1.10,
                    "shake": False,
                    "entrance": "right",
                },
                {
                    "location": "office_climax",
                    "sentences": [
                        "И выдаёт: прибавки не будет! С завтрашнего дня режем бонусы на тридцать процентов!",
                        "И вешаем на тебя отдел уволенного коллеги!",
                    ],
                    "mood": "shocked",
                    "gesture": "hands_on_head",
                    "hud_balance": "ОКЛАД: 42 000 ₽",
                    "hud_status": "💀 НАГРУЗКА: x3",
                    "loc_pill": "РЕЗУЛЬТАТ ПЕРЕГОВОРОВ: -30%",
                    "bubble": "«В СМЫСЛЕ УРЕЗАЕТЕ?! Я ЖЕ ЗА ПРИБАВКОЙ ПРИШЁЛ!»",
                    "sfx": "boom",
                    "effect": "sirens_impact",
                    "stamp": "ОТКАЗАНО!",
                    "zoom_start": 1.16,
                    "zoom_end": 1.22,
                    "shake": True,
                    "entrance": "up",
                },
                {
                    "location": "rainy_bus_stop",
                    "sentences": [
                        "Вышел с тройной нагрузкой и меньшей зарплатой. Пора обновлять резюме.",
                        "Не бойтесь уходить с токсичной работы!",
                    ],
                    "mood": "devastated",
                    "gesture": "relax",
                    "hud_balance": "HH.RU: ОБНОВЛЕНО",
                    "hud_status": "📉 ИЩУ НОВУЮ РАБОТУ",
                    "loc_pill": "ОСТАНОВКА • ВЕЧЕР • ДОЖДЬ",
                    "bubble": "«Кто-нибудь нанимает толковых ребят?..»",
                    "sfx": "drip",
                    "effect": "rain",
                    "zoom_start": 1.05,
                    "zoom_end": 1.00,
                    "shake": False,
                    "entrance": "left",
                },
            ],
        }

    else:
        topic_clean = topic.replace('"', '').strip()
        return {
            "title": topic_clean,
            "outfit": "hoodie",
            "outfit_color": (249, 115, 22),
            "hair_style": "messy",
            "chapters": [
                {
                    "location": "bank_vault",
                    "sentences": [
                        f"История про {topic_clean}.",
                        "Всё начиналось идеально, и я был уверен в стопроцентном успехе.",
                    ],
                    "mood": "smug",
                    "gesture": "holding_money",
                    "hud_balance": "СТАРТ: 1 000 000 ₽",
                    "hud_status": "УВЕРЕННЫЙ СТАРТ",
                    "loc_pill": f"ТЕМА: {topic_clean.upper()[:26]}",
                    "bubble": "«Всё под контролем, сейчас взлетим!»",
                    "sfx": "coin",
                    "effect": "money",
                    "zoom_start": 1.00,
                    "zoom_end": 1.07,
                    "shake": False,
                    "entrance": "up",
                },
                {
                    "location": "office",
                    "sentences": [
                        "Но в самый ответственный момент раздался звонок, и всё пошло не по плану.",
                    ],
                    "mood": "alert",
                    "gesture": "holding_phone",
                    "hud_balance": "ВНИМАНИЕ...",
                    "hud_status": "⚠️ НЕОЖИДАННЫЙ ПОВОРОТ",
                    "loc_pill": "ТРЕВОЖНЫЙ СИГНАЛ",
                    "bubble": "«Подождите... Что это значит?!»",
                    "sfx": "phone",
                    "effect": None,
                    "zoom_start": 1.02,
                    "zoom_end": 1.10,
                    "shake": False,
                    "entrance": "right",
                },
                {
                    "location": "office_climax",
                    "sentences": [
                        "Внезапный форс-мажор перечеркнул все планы за пару секунд!",
                        "Это был полный и сокрушительный провал!",
                    ],
                    "mood": "shocked",
                    "gesture": "hands_on_head",
                    "hud_balance": "БАЛАНС: 0 ₽",
                    "hud_status": "💀 ПОЛНЫЙ ПРОВАЛ",
                    "loc_pill": "ЭПИЧНЫЙ ФАКАП",
                    "bubble": "«КАК ТАКОЕ ВООБЩЕ МОГЛО ПРОИЗОЙТИ?!»",
                    "sfx": "boom",
                    "effect": "sirens_impact",
                    "stamp": "ПРОВАЛ!",
                    "zoom_start": 1.16,
                    "zoom_end": 1.22,
                    "shake": True,
                    "entrance": "up",
                },
                {
                    "location": "rainy_bus_stop",
                    "sentences": [
                        "Вот так за секунды рушатся грандиозные планы.",
                        "Учитесь на чужих ошибках и ставьте лайк, если было полезно!",
                    ],
                    "mood": "devastated",
                    "gesture": "relax",
                    "hud_balance": "ОПЫТ: +1000",
                    "hud_status": "📉 ГЛАВНЫЙ ВЫВОД",
                    "loc_pill": "МОРАЛЬ: БУДЬ НАЧЕКУ",
                    "bubble": "«Зато теперь есть отличная история...»",
                    "sfx": "drip",
                    "effect": "rain",
                    "zoom_start": 1.05,
                    "zoom_end": 1.00,
                    "shake": False,
                    "entrance": "left",
                },
            ],
        }


# ---------------------------------------------------------------------------
# 3. SINGLE-SCENE FRAME COMPOSITOR HELPER
# ---------------------------------------------------------------------------

def _compose_chapter_frame(
    ch: Dict,
    base_bg: Image.Image,
    sprites: Dict,
    camera: CameraController,
    t: float,
    t_local: float,
    ch_dur: float,
    speaking: bool,
) -> Image.Image:
    """Renders one complete animated frame for a given chapter at local time t_local."""
    frame = base_bg.copy()

    # 1. Background/ambient effects that sit behind or around character
    effect = ch.get("effect")
    if effect == "money":
        frame = draw_money_rain(frame, t)

    # 2. Lip-sync + natural eye blinking
    # Blink naturally every ~2.7s for 0.13s (except when shocked wide-eyed)
    m = ch["mood"]
    g = ch["gesture"]
    is_blinking = (m != "shocked") and ((t % 2.75) > 2.62)

    if speaking:
        phase = int((t * 9.0) % 3)
        mouth = ["half", "open", "half"][phase]
        # Expressive cartoon bounce & body sway while talking!
        bob_y = int(math.sin(t * 14.0) * 11)
        sway_angle = math.sin(t * 7.0) * 3.2
    else:
        mouth = "closed"
        # Gentle idle breathing
        bob_y = int(math.sin(t * 3.0) * 4)
        sway_angle = math.sin(t * 2.0) * 0.8

    sprite = sprites[(m, g, mouth, is_blinking)]

    # 3. Springy Character Entrance animation (first 0.38s of each chapter)
    ent_dx, ent_dy = 0, 0
    if t_local < 0.38:
        prog = ease_out_back(t_local / 0.38)
        ent_mode = ch.get("entrance", "up")
        if ent_mode == "up":
            ent_dy = int((1.0 - prog) * 420)
        elif ent_mode == "right":
            ent_dx = int((1.0 - prog) * 460)
        elif ent_mode == "left":
            ent_dx = int((prog - 1.0) * 460)

    # Rotate character slightly around torso pivot (center-bottom) for fluid puppet motion
    if abs(sway_angle) > 0.2:
        char_layer = sprite.rotate(sway_angle, resample=Image.Resampling.BILINEAR, center=(540, 1650))
    else:
        char_layer = sprite

    # Paste character with bounce & entrance offset
    char_canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    char_canvas.paste(char_layer, (ent_dx, bob_y + ent_dy))
    frame = Image.alpha_composite(frame, char_canvas)

    # 4. Foreground Atmospheric Effects (Rain, Sirens, Speedlines)
    if effect == "rain":
        frame = draw_rain(frame, t)
    elif effect == "sirens_impact":
        frame = draw_siren_flash(frame, t)
        frame = draw_impact_speedlines(frame, t)

    # 5. Camera Choreography (Continuous Ken Burns Zoom Drift + Shock Shake)
    ch_prog = max(0.0, min(1.0, t_local / max(0.1, ch_dur)))
    z_start = ch.get("zoom_start", 1.0)
    z_end = ch.get("zoom_end", 1.06)
    cur_zoom = z_start + (z_end - z_start) * ch_prog

    shake = 0.0
    if ch.get("shake", False) and 0.0 <= t_local <= 0.65:
        shake = (1.0 - t_local / 0.65) ** 1.4

    # Apply camera zoom/shake to world + character BEFORE static HUD overlays
    # (so the top HUD stays crisp and readable while the world shakes and zooms!)
    frame = camera.apply(
        frame,
        zoom=cur_zoom,
        focal_point=(540, 1120),
        shake_intensity=shake,
        t=t,
    )

    # 6. Slamming Red Rubber Stamp (if present for climax)
    if ch.get("stamp"):
        frame = draw_animated_stamp(frame, ch["stamp"], t_local - 0.15, center=(540, 450))

    # 7. Crisp UI Overlays (HUD + Location Pill + Springy Speech Bubble + Alert Badge)
    hud_theme = ch.get("hud_theme")
    if not hud_theme:
        hud_theme = "danger" if m == "shocked" else ("alert" if m == "alert" else ("muted" if m == "devastated" else "green"))
    clean_status = ch["hud_status"].replace("⚠️ ", "").replace("💀 ", "").replace("📉 ", "")
    draw_top_hud(frame, balance_text=ch["hud_balance"], status_text=clean_status, theme=hud_theme)
    draw_location_pill(frame, text=ch["loc_pill"])

    # Animated speech bubble pop-in (drops in smoothly after 0.12s)
    if t_local >= 0.10:
        b_prog = min(1.0, (t_local - 0.10) / 0.22)
        b_ease = ease_out_back(b_prog)
        b_y_shift = int((1.0 - b_ease) * -90)
        bubble_rect = (140, 560 + b_y_shift, 940, 740 + b_y_shift)
        tail_tip = (540, 920 + b_y_shift)
        draw_speech_bubble(frame, ch["bubble"], box_rect=bubble_rect, tail_tip=tail_tip)

    if m == "shocked":
        badge_bob = int(math.sin(t * 20.0) * 8)
        draw_floating_badge(frame, text="?!", center_pos=(750, 970 + badge_bob), badge_color=(239, 68, 68))
    elif m == "alert":
        badge_bob = int(math.sin(t * 12.0) * 6)
        draw_floating_badge(frame, text="!", center_pos=(750, 970 + badge_bob), badge_color=(251, 146, 60))

    return frame


# ---------------------------------------------------------------------------
# 4. MASTER AUTOPILOT VIDEO ASSEMBLER
# ---------------------------------------------------------------------------

def render_autopilot_video(
    topic: str,
    output_path: Path,
    speaker: str = "eugene",
    fps: int = 30,
) -> Path:
    """Generates a multi-location, high-motion animated video for any topic."""
    output_path = Path(output_path)
    work_dir = output_path.parent / "temp_autopilot"
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[AUTOPILOT v2] 1. Планируем 4-локационный сценарий: '{topic}'...")
    plan = plan_story_for_topic(topic)
    chapters = plan["chapters"]

    # Collect sentences and count words per chapter for EXACT chapter timestamps!
    all_sentences = []
    chapter_word_counts = []
    for ch in chapters:
        w_cnt = 0
        for s in ch["sentences"]:
            all_sentences.append(s)
            clean_s = s.replace(".", "").replace("!", "").replace("?", "").replace(",", "")
            w_cnt += len(clean_s.split())
        chapter_word_counts.append(w_cnt)

    print(f"[AUTOPILOT v2] 2. Синтезируем голос диктора ({speaker})...")
    voice_wav = work_dir / f"voice_{speaker}.wav"
    if speaker in ("f5", "f5tts", "clone") and is_f5_available():
        voice_file, words, duration = synthesize_f5_script(
            all_sentences,
            out_wav=voice_wav,
            speed=1.06,
        )
    else:
        voice_file, words, duration = synthesize_silero_script(
            all_sentences,
            speaker=speaker if speaker not in ("f5", "f5tts", "clone") else "eugene",
            out_wav=voice_wav,
        )
    print(f"               Длительность: {duration:.2f}s, слов: {len(words)}")

    # Compute exact start timestamp for each chapter from the synthesized word timestamps!
    ch_starts = [0.0]
    word_cursor = 0
    for i in range(len(chapters) - 1):
        word_cursor += chapter_word_counts[i]
        if word_cursor < len(words):
            ch_starts.append(max(ch_starts[-1] + 1.0, words[word_cursor]["start"] - 0.12))
        else:
            ch_starts.append((i + 1) * (duration / len(chapters)))
    ch_ends = ch_starts[1:] + [duration]
    print(f"               Смена локаций на: {[round(x, 2) for x in ch_starts]} сек")

    print("[AUTOPILOT v2] 3. Генерируем звуковые эффекты (монеты, звонок, взрыв, whoosh)...")
    sfx_dir = work_dir / "sfx"
    sfx_map = {
        "coin": synth_coin_ding(sfx_dir / "coin.wav"),
        "phone": synth_phone_vibrate(sfx_dir / "phone.wav"),
        "boom": synth_liquidation_boom(sfx_dir / "boom.wav"),
        "drip": synth_drip_drop(sfx_dir / "drip.wav"),
        "whoosh": synth_whoosh(sfx_dir / "whoosh.wav"),
    }

    sfx_events = []
    for i, ch in enumerate(chapters):
        # Add crisp whoosh sound on every location transition (chapters 1, 2, 3)
        if i > 0:
            sfx_events.append((max(0.0, ch_starts[i] - 0.10), sfx_map["whoosh"], 0.72))
        sfx_type = ch.get("sfx")
        if sfx_type in sfx_map:
            vol = 0.95 if sfx_type == "boom" else 0.80
            sfx_events.append((ch_starts[i] + 0.18, sfx_map[sfx_type], vol))

    # Mix master audio
    master_audio = work_dir / "master_audio.wav"
    sr = 44100
    total_samples = int((duration + 0.5) * sr)
    master = np.zeros(total_samples, dtype=np.float32)

    cmd = [FFMPEG_BIN, "-y", "-i", str(voice_file), "-f", "s16le", "-ac", "1", "-ar", str(sr), "pipe:1"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw_voice, _ = p.communicate()
    voice_samples = np.frombuffer(raw_voice, dtype=np.int16).astype(np.float32) / 32768.0
    v_len = min(len(voice_samples), total_samples)
    master[:v_len] += voice_samples[:v_len]

    for ts, sfx_f, vol in sfx_events:
        if sfx_f.exists():
            with wave.open(str(sfx_f), "rb") as wf:
                data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0 * vol
            s_idx = int(ts * sr)
            e_idx = min(s_idx + len(data), total_samples)
            if e_idx > s_idx:
                master[s_idx:e_idx] += data[:(e_idx - s_idx)]

    mx = np.max(np.abs(master))
    if mx > 0.95:
        master = master / mx * 0.95
    m_int16 = (master * 32767).astype(np.int16)
    with wave.open(str(master_audio), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(m_int16.tobytes())

    print("[AUTOPILOT v2] 4. Генерируем караоке-субтитры...")
    ass_path = work_dir / "autopilot_subtitles.ass"
    generate_cinematic_ass(
        words,
        ass_path,
        words_per_phrase=3,
        font_name="Arial",
        font_size=66,
        primary_color="&H00FFFFFF",
        highlight_color="&H002BF5FF",
        outline_color="&H00050505",
        margin_v=340,
    )

    print("[AUTOPILOT v2] 5. Предрендер локаций и спрайтов (с морганием и жестами)...")
    bg_cache = {}
    for ch in chapters:
        loc = ch["location"]
        if loc not in bg_cache:
            bg_cache[loc] = get_location_image(loc)

    rig = CharacterRig()
    camera = CameraController()
    outfit = plan.get("outfit", "hoodie")
    outfit_color = plan.get("outfit_color", (249, 115, 22))
    hair_style = plan.get("hair_style", "messy")

    sprites = {}
    for ch in chapters:
        m = ch["mood"]
        g = ch["gesture"]
        for ms in ["closed", "half", "open"]:
            for blink in [False, True]:
                key = (m, g, ms, blink)
                if key not in sprites:
                    sprites[key] = rig.render(
                        mood=m,
                        mouth_state=ms,
                        gesture=g,
                        outfit=outfit,
                        outfit_color=outfit_color,
                        hair_style=hair_style,
                        blink=blink,
                    )

    def is_speaking(t: float) -> bool:
        for w in words:
            if w["start"] - 0.04 <= t <= w["end"] + 0.04:
                return True
        return False

    print("[AUTOPILOT v2] 6. Рендерим динамичную анимацию, переходы и частицы...")
    total_frames = int(duration * fps)
    raw_video = work_dir / "raw_autopilot.mp4"

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
        str(raw_video),
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    TRANSITION_DUR = 0.24  # crisp 0.24s whip-pan slide between locations

    for f in range(total_frames):
        t = f / fps

        # Determine active chapter index
        ch_idx = 0
        for i in range(len(chapters)):
            if t >= ch_starts[i]:
                ch_idx = i

        cur_ch = chapters[ch_idx]
        t_local = t - ch_starts[ch_idx]
        ch_dur = ch_ends[ch_idx] - ch_starts[ch_idx]
        speaking = is_speaking(t)

        cur_frame = _compose_chapter_frame(
            cur_ch, bg_cache[cur_ch["location"]], sprites, camera, t, t_local, ch_dur, speaking
        )

        # Apply whip-pan slide transition during the first 0.24s of chapters 1, 2, 3
        if ch_idx > 0 and t_local < TRANSITION_DUR:
            prev_ch = chapters[ch_idx - 1]
            prev_dur = ch_ends[ch_idx - 1] - ch_starts[ch_idx - 1]
            prev_frame = _compose_chapter_frame(
                prev_ch, bg_cache[prev_ch["location"]], sprites, camera, t, prev_dur, prev_dur, False
            )
            frame = apply_whip_transition(prev_frame, cur_frame, t_local / TRANSITION_DUR)
        else:
            frame = cur_frame

        proc.stdin.write(frame.convert("RGB").tobytes())

    proc.stdin.close()
    proc.wait()

    print("[AUTOPILOT v2] 7. Финальная сборка MP4 со звуком и субтитрами...")
    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(raw_video),
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
        fallback_cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(raw_video),
            "-i", str(master_audio),
            "-c:v", "copy",
            "-c:a", "aac",
            str(output_path),
        ]
        subprocess.run(fallback_cmd, check=True)

    print(f"[OK] Динамичный 4-локационный ролик готов: {output_path}")
    return output_path
