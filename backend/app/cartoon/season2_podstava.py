"""
Season 2: "АВТОПОДСТАВА" — Complete 5-Episode Animated Vertical Mini-Series (v3 PRO Engine).
All 5 episodes feature:
- 4 distinct 2x-supersampled anti-aliased vector scenes per episode (20 scenes total!)
- Articulated full-body multi-character staging (Hero, Scammer Boss, Accomplice in cap,
  DPS Traffic Inspector with baton, Lawyer, Judge)
- Real dynamic motion: driving cars, flying water bottle, patrol car rushing in,
  marked glowing cash, flashing sirens, slamming stamps, whip-pan transitions, camera shake!
- Live F5-TTS Russian GPU voiceover (RTX 4050) + studio SFX + karaoke subtitles.
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
    synth_drip_drop,
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
    build_v3_backgrounds,
    draw_compact_pill,
    draw_sleek_hud,
    draw_smart_bubble,
    render_full_body_character,
)
from backend.app.cartoon.v3_part2 import (
    build_judge_bench_overlay,
    build_part2_backgrounds,
    draw_rec_camera_overlay,
    render_special_character,
)
from backend.app.cartoon.v3_part3 import render_boss_character
from backend.app.cinematic.subtitles import generate_cinematic_ass

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


# ---------------------------------------------------------------------------
# 1. SEASON 2 CHARACTERS & PROPS (ACCOMPLICE IN CAP, DPS OFFICER, PATROL CAR)
# ---------------------------------------------------------------------------

def render_accomplice(
    mood: str = "shady",
    mouth_state: str = "closed",
    gesture: str = "point_left",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "left",
    scale: float = 0.90,
) -> Image.Image:
    """Scammer accomplice wearing gray tracksuit hoodie & baseball cap."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(71, 85, 105), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    # Baseball cap on head
    d.chord([cx - 72, 102, cx + 72, 174], start=180, end=360, fill=(30, 41, 59, 255), outline=INK, width=4)
    brim_dir = -1 if facing == "left" else 1
    d.rounded_rectangle(
        [(cx - 76 if brim_dir == -1 else cx - 10, 134), (cx + 10 if brim_dir == -1 else cx + 76, 148)],
        radius=5, fill=(15, 23, 42, 255), outline=INK, width=3,
    )
    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_dps_officer(
    mood: str = "confident",
    mouth_state: str = "closed",
    gesture: str = "point_left",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "left",
    scale: float = 0.93,
) -> Image.Image:
    """Traffic Police (DPS) Inspector with neon vest stripe & striped traffic baton!"""
    base = render_special_character(
        role="police", mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    # High-vis reflective lime-yellow traffic vest stripes across chest
    d.rectangle([(cx - 56, 336), (cx + 56, 352)], fill=(190, 242, 100, 245), outline=INK, width=2)
    d.rectangle([(cx - 62, 370), (cx + 62, 386)], fill=(190, 242, 100, 245), outline=INK, width=2)
    # Black-and-white striped traffic baton if pointing!
    if gesture == "point_left":
        bx, by = cx - 128, 286
        d.line([(bx, by), (bx - 42, by - 46)], fill=(255, 255, 255, 255), width=10)
        for seg in range(0, 40, 14):
            d.line([(bx - seg, by - seg), (bx - seg - 7, by - seg - 7)], fill=INK, width=10)
    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def build_car_sprite(
    body_color: Tuple[int, int, int] = (248, 250, 252),
    is_police: bool = False,
    damaged: bool = False,
) -> Image.Image:
    """Renders a crisp 2x-supersampled movable car sprite (white hero car, black beater, or DPS patrol!)."""
    S = 2
    W, H = 560 * S, 240 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _draw_car(d, cx=280 * S, wheel_y=175 * S, S=S, body_color=body_color, split_gap=0)

    if is_police:
        # Blue DPS stripe + red/blue lightbar on roof!
        d.rectangle([(52 * S, 134 * S), (508 * S, 152 * S)], fill=(37, 99, 235, 255), outline=INK, width=2 * S)
        # Roof siren lightbar
        d.rounded_rectangle([(232 * S, 22 * S), (280 * S, 42 * S)], radius=5 * S, fill=(239, 68, 68, 255), outline=INK, width=3 * S)
        d.rounded_rectangle([(280 * S, 22 * S), (328 * S, 42 * S)], radius=5 * S, fill=(59, 130, 246, 255), outline=INK, width=3 * S)
        d.text((240 * S, 110 * S), "ДПС", fill=(30, 58, 138, 255), font=_font(FONT_BOLD, 24 * S))

    if damaged:
        # Visible scratch/dent zig-zag on fender
        d.line([(390 * S, 128 * S), (420 * S, 142 * S), (402 * S, 156 * S), (432 * S, 166 * S)], fill=(239, 68, 68, 255), width=5 * S)

    return img.resize((560, 240), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 2. SEASON 2 2x-SUPERSAMPLED LOCATIONS (MKAD HIGHWAY, DASHCAM, CCTV, DOSSIER, INTERROGATION)
# ---------------------------------------------------------------------------

def build_season2_backgrounds() -> Dict[str, Image.Image]:
    S = 2
    W, H = 1080 * S, 1920 * S
    bgs = {}

    # ------------------------------------------------------------------
    # LOC 1: MKAD HIGHWAY (Bright Daylight Highway with Road Sign & Guardrail)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (186, 224, 248, 255))
    d = ImageDraw.Draw(img)
    horizon_y = 950 * S
    road_bottom = 1265 * S

    # Sky gradient
    for y in range(0, horizon_y, 4):
        rat = y / horizon_y
        d.rectangle([(0, y), (W, y + 4)], fill=(int(156 + rat * 58), int(208 + rat * 32), 248, 255))

    # Distant city skyline & highway green overhead gantry sign!
    for bx, bw, bh in [(20, 170, 260), (220, 180, 320), (680, 190, 290), (900, 160, 250)]:
        d.rectangle([(bx * S, horizon_y - bh * S), ((bx + bw) * S, horizon_y)], fill=(186, 198, 214, 255), outline=(148, 163, 184, 255), width=3 * S)

    # Overhead Highway Sign: "МКАД • 42 КМ"
    d.line([(210 * S, 265 * S), (210 * S, horizon_y)], fill=(100, 116, 139, 255), width=10 * S)
    d.line([(870 * S, 265 * S), (870 * S, horizon_y)], fill=(100, 116, 139, 255), width=10 * S)
    d.rounded_rectangle([(200 * S, 260 * S), (880 * S, 355 * S)], radius=14 * S, fill=(22, 101, 52, 255), outline=(255, 255, 255, 255), width=6 * S)
    f_hw = _font(FONT_BOLD, 42 * S)
    htxt = "МКАД • 42 КМ  →  ЦЕНТР"
    hbb = f_hw.getbbox(htxt)
    d.text(((W - (hbb[2] - hbb[0])) // 2, 282 * S), htxt, fill=(255, 255, 255, 255), font=f_hw)

    # Metal highway guardrail
    d.rectangle([(0, horizon_y - 36 * S), (W, horizon_y)], fill=(203, 213, 225, 255), outline=INK, width=4 * S)
    d.line([(0, horizon_y - 18 * S), (W, horizon_y - 18 * S)], fill=(148, 163, 184, 255), width=4 * S)

    # Multi-lane asphalt highway
    d.rectangle([(0, horizon_y), (W, road_bottom)], fill=(71, 85, 105, 255))
    d.line([(0, horizon_y), (W, horizon_y)], fill=INK, width=5 * S)
    # Dashed lane markings
    for ly in [1055 * S, 1165 * S]:
        for lx in range(30 * S, W, 160 * S):
            d.rectangle([(lx, ly), (lx + 85 * S, ly + 12 * S)], fill=(241, 245, 249, 225))

    # Clean light shoulder/foreground for character standing + subtitles!
    d.rectangle([(0, road_bottom), (W, H)], fill=(230, 228, 222, 255))
    d.line([(0, road_bottom), (W, road_bottom)], fill=INK, width=5 * S)

    bgs["highway"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 2: DASHCAM CLOSEUP SCREEN (4K Active vs Red SD Card Error!)
    # ------------------------------------------------------------------
    for mode in ["dashcam_ok", "dashcam_error"]:
        img = Image.new("RGBA", (W, H), (26, 32, 44, 255))
        d = ImageDraw.Draw(img)
        floor_y = 1245 * S
        # Car interior dark ceiling / windshield backdrop
        d.rectangle([(0, 0), (W, floor_y)], fill=(30, 41, 59, 255))
        # Large Dashcam Device Body mounted in center-upper area!
        dx1, dy1, dx2, dy2 = 140 * S, 310 * S, 940 * S, 780 * S
        d.rounded_rectangle([(dx1, dy1), (dx2, dy2)], radius=28 * S, fill=(15, 23, 42, 255), outline=(148, 163, 184, 255), width=7 * S)
        # Inner screen
        sx1, sy1, sx2, sy2 = dx1 + 28 * S, dy1 + 28 * S, dx2 - 28 * S, dy2 - 28 * S
        scr_col = (12, 42, 34, 255) if mode == "dashcam_ok" else (69, 14, 18, 255)
        scr_brd = (34, 197, 94, 255) if mode == "dashcam_ok" else (239, 68, 68, 255)
        d.rounded_rectangle([(sx1, sy1), (sx2, sy2)], radius=16 * S, fill=scr_col, outline=scr_brd, width=5 * S)

        if mode == "dashcam_ok":
            d.ellipse([sx1 + 36 * S, sy1 + 36 * S, sx1 + 66 * S, sy1 + 66 * S], fill=(239, 68, 68, 255))
            d.text((sx1 + 82 * S, sy1 + 32 * S), "REC • 4K HDR", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 34 * S))
            f_m = _font(FONT_IMPACT, 66 * S)
            mt = "ВИДЕОРЕГИСТРАТОР"
            mbb = f_m.getbbox(mt)
            d.text(((W - (mbb[2] - mbb[0])) // 2, sy1 + 150 * S), mt, fill=(74, 222, 128, 255), font=f_m)
            f_s = _font(FONT_BOLD, 30 * S)
            st = "ВСЯ ПОДСТАВА ЗАПИСАНА НА КАРТУ!"
            sbb = f_s.getbbox(st)
            d.text(((W - (sbb[2] - sbb[0])) // 2, sy1 + 255 * S), st, fill=(226, 232, 240, 255), font=f_s)
        else:
            f_m = _font(FONT_IMPACT, 66 * S)
            mt = "ОШИБКА SD-КАРТЫ!"
            mbb = f_m.getbbox(mt)
            d.text(((W - (mbb[2] - mbb[0])) // 2, sy1 + 125 * S), mt, fill=(248, 113, 113, 255), font=f_m)
            f_s = _font(FONT_BOLD, 32 * S)
            st = "ФАЙЛ ЗАПИСИ ПОВРЕЖДЁН • 0 БАЙТ"
            sbb = f_s.getbbox(st)
            d.text(((W - (sbb[2] - sbb[0])) // 2, sy1 + 245 * S), st, fill=(254, 226, 226, 255), font=f_s)

        # Light clean lower third for characters & subtitles
        d.rectangle([(0, floor_y), (W, H)], fill=(230, 228, 224, 255))
        d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
        bgs[mode] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 3: CITY CCTV MONITORING ROOM ("КАМЕРА МКАД • 4K")
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (220, 228, 238, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S
    d.rectangle([(0, 0), (W, floor_y)], fill=(224, 232, 242, 255))

    # Giant CCTV Monitor Wall Screen showing the bottle throw freeze-frame!
    mx1, my1, mx2, my2 = 120 * S, 265 * S, 960 * S, 740 * S
    d.rounded_rectangle([(mx1, my1), (mx2, my2)], radius=22 * S, fill=(15, 23, 42, 255), outline=INK, width=6 * S)
    # Top CCTV HUD inside monitor
    d.text((mx1 + 30 * S, my1 + 22 * S), "КАМЕРА МКАД-42  |  14:22:08  |  ZOOM 8x", fill=(74, 222, 128, 255), font=_font(FONT_BOLD, 24 * S))
    # Road miniature inside monitor + zoomed red target circle around flying bottle!
    d.rectangle([(mx1 + 26 * S, my1 + 85 * S), (mx2 - 26 * S, my2 - 80 * S)], fill=(51, 65, 85, 255))
    # Small white car & black car icons inside CCTV screen
    d.rounded_rectangle([(mx1 + 120 * S, my1 + 210 * S), (mx1 + 310 * S, my1 + 290 * S)], radius=12 * S, fill=(248, 250, 252, 255), outline=INK, width=3 * S)
    d.rounded_rectangle([(mx1 + 480 * S, my1 + 210 * S), (mx1 + 680 * S, my1 + 290 * S)], radius=12 * S, fill=(24, 30, 42, 255), outline=(148, 163, 184, 255), width=3 * S)
    # Red target reticle around thrown bottle!
    tx, ty = mx1 + 400 * S, my1 + 195 * S
    d.ellipse([tx - 48 * S, ty - 48 * S, tx + 48 * S, ty + 48 * S], outline=(239, 68, 68, 255), width=5 * S)
    d.rounded_rectangle([(tx - 10 * S, ty - 22 * S), (tx + 10 * S, ty + 22 * S)], radius=4 * S, fill=(56, 189, 248, 255), outline=INK, width=2 * S)
    d.text((mx1 + 185 * S, my2 - 64 * S), "УЛИКА: БРОСОК БУТЫЛКИ В КУЗОВ!", fill=(250, 204, 21, 255), font=_font(FONT_BOLD, 28 * S))

    d.rectangle([(0, floor_y), (W, H)], fill=(238, 236, 230, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["cctv_room"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 4: CRIMINAL DOSSIER BOARD ("17 ПОДСТАВ • 5 400 000 ₽")
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (55, 22, 28, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S
    d.rectangle([(0, 0), (W, floor_y)], fill=(58, 20, 26, 255))

    # Cork/Red Investigation Dossier Card
    cx1, cy1, cx2, cy2 = 120 * S, 265 * S, 960 * S, 740 * S
    d.rounded_rectangle([(cx1, cy1), (cx2, cy2)], radius=22 * S, fill=(24, 14, 18, 248), outline=(239, 68, 68, 255), width=6 * S)
    f_d1 = _font(FONT_IMPACT, 54 * S)
    dt1 = "БАЗА ГИБДД: БАНДА ПОДСТАВЩИКОВ"
    dbb1 = f_d1.getbbox(dt1)
    d.text(((W - (dbb1[2] - dbb1[0])) // 2, cy1 + 32 * S), dt1, fill=(248, 113, 113, 255), font=f_d1)

    # Stats boxes inside board
    for idx, (lbl, val, bx) in enumerate([
        ("ПОДСТАВ ЗА ГОД", "17 СЛУЧАЕВ", 160 * S),
        ("СУММА УЩЕРБА", "5 400 000 ₽", 570 * S),
    ]):
        d.rounded_rectangle([(bx, cy1 + 140 * S), (bx + 350 * S, cy1 + 300 * S)], radius=14 * S, fill=(45, 18, 24, 255), outline=(248, 113, 113, 200), width=4 * S)
        d.text((bx + 26 * S, cy1 + 165 * S), lbl, fill=(254, 202, 202, 255), font=_font(FONT_BOLD, 24 * S))
        d.text((bx + 26 * S, cy1 + 215 * S), val, fill=(255, 255, 255, 255), font=_font(FONT_IMPACT, 44 * S))

    d.text((225 * S, cy1 + 365 * S), "АВТОМОБИЛЬ: ЧЁРНЫЙ СЕДАН • В РОЗЫСКЕ", fill=(250, 204, 21, 255), font=_font(FONT_BOLD, 28 * S))

    d.rectangle([(0, floor_y), (W, H)], fill=(232, 226, 224, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["scam_board"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 5: POLICE INTERROGATION ROOM (Hanging Lamp + Metal Table)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (44, 52, 64, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S
    d.rectangle([(0, 0), (W, floor_y)], fill=(52, 62, 76, 255))
    # One-way interrogation mirror on back wall
    d.rounded_rectangle([(200 * S, 350 * S), (880 * S, 760 * S)], radius=10 * S, fill=(28, 38, 52, 255), outline=(148, 163, 184, 255), width=6 * S)
    d.text((370 * S, 410 * S), "ДОПРОС • ОТДЕЛ ПОЛИЦИИ", fill=(148, 163, 184, 220), font=_font(FONT_BOLD, 28 * S))
    # Hanging interrogation spotlight cone
    d.line([(540 * S, 200 * S), (540 * S, 295 * S)], fill=INK, width=6 * S)
    d.polygon([(485 * S, 325 * S), (595 * S, 325 * S), (565 * S, 290 * S), (515 * S, 290 * S)], fill=(100, 116, 139, 255), outline=INK)
    cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cone).polygon([(495 * S, 325 * S), (585 * S, 325 * S), (880 * S, floor_y), (200 * S, floor_y)], fill=(254, 240, 138, 28))
    img = Image.alpha_composite(img, cone)
    d = ImageDraw.Draw(img)

    # Clean light floor
    d.rectangle([(0, floor_y), (W, H)], fill=(224, 228, 232, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["interrogation"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # Reuse crisp editorial Law Office, Courtroom, Sunny Boulevard & Vault from v3!
    p2_bgs = build_part2_backgrounds()
    v3_bgs = build_v3_backgrounds()
    bgs["law_office"] = p2_bgs["law_office"]
    bgs["courtroom"] = p2_bgs["courtroom"]
    bgs["sunny_boulevard"] = p2_bgs["sunny_boulevard"]
    bgs["vault"] = v3_bgs["vault"]

    return bgs


# ---------------------------------------------------------------------------
# 3. ALL 5 EPISODES OF SEASON 2 ("АВТОПОДСТАВА")
# ---------------------------------------------------------------------------

SEASON2_EPISODES = {
    1: {
        "filename": "season2_ep1_hit.mp4",
        "title": "Сезон 2 • Часть 1: Удар на МКАДе",
        "chapters": [
            {
                "scene_id": "ep1_s1",
                "loc": "highway",
                "sentences": [
                    "Сезон второй, часть первая. Я спокойно ехал по МКАДу на своей новой машине.",
                    "Внезапно меня жёстко подрезал старый чёрный седан!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "ПОЕЗДКА ПО МКАД",
                "theme": "green",
                "pill": "МКАД • 42 КМ • 14:20",
                "sfx": "whoosh",
            },
            {
                "scene_id": "ep1_s2",
                "loc": "highway",
                "sentences": [
                    "Раздался глухой хлопок по кузову! Я остановился на обочине.",
                    "Из чёрной машины выскочил амбал и начал орать, что я снёс ему дорогое зеркало!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "СТРАННОЕ ДТП!",
                "theme": "alert",
                "pill": "ОБОЧИНА • КОНФЛИКТ",
                "sfx": "boom",
            },
            {
                "scene_id": "ep1_s3",
                "loc": "highway",
                "sentences": [
                    "Он сунул мне под нос царапину и потребовал триста пятьдесят тысяч наличкой прямо сейчас!",
                    "Иначе, мол, приедут его люди и меня лишат прав!",
                ],
                "hud_bal": "-350 000 ₽ ?",
                "hud_st": "ВЫМОГАТЕЛЬСТВО!",
                "theme": "danger",
                "pill": "ТРЕБУЮТ 350 000 ₽ НА МЕСТЕ",
                "sfx": "boom",
            },
            {
                "scene_id": "ep1_s4",
                "loc": "dashcam_ok",
                "sentences": [
                    "Они были уверены, что я испугаюсь и отдам деньги.",
                    "Но они не заметили маленькую красную лампочку под моим зеркалом... Продолжение во второй части!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "ЕСТЬ КОЗЫРЬ!",
                "theme": "green",
                "pill": "ВИДЕОРЕГИСТРАТОР • 4K",
                "sfx": "coin",
            },
        ],
    },
    2: {
        "filename": "season2_ep2_witness.mp4",
        "title": "Сезон 2 • Часть 2: Фальшивый свидетель и ошибка SD-карты",
        "chapters": [
            {
                "scene_id": "ep2_s1",
                "loc": "highway",
                "sentences": [
                    "Часть вторая. Как только я отказался платить, рядом резко тормозит вторая машина.",
                    "Оттуда выходит якобы случайный свидетель в кепке!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "ЛОЖНЫЙ СВИДЕТЕЛЬ!",
                "theme": "alert",
                "pill": "МКАД • ПОЯВИЛСЯ ПОДЕЛЬНИК",
                "sfx": "phone",
            },
            {
                "scene_id": "ep2_s2",
                "loc": "highway",
                "sentences": [
                    "Он клялся, что видел, как я подрезал чёрный седан!",
                    "Двое окружили меня и скинули цену до двухсот тысяч — только переводи прямо сейчас!",
                ],
                "hud_bal": "-200 000 ₽ ?",
                "hud_st": "ДАВЛЕНИЕ ВДВОЁМ!",
                "theme": "danger",
                "pill": "ТРЕБУЮТ ПЕРЕВОД НА КАРТУ",
                "sfx": "boom",
            },
            {
                "scene_id": "ep2_s3",
                "loc": "highway",
                "sentences": [
                    "Я не повёлся и вызвал официальный экипаж ДПС.",
                    "Инспектор приехал через десять минут, но подставщики почему-то вообще не нервничали...",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "ПРИЕХАЛИ ДПС",
                "theme": "alert",
                "pill": "ОФОРМЛЕНИЕ ДТП НА ОБОЧИНЕ",
                "sfx": "phone",
            },
            {
                "scene_id": "ep2_s4",
                "loc": "dashcam_error",
                "sentences": [
                    "Я гордо достал флешку из регистратора, чтобы показать запись инспектору...",
                    "А экран выдал: карта памяти повреждена! Неужели они победили?! Смотри в третьей части!",
                ],
                "hud_bal": "РИСК: ЛИШЕНИЕ!",
                "hud_st": "ЗАПИСЬ ПРОПАЛА!",
                "theme": "danger",
                "pill": "ОШИБКА SD-КАРТЫ • КРИЗИС",
                "sfx": "boom",
            },
        ],
    },
    3: {
        "filename": "season2_ep3_cctv.mp4",
        "title": "Сезон 2 • Часть 3: Камеры МКАДа и база банды",
        "chapters": [
            {
                "scene_id": "ep3_s1",
                "loc": "law_office",
                "sentences": [
                    "Часть третья. Инспектор выписал временный протокол, а на разбор дали ровно три дня.",
                    "Я сразу поехал к своему проверенному юристу!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "СРОК: 3 ДНЯ",
                "theme": "alert",
                "pill": "КАБИНЕТ ЮРИСТА • ПОИСК УЛИК",
                "sfx": "phone",
            },
            {
                "scene_id": "ep3_s2",
                "loc": "cctv_room",
                "sentences": [
                    "Мы подали срочный запрос на городские дорожные камеры.",
                    "На записи чётко видно, как подельник в кепке кидает бутылку с водой мне в крыло, чтобы имитировать удар!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "УЛИКА НАЙДЕНА!",
                "theme": "green",
                "pill": "КАМЕРА МКАД • 4K УВЕЛИЧЕНИЕ",
                "sfx": "coin",
            },
            {
                "scene_id": "ep3_s3",
                "loc": "scam_board",
                "sentences": [
                    "Но самое жёсткое ждало дальше. Мы пробили номера чёрного седана!",
                    "За год эта банда оформила семнадцать таких же подстав на пять миллионов рублей!",
                ],
                "hud_bal": "УЩЕРБ: 5.4 МЛН ₽",
                "hud_st": "ОПГ НА ТРАССЕ!",
                "theme": "danger",
                "pill": "БАЗА ГИБДД • 17 ЭПИЗОДОВ",
                "sfx": "boom",
            },
            {
                "scene_id": "ep3_s4",
                "loc": "law_office",
                "sentences": [
                    "Мы отнесли все записи оперативникам. Они предложили поймать банду с поличным завтра на той же трассе!",
                    "Операция захвата — в четвёртой части!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "ПЛАН ЛОВУШКИ!",
                "theme": "green",
                "pill": "ПОДГОТОВКА СПЕЦОПЕРАЦИИ",
                "sfx": "coin",
            },
        ],
    },
    4: {
        "filename": "season2_ep4_trap.mp4",
        "title": "Сезон 2 • Часть 4: Ловля на живца!",
        "chapters": [
            {
                "scene_id": "ep4_s1",
                "loc": "highway",
                "sentences": [
                    "Часть четвёртая. На следующее утро мы выехали на МКАД на машине-приманке со скрытыми камерами.",
                    "В соседнем ряду незаметно шли два экипажа полиции!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "ОПЕРАЦИЯ ЖИВЕЦ",
                "theme": "alert",
                "pill": "МКАД • СКРЫТОЕ НАБЛЮДЕНИЕ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "ep4_s2",
                "loc": "highway",
                "sentences": [
                    "Через двадцать минут чёрный седан снова клюнул!",
                    "Амбал выскочил с тем же самым разбитым зеркалом и начал требовать триста тысяч наличкой.",
                ],
                "hud_bal": "300 000 ₽",
                "hud_st": "ПОПАЛИСЬ НА КРЮЧОК!",
                "theme": "alert",
                "pill": "ЗАПИСЬ ВЫМОГАТЕЛЬСТВА • REC",
                "sfx": "phone",
            },
            {
                "scene_id": "ep4_s3",
                "loc": "highway",
                "sentences": [
                    "В этот раз я спокойно протянул ему пачку меченых купюр.",
                    "Как только он пересчитал деньги и убрал их в карман, я подал условный сигнал!",
                ],
                "hud_bal": "МЕЧЕНЫЕ КУПЮРЫ",
                "hud_st": "ПЕРЕДАЧА ДЕНЕГ!",
                "theme": "green",
                "pill": "СПЕЦОПЕРАЦИЯ • СИГНАЛ ПОЛЬЗОВАТЕЛЯ",
                "sfx": "coin",
            },
            {
                "scene_id": "ep4_s4",
                "loc": "highway",
                "sentences": [
                    "Через три секунды обочину перекрыли патрульные машины!",
                    "Подставщиков повязали прямо с мечеными деньгами в руках! Чем закончился суд — в финальной пятой части!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "БАНДА ЗАДЕРЖАНА!",
                "theme": "danger",
                "pill": "ЗАХВАТ НА МКАДЕ • ПОЛИЦИЯ",
                "sfx": "boom",
            },
        ],
    },
    5: {
        "filename": "season2_ep5_finale.mp4",
        "title": "Сезон 2 • Часть 5 (Финал): Суд и 17 спасённых водителей",
        "chapters": [
            {
                "scene_id": "ep5_s1",
                "loc": "interrogation",
                "sentences": [
                    "Пятая, финальная часть. В отделе полиции вся банда посыпалась за пять минут.",
                    "Увидев видео с камер МКАДа, подельник сразу сдал главаря и все их схемы!",
                ],
                "hud_bal": "1 250 000 ₽",
                "hud_st": "ПРИЗНАНИЕ ВИНЫ!",
                "theme": "alert",
                "pill": "ДОПРОС • ЯВКА С ПОВИННОЙ",
                "sfx": "phone",
            },
            {
                "scene_id": "ep5_s2",
                "loc": "courtroom",
                "sentences": [
                    "В суде собрались все семнадцать обманутых водителей!",
                    "Подставщикам дали реальные сроки, а их чёрный седан конфисковали в счёт компенсаций.",
                ],
                "hud_bal": "3 800 000 ₽",
                "hud_st": "5 ЛЕТ ТЮРЬМЫ!",
                "theme": "danger",
                "pill": "ЗАЛ СУДА • ПРИГОВОР БАНДЕ",
                "sfx": "boom",
            },
            {
                "scene_id": "ep5_s3",
                "loc": "vault",
                "sentences": [
                    "Всем пострадавшим полностью вернули украденные деньги!",
                    "А мне выплатили крупную компенсацию за моральный ущерб и помощь следствию.",
                ],
                "hud_bal": "3 800 000 ₽",
                "hud_st": "ВОЗВРАТ 100%!",
                "theme": "green",
                "pill": "КОМПЕНСАЦИЯ • СПРАВЕДЛИВОСТЬ",
                "sfx": "coin",
            },
            {
                "scene_id": "ep5_s4",
                "loc": "sunny_boulevard",
                "sentences": [
                    "Запомните главное правило: при любой странной аварии никогда не платите на месте и всегда вызывайте полицию!",
                    "Ставьте лайк и пишите в комментариях, про какой развод снять третий сезон!",
                ],
                "hud_bal": "3 800 000 ₽",
                "hud_st": "КАРМА СРАБОТАЛА!",
                "theme": "green",
                "pill": "ФИНАЛ 2-ГО СЕЗОНА • СОВЕТ",
                "sfx": "coin",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# 4. EPISODE SCENE COMPOSITOR & BATCH RENDERER
# ---------------------------------------------------------------------------

def render_season2_episode(
    ep_num: int,
    out_dir: Path = Path("output/season2_podstava"),
    speaker: str = "f5",
    fps: int = 30,
    shared_bgs: Optional[Dict[str, Image.Image]] = None,
) -> Path:
    """Renders one complete episode of Season 2 ('Автоподстава')."""
    ep = SEASON2_EPISODES[ep_num]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / ep["filename"]
    work_dir = out_dir / f"temp_ep{ep_num}"
    work_dir.mkdir(parents=True, exist_ok=True)

    chapters = ep["chapters"]
    all_sentences = []
    chapter_word_counts = []
    for ch in chapters:
        cnt = 0
        for s in ch["sentences"]:
            all_sentences.append(s)
            cnt += len(s.replace(".", "").replace("!", "").replace("?", "").replace(",", "").replace("...", "").replace("—", "").split())
        chapter_word_counts.append(cnt)

    # 1. Voice Synthesis (F5-TTS Russian on RTX 4050 GPU, cached!)
    voice_wav = work_dir / f"voice_ep{ep_num}_{speaker}.wav"
    cached_words = work_dir / f"words_f5_voice_ep{ep_num}_{speaker}.json"

    if speaker == "f5" and voice_wav.exists() and cached_words.exists():
        print(f"[S2 EP{ep_num}] 1. Используем кэшированную GPU-озвучку F5-TTS...")
        voice_file = voice_wav
        meta = json.loads(cached_words.read_text(encoding="utf-8"))
        words = meta["words"]
        duration = float(meta["duration"])
    elif speaker == "f5" and is_f5_available():
        print(f"[S2 EP{ep_num}] 1. Синтезируем живую озвучку '{ep['title']}' (F5-TTS RTX 4050)...")
        voice_file, words, duration = synthesize_f5_script(all_sentences, out_wav=voice_wav, speed=1.07)
    else:
        print(f"[S2 EP{ep_num}] 1. Синтезируем озвучку Silero v5.6 ({speaker})...")
        voice_file, words, duration = synthesize_silero_script(all_sentences, speaker=speaker, out_wav=voice_wav)

    # Exact synced chapter timestamps
    ch_starts = [0.0]
    wc = 0
    for i in range(len(chapters) - 1):
        wc += chapter_word_counts[i]
        ch_starts.append(max(ch_starts[-1] + 1.5, words[wc]["start"] - 0.12) if wc < len(words) else (i + 1) * (duration / 4.0))
    ch_ends = ch_starts[1:] + [duration]
    print(f"          Длительность: {duration:.2f}s | Смены сцен: {[round(x, 2) for x in ch_starts]}s")

    # 2. SFX Mixing
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
        if i > 0:
            sfx_events.append((max(0.0, ch_starts[i] - 0.10), sfx_map["whoosh"], 0.72))
        sfx_events.append((ch_starts[i] + 0.22, sfx_map[ch["sfx"]], 0.90 if ch["sfx"] == "boom" else 0.72))

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

    # 3. Subtitles
    ass_path = work_dir / f"ep{ep_num}_subtitles.ass"
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

    # 4. Load / reuse backgrounds & movable car sprites
    bgs = shared_bgs if shared_bgs is not None else build_season2_backgrounds()
    white_car = build_car_sprite((248, 250, 252), is_police=False, damaged=False)
    white_car_hit = build_car_sprite((248, 250, 252), is_police=False, damaged=True)
    black_car = build_car_sprite((30, 36, 48), is_police=False, damaged=True)
    dps_car = build_car_sprite((248, 250, 252), is_police=True, damaged=False)
    judge_bench = build_judge_bench_overlay()
    camera = CameraController()

    def is_speaking(t: float) -> bool:
        for w in words:
            if w["start"] - 0.04 <= t <= w["end"] + 0.04:
                return True
        return False

    def paste_obj(frame: Image.Image, sprite: Image.Image, x: int, y: int) -> Image.Image:
        layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        layer.paste(sprite, (x, y))
        return Image.alpha_composite(frame, layer)

    def paste_char(frame: Image.Image, sprite: Image.Image, foot_x: int, foot_y: int) -> Image.Image:
        return paste_obj(frame, sprite, foot_x - sprite.width // 2, foot_y - sprite.height + 16)

    def compose_scene(ch_idx: int, t: float, t_local: float, ch_dur: float, speaking: bool) -> Image.Image:
        ch = chapters[ch_idx]
        sid = ch["scene_id"]
        frame = bgs[ch["loc"]].copy()
        blink = (t % 2.8) > 2.67
        mouth = (["half", "open", "half"][int((t * 9.5) % 3)]) if speaking else "closed"
        p_ch = max(0.0, min(1.0, t_local / max(0.1, ch_dur)))
        pop_late = ease_out_back(min(1.0, max(0.0, (t_local - 0.35) / 0.22)))

        # ================================================================
        # EPISODE 1: УДАР НА МКАДЕ
        # ================================================================
        if sid == "ep1_s1":
            # Driving white car + black beater cutting in aggressively from right!
            wx = int(40 + p_ch * 140)
            bx = int(680 - ease_out_back(min(1.0, t_local / 2.2)) * 210)
            frame = paste_obj(frame, black_car, bx, 920)
            frame = paste_obj(frame, white_car, wx, 1020)
            frame = camera.apply(frame, zoom=1.00 + 0.06 * p_ch, focal_point=(540, 1060), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Куда он лезет прямо под колёса?!»", anchor_x=wx + 240, anchor_y=940, align="left", pop_scale=pop_late)

        elif sid == "ep1_s2":
            # Stopped cars + Scammer Boss storms out yelling!
            frame = paste_obj(frame, white_car_hit, 20, 1015)
            frame = paste_obj(frame, black_car, 510, 995)
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="alert", mouth_state="closed", gesture="relax", blink=blink, facing="right", scale=0.90)
            boss = render_boss_character(mood="shady", mouth_state=mouth, gesture="point_left", facing="left", scale=0.95)
            frame = paste_char(frame, hero, 235, 1320)
            frame = paste_char(frame, boss, 835, 1320)
            shake = ((1.0 - t_local / 0.5) ** 1.4) if t_local <= 0.5 else 0.0
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 1080), shake_intensity=shake, t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Ты мне зеркало снёс! Гони бабки!»", anchor_x=810, anchor_y=820, align="right", pop_scale=pop_late)

        elif sid == "ep1_s3":
            # Threatening demanding 350k cash + "РАЗВОД!" stamp!
            frame = paste_obj(frame, white_car_hit, 20, 1015)
            frame = paste_obj(frame, black_car, 510, 995)
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="right", scale=0.90)
            boss = render_boss_character(mood="shady", mouth_state=mouth, gesture="hold_money", facing="left", scale=0.96)
            frame = paste_char(frame, hero, 220, 1320)
            frame = paste_char(frame, boss, 820, 1320)
            shake = ((1.0 - t_local / 0.55) ** 1.4) if t_local <= 0.55 else 0.0
            frame = camera.apply(frame, zoom=1.05 + 0.06 * p_ch, focal_point=(540, 1060), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "РАЗВОД!", t_local - 0.15, center=(540, 560))
            if t_local > 0.4:
                draw_smart_bubble(frame, "«350 тысяч наличкой — или лишат прав!»", anchor_x=800, anchor_y=820, align="right", pop_scale=pop_late)

        elif sid == "ep1_s4":
            # Smug Hero next to 4K Dashcam screen!
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="smug", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            frame = paste_char(frame, hero, 300, 1315)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 960), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Улыбайтесь — вас снимает 4K камера!»", anchor_x=380, anchor_y=850, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 2: ФАЛЬШИВЫЙ СВИДЕТЕЛЬ И ОШИБКА SD-КАРТЫ
        # ================================================================
        elif sid == "ep2_s1":
            frame = paste_obj(frame, white_car_hit, 20, 1015)
            frame = paste_obj(frame, black_car, 510, 995)
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="alert", mouth_state="closed", gesture="relax", blink=blink, facing="right", scale=0.88)
            acc_x = int(1060 - ease_out_back(min(1.0, t_local / 1.0)) * 220)
            acc = render_accomplice(mood="shady", mouth_state=mouth, gesture="point_left", walk_phase=(t * 14.0 if t_local < 0.95 else 0.0), facing="left", scale=0.92)
            frame = paste_char(frame, hero, 210, 1320)
            frame = paste_char(frame, acc, acc_x, 1320)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1060), t=t)
            if t_local > 0.5:
                draw_smart_bubble(frame, "«Я всё видел! Это он вас подрезал!»", anchor_x=acc_x - 30, anchor_y=820, align="right", pop_scale=pop_late)

        elif sid == "ep2_s2":
            # Both scammers surrounding hero!
            frame = paste_obj(frame, white_car_hit, 20, 1015)
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="alert", mouth_state="closed", gesture="hold_phone", blink=blink, facing="right", scale=0.88)
            boss = render_boss_character(mood="shady", mouth_state=mouth, gesture="hold_money", facing="left", scale=0.93)
            acc = render_accomplice(mood="shady", mouth_state="closed", gesture="point_left", facing="left", scale=0.88)
            frame = paste_char(frame, hero, 205, 1320)
            frame = paste_char(frame, boss, 630, 1320)
            frame = paste_char(frame, acc, 885, 1320)
            shake = ((1.0 - t_local / 0.5) ** 1.4) if t_local <= 0.5 else 0.0
            frame = camera.apply(frame, zoom=1.03 + 0.06 * p_ch, focal_point=(540, 1060), shake_intensity=shake, t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Ладно, давай 200 тысяч и разъедемся!»", anchor_x=630, anchor_y=810, align="right", pop_scale=pop_late)

        elif sid == "ep2_s3":
            # DPS patrol car pulls in + DPS Inspector steps out!
            car_x = int(1120 - ease_out_back(min(1.0, t_local / 1.1)) * 610)
            frame = paste_obj(frame, white_car_hit, 10, 1020)
            frame = paste_obj(frame, dps_car, car_x, 990)
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="confident", mouth_state="closed", gesture="point_right", blink=blink, facing="right", scale=0.88)
            dps = render_dps_officer(mood="confident", mouth_state=mouth, gesture="point_left", facing="left", scale=0.93)
            frame = paste_char(frame, hero, 215, 1325)
            frame = paste_char(frame, dps, 845, 1325)
            frame = draw_siren_flash(frame, t)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1060), t=t)
            if t_local > 0.5:
                draw_smart_bubble(frame, "«Инспектор ДПС! Предъявите запись!»", anchor_x=820, anchor_y=820, align="right", pop_scale=pop_late)

        elif sid == "ep2_s4":
            # SD Card Error Cliffhanger!
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="shocked", mouth_state=mouth, gesture="hands_on_head", blink=False, facing="right", scale=0.94)
            frame = paste_char(frame, hero, 300, 1320)
            shake = ((1.0 - t_local / 0.6) ** 1.4) if t_local <= 0.6 else 0.0
            frame = camera.apply(frame, zoom=1.04 + 0.06 * p_ch, focal_point=(540, 960), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "НЕТ ЗАПИСИ!", t_local - 0.15, center=(730, 930))
            if t_local > 0.4:
                draw_smart_bubble(frame, "«КАК ПОВРЕЖДЕНА?! ЧТО ДЕЛАТЬ?!»", anchor_x=340, anchor_y=850, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 3: КАМЕРЫ МКАДА И БАЗА БАНДЫ
        # ================================================================
        elif sid == "ep3_s1":
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.92)
            lawyer = render_special_character(role="lawyer", mood="confident", mouth_state="closed", gesture="point_left", blink=blink, facing="left", scale=0.94)
            frame = paste_char(frame, lawyer, 845, 1300)
            frame = paste_char(frame, hero, 245, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Без паники — запросим камеры МКАДа!»", anchor_x=820, anchor_y=800, align="right", pop_scale=pop_late)

        elif sid == "ep3_s2":
            # CCTV Room with clear bottle-throw evidence on giant screen!
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="smug", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.92)
            lawyer = render_special_character(role="lawyer", mood="smug", mouth_state="closed", gesture="point_left", blink=blink, facing="left", scale=0.93)
            frame = paste_char(frame, hero, 260, 1305)
            frame = paste_char(frame, lawyer, 825, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 960), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Вот она — бутылка летит прямо в крыло!»", anchor_x=300, anchor_y=820, align="left", pop_scale=pop_late)

        elif sid == "ep3_s3":
            # Criminal Dossier Board: 17 scams / 5.4M rubles!
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="shocked", mouth_state=mouth, gesture="hands_on_head", blink=False, facing="right", scale=0.92)
            lawyer = render_special_character(role="lawyer", mood="alert", mouth_state="closed", gesture="hold_phone", blink=blink, facing="left", scale=0.93)
            frame = paste_char(frame, hero, 250, 1305)
            frame = paste_char(frame, lawyer, 830, 1305)
            shake = ((1.0 - t_local / 0.55) ** 1.4) if t_local <= 0.55 else 0.0
            frame = camera.apply(frame, zoom=1.03 + 0.06 * p_ch, focal_point=(540, 960), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "17 ПОДСТАВ!", t_local - 0.15, center=(540, 860))

        elif sid == "ep3_s4":
            # Hero + Lawyer + DPS Officer planning the sting!
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="smug", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.90)
            dps = render_dps_officer(mood="confident", mouth_state="closed", gesture="point_left", facing="left", scale=0.92)
            frame = paste_char(frame, hero, 240, 1300)
            frame = paste_char(frame, dps, 840, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Завтра берём их с поличным на МКАДе!»", anchor_x=815, anchor_y=800, align="right", pop_scale=pop_late)

        # ================================================================
        # EPISODE 4: ОПЕРАЦИЯ НА ТРАССЕ — ЛОВЛЯ НА ЖИВЦА!
        # ================================================================
        elif sid == "ep4_s1":
            # Bait white car + undercover DPS car cruising behind!
            wx = int(420 + p_ch * 140)
            dx = int(-60 + p_ch * 180)
            frame = paste_obj(frame, dps_car, dx, 945)
            frame = paste_obj(frame, white_car, wx, 1030)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1050), t=t)
            frame = draw_rec_camera_overlay(frame, t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Экипажи на позиции. Выходим на цель!»", anchor_x=540, anchor_y=920, align="center", pop_scale=pop_late)

        elif sid == "ep4_s2":
            # Scammer falls for the bait again!
            frame = paste_obj(frame, white_car, 20, 1015)
            frame = paste_obj(frame, black_car, 510, 995)
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="smug", mouth_state="closed", gesture="hold_phone", blink=blink, facing="right", scale=0.90)
            boss = render_boss_character(mood="shady", mouth_state=mouth, gesture="point_left", facing="left", scale=0.95)
            frame = paste_char(frame, hero, 225, 1320)
            frame = paste_char(frame, boss, 825, 1320)
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 1060), t=t)
            frame = draw_rec_camera_overlay(frame, t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«300 тысяч сюда — и без разговоров!»", anchor_x=800, anchor_y=820, align="right", pop_scale=pop_late)

        elif sid == "ep4_s3":
            # Handing over glowing marked cash!
            frame = paste_obj(frame, white_car, 20, 1015)
            frame = paste_obj(frame, black_car, 510, 995)
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="smug", mouth_state=mouth, gesture="hold_money", blink=blink, facing="right", scale=0.90)
            boss = render_boss_character(mood="smug", mouth_state="closed", gesture="hold_money", facing="left", scale=0.95)
            frame = paste_char(frame, hero, 260, 1320)
            frame = paste_char(frame, boss, 790, 1320)
            frame = camera.apply(frame, zoom=1.03 + 0.05 * p_ch, focal_point=(540, 1060), t=t)
            frame = draw_rec_camera_overlay(frame, t)
            frame = draw_animated_stamp(frame, "МЕЧЕНЫЕ!", t_local - 0.15, center=(540, 560))
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Пересчитывай... Работайте, парни!»", anchor_x=300, anchor_y=820, align="left", pop_scale=pop_late)

        elif sid == "ep4_s4":
            # Full highway arrest! Patrol car blocks road + DPS officers arrest both scammers!
            frame = paste_obj(frame, dps_car, 260, 975)
            dps = render_dps_officer(mood="alert", mouth_state=mouth, gesture="point_right", facing="right", scale=0.92)
            boss = render_boss_character(mood="shocked", mouth_state="open", gesture="hands_on_head", facing="left", scale=0.92)
            acc = render_accomplice(mood="shocked", mouth_state="open", gesture="hands_on_head", facing="left", scale=0.88)
            frame = paste_char(frame, dps, 200, 1320)
            frame = paste_char(frame, boss, 610, 1320)
            frame = paste_char(frame, acc, 880, 1320)
            frame = draw_siren_flash(frame, t)
            shake = ((1.0 - t_local / 0.6) ** 1.4) if t_local <= 0.6 else 0.0
            frame = camera.apply(frame, zoom=1.04 + 0.05 * p_ch, focal_point=(540, 1060), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "ЗАДЕРЖАНЫ!", t_local - 0.15, center=(540, 560))
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Руки за голову! Вы взяты с поличным!»", anchor_x=240, anchor_y=810, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 5 (FINALE): СУД, КОНФИСКАЦИЯ И КАРМА!
        # ================================================================
        elif sid == "ep5_s1":
            # Interrogation room: Boss & Accomplice blaming each other under lamp!
            dps = render_dps_officer(mood="confident", mouth_state="closed", gesture="point_right", facing="right", scale=0.92)
            boss = render_boss_character(mood="shocked", mouth_state="open", gesture="hands_on_head", facing="left", scale=0.90)
            acc = render_accomplice(mood="sad", mouth_state=mouth, gesture="point_left", facing="left", scale=0.88)
            frame = paste_char(frame, dps, 205, 1310)
            frame = paste_char(frame, boss, 595, 1310)
            frame = paste_char(frame, acc, 885, 1310)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1040), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Это всё он придумал! Я просто кидал!»", anchor_x=860, anchor_y=810, align="right", pop_scale=pop_late)

        elif sid == "ep5_s2":
            # Courtroom Verdict: 5 years prison + black car confiscated!
            judge = render_special_character(role="judge", mood="confident", mouth_state=mouth, facing="left", scale=0.92)
            frame = paste_char(frame, judge, 540, 1180)
            frame = paste_obj(frame, judge_bench, 540 - judge_bench.width // 2, 1005)
            hero = render_full_body_character(outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut", mood="smug", mouth_state="closed", gesture="hold_money", blink=blink, facing="right", scale=0.90)
            boss = render_boss_character(mood="shocked", mouth_state="open", gesture="hands_on_head", facing="left", scale=0.90)
            frame = paste_char(frame, hero, 200, 1305)
            frame = paste_char(frame, boss, 885, 1305)
            shake = ((1.0 - t_local / 0.55) ** 1.4) if t_local <= 0.55 else 0.0
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 990), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "5 ЛЕТ ТЮРЬМЫ!", t_local - 0.15, center=(740, 485))
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Виновны! Автомобиль конфисковать!»", anchor_x=500, anchor_y=755, align="left", pop_scale=pop_late)

        elif sid == "ep5_s3":
            # Bank Compensation & Justice!
            frame = draw_money_rain(frame, t)
            hero = render_special_character(role="hero_cool", mood="smug", mouth_state=mouth, gesture="hold_money", facing="right", scale=0.94)
            lawyer = render_special_character(role="lawyer", mood="smug", mouth_state="closed", gesture="hold_money", blink=blink, facing="left", scale=0.92)
            frame = paste_char(frame, hero, 260, 1305)
            frame = paste_char(frame, lawyer, 830, 1305)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Все 17 водителей получили деньги назад!»", anchor_x=310, anchor_y=800, align="left", pop_scale=pop_late)

        else:  # ep5_s4 — Sunny Finale & Advice to Drivers!
            frame = draw_money_rain(frame, t)
            hero = render_special_character(role="hero_cool", mood="smug", mouth_state=mouth, gesture="point_right", facing="right", scale=0.95)
            frame = paste_char(frame, hero, 285, 1315)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1040), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Никогда не плати на месте — звони в ДПС!»", anchor_x=330, anchor_y=800, align="left", pop_scale=pop_late)

        draw_sleek_hud(frame, balance_text=ch["hud_bal"], status_text=ch["hud_st"], theme=ch["theme"])
        draw_compact_pill(frame, text=ch["pill"])
        return frame

    print(f"[S2 EP{ep_num}] 2. Рендерим 4-сценовую анимацию ({ep['title']})...")
    total_frames = int(duration * fps)
    raw_video = work_dir / f"raw_ep{ep_num}.mp4"

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

    print(f"[S2 EP{ep_num}] 3. Финальная сборка MP4...")
    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
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

    print(f"[OK] Серия {ep_num}/5 готова -> {output_path}")
    return output_path


def render_full_season2(speaker: str = "f5", fps: int = 30) -> List[Path]:
    """Renders ALL 5 episodes of Season 2 ('Автоподстава') in one batch!"""
    print("=" * 64)
    print("  SEASON 2: 'АВТОПОДСТАВА' — BATCH RENDER ALL 5 EPISODES")
    print("=" * 64)
    shared_bgs = build_season2_backgrounds()
    outputs = []
    for ep_num in range(1, 6):
        out = render_season2_episode(ep_num, speaker=speaker, fps=fps, shared_bgs=shared_bgs)
        outputs.append(out)
    print("=" * 64)
    print("  ALL 5 EPISODES OF SEASON 2 COMPLETED SUCCESSFULLY!")
    print("=" * 64)
    return outputs
