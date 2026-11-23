"""
Standalone 5-Part Animated Mini-Series:
"ПРИГОН АВТО ИЗ КОРЕИ И ЕВРОПЫ — ПОБЕГ БРОКЕРА В ДУБАЙ" (v3 PRO Engine).

100% Brand-New Characters & Brand-New 2x-Supersampled Locations:

Characters:
- Sergey (husband, determined family man in navy jacket & groomed beard)
- Lena (wife, smart woman in emerald cardigan with flowing hair)
- Auto-Broker Artur (slick conman in camel-beige coat, silk scarf & leather suitcase)
- Customs Inspector (official in dark-green Federal Customs Service uniform with gold epaulets)
- Airport Border Officer (police/border control officer in airport security uniform)

Locations:
- Luxury Broker Office (panoramic skyscraper view, giant glowing world logistics map)
- Seaport Container Dock (giant container ship with MAERSK/COSCO boxes, portal cranes)
- Customs Terminal (FTS barrier post, official database terminal)
- Airport Departure Hall (huge digital board "MOSCOW -> DUBAI • BOARDING")
- Passport Control Gates (border control booths, turnstiles, 15 minutes before flight)
- Justice Finale Plaza (handcuffed broker, open suitcase with cash, victory graphics)
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
# 1. BRAND-NEW CHARACTERS FOR "ПРИГОН АВТО: ПОБЕГ В ДУБАЙ"
# ---------------------------------------------------------------------------

def render_sergey(
    mood: str = "confident",
    mouth_state: str = "closed",
    gesture: str = "relax",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    holding_contract: bool = False,
    scale: float = 0.94,
) -> Image.Image:
    """Sergey — determined family man in navy jacket with groomed short beard."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(30, 41, 59), hair_style="slicked",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    shift = 8 if facing == "right" else -8

    # Short groomed brown beard along jawline
    d.arc([cx - 54 + shift // 2, 202, cx + 54 + shift // 2, 258], start=18, end=162, fill=(60, 48, 38, 255), width=14)

    # Contract document in hand
    if holding_contract:
        hx = cx + 80 if facing == "right" else cx - 80
        hy = 340
        d.rounded_rectangle([(hx - 18, hy - 25), (hx + 24, hy + 30)], radius=3, fill=(255, 255, 255, 255), outline=INK, width=2)
        d.rectangle([(hx - 12, hy - 18), (hx + 18, hy - 10)], fill=(37, 99, 235, 255))
        d.line([(hx - 12, hy + 2), (hx + 16, hy + 2)], fill=(148, 163, 184, 255), width=2)
        d.line([(hx - 12, hy + 12), (hx + 16, hy + 12)], fill=(148, 163, 184, 255), width=2)

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_lena(
    mood: str = "confident",
    mouth_state: str = "closed",
    gesture: str = "relax",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    holding_phone: bool = False,
    scale: float = 0.91,
) -> Image.Image:
    """Lena — smart stylish wife in emerald-green cardigan with flowing brown hair."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(16, 118, 110), hair_style="messy",
        mood=mood, mouth_state=mouth_state, gesture=("hold_phone" if holding_phone else gesture),
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    shift = 8 if facing == "right" else -8

    # Flowing long chestnut hair cascading over shoulders
    hair_c = (78, 48, 36, 255)
    if facing == "right":
        d.chord([cx - 85, 140, cx - 20, 320], start=90, end=270, fill=hair_c, outline=INK, width=3)
        d.arc([cx - 35, 120, cx + 55, 180], start=180, end=330, fill=hair_c, width=12)
    else:
        d.chord([cx + 20, 140, cx + 85, 320], start=270, end=90, fill=hair_c, outline=INK, width=3)
        d.arc([cx - 55, 120, cx + 35, 180], start=210, end=360, fill=hair_c, width=12)

    # Feminine eyelashes & cheek blush
    ey = 186
    ex_l = cx - 22 + shift
    ex_r = cx + 22 + shift
    d.line([(ex_l - 12, ey - 10), (ex_l - 6, ey - 6)], fill=INK, width=2)
    d.line([(ex_r + 6, ey - 6), (ex_r + 12, ey - 10)], fill=INK, width=2)
    d.ellipse([ex_l - 16, ey + 10, ex_l + 2, ey + 20], fill=(251, 113, 133, 90))
    d.ellipse([ex_r - 2, ey + 10, ex_r + 16, ey + 20], fill=(251, 113, 133, 90))

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_broker(
    mood: str = "smug",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "left",
    holding_suitcase: bool = True,
    scale: float = 0.95,
) -> Image.Image:
    """Auto-Broker Artur — slick conman in luxurious camel-beige coat & silk scarf."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(214, 180, 136), hair_style="slicked",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2

    # Burgundy silk scarf tucked inside coat collar
    d.polygon([(cx - 20, 248), (cx, 320), (cx + 20, 248)], fill=(136, 19, 55, 255), outline=INK, width=2)

    # Gold Rolex watch on wrist
    d.rectangle([(cx - 78, 342), (cx - 64, 356)], fill=(234, 179, 8, 255), outline=INK, width=2)

    # Expensive leather travel suitcase with gold latches & airport baggage tags
    if holding_suitcase:
        hx = cx - 85 if facing == "left" else cx + 85
        hy = 360
        # Leather suitcase body
        d.rounded_rectangle([(hx - 28, hy - 15), (hx + 28, hy + 50)], radius=8, fill=(120, 53, 15, 255), outline=INK, width=3)
        # Gold latches & corner reinforcements
        d.rectangle([(hx - 24, hy - 5), (hx - 16, hy + 5)], fill=(234, 179, 8, 255))
        d.rectangle([(hx + 16, hy - 5), (hx + 24, hy + 5)], fill=(234, 179, 8, 255))
        # Telescopic handle sticking up to hand
        d.line([(hx - 10, hy - 15), (hx - 10, hy - 35)], fill=(148, 163, 184, 255), width=3)
        d.line([(hx + 10, hy - 15), (hx + 10, hy - 35)], fill=(148, 163, 184, 255), width=3)
        d.line([(hx - 14, hy - 35), (hx + 14, hy - 35)], fill=(15, 23, 42, 255), width=4)
        # White baggage tag: "DXB / DUBAI"
        d.rectangle([(hx - 20, hy + 20), (hx + 5, hy + 40)], fill=(255, 255, 255, 255), outline=INK)
        d.text((hx - 18, hy + 22), "DXB", fill=(220, 38, 38, 255), font=_font(FONT_BOLD, 9))

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_customs_officer(
    mood: str = "alert",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    scale: float = 0.94,
) -> Image.Image:
    """Customs Inspector — Federal Customs Service (ФТС) officer in dark-green uniform."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(20, 83, 45), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2

    # Gold customs epaulets on shoulders
    d.rectangle([(cx - 62, 240), (cx - 40, 256)], fill=(234, 179, 8, 255), outline=INK, width=2)
    d.rectangle([(cx + 40, 240), (cx + 62, 256)], fill=(234, 179, 8, 255), outline=INK, width=2)

    # Green tie & gold badge
    d.polygon([(cx - 6, 255), (cx + 6, 255), (cx + 8, 335), (cx, 345), (cx - 8, 335)], fill=(15, 23, 42, 255))
    d.rounded_rectangle([(cx - 38, 280), (cx + 38, 304)], radius=3, fill=(254, 240, 138, 255), outline=INK, width=2)
    d.text((cx - 26, 284), "ТАМОЖНЯ", fill=INK, font=_font(FONT_BOLD, 9))

    # Tablet with official database
    hx = cx + 80 if facing == "right" else cx - 80
    hy = 340
    d.rounded_rectangle([(hx - 20, hy - 30), (hx + 24, hy + 30)], radius=4, fill=(15, 23, 42, 255), outline=INK, width=2)
    d.rectangle([(hx - 16, hy - 24), (hx + 20, hy + 24)], fill=(56, 189, 248, 255))
    d.text((hx - 14, hy - 12), "VIN: 0", fill=(220, 38, 38, 255), font=_font(FONT_BOLD, 10))

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_border_police(
    mood: str = "alert",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    facing: str = "right",
    scale: float = 0.94,
) -> Image.Image:
    """Airport Border Security Police Officer in dark navy with peaked cap."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(15, 23, 42), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2

    # Peaked police cap with gold cockade badge
    d.chord([cx - 76, 95, cx + 76, 175], start=180, end=360, fill=(30, 41, 59, 255), outline=INK, width=4)
    d.rectangle([(cx - 74, 150), (cx + 74, 166)], fill=(15, 23, 42, 255), outline=INK, width=2)
    d.ellipse([cx - 10, 132, cx + 10, 152], fill=(234, 179, 8, 255), outline=INK, width=2)

    # Steel handcuffs in hand
    hx = cx + 80 if facing == "right" else cx - 80
    hy = 340
    d.ellipse([hx - 16, hy - 14, hx - 2, hy], fill=(203, 213, 225, 255), outline=INK, width=2)
    d.ellipse([hx + 2, hy - 14, hx + 16, hy], fill=(203, 213, 225, 255), outline=INK, width=2)
    d.line([(hx - 2, hy - 7), (hx + 2, hy - 7)], fill=INK, width=3)

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 2. VEHICLE & PROPS SPRITES
# ---------------------------------------------------------------------------

def build_korean_suv_sprite() -> Image.Image:
    """Dream Korean white crossover SUV sprite (Kia Sorento / Hyundai Santa Fe)."""
    S = 2
    W, H = 560 * S, 250 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _draw_car(d, cx=280 * S, wheel_y=182 * S, S=S, body_color=(248, 250, 252), split_gap=0)
    # Sleek roof rails
    d.line([(205 * S, 42 * S), (355 * S, 42 * S)], fill=INK, width=6 * S)
    # Tinted panoramic sunroof
    d.polygon([(230 * S, 48 * S), (330 * S, 48 * S), (340 * S, 80 * S), (220 * S, 80 * S)], fill=(30, 41, 59, 200))
    return img.resize((560, 250), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 3. 2X-SUPERSAMPLED BACKGROUND BUILDER (6 UNIQUE LOCATIONS)
# ---------------------------------------------------------------------------

def build_broker_backgrounds() -> Dict[str, Image.Image]:
    """Generates all high-res backgrounds for the international auto import broker story."""
    S = 2
    W, H = 1080 * S, 1920 * S
    bgs = {}

    # ------------------------------------------------------------------
    # LOC 1: LUXURY BROKER OFFICE (Panoramic Skyscraper View + World Map)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (241, 245, 249, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Panoramic Skyscraper Windows (View of high-rise city towers)
    d.rectangle([(60 * S, 180 * S), (1020 * S, 620 * S)], fill=(224, 242, 254, 240), outline=INK, width=6 * S)
    for bx, bw, bh in [(100, 160, 360), (300, 200, 420), (540, 180, 380), (760, 220, 400)]:
        d.rectangle([(bx * S, 620 * S - bh * S), ((bx + bw) * S, 620 * S)], fill=(148, 163, 184, 180), outline=INK, width=3 * S)
    # Window frames
    for wx in [300 * S, 540 * S, 780 * S]:
        d.line([(wx, 180 * S), (wx, 620 * S)], fill=INK, width=5 * S)

    # GIANT WORLD LOGISTICS MAP ON ACCENT WALL
    map_y = 660 * S
    d.rounded_rectangle([(80 * S, map_y), (1000 * S, map_y + 260 * S)], radius=16 * S, fill=(15, 23, 42, 255), outline=(214, 180, 136, 255), width=5 * S)
    # Neon route lines: Korea -> Vladivostok -> Moscow / Germany -> Moscow
    f_map = _font(FONT_BOLD, 22 * S)
    d.text((120 * S, map_y + 25 * S), "МЕЖДУНАРОДНЫЙ ИМПОРТ • АВТО ИЗ КОРЕИ И ЕВРОПЫ", fill=(214, 180, 136, 255), font=f_map)
    # Continents silhouettes simplified
    d.ellipse([140 * S, map_y + 80 * S, 320 * S, map_y + 210 * S], fill=(51, 65, 85, 255))
    d.ellipse([420 * S, map_y + 70 * S, 880 * S, map_y + 220 * S], fill=(51, 65, 85, 255))
    # Glowing green and yellow route arrows
    d.line([(820 * S, map_y + 140 * S), (520 * S, map_y + 110 * S)], fill=(34, 197, 94, 255), width=4 * S)
    d.text((810 * S, map_y + 160 * S), "СЕУЛ 🇰🇷", fill=(34, 197, 94, 255), font=_font(FONT_BOLD, 18 * S))
    d.text((480 * S, map_y + 80 * S), "МОСКВА 🇷🇺", fill=(250, 204, 21, 255), font=_font(FONT_BOLD, 18 * S))

    # Glass desk in foreground
    d.rectangle([(160 * S, 960 * S), (920 * S, floor_y)], fill=(30, 41, 59, 255), outline=INK, width=5 * S)
    d.rectangle([(120 * S, 940 * S), (960 * S, 970 * S)], fill=(148, 163, 184, 255), outline=INK, width=4 * S)

    # Document on desk: "ДОГОВОР ПОСТАВКИ: 2 500 000 ₽"
    d.rounded_rectangle([(320 * S, 800 * S), (760 * S, 940 * S)], radius=6 * S, fill=(255, 255, 255, 255), outline=INK, width=4 * S)
    d.rectangle([(335 * S, 815 * S), (745 * S, 845 * S)], fill=(37, 99, 235, 255))
    d.text((345 * S, 820 * S), "ДОГОВОР ПОСТАВКИ АВТО", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 18 * S))
    d.text((345 * S, 860 * S), "Аванс под ключ: 2 500 000 ₽", fill=(220, 38, 38, 255), font=_font(FONT_BOLD, 22 * S))

    # Marble showroom floor
    d.rectangle([(0, floor_y), (W, H)], fill=(226, 232, 240, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["luxury_office"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 2: SEAPORT CONTAINER DOCK (Giant Container Ship + Cranes)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (14, 116, 144, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Ocean sky
    for y in range(0, floor_y, 4):
        rat = y / floor_y
        d.rectangle([(0, y), (W, y + 4)], fill=(int(186 - rat * 30), int(230 - rat * 30), int(253 - rat * 20), 255))

    # Deep blue sea water line
    water_y = 740 * S
    d.rectangle([(0, water_y), (W, floor_y)], fill=(3, 105, 161, 255))

    # Giant Cargo Container Ship Hull in water!
    d.polygon([(40 * S, water_y + 120 * S), (1020 * S, water_y + 120 * S), (940 * S, water_y + 240 * S), (120 * S, water_y + 240 * S)], fill=(185, 28, 28, 255), outline=INK, width=5 * S)
    # Stacks of colorful shipping containers on deck (MAERSK / COSCO)
    colors = [(37, 99, 235), (234, 88, 12), (22, 163, 74), (202, 138, 4)]
    ci = 0
    for cy_idx in range(3):
        for cx_idx in range(7):
            bx = (140 + cx_idx * 115) * S
            by = (water_y - 20 - cy_idx * 45) * S
            d.rectangle([(bx, by), (bx + 105 * S, by + 40 * S)], fill=colors[ci % len(colors)], outline=INK, width=3 * S)
            ci += 1

    # Giant Portal Gantry Cranes in background
    for cr_x in [220 * S, 780 * S]:
        d.line([(cr_x - 80 * S, water_y + 180 * S), (cr_x, 260 * S)], fill=(250, 204, 21, 255), width=8 * S)
        d.line([(cr_x + 80 * S, water_y + 180 * S), (cr_x, 260 * S)], fill=(250, 204, 21, 255), width=8 * S)
        d.line([(cr_x - 140 * S, 260 * S), (cr_x + 140 * S, 260 * S)], fill=(250, 204, 21, 255), width=10 * S)

    # Concrete dock pier in foreground
    d.rectangle([(0, floor_y), (W, H)], fill=(203, 213, 225, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    # Yellow and black safety hazard edge strip
    for hx in range(0, W, 80 * S):
        d.polygon([(hx, floor_y), (hx + 40 * S, floor_y), (hx + 20 * S, floor_y + 30 * S), (hx - 20 * S, floor_y + 30 * S)], fill=(250, 204, 21, 255))
        d.polygon([(hx + 20 * S, floor_y + 30 * S), (hx + 40 * S, floor_y), (hx + 60 * S, floor_y), (hx + 40 * S, floor_y + 30 * S)], fill=INK)

    bgs["seaport_containers"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 3: CUSTOMS TERMINAL (FTS Post + Computer Database)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (241, 245, 249, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Official Customs Administrative wall
    d.rectangle([(0, 0), (W, floor_y)], fill=(241, 245, 249, 255))
    # Green and gold corporate stripe of Federal Customs Service
    d.rectangle([(0, 260 * S), (W, 360 * S)], fill=(20, 83, 45, 255), outline=INK, width=4 * S)
    f_fts = _font(FONT_IMPACT, 42 * S)
    ftst = "ФЕДЕРАЛЬНАЯ ТАМОЖЕННАЯ СЛУЖБА РФ"
    ftsb = f_fts.getbbox(ftst)
    d.text(((W - (ftsb[2] - ftsb[0])) // 2, 285 * S), ftst, fill=(254, 240, 138, 255), font=f_fts)

    # Red-and-White striped customs barrier boom
    d.rectangle([(140 * S, 960 * S), (200 * S, floor_y)], fill=(220, 38, 38, 255), outline=INK, width=4 * S)
    d.rectangle([(170 * S, 980 * S), (980 * S, 1020 * S)], fill=(255, 255, 255, 255), outline=INK, width=4 * S)
    for sx in range(210 * S, 950 * S, 120 * S):
        d.rectangle([(sx, 982 * S), (sx + 60 * S, 1018 * S)], fill=(220, 38, 38, 255))

    # Giant Red Alert Window in center: "VIN НЕ НАЙДЕН В БАЗЕ ФТС!"
    d.rounded_rectangle([(160 * S, 520 * S), (920 * S, 820 * S)], radius=16 * S, fill=(254, 242, 242, 255), outline=(220, 38, 38, 255), width=6 * S)
    d.rectangle([(160 * S, 520 * S), (920 * S, 600 * S)], fill=(220, 38, 38, 255))
    f_alt = _font(FONT_IMPACT, 38 * S)
    at = "ОШИБКА: VIN ОТСУТСТВУЕТ В БАЗЕ!"
    ab = f_alt.getbbox(at)
    d.text(((W - (ab[2] - ab[0])) // 2, 540 * S), at, fill=(255, 255, 255, 255), font=f_alt)

    f_inf = _font(FONT_BOLD, 24 * S)
    d.text((200 * S, 630 * S), "Автомобиль таможню НЕ проходил", fill=(30, 41, 59, 255), font=f_inf)
    d.text((200 * S, 680 * S), "Утильсбор 800 000 ₽ — ФАЛЬШИВКА!", fill=(220, 38, 38, 255), font=f_inf)
    d.text((200 * S, 730 * S), "Квитанции нарисованы в Фотошопе!", fill=(100, 116, 139, 255), font=f_inf)

    # Asphalt floor
    d.rectangle([(0, floor_y), (W, H)], fill=(226, 232, 240, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["customs_terminal"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 4: AIRPORT DEPARTURE HALL (Giant Flight Board "MOSCOW -> DUBAI")
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Airport modern terminal interior ceiling
    d.rectangle([(0, 0), (W, floor_y)], fill=(30, 41, 59, 255))
    for tx in range(0, W, 180 * S):
        d.line([(tx, 0), (tx, 220 * S)], fill=(71, 85, 105, 255), width=4 * S)

    # GIANT ELECTRONIC FLIGHT STATUS BOARD (DEPARTURES)
    d.rounded_rectangle([(80 * S, 240 * S), (1000 * S, 820 * S)], radius=18 * S, fill=(10, 15, 26, 255), outline=(71, 85, 105, 255), width=6 * S)
    # Header
    d.rectangle([(80 * S, 240 * S), (1000 * S, 320 * S)], fill=(250, 204, 21, 255))
    f_brd = _font(FONT_IMPACT, 42 * S)
    d.text((120 * S, 260 * S), "ВЫЛЕТЫ • DEPARTURES • ТЕРМИНАЛ C", fill=INK, font=f_brd)

    # Flight Rows
    flights = [
        ("13:50", "SU-214", "СТАМБУЛ", "ВЫЛЕТЕЛ", (148, 163, 184)),
        ("14:15", "EK-132", "ДОХА", "ПОСАДКА", (250, 204, 21)),
        ("14:30", "SU-524", "ДУБАЙ 🇦🇪", "ПОСАДКА ЗАКАНЧИВАЕТСЯ!", (239, 68, 68)),
        ("15:00", "FZ-988", "БАНГКОК", "РЕГИСТРАЦИЯ", (148, 163, 184)),
    ]
    f_fl = _font(FONT_BOLD, 24 * S)
    f_fl_bold = _font(FONT_IMPACT, 28 * S)
    row_y = 360 * S
    for tm, code, dst, st, clr in flights:
        if "ДУБАЙ" in dst:
            # Highlight Dubai row with pulsing red frame!
            d.rounded_rectangle([(100 * S, row_y - 10 * S), (980 * S, row_y + 80 * S)], radius=8 * S, fill=(220, 38, 38, 60), outline=(239, 68, 68, 255), width=4 * S)
        d.text((120 * S, row_y), tm, fill=(255, 255, 255, 255), font=f_fl)
        d.text((240 * S, row_y), code, fill=(254, 240, 138, 255), font=f_fl)
        d.text((400 * S, row_y), dst, fill=(255, 255, 255, 255), font=f_fl_bold)
        d.text((640 * S, row_y), st, fill=clr, font=f_fl_bold)
        row_y += 105 * S

    # Polished airport terminal floor reflecting lights
    d.rectangle([(0, floor_y), (W, H)], fill=(203, 213, 225, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["airport_departure_hall"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 5: PASSPORT CONTROL GATES (Border Control Booths)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (30, 41, 59, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Passport Control overhead sign: "ПАСПОРТНЫЙ КОНТРОЛЬ / PASSPORT CONTROL"
    d.rectangle([(0, 200 * S), (W, 360 * S)], fill=(37, 99, 235, 255), outline=INK, width=5 * S)
    f_pas = _font(FONT_IMPACT, 44 * S)
    pt = "ПАСПОРТНЫЙ КОНТРОЛЬ • BORDER CONTROL"
    pb = f_pas.getbbox(pt)
    d.text(((W - (pb[2] - pb[0])) // 2, 230 * S), pt, fill=(255, 255, 255, 255), font=f_pas)
    d.text((420 * S, 295 * S), "ВЫХОД НА ПОСАДКУ К ГЕЙТАМ 1-24", fill=(254, 240, 138, 255), font=_font(FONT_BOLD, 22 * S))

    # Border Control Glass Booths
    for bx in [240 * S, 700 * S]:
        d.rectangle([(bx, 480 * S), (bx + 280 * S, floor_y)], fill=(51, 65, 85, 255), outline=INK, width=5 * S)
        d.rectangle([(bx + 30 * S, 520 * S), (bx + 250 * S, 800 * S)], fill=(219, 234, 254, 200), outline=INK, width=4 * S)
        d.line([(bx + 30 * S, 800 * S), (bx + 250 * S, 800 * S)], fill=INK, width=6 * S)

    # Crowd barrier poles with red velvet ropes
    for px in [140 * S, 480 * S, 880 * S]:
        d.line([(px, 860 * S), (px, floor_y)], fill=(234, 179, 8, 255), width=8 * S)
        d.ellipse([px - 14 * S, 846 * S, px + 14 * S, 874 * S], fill=(234, 179, 8, 255), outline=INK, width=2 * S)
    d.arc([140 * S, 860 * S, 480 * S, 960 * S], start=0, end=180, fill=(220, 38, 38, 255), width=8 * S)
    d.arc([480 * S, 860 * S, 880 * S, 960 * S], start=0, end=180, fill=(220, 38, 38, 255), width=8 * S)

    # Floor
    d.rectangle([(0, floor_y), (W, H)], fill=(226, 232, 240, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["passport_control_gates"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 6: JUSTICE FINALE PLAZA (Sunny City + Reunited Savings & SUV)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (224, 242, 254, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Fresh blue sky gradient
    for y in range(0, floor_y, 4):
        rat = y / floor_y
        d.rectangle([(0, y), (W, y + 4)], fill=(int(186 - rat * 20), int(230 - rat * 15), int(253), 255))

    # Bright morning sun
    d.ellipse([780 * S, 180 * S, 940 * S, 340 * S], fill=(254, 240, 138, 255), outline=(250, 204, 21, 255), width=6 * S)

    # Modern city skyline
    for bx, bw, bh in [(30, 260, 800), (330, 340, 920), (710, 340, 780)]:
        d.rectangle([(bx * S, floor_y - bh * S), ((bx + bw) * S, floor_y)], fill=(203, 213, 225, 255), outline=INK, width=4 * S)

    # Sunlit plaza floor
    d.rectangle([(0, floor_y), (W, H)], fill=(241, 245, 249, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["justice_finale_plaza"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    return bgs


# ---------------------------------------------------------------------------
# 4. STORY EPISODES DATA (5 FULL-LENGTH EPISODES)
# ---------------------------------------------------------------------------

BROKER_EPISODES = {
    1: {
        "filename": "broker_ep1_contract.mp4",
        "title": "Пригон авто из Кореи • Часть 1: Аванс 2.5 миллиона",
        "chapters": [
            {
                "scene_id": "br1_s1",
                "loc": "luxury_office",
                "sentences": [
                    "Сергей и Лена копили на новый семейный кроссовер четыре года и пришли в пафосный офис международного авто-брокера в Сити.",
                    "Лощёный менеджер в бежевом пальто улыбнулся: «Привезём идеальный автомобиль напрямую из Кореи всего за тридцать дней!»",
                ],
                "hud_bal": "2 500 000 ₽",
                "hud_st": "ОФОРМЛЕНИЕ ДОГОВОРА",
                "theme": "green",
                "pill": "МОСКВА-СИТИ • ОФИС БРОКЕРА",
                "sfx": "coin",
            },
            {
                "scene_id": "br1_s2",
                "loc": "luxury_office",
                "sentences": [
                    "Супруги подписали официальный договор и перевели два с половиной миллиона рублей аванса.",
                    "Брокер Артур клятвенно обещал присылать видеоотчёты с погрузки авто на контейнеровоз.",
                ],
                "hud_bal": "АВАНС ОПЛАЧЕН",
                "hud_st": "ОЖИДАНИЕ ДОСТАВКИ",
                "theme": "green",
                "pill": "ПОДПИСАНИЕ ДОГОВОРА • 100% ГАРАНТИЯ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "br1_s3",
                "loc": "seaport_containers",
                "sentences": [
                    "Спустя три недели брокер скинул короткое видео из порта Владивостока с белым кроссовером на фоне контейнеров.",
                    "Но на следующий день в трубке раздался его тревожный голос!",
                ],
                "hud_bal": "ПОРТ ДОСТАВКИ",
                "hud_st": "ВИДЕО ИЗ ПОРТА",
                "theme": "alert",
                "pill": "МОРСКОЙ ПОРТ • КОНТЕЙНЕРЫ",
                "sfx": "phone",
            },
            {
                "scene_id": "br1_s4",
                "loc": "luxury_office",
                "sentences": [
                    "«Срочно! Таможня ввела повышенный утильсбор! Переведите ещё восемьсот тысяч прямо сейчас, иначе машину конфискуют!»",
                    "Сергей замер... Ловушка захлопнулась! Смотри вторую часть!",
                ],
                "hud_bal": "+800 000 ₽!",
                "hud_st": "ШАНТАЖ УТИЛЬСБОРОМ!",
                "theme": "danger",
                "pill": "СРОЧНЫЙ ПЕРЕВОД • УТИЛЬСБОР",
                "sfx": "boom",
            },
        ],
    },
    2: {
        "filename": "broker_ep2_customs.mp4",
        "title": "Пригон авто из Кореи • Часть 2: Фальшивая таможня",
        "chapters": [
            {
                "scene_id": "br2_s1",
                "loc": "luxury_office",
                "sentences": [
                    "Часть вторая. Испугавшись потерять автомобиль, семья заняла у родственников последние восемьсот тысяч и перевела брокеру.",
                    "Но сразу после этого телефон Артура отключился, а вывеску компании в офисе сняли!",
                ],
                "hud_bal": "3 300 000 ₽",
                "hud_st": "ТЕЛЕФОН ВЫКЛЮЧЕН!",
                "theme": "danger",
                "pill": "БРОКЕР ПРОПАЛ СО СВЯЗИ",
                "sfx": "boom",
            },
            {
                "scene_id": "br2_s2",
                "loc": "customs_terminal",
                "sentences": [
                    "Почуяв неладное, Сергей взял копии таможенных платёжек и помчался на центральный пост Федеральной таможенной службы.",
                    "Там его встретил дежурный инспектор в зелёной форме.",
                ],
                "hud_bal": "ТАМОЖЕННЫЙ ПОСТ",
                "hud_st": "ПРОВЕРКА VIN",
                "theme": "alert",
                "pill": "ФТС РОССИИ • ПРОВЕРКА БАЗЫ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "br2_s3",
                "loc": "customs_terminal",
                "sentences": [
                    "Инспектор вбил VIN-номер в единую базу данных и покачал головой.",
                    "«Мужчина, эта машина вообще никогда не пересекала границу России, а ваш утильсбор — грубая подделка в Фотошопе!»",
                ],
                "hud_bal": "VIN: 0 В БАЗЕ",
                "hud_st": "ФАЛЬШИВЫЙ СБОР!",
                "theme": "danger",
                "pill": "ТАМОЖНЯ • ДОКУМЕНТЫ ПОДДЕЛЬНЫЕ",
                "sfx": "boom",
            },
            {
                "scene_id": "br2_s4",
                "loc": "customs_terminal",
                "sentences": [
                    "У Сергея потемнело в глазах: три миллиона триста тысяч рублей ушли аферисту!",
                    "Но как найти брокера, если он удалил все контакты? Разгадка — в третьей части!",
                ],
                "hud_bal": "УЩЕРБ 3.3 МЛН",
                "hud_st": "ОБМАН РАСКРЫТ!",
                "theme": "danger",
                "pill": "УЩЕРБ 3.3 МЛН • ПОИСК АФЕРИСТА",
                "sfx": "boom",
            },
        ],
    },
    3: {
        "filename": "broker_ep3_dubai.mp4",
        "title": "Пригон авто из Кореи • Часть 3: Билет в Дубай",
        "chapters": [
            {
                "scene_id": "br3_s1",
                "loc": "luxury_office",
                "sentences": [
                    "Часть третья. Лена сидела на диване и плакала — они потеряли все семейные накопления.",
                    "Но Лена работала digital-аналитиком и решила пробить скрытые профили брокера через архивные привязки телефонов!",
                ],
                "hud_bal": "ПОИСК В СЕТИ",
                "hud_st": "АНАЛИЗ ЦИФРОВОГО СЛЕДА",
                "theme": "alert",
                "pill": "ПОИСК ЦИФРОВОГО СЛЕДА",
                "sfx": "coin",
            },
            {
                "scene_id": "br3_s2",
                "loc": "luxury_office",
                "sentences": [
                    "Через двадцать минут поисков она наткнулась на закрытый аккаунт Артура в соцсетях.",
                    "И там горела свежая сторис, выложенная буквально пятнадцать минут назад!",
                ],
                "hud_bal": "СВЕЖАЯ СТОРИС",
                "hud_st": "АККАУНТ НАЙДЕН!",
                "theme": "alert",
                "pill": "СОЦСЕТИ • СВЕЖИЙ СЛЕД",
                "sfx": "whoosh",
            },
            {
                "scene_id": "br3_s3",
                "loc": "airport_departure_hall",
                "sentences": [
                    "На фото был стаканчик кофе из аэропорта Шереметьево и край посадочного талона на рейс в Дубай с вылетом через пятьдесят минут!",
                    "А рядом стоял тот самый кожаный чемодан, набитый чужими деньгами!",
                ],
                "hud_bal": "РЕЙС В ДУБАЙ!",
                "hud_st": "ВЫЛЕТ ЧЕРЕЗ 50 МИН",
                "theme": "danger",
                "pill": "ШЕРЕМЕТЬЕВО • ПОБЕГ ИЗ СТРАНЫ",
                "sfx": "boom",
            },
            {
                "scene_id": "br3_s4",
                "loc": "luxury_office",
                "sentences": [
                    "«Серёжа, он в Шереметьево на терминале C! У нас есть меньше часа, чтобы его остановить!»",
                    "Сергей прыгнул за руль и втопил педаль газа в пол. В четвёртой части начнётся гонка за беглецом!",
                ],
                "hud_bal": "ГОНКА В АЭРОПОРТ",
                "hud_st": "УСПЕТЬ ЗА 40 МИНУТ!",
                "theme": "danger",
                "pill": "ГОНКА ПО МКАДУ • ВРЕМЯ НА ИСХОДЕ",
                "sfx": "whoosh",
            },
        ],
    },
    4: {
        "filename": "broker_ep4_airport.mp4",
        "title": "Пригон авто из Кореи • Часть 4: Перехват за 15 минут",
        "chapters": [
            {
                "scene_id": "br4_s1",
                "loc": "airport_departure_hall",
                "sentences": [
                    "Часть четвёртая. Сергей и Лена влетели в терминал аэропорта, сбивая дыхание от бега.",
                    "На огромном табло вылетов красным мигало: «SU-524 МОСКВА — ДУБАЙ • ПОСАДКА ЗАКАНЧИВАЕТСЯ»!",
                ],
                "hud_bal": "ТАБЛО ВЫЛЕТОВ",
                "hud_st": "ПОСАДКА ЗАКАНЧИВАЕТСЯ!",
                "theme": "danger",
                "pill": "ШЕРЕМЕТЬЕВО • ТЕРМИНАЛ C",
                "sfx": "boom",
            },
            {
                "scene_id": "br4_s2",
                "loc": "passport_control_gates",
                "sentences": [
                    "Они рванули к зоне паспортного контроля и сквозь толпу заметили знакомое верблюжье пальто и кожаный чемодан!",
                    "Брокер Артур уже стоял в очереди у третьей кабинки пограничников!",
                ],
                "hud_bal": "БЕГЛЕЦ В ОЧЕРЕДИ",
                "hud_st": "3-Я КАБИНКА",
                "theme": "alert",
                "pill": "ПАСПОРТНЫЙ КОНТРОЛЬ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "br4_s3",
                "loc": "passport_control_gates",
                "sentences": [
                    "Мошенник протянул загранпаспорт офицеру и самодовольно ухмыльнулся, предвкушая жизнь в Арабских Эмиратах.",
                    "Но за пятнадцать минут до вылета Сергей прорвался сквозь ограждения и крикнул: «Полиция! Задержите мошенника!»",
                ],
                "hud_bal": "15 МИНУТ ДО ВЫЛЕТА",
                "hud_st": "ПЕРЕХВАТ!",
                "theme": "danger",
                "pill": "КРИК О ПОМОЩИ • ПОГРАНКОНТРОЛЬ",
                "sfx": "boom",
            },
            {
                "scene_id": "br4_s4",
                "loc": "passport_control_gates",
                "sentences": [
                    "Артур попытался вырваться и побежать к гейту, но сотрудники пограничной службы мгновенно заблокировали турникет!",
                    "Офицер защёлкнул на его запястьях стальные наручники! Смотри развязку в финале!",
                ],
                "hud_bal": "АРЕСТ НА ГРАНИЦЕ",
                "hud_st": "ВЫЕЗД ПЕРЕКРЫТ!",
                "theme": "danger",
                "pill": "ЗАДЕРЖАНИЕ С ПОЛИЧНЫМ",
                "sfx": "boom",
            },
        ],
    },
    5: {
        "filename": "broker_ep5_finale.mp4",
        "title": "Пригон авто из Кореи • Часть 5: Чемодан с миллионами и 3 правила",
        "chapters": [
            {
                "scene_id": "br5_s1",
                "loc": "passport_control_gates",
                "sentences": [
                    "Финал истории! При досмотре в чемодане брокера оперативники обнаружили сорок два миллиона рублей наличными и фальшивые печати таможни.",
                    "Оказалось, он кинул больше двадцати семей по всей стране и планировал скрыться в Дубае!",
                ],
                "hud_bal": "42 МЛН В ЧЕМОДАНЕ",
                "hud_st": "20 ПОСТРАДАВШИХ",
                "theme": "danger",
                "pill": "ДОСМОТР • ИЗЪЯТИЕ 42 000 000 ₽",
                "sfx": "boom",
            },
            {
                "scene_id": "br5_s2",
                "loc": "justice_finale_plaza",
                "sentences": [
                    "В отношении афериста возбудили уголовное дело по четвёртой части статьи мошенничество — ему светит до десяти лет колонии.",
                    "Благодаря молниеносному задержанию семье Сергея и Лены полностью вернули все три миллиона триста тысяч рублей!",
                ],
                "hud_bal": "3.3 МЛН ВОЗВРАЩЕНО!",
                "hud_st": "СТ. 159 Ч. 4 УК РФ",
                "theme": "green",
                "pill": "ВОЗВРАТ ВСЕХ СБЕРЕЖЕНИЙ",
                "sfx": "coin",
            },
            {
                "scene_id": "br5_s3",
                "loc": "justice_finale_plaza",
                "sentences": [
                    "А через месяц они купили проверенный автомобиль у официального дилера с прозрачной историей.",
                    "Но чтобы никогда не подарить миллионы авто-брокеру, запомните три главных правила безопасного пригона авто!",
                ],
                "hud_bal": "ХЭППИ-ЭНД!",
                "hud_st": "БЕЗОПАСНАЯ ПОКУПКА",
                "theme": "green",
                "pill": "ГЛАВНЫЙ ЮРИДИЧЕСКИЙ РАЗБОР",
                "sfx": "whoosh",
            },
            {
                "scene_id": "br5_s4",
                "loc": "justice_finale_plaza",
                "sentences": [
                    "Первое: никаких переводов на карты физлиц — только официальный банковский аккредитив. Второе: проверяйте пассажирскую декларацию на сайте ФТС лично!",
                    "И третье: утильсбор оплачивается ТОЛЬКО напрямую в Казначейство по вашему личному ИНН, а не брокеру в руки! Сохрани и поделись с друзьями!",
                ],
                "hud_bal": "ИНН + КАЗНАЧЕЙСТВО",
                "hud_st": "НЕ ДАЙ СЕБЯ КИНУТЬ!",
                "theme": "green",
                "pill": "ЗАЩИТИ СВОИ ДЕНЬГИ ПРИ ПОКУПКЕ АВТО!",
                "sfx": "coin",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# 5. MASTER EPISODE RENDERER
# ---------------------------------------------------------------------------

def render_broker_episode(
    ep_num: int,
    out_dir: Path = Path("output/story_broker"),
    speaker: str = "f5",
    fps: int = 30,
    shared_bgs: Optional[Dict[str, Image.Image]] = None,
) -> Path:
    ep = BROKER_EPISODES[ep_num]
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

    # 1. Voiceover via F5-TTS Russian GPU (cached per episode)
    voice_wav = work_dir / f"voice_broker_ep{ep_num}_{speaker}.wav"
    cached_words = work_dir / f"words_f5_voice_broker_ep{ep_num}_{speaker}.json"

    if speaker == "f5" and voice_wav.exists() and cached_words.exists():
        print(f"[BROKER EP{ep_num}] 1. Используем кэшированную GPU-озвучку F5-TTS...")
        voice_file = voice_wav
        meta = json.loads(cached_words.read_text(encoding="utf-8"))
        words = meta["words"]
        duration = float(meta["duration"])
    elif speaker == "f5" and is_f5_available():
        print(f"[BROKER EP{ep_num}] 1. Синтезируем живую озвучку '{ep['title']}' (F5-TTS RTX 4050)...")
        voice_file, words, duration = synthesize_f5_script(all_sentences, out_wav=voice_wav, speed=1.07)
    else:
        print(f"[BROKER EP{ep_num}] 1. Синтезируем Silero v5.6 ({speaker})...")
        voice_file, words, duration = synthesize_silero_script(all_sentences, speaker=speaker, out_wav=voice_wav)

    ch_starts = [0.0]
    wc = 0
    for i in range(len(chapters) - 1):
        wc += chapter_word_counts[i]
        ch_starts.append(max(ch_starts[-1] + 1.5, words[wc]["start"] - 0.12) if wc < len(words) else (i + 1) * (duration / 4.0))
    ch_ends = ch_starts[1:] + [duration]
    print(f"            Длительность: {duration:.2f}s | Смены сцен: {[round(x, 2) for x in ch_starts]}s")

    # 2. Mix SFX
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

    # 3. Karaoke Subtitles
    ass_path = work_dir / f"broker_ep{ep_num}.ass"
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

    # 4. Load / Reuse Backgrounds & Sprites
    bgs = shared_bgs if shared_bgs is not None else build_broker_backgrounds()
    korean_suv = build_korean_suv_sprite()
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
        # EPISODE 1: АВАНС 2.5 МИЛЛИОНА
        # ================================================================
        if sid == "br1_s1":
            # Sergey & Lena arrive at broker office, broker welcomes them
            sergey = render_sergey(mood="confident", mouth_state=mouth, gesture="relax", blink=blink, facing="right", scale=0.93)
            lena = render_lena(mood="confident", mouth_state="closed", gesture="relax", blink=blink, facing="right", scale=0.91)
            broker = render_broker(mood="smug", mouth_state="closed", gesture="relax", blink=blink, facing="left", holding_suitcase=False, scale=0.94)
            frame = paste_char(frame, sergey, 240, 1300)
            frame = paste_char(frame, lena, 370, 1300)
            frame = paste_char(frame, broker, 830, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Пригоним авто из Кореи за 30 дней в идеале!»", anchor_x=790, anchor_y=800, align="right", pop_scale=pop_late)

        elif sid == "br1_s2":
            # Sergey signs contract, transfers 2.5M
            sergey = render_sergey(mood="confident", mouth_state="closed", gesture="point_right", blink=blink, facing="right", holding_contract=True, scale=0.93)
            broker = render_broker(mood="smug", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", holding_suitcase=False, scale=0.94)
            frame = paste_char(frame, sergey, 310, 1300)
            frame = paste_char(frame, broker, 820, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "АВАНС: 2 500 000 ₽!", t_local - 0.20, center=(540, 560))

        elif sid == "br1_s3":
            # Seaport with container ship: fake photo of white SUV sent
            frame = paste_obj(frame, korean_suv, 280, 990)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Ваш кроссовер уже в порту погружен!»", anchor_x=340, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "br1_s4":
            # Broker demands +800k urgent recycling fee
            broker = render_broker(mood="shady", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", holding_suitcase=False, scale=0.95)
            sergey = render_sergey(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="right", scale=0.93)
            frame = paste_char(frame, sergey, 280, 1300)
            frame = paste_char(frame, broker, 830, 1300)
            frame = camera.apply(frame, zoom=1.02 + 0.06 * p_ch, focal_point=(520, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Срочно 800 000 ₽ на утильсбор, или арест!»", anchor_x=790, anchor_y=800, align="right", pop_scale=pop_late)

        # ================================================================
        # EPISODE 2: ФАЛЬШИВАЯ ТАМОЖНЯ
        # ================================================================
        elif sid == "br2_s1":
            # Empty office, phone disconnected
            sergey = render_sergey(mood="shocked", mouth_state=mouth, gesture="hands_on_head", blink=False, facing="right", scale=0.94)
            lena = render_lena(mood="sad", mouth_state="closed", gesture="relax", blink=blink, facing="right", scale=0.91)
            frame = paste_char(frame, sergey, 320, 1300)
            frame = paste_char(frame, lena, 460, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "АБОНЕНТ ВЫКЛЮЧЕН!", t_local - 0.20, center=(540, 560))

        elif sid == "br2_s2":
            # Customs terminal: Sergey with documents talking to customs inspector
            sergey = render_sergey(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", holding_contract=True, scale=0.93)
            officer = render_customs_officer(mood="alert", mouth_state="closed", gesture="relax", blink=blink, facing="left", scale=0.94)
            frame = paste_char(frame, sergey, 280, 1305)
            frame = paste_char(frame, officer, 820, 1305)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Проверьте VIN по базе! Машина растаможена?»", anchor_x=340, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "br2_s3":
            # Inspector reveals: VIN missing, receipts are fake
            officer = render_customs_officer(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", scale=0.95)
            sergey = render_sergey(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="right", scale=0.93)
            frame = paste_char(frame, sergey, 270, 1305)
            frame = paste_char(frame, officer, 830, 1305)
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Машина не въезжала! Платёжки нарисованы!»", anchor_x=790, anchor_y=790, align="right", pop_scale=pop_late)

        elif sid == "br2_s4":
            # Sergey devastated
            sergey = render_sergey(mood="sad", mouth_state=mouth, gesture="hands_on_head", blink=blink, facing="right", scale=0.94)
            frame = paste_char(frame, sergey, 380, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "УЩЕРБ: 3 300 000 ₽!", t_local - 0.15, center=(540, 520))

        # ================================================================
        # EPISODE 3: БИЛЕТ В ДУБАЙ
        # ================================================================
        elif sid == "br3_s1":
            # Lena analyzing digital footprints on smartphone
            lena = render_lena(mood="alert", mouth_state=mouth, gesture="hold_phone", blink=blink, facing="right", holding_phone=True, scale=0.93)
            sergey = render_sergey(mood="sad", mouth_state="closed", gesture="relax", blink=blink, facing="left", scale=0.92)
            frame = paste_char(frame, lena, 340, 1300)
            frame = paste_char(frame, sergey, 780, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Я нашла его скрытый аккаунт в соцсетях!»", anchor_x=400, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "br3_s2":
            # Story found
            lena = render_lena(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", holding_phone=True, scale=0.93)
            sergey = render_sergey(mood="alert", mouth_state="closed", gesture="relax", blink=blink, facing="left", scale=0.92)
            frame = paste_char(frame, lena, 320, 1300)
            frame = paste_char(frame, sergey, 790, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "СВЕЖАЯ СТОРИС: 15 МИН НАЗАД!", t_local - 0.20, center=(540, 560))

        elif sid == "br3_s3":
            # Flight board view: Moscow -> Dubai
            frame = camera.apply(frame, zoom=1.00 + 0.06 * p_ch, focal_point=(540, 960), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Рейс SU-524 в Дубай! Вылет через 50 минут!»", anchor_x=340, anchor_y=380, align="left", pop_scale=pop_late)

        elif sid == "br3_s4":
            # Sergey jumps into action: race to airport
            sergey = render_sergey(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            lena = render_lena(mood="confident", mouth_state="closed", gesture="relax", blink=blink, facing="right", scale=0.91)
            frame = paste_char(frame, sergey, 290, 1300)
            frame = paste_char(frame, lena, 420, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«По газам! Мы успеем его перехватить!»", anchor_x=350, anchor_y=800, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 4: ПЕРЕХВАТ ЗА 15 МИНУТ
        # ================================================================
        elif sid == "br4_s1":
            # Airport departure hall: running spouses
            sergey = render_sergey(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, walk_phase=t * 10.0, facing="right", scale=0.93)
            lena = render_lena(mood="alert", mouth_state="closed", gesture="relax", blink=blink, walk_phase=t * 10.0, facing="right", scale=0.91)
            frame = paste_char(frame, sergey, 260, 1305)
            frame = paste_char(frame, lena, 390, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1000), t=t)
            frame = draw_animated_stamp(frame, "ПОСАДКА ЗАКАНЧИВАЕТСЯ!", t_local - 0.20, center=(540, 560))

        elif sid == "br4_s2":
            # Passport control: spotting the camel coat
            sergey = render_sergey(mood="alert", mouth_state="closed", gesture="point_right", blink=blink, facing="right", scale=0.93)
            broker = render_broker(mood="smug", mouth_state="closed", gesture="relax", blink=blink, facing="right", holding_suitcase=True, scale=0.94)
            frame = paste_char(frame, sergey, 270, 1305)
            frame = paste_char(frame, broker, 810, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Вон он! Стоит на паспортном контроле!»", anchor_x=330, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "br4_s3":
            # Sergey shouting: "Police! Stop the scammer!"
            sergey = render_sergey(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            broker = render_broker(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="left", holding_suitcase=True, scale=0.94)
            frame = paste_char(frame, sergey, 290, 1305)
            frame = paste_char(frame, broker, 820, 1305)
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«ПОЛИЦИЯ! ЗАДЕРЖИТЕ МОШЕННИКА!»", anchor_x=350, anchor_y=790, align="left", pop_scale=pop_late)

        elif sid == "br4_s4":
            # Police handcuffing conman at turnstile
            police = render_border_police(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.95)
            broker = render_broker(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="left", holding_suitcase=False, scale=0.93)
            frame = paste_char(frame, police, 310, 1305)
            frame = paste_char(frame, broker, 810, 1305)
            frame = draw_siren_flash(frame, t)
            shake = ((1.0 - t_local / 0.5) ** 1.4) if t_local <= 0.5 else 0.0
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 1020), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "ПОГРАНКОНТРОЛЬ: АРЕСТ!", t_local - 0.15, center=(540, 520))

        # ================================================================
        # EPISODE 5: ЧЕМОДАН С МИЛЛИОНАМИ И 3 ПРАВИЛА
        # ================================================================
        elif sid == "br5_s1":
            # Open suitcase: 42M cash found
            police = render_border_police(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            broker = render_broker(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="left", holding_suitcase=False, scale=0.92)
            frame = paste_char(frame, police, 290, 1305)
            frame = paste_char(frame, broker, 820, 1305)
            frame = draw_siren_flash(frame, t)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "42 МЛН В ЧЕМОДАНЕ: СТ. 159 Ч. 4!", t_local - 0.20, center=(540, 520))

        elif sid == "br5_s2":
            # Sergey & Lena reunited with savings
            sergey = render_sergey(mood="confident", mouth_state="closed", gesture="relax", blink=blink, facing="right", scale=0.93)
            lena = render_lena(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", scale=0.92)
            frame = paste_char(frame, sergey, 310, 1300)
            frame = paste_char(frame, lena, 790, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Все 3.3 миллиона вернули до копейки!»", anchor_x=750, anchor_y=800, align="right", pop_scale=pop_late)

        elif sid == "br5_s3":
            # Family next to Korean crossover SUV in sunny plaza
            frame = paste_obj(frame, korean_suv, 380, 990)
            sergey = render_sergey(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            lena = render_lena(mood="confident", mouth_state="closed", gesture="relax", blink=blink, facing="right", scale=0.91)
            frame = paste_char(frame, sergey, 240, 1300)
            frame = paste_char(frame, lena, 360, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Запомните 3 правила пригона авто!»", anchor_x=300, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "br5_s4":
            # Finale: Thumbs up, legal rules checklist stamp
            frame = paste_obj(frame, korean_suv, 380, 990)
            sergey = render_sergey(mood="confident", mouth_state=mouth, gesture="thumbs_up", blink=blink, facing="right", scale=0.95)
            frame = paste_char(frame, sergey, 260, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "УТИЛЬСБОР ТОЛЬКО В КАЗНАЧЕЙСТВО!", t_local - 0.15, center=(540, 520))

        # --- UNIVERSAL HUD & TOP PILL ---
        theme = ch["theme"] if ch["theme"] in ("green", "alert", "danger", "muted") else "green"
        draw_sleek_hud(
            frame,
            balance_text=ch["hud_bal"],
            status_text=ch["hud_st"],
            theme=theme,
        )
        draw_compact_pill(
            frame,
            text=ch["pill"],
            y_pos=166,
        )

        return frame

    # 5. Render Video & Subtitles
    print(f"[BROKER EP{ep_num}] 2. Рендерим анимацию ({ep['title']})...")
    total_frames = int(duration * fps)
    raw_video = work_dir / f"raw_broker_ep{ep_num}.mp4"

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

        if f % 150 == 0 or f == total_frames - 1:
            pct = int((f + 1) / total_frames * 100)
            print(f"            Рендер: {pct}% ({f + 1}/{total_frames} кадров)")

    proc.stdin.close()
    proc.wait()

    print(f"[BROKER EP{ep_num}] 3. Финальная сборка MP4 (субтитры ASS + аудио)...")
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

    print(f"[OK] Серия {ep_num}/5 готова -> {output_path} ({duration:.2f}s, {output_path.stat().st_size / 1024 / 1024:.2f} MB)")
    return output_path


def render_all_broker_episodes(speaker: str = "f5", fps: int = 30) -> List[Path]:
    print("=" * 65)
    print("🚢 ПРИГОН АВТО ИЗ КОРЕИ И ЕВРОПЫ — ПОБЕГ БРОКЕРА В ДУБАЙ")
    print(f"   Движок: v3 PRO • Озвучка: {speaker.upper()} • Выход: output/story_broker/")
    print("=" * 65)
    shared_bgs = build_broker_backgrounds()
    outputs = []
    for ep_num in range(1, 6):
        out = render_broker_episode(ep_num, speaker=speaker, fps=fps, shared_bgs=shared_bgs)
        outputs.append(out)
    print("=" * 65)
    print("🎉 ВСЕ 5 СЕРИЙ УСПЕШНО СГЕНЕРИРОВАНЫ В output/story_broker/")
    print("=" * 65)
    return outputs


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate 5-part Auto Import Scam animated series.")
    parser.add_argument("--ep", type=int, default=0, help="Episode number (1-5), or 0 for all 5.")
    parser.add_argument("--speaker", type=str, default="f5", help="Voice engine: f5 (GPU) or eugene/aidar")
    args = parser.parse_args()

    bgs = build_broker_backgrounds()
    episodes = [args.ep] if args.ep in (1, 2, 3, 4, 5) else [1, 2, 3, 4, 5]

    for ep_num in episodes:
        render_broker_episode(ep_num=ep_num, speaker=args.speaker, shared_bgs=bgs)


if __name__ == "__main__":
    main()
