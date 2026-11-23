"""
Part 2 of the Autodealer Mini-Series (v3 PRO Full-Body Multi-Character Engine):
"МЕСТЬ АВТОДИЛЕРУ: Как я вернул 1.85 миллиона и посадил перекупа"

Features 4 brand-new 2x-supersampled locations & 5 distinct characters:
1. Law Office — Hero + Stern Lawyer in glasses preparing lawsuit
2. Dealership Raid — Hidden camera REC ● overlay + Hero + Shady Manager + Police Officer entering!
3. Courtroom — Judge in black robe on wooden bench slamming gavel + Panicked Manager + Happy Hero + "ВИНОВЕН!" stamp!
4. Sunny Boulevard — Bright sunny street + Brand-new white sports car with red bow + Hero in sunglasses + passing police van!
Voiceover: Live F5-TTS Russian GPU voice cloning (exact same narrator as Part 1!).
"""

import json
import math
import subprocess
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.app.cartoon.camera import CameraController
from backend.app.cartoon.crypto_scene import (
    synth_coin_ding,
    synth_liquidation_boom,
    synth_phone_vibrate,
)
from backend.app.cartoon.effects import (
    apply_whip_transition,
    draw_animated_stamp,
    draw_money_rain,
    draw_siren_flash,
    ease_out_back,
)
from backend.app.cartoon.f5_voice import is_f5_available, synthesize_f5_script
from backend.app.cartoon.sfx import synth_whoosh
from backend.app.cartoon.silero_voice import synthesize_silero_script
from backend.app.cartoon.v3_engine import (
    FONT_BOLD,
    FONT_IMPACT,
    INK,
    _draw_car,
    _font,
    draw_compact_pill,
    draw_sleek_hud,
    draw_smart_bubble,
    render_full_body_character,
)
from backend.app.cinematic.subtitles import generate_cinematic_ass

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


# ---------------------------------------------------------------------------
# 1. EXTRA SPECIALIZED CHARACTERS (LAWYER, POLICE, JUDGE, HERO W/ SUNGLASSES)
# ---------------------------------------------------------------------------

def render_special_character(
    role: str,                      # hero_cool | lawyer | police | judge
    mood: str = "confident",
    mouth_state: str = "closed",
    gesture: str = "relax",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    scale: float = 0.94,
) -> Image.Image:
    """Renders specialized full-body characters with unique accessories (glasses, police cap, judge robe & gavel)."""
    if role == "hero_cool":
        base = render_full_body_character(
            outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
            mood="smug", mouth_state=mouth_state, gesture=gesture,
            blink=False, walk_phase=walk_phase, facing=facing, scale=1.0,
        )
        # Overlay cool dark sunglasses on head!
        d = ImageDraw.Draw(base, "RGBA")
        cx = base.width // 2
        ey = 186
        shift = 10 if facing == "right" else -10
        d.rounded_rectangle([(cx - 48 + shift, ey - 14), (cx - 4 + shift, ey + 14)], radius=6, fill=(15, 23, 42, 250), outline=INK, width=3)
        d.rounded_rectangle([(cx + 4 + shift, ey - 14), (cx + 48 + shift, ey + 14)], radius=6, fill=(15, 23, 42, 250), outline=INK, width=3)
        d.line([(cx - 4 + shift, ey - 4), (cx + 4 + shift, ey - 4)], fill=INK, width=4)
        # White specular shine on lenses
        d.line([(cx - 40 + shift, ey - 6), (cx - 26 + shift, ey + 6)], fill=(255, 255, 255, 190), width=3)
        d.line([(cx + 12 + shift, ey - 6), (cx + 26 + shift, ey + 6)], fill=(255, 255, 255, 190), width=3)
        return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)

    elif role == "lawyer":
        base = render_full_body_character(
            outfit="suit", hair_style="undercut",
            mood=mood, mouth_state=mouth_state, gesture=gesture,
            blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
        )
        # Draw smart rectangular eyeglasses!
        d = ImageDraw.Draw(base, "RGBA")
        cx = base.width // 2
        ey = 186
        shift = 10 if facing == "right" else -10
        d.rounded_rectangle([(cx - 46 + shift, ey - 13), (cx - 6 + shift, ey + 13)], radius=5, fill=(224, 242, 254, 70), outline=INK, width=4)
        d.rounded_rectangle([(cx + 6 + shift, ey - 13), (cx + 46 + shift, ey + 13)], radius=5, fill=(224, 242, 254, 70), outline=INK, width=4)
        d.line([(cx - 6 + shift, ey), (cx + 6 + shift, ey)], fill=INK, width=4)
        return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)

    elif role == "police":
        base = render_full_body_character(
            outfit="hoodie", outfit_color=(30, 58, 138), hair_style="undercut",
            mood="alert", mouth_state=mouth_state, gesture=gesture,
            blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
        )
        # Police Cap + Gold Star Badge on chest!
        d = ImageDraw.Draw(base, "RGBA")
        cx = base.width // 2
        # Visor cap on head
        d.rounded_rectangle([(cx - 66, 92), (cx + 66, 134)], radius=12, fill=(23, 37, 84, 255), outline=INK, width=4)
        d.rectangle([(cx - 72, 128), (cx + 72, 142)], fill=(15, 23, 42, 255), outline=INK, width=3)
        # Gold cap emblem
        d.ellipse([cx - 10, 102, cx + 10, 122], fill=(250, 204, 21, 255), outline=INK, width=2)
        # Gold chest badge
        d.ellipse([cx - 34, 294, cx - 10, 318], fill=(250, 204, 21, 255), outline=INK, width=2)
        return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)

    else:  # judge (black robe + white collar + gavel)
        base = render_full_body_character(
            outfit="hoodie", outfit_color=(24, 24, 30), hair_style="slicked",
            mood="confident", mouth_state=mouth_state, gesture="point_left",
            blink=blink, walk_phase=0.0, facing=facing, scale=1.0,
        )
        d = ImageDraw.Draw(base, "RGBA")
        cx = base.width // 2
        # White judge jabot collar
        d.polygon([(cx - 22, 266), (cx + 22, 266), (cx + 14, 326), (cx - 14, 326)], fill=(255, 255, 255, 255), outline=INK)
        # Wooden gavel in left raised hand!
        gx, gy = cx - 128, 280
        d.line([(gx, gy + 20), (gx - 28, gy - 32)], fill=(120, 53, 15, 255), width=8)
        d.rounded_rectangle([(gx - 56, gy - 54), (gx - 4, gy - 24)], radius=6, fill=(146, 64, 14, 255), outline=INK, width=3)
        return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 2. 4 BRAND-NEW 2x-SUPERSAMPLED EDITORIAL LOCATIONS FOR PART 2
# ---------------------------------------------------------------------------

def build_part2_backgrounds() -> Dict[str, Image.Image]:
    S = 2
    W, H = 1080 * S, 1920 * S
    bgs = {}

    # ------------------------------------------------------------------
    # LOC 1: LAWYER OFFICE (Warm Wood Bookshelves + Legal Desk)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (235, 229, 218, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1230 * S

    # Warm cream office wall
    d.rectangle([(0, 0), (W, floor_y)], fill=(238, 232, 220, 255))
    # Wooden wainscoting panel along lower wall
    d.rectangle([(0, 880 * S), (W, floor_y)], fill=(180, 145, 108, 255), outline=INK, width=4 * S)

    # Tall Wooden Bookshelf on Left-Center
    bx1, by1, bx2, by2 = 120 * S, 360 * S, 520 * S, 1100 * S
    d.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=12 * S, fill=(120, 72, 42, 255), outline=INK, width=5 * S)
    book_cols = [(185, 28, 28), (30, 64, 175), (22, 101, 52), (180, 83, 9), (71, 85, 105)]
    for shelf_i in range(4):
        sy = by1 + 40 * S + shelf_i * 170 * S
        d.rectangle([(bx1 + 16 * S, sy + 120 * S), (bx2 - 16 * S, sy + 140 * S)], fill=(92, 52, 28, 255), outline=INK, width=3 * S)
        # Books on shelf
        for bi in range(8):
            bkx = bx1 + 26 * S + bi * 44 * S
            bkh = (86 + (bi * 17 + shelf_i * 13) % 32) * S
            bcol = book_cols[(bi + shelf_i) % len(book_cols)]
            d.rectangle([(bkx, sy + 120 * S - bkh), (bkx + 36 * S, sy + 120 * S)], fill=(bcol[0], bcol[1], bcol[2], 255), outline=INK, width=3 * S)

    # Framed Legal Sign on Right Wall: "АДВОКАТ • ЗАКОН"
    d.rounded_rectangle([(580 * S, 390 * S), (960 * S, 540 * S)], radius=14 * S, fill=(30, 41, 59, 255), outline=(217, 119, 6, 255), width=6 * S)
    f_law = _font(FONT_BOLD, 38 * S)
    lt1 = "ЮРИСТ • АДВОКАТ"
    bb = f_law.getbbox(lt1)
    d.text((580 * S + (380 * S - (bb[2] - bb[0])) // 2, 420 * S), lt1, fill=(254, 240, 138, 255), font=f_law)
    f_law2 = _font(FONT_BOLD, 24 * S)
    lt2 = "ВОЗВРАТ ДЕНЕГ 100%"
    bb2 = f_law2.getbbox(lt2)
    d.text((580 * S + (380 * S - (bb2[2] - bb2[0])) // 2, 480 * S), lt2, fill=(226, 232, 240, 255), font=f_law2)

    # Parquet Floor
    d.rectangle([(0, floor_y), (W, H)], fill=(236, 232, 224, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)

    # Lawyer Desk in center-right with laptop & lawsuit folder
    d.rounded_rectangle([(430 * S, 1050 * S), (820 * S, floor_y)], radius=12 * S, fill=(134, 84, 50, 255), outline=INK, width=5 * S)
    # Silver Laptop on desk
    d.rounded_rectangle([(560 * S, 960 * S), (720 * S, 1050 * S)], radius=8 * S, fill=(203, 213, 225, 255), outline=INK, width=4 * S)
    d.ellipse([630 * S, 995 * S, 650 * S, 1015 * S], fill=(255, 255, 255, 255))
    # Red "ИСК В СУД" Folder on desk
    d.rounded_rectangle([(460 * S, 1020 * S), (545 * S, 1050 * S)], radius=4 * S, fill=(220, 38, 38, 255), outline=INK, width=3 * S)

    bgs["law_office"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 2: DEALERSHIP RETURN RAID (Same Showroom for Continuity!)
    # ------------------------------------------------------------------
    from backend.app.cartoon.v3_engine import build_v3_backgrounds
    v3_bgs = build_v3_backgrounds()
    bgs["dealership_raid"] = v3_bgs["showroom"].copy()

    # ------------------------------------------------------------------
    # LOC 3: COURTROOM (Judge's Bench + Scales of Justice + Wood Panels)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (232, 224, 212, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1230 * S

    # Formal Courtroom Wall
    d.rectangle([(0, 0), (W, floor_y)], fill=(222, 212, 196, 255))
    # Classical vertical columns
    for cx_col in [90 * S, 990 * S]:
        d.rectangle([(cx_col - 48 * S, 180 * S), (cx_col + 48 * S, floor_y)], fill=(241, 236, 228, 255), outline=INK, width=5 * S)

    # Golden Emblem / Scales of Justice above Judge's Bench
    sc_x, sc_y = 540 * S, 410 * S
    d.ellipse([sc_x - 110 * S, sc_y - 110 * S, sc_x + 110 * S, sc_y + 110 * S], fill=(30, 41, 59, 255), outline=(217, 119, 6, 255), width=8 * S)
    # Scales beam & pans
    d.line([(sc_x, sc_y - 60 * S), (sc_x, sc_y + 65 * S)], fill=(250, 204, 21, 255), width=8 * S)
    d.line([(sc_x - 65 * S, sc_y - 32 * S), (sc_x + 65 * S, sc_y - 32 * S)], fill=(250, 204, 21, 255), width=8 * S)
    d.polygon([(sc_x - 85 * S, sc_y + 18 * S), (sc_x - 45 * S, sc_y + 18 * S), (sc_x - 65 * S, sc_y - 30 * S)], outline=(250, 204, 21, 255), fill=(217, 119, 6, 180))
    d.polygon([(sc_x + 45 * S, sc_y + 18 * S), (sc_x + 85 * S, sc_y + 18 * S), (sc_x + 65 * S, sc_y - 30 * S)], outline=(250, 204, 21, 255), fill=(217, 119, 6, 180))

    # Clean Court Floor
    d.rectangle([(0, floor_y), (W, H)], fill=(238, 234, 226, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)

    # High Wooden Judge's Bench (drawn in foreground helper or mid-ground)
    bgs["courtroom"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 4: SUNNY BOULEVARD (Blue Sky, Green Trees, Brand-New White Car!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (186, 230, 253, 255))
    d = ImageDraw.Draw(img)
    road_y = 1090 * S
    sidewalk_y = 1245 * S

    # Bright sunny sky gradient
    for y in range(0, road_y, 4):
        rat = y / road_y
        c = (int(147 + rat * 65), int(210 + rat * 32), int(252), 255)
        d.rectangle([(0, y), (W, y + 4)], fill=c)

    # Bright yellow sun + soft fluffy clouds
    d.ellipse([830 * S, 240 * S, 960 * S, 370 * S], fill=(254, 240, 138, 255), outline=(250, 204, 21, 255), width=5 * S)
    for clx, cly in [(220, 320), (620, 290)]:
        d.ellipse([(clx - 70) * S, (cly - 30) * S, (clx + 70) * S, (cly + 30) * S], fill=(255, 255, 255, 235))
        d.ellipse([(clx - 30) * S, (cly - 52) * S, (clx + 48) * S, (cly + 16) * S], fill=(255, 255, 255, 235))

    # Bright modern city skyline + lush green park trees
    for bx, bw, bh in [(30, 190, 420), (240, 200, 500), (640, 210, 460), (880, 180, 400)]:
        d.rectangle([(bx * S, road_y - bh * S), ((bx + bw) * S, road_y)], fill=(203, 213, 225, 255), outline=(148, 163, 184, 255), width=4 * S)
        for wy in range(road_y - bh * S + 36 * S, road_y - 40 * S, 54 * S):
            for wx in range((bx + 26) * S, (bx + bw - 26) * S, 44 * S):
                d.rectangle([(wx, wy), (wx + 22 * S, wy + 28 * S)], fill=(241, 245, 249, 255))

    # Vibrant green cartoon trees
    for tx in [150 * S, 890 * S]:
        d.rectangle([(tx - 16 * S, road_y - 160 * S), (tx + 16 * S, road_y)], fill=(120, 72, 42, 255), outline=INK, width=4 * S)
        d.ellipse([tx - 90 * S, road_y - 290 * S, tx + 90 * S, road_y - 120 * S], fill=(74, 173, 94, 255), outline=INK, width=5 * S)
        d.ellipse([tx - 60 * S, road_y - 340 * S, tx + 60 * S, road_y - 200 * S], fill=(104, 196, 114, 255), outline=INK, width=5 * S)

    # Clean asphalt road
    d.rectangle([(0, road_y), (W, sidewalk_y)], fill=(100, 116, 139, 255))
    d.line([(0, road_y), (W, road_y)], fill=INK, width=5 * S)
    for dx in range(40 * S, W, 170 * S):
        d.rectangle([(dx, road_y + 64 * S), (dx + 90 * S, road_y + 78 * S)], fill=(255, 255, 255, 230))

    # Warm Sunny Sidewalk foreground
    d.rectangle([(0, sidewalk_y), (W, H)], fill=(240, 236, 226, 255))
    d.line([(0, sidewalk_y), (W, sidewalk_y)], fill=INK, width=5 * S)

    # Brand-new Gleaming White/Emerald Sports Car parked on right-center with RED GIFT BOW!
    _draw_car(d, cx=650 * S, wheel_y=1185 * S, S=S, body_color=(248, 250, 252), split_gap=0)
    # Red gift ribbon bow on roof of new car!
    rx, ry = 650 * S, 1045 * S
    d.polygon([(rx, ry), (rx - 52 * S, ry - 34 * S), (rx - 44 * S, ry + 8 * S)], fill=(220, 38, 38, 255), outline=INK)
    d.polygon([(rx, ry), (rx + 52 * S, ry - 34 * S), (rx + 44 * S, ry + 8 * S)], fill=(220, 38, 38, 255), outline=INK)
    d.ellipse([rx - 14 * S, ry - 14 * S, rx + 14 * S, ry + 14 * S], fill=(239, 68, 68, 255), outline=INK, width=3 * S)

    bgs["sunny_boulevard"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)
    return bgs


def build_judge_bench_overlay() -> Image.Image:
    """Wooden courtroom bench placed cleanly in front of the Judge's lower body."""
    S = 2
    W, H = 440 * S, 240 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(12 * S, 16 * S), (428 * S, 52 * S)], radius=8 * S, fill=(146, 84, 46, 255), outline=INK, width=5 * S)
    d.rounded_rectangle([(26 * S, 52 * S), (414 * S, 228 * S)], radius=10 * S, fill=(116, 66, 36, 255), outline=INK, width=5 * S)
    d.rounded_rectangle([(60 * S, 82 * S), (380 * S, 196 * S)], radius=8 * S, fill=(96, 52, 26, 255), outline=INK, width=4 * S)
    f = _font(FONT_BOLD, 30 * S)
    t = "СУД РФ"
    bb = f.getbbox(t)
    d.text(((W - (bb[2] - bb[0])) // 2, 120 * S), t, fill=(254, 240, 138, 255), font=f)
    return img.resize((440, 240), Image.Resampling.LANCZOS)


def draw_rec_camera_overlay(canvas: Image.Image, t: float) -> Image.Image:
    """Draws authentic hidden-camera viewfinder brackets + blinking REC ● indicator."""
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    w, h = canvas.size
    # Viewfinder corner brackets
    col = (255, 255, 255, 210)
    m_x, m_top, m_bot = 55, 235, 1360
    L = 48
    for (x, y, dx, dy) in [
        (m_x, m_top, L, L), (w - m_x, m_top, -L, L),
        (m_x, m_bot, L, -L), (w - m_x, m_bot, -L, -L),
    ]:
        d.line([(x, y), (x + dx, y)], fill=col, width=5)
        d.line([(x, y), (x, y + dy)], fill=col, width=5)

    # Blinking red REC dot
    if int(t * 2.5) % 2 == 0:
        d.ellipse([m_x + 24, m_top + 22, m_x + 50, m_top + 48], fill=(239, 68, 68, 255))
    d.text((m_x + 62, m_top + 18), f"REC  00:{int(t):02d}", fill=(255, 255, 255, 235), font=_font(FONT_BOLD, 28))
    return Image.alpha_composite(canvas, overlay)


# ---------------------------------------------------------------------------
# 3. MASTER PART 2 RENDERER
# ---------------------------------------------------------------------------

def render_autodealer_part2(
    output_path: Path = Path("output/cartoon_master/autodealer_part2_revenge.mp4"),
    speaker: str = "f5",
    fps: int = 30,
) -> Path:
    """Renders Part 2: 'Месть автодилеру' in v3 PRO Full-Body Multi-Character style."""
    output_path = Path(output_path)
    work_dir = output_path.parent / "temp_part2"
    work_dir.mkdir(parents=True, exist_ok=True)

    chapters = [
        {
            "loc": "law_office",
            "sentences": [
                "Часть вторая. Я не стал мириться с обманом и пошёл к знакомому юристу.",
                "Оказалось, автосалон кинул так уже двенадцать человек!",
            ],
            "hud_bal": "42 ₽",
            "hud_st": "ГОТОВИМ ИСК!",
            "theme": "alert",
            "pill": "КАБИНЕТ ЮРИСТА • ДЕНЬ 2",
            "sfx": "phone",
        },
        {
            "loc": "dealership_raid",
            "sentences": [
                "На следующий день мы вернулись в салон со скрытой камерой и полицией.",
                "Менеджер снова клялся, что машина в идеале... Пока в двери не зашли оперативники!",
            ],
            "hud_bal": "42 ₽",
            "hud_st": "СКРЫТАЯ СЪЁМКА",
            "theme": "danger",
            "pill": "АВТОСАЛОН • ОПЕРАЦИЯ ЗАДЕРЖАНИЯ",
            "sfx": "boom",
        },
        {
            "loc": "courtroom",
            "sentences": [
                "В суде всё решилось за десять минут!",
                "Салон обязали вернуть полную сумму, штраф и моральный ущерб. Три миллиона рублей!",
            ],
            "hud_bal": "3 100 000 ₽",
            "hud_st": "ПОБЕДА В СУДЕ!",
            "theme": "green",
            "pill": "ЗАЛ СУДА • ПРИГОВОР",
            "sfx": "boom",
        },
        {
            "loc": "sunny_boulevard",
            "sentences": [
                "Деньги пришли через неделю, и я купил новую машину напрямую у официалов.",
                "Никогда не сдавайтесь — и подписывайтесь, впереди новые истории!",
            ],
            "hud_bal": "1 250 000 ₽",
            "hud_st": "МЕЧТА СБЫЛАСЬ!",
            "theme": "green",
            "pill": "СОЛНЕЧНЫЙ ПРОСПЕКТ • ФИНАЛ",
            "sfx": "coin",
        },
    ]

    all_sentences = []
    chapter_word_counts = []
    for ch in chapters:
        cnt = 0
        for s in ch["sentences"]:
            all_sentences.append(s)
            cnt += len(s.replace(".", "").replace("!", "").replace("?", "").replace(",", "").replace("...", "").replace("—", "").split())
        chapter_word_counts.append(cnt)

    # Synthesize fresh Part 2 voiceover on RTX 4050 GPU via F5-TTS Russian (or reuse cache!)
    voice_wav = work_dir / f"voice_part2_{speaker}.wav"
    cached_words = work_dir / f"words_f5_voice_part2_{speaker}.json"
    if speaker == "f5" and voice_wav.exists() and cached_words.exists():
        print("[PART 2] 1. Используем готовую озвучку Части 2 (F5-TTS GPU) из кэша...")
        voice_file = voice_wav
        meta = json.loads(cached_words.read_text(encoding="utf-8"))
        words = meta["words"]
        duration = float(meta["duration"])
    elif speaker == "f5" and is_f5_available():
        print("[PART 2] 1. Синтезируем живую озвучку Части 2 через F5-TTS Russian (RTX 4050 GPU)...")
        voice_file, words, duration = synthesize_f5_script(all_sentences, out_wav=voice_wav, speed=1.06)
    else:
        print(f"[PART 2] 1. Синтезируем озвучку Silero v5.6 ({speaker})...")
        voice_file, words, duration = synthesize_silero_script(all_sentences, speaker=speaker, out_wav=voice_wav)

    # Exact chapter boundaries synced to synthesized words
    ch_starts = [0.0]
    wc = 0
    for i in range(len(chapters) - 1):
        wc += chapter_word_counts[i]
        ch_starts.append(max(ch_starts[-1] + 1.5, words[wc]["start"] - 0.12) if wc < len(words) else (i + 1) * (duration / 4.0))
    ch_ends = ch_starts[1:] + [duration]
    print(f"         Длительность: {duration:.2f}s | Смены локаций: {[round(x, 2) for x in ch_starts]}s")

    # SFX Mixing
    print("[PART 2] 2. Сводим звук + SFX (whoosh, удар молотка, сирена, звон монет)...")
    sfx_dir = work_dir / "sfx"
    sfx_map = {
        "coin": synth_coin_ding(sfx_dir / "coin.wav"),
        "phone": synth_phone_vibrate(sfx_dir / "phone.wav"),
        "boom": synth_liquidation_boom(sfx_dir / "boom.wav"),
        "whoosh": synth_whoosh(sfx_dir / "whoosh.wav"),
    }
    sfx_events = []
    for i, ch in enumerate(chapters):
        if i > 0:
            sfx_events.append((max(0.0, ch_starts[i] - 0.10), sfx_map["whoosh"], 0.72))
        sfx_events.append((ch_starts[i] + 0.25, sfx_map[ch["sfx"]], 0.90 if ch["sfx"] == "boom" else 0.75))

    master_audio = work_dir / "master_audio.wav"
    sr = 44100
    total_samples = int((duration + 0.5) * sr)
    master = np.zeros(total_samples, dtype=np.float32)

    p = subprocess.Popen([FFMPEG_BIN, "-y", "-i", str(voice_file), "-f", "s16le", "-ac", "1", "-ar", str(sr), "pipe:1"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw_v, _ = p.communicate()
    vs = np.frombuffer(raw_v, dtype=np.int16).astype(np.float32) / 32768.0
    master[:min(len(vs), total_samples)] += vs[:min(len(vs), total_samples)]

    for ts, sf_path, vol in sfx_events:
        if sf_path.exists():
            with wave.open(str(sf_path), "rb") as wf:
                data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0 * vol
            si = int(ts * sr)
            ei = min(si + len(data), total_samples)
            if ei > si:
                master[si:ei] += data[:(ei - si)]

    mx = np.max(np.abs(master))
    if mx > 0.95:
        master = master / mx * 0.95
    with wave.open(str(master_audio), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((master * 32767).astype(np.int16).tobytes())

    # Subtitles
    print("[PART 2] 3. Генерируем караоке-субтитры...")
    ass_path = work_dir / "part2_subtitles.ass"
    generate_cinematic_ass(
        words,
        ass_path,
        words_per_phrase=3,
        font_name="Arial",
        font_size=68,
        primary_color="&H00FFFFFF",
        highlight_color="&H0026A6FF",
        outline_color="&H001C2026",
        margin_v=310,
    )

    print("[PART 2] 4. Строим 4 новые 2x-суперсэмплированные локации...")
    bgs = build_part2_backgrounds()
    judge_bench = build_judge_bench_overlay()
    camera = CameraController()

    def is_speaking(t: float) -> bool:
        for w in words:
            if w["start"] - 0.04 <= t <= w["end"] + 0.04:
                return True
        return False

    def paste_char(frame: Image.Image, sprite: Image.Image, foot_x: int, foot_y: int) -> Image.Image:
        layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        px = foot_x - sprite.width // 2
        py = foot_y - sprite.height + 16
        layer.paste(sprite, (px, py))
        return Image.alpha_composite(frame, layer)

    def compose_scene(ch_idx: int, t: float, t_local: float, ch_dur: float, speaking: bool) -> Image.Image:
        ch = chapters[ch_idx]
        frame = bgs[ch["loc"]].copy()
        blink = (t % 2.8) > 2.67
        mouth = (["half", "open", "half"][int((t * 9.5) % 3)]) if speaking else "closed"
        ch_prog = max(0.0, min(1.0, t_local / max(0.1, ch_dur)))

        # ------------------ SCENE 1: LAWYER OFFICE ------------------
        if ch_idx == 0:
            # Hero walks in from left toward Lawyer's desk
            walk_p = min(1.0, t_local / 1.3)
            hero_x = int(95 + ease_out_back(walk_p) * 185)
            w_phase = t * 11.0 if walk_p < 0.98 else 0.0
            hero = render_full_body_character(
                outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
                mood="alert", mouth_state=mouth, gesture="point_right",
                blink=blink, walk_phase=w_phase, facing="right", scale=0.92,
            )
            lawyer = render_special_character(
                role="lawyer", mood="confident",
                mouth_state=("half" if (t_local > 2.5 and speaking) else "closed"),
                gesture="point_left", blink=((t + 1.2) % 3.1) > 2.98, facing="left", scale=0.94,
            )
            frame = paste_char(frame, lawyer, 850, 1295)
            frame = paste_char(frame, hero, hero_x, 1295)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * ch_prog, focal_point=(540, 1020), t=t)

            if t_local > 0.55:
                pop = ease_out_back(min(1.0, (t_local - 0.55) / 0.25))
                draw_smart_bubble(frame, "«Заберём у них в три раза больше!»", anchor_x=830, anchor_y=790, align="right", pop_scale=pop)

        # ------------------ SCENE 2: DEALERSHIP HIDDEN CAMERA RAID ------------------
        elif ch_idx == 1:
            raid_moment = t_local > (ch_dur * 0.45)

            # Hero on left holding phone recording hidden video!
            hero = render_full_body_character(
                outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
                mood="smug" if raid_moment else "confident",
                mouth_state=mouth if not raid_moment else "closed",
                gesture="hold_phone", blink=blink, facing="right", scale=0.90,
            )
            # Shady Manager in center-right — smug until Police burst in!
            mgr = render_full_body_character(
                outfit="suit", hair_style="slicked",
                mood="shocked" if raid_moment else "shady",
                mouth_state="open" if raid_moment else ("half" if speaking else "closed"),
                gesture="hands_on_head" if raid_moment else "point_left",
                blink=False if raid_moment else blink, facing="left", scale=0.90,
            )
            frame = paste_char(frame, hero, 200, 1295)
            frame = paste_char(frame, mgr, 660, 1290)

            # Police Officer runs in from the RIGHT edge when raid triggers!
            if raid_moment:
                rp = min(1.0, (t_local - ch_dur * 0.45) / 0.8)
                cop_x = int(1150 - ease_out_back(rp) * 230)
                cop = render_special_character(
                    role="police", mood="alert", mouth_state="open",
                    gesture="point_left" if rp > 0.8 else "run",
                    walk_phase=(t * 18.0 if rp < 0.85 else 0.0), facing="left", scale=0.93,
                )
                frame = paste_char(frame, cop, cop_x, 1298)
                frame = draw_siren_flash(frame, t)

            shake = ((1.0 - (t_local - ch_dur * 0.45) / 0.5) ** 1.4) if (raid_moment and (t_local - ch_dur * 0.45) < 0.5) else 0.0
            frame = camera.apply(frame, zoom=1.01 + 0.06 * ch_prog, focal_point=(540, 1020), shake_intensity=shake, t=t)
            frame = draw_rec_camera_overlay(frame, t)

            if not raid_moment and t_local > 0.35:
                pop = ease_out_back(min(1.0, (t_local - 0.35) / 0.22))
                draw_smart_bubble(frame, "«Клянусь, машина в идеале!»", anchor_x=660, anchor_y=790, align="right", pop_scale=pop)
            elif raid_moment:
                pop = ease_out_back(min(1.0, (t_local - ch_dur * 0.45) / 0.22))
                draw_smart_bubble(frame, "«Полиция! Вы задержаны!»", anchor_x=880, anchor_y=790, align="right", pop_scale=pop)

        # ------------------ SCENE 3: COURTROOM & GAVEL VICTORY ------------------
        elif ch_idx == 2:
            # Judge behind bench in CENTER!
            judge = render_special_character(
                role="judge", mood="confident",
                mouth_state=mouth, facing="left", scale=0.92,
            )
            frame = paste_char(frame, judge, 540, 1180)
            # Overlay wooden Judge's bench cleanly in front of judge's waist
            bench_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            bench_layer.paste(judge_bench, (540 - judge_bench.width // 2, 1005))
            frame = Image.alpha_composite(frame, bench_layer)

            # Happy Hero on LEFT holding cash!
            hero = render_full_body_character(
                outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
                mood="smug", mouth_state="open" if t_local > 2.5 else "closed",
                gesture="hold_money", blink=blink, facing="right", scale=0.92,
            )
            # Devastated Shady Manager on RIGHT!
            mgr = render_full_body_character(
                outfit="suit", hair_style="slicked",
                mood="sad", mouth_state="closed", gesture="hands_on_head",
                blink=False, facing="left", scale=0.90,
            )
            frame = paste_char(frame, hero, 200, 1305)
            frame = paste_char(frame, mgr, 885, 1305)

            # Gavel impact shake!
            shake = ((1.0 - t_local / 0.55) ** 1.4) if t_local <= 0.55 else 0.0
            frame = camera.apply(frame, zoom=1.02 + 0.06 * ch_prog, focal_point=(540, 990), shake_intensity=shake, t=t)

            # Slamming stamp "ВИНОВЕН!" cleanly above Judge's speech bubble (zero overlap!)
            frame = draw_animated_stamp(frame, "ВИНОВЕН!", t_local - 0.18, center=(760, 485))

            if t_local > 0.35:
                pop = ease_out_back(min(1.0, (t_local - 0.35) / 0.22))
                draw_smart_bubble(frame, "«Взыскать 3 000 000 ₽ в пользу истца!»", anchor_x=500, anchor_y=755, align="left", pop_scale=pop)

        # ------------------ SCENE 4: SUNNY BOULEVARD VICTORY FINALE ------------------
        else:
            frame = draw_money_rain(frame, t)
            # Cool Hero in dark sunglasses standing proudly next to brand-new white car with red bow!
            walk_p = min(1.0, t_local / 1.1)
            hero_x = int(140 + ease_out_back(walk_p) * 165)
            w_phase = t * 10.0 if walk_p < 0.96 else 0.0
            hero = render_special_character(
                role="hero_cool", mood="smug", mouth_state=mouth,
                gesture="hold_money", walk_phase=w_phase, facing="right", scale=0.95,
            )
            frame = paste_char(frame, hero, hero_x, 1315)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * ch_prog, focal_point=(540, 1040), t=t)

            if t_local > 0.45:
                pop = ease_out_back(min(1.0, (t_local - 0.45) / 0.25))
                draw_smart_bubble(frame, "«На этот раз — с гарантией от официалов!»", anchor_x=hero_x + 60, anchor_y=800, align="left", pop_scale=pop)

        # Sleek Frosted Editorial HUD + Location Pill
        draw_sleek_hud(frame, balance_text=ch["hud_bal"], status_text=ch["hud_st"], theme=ch["theme"])
        draw_compact_pill(frame, text=ch["pill"])
        return frame

    print("[PART 2] 5. Рендерим анимацию Части 2 (Юрист -> Полиция -> Суд -> Новая тачка)...")
    total_frames = int(duration * fps)
    raw_video = work_dir / "raw_part2.mp4"

    proc = subprocess.Popen([
        FFMPEG_BIN, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", "1080x1920", "-pix_fmt", "rgb24", "-r", str(fps),
        "-i", "pipe:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        str(raw_video),
    ], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    TRANS_DUR = 0.22
    for f in range(total_frames):
        t = f / fps
        ch_idx = 0
        for i in range(len(chapters)):
            if t >= ch_starts[i]:
                ch_idx = i
        t_local = t - ch_starts[ch_idx]
        ch_dur = ch_ends[ch_idx] - ch_starts[ch_idx]
        speaking = is_speaking(t)

        cur_frame = compose_scene(ch_idx, t, t_local, ch_dur, speaking)
        if ch_idx > 0 and t_local < TRANS_DUR:
            prev_dur = ch_ends[ch_idx - 1] - ch_starts[ch_idx - 1]
            prev_frame = compose_scene(ch_idx - 1, t, prev_dur, prev_dur, False)
            frame = apply_whip_transition(prev_frame, cur_frame, t_local / TRANS_DUR)
        else:
            frame = cur_frame

        proc.stdin.write(frame.convert("RGB").tobytes())

    proc.stdin.close()
    proc.wait()

    print("[PART 2] 6. Финальная сборка MP4 с живой озвучкой F5-TTS и караоке-субтитрами...")
    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    res = subprocess.run([
        FFMPEG_BIN, "-y",
        "-i", str(raw_video),
        "-i", str(master_audio),
        "-vf", f"ass='{ass_escaped}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(output_path),
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        subprocess.run([FFMPEG_BIN, "-y", "-i", str(raw_video), "-i", str(master_audio), "-c:v", "copy", "-c:a", "aac", str(output_path)], check=True)

    print(f"[OK] Часть 2 ('Месть автодилеру') готова: {output_path}")
    return output_path
