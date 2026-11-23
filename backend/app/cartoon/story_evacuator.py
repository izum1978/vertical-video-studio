"""
Standalone 5-Part Animated Mini-Series:
"ФАЛЬШИВЫЙ ЭВАКУАТОР И ШТРАФСТОЯНКА В ПРОМЗОНЕ" (v3 PRO Engine).

100% Brand-New Characters & Brand-New 2x-Supersampled Locations:

Characters:
- Maxim (young driver/father in smart vest over collared shirt)
- Tow Truck Driver (burly rude tow operator in neon-orange reflective vest & cap)
- Rude Cashier (angry woman in guard booth behind window bars demanding 60k cash)
- TV Blogger / Journalist (sharp reporter with handheld mic & "LIVE" badge)
- Prosecutor Inspector (official in deep navy uniform with gold insignia & case file)

Locations:
- Night Courtyard (peaceful residential neighborhood at 03:00 with fake sign hammered into lawn)
- Morning Empty Courtyard (daylight 08:00, 15 cars missing, empty asphalt, fresh sign)
- Fake Impound Lot (industrial wasteland, barbed wire fence, "СПЕЦСТОЯНКА №12" sign)
- Guard Booth & Cashier Window (rusty shack, steel window bars, "ТОЛЬКО НАЛИЧНЫЕ 60 000 ₽")
- Intercom Night-Cam Screen (smart intercom UI, timestamp 03:14:22, driver caught on camera)
- Live Broadcast & Prosecutor Raid (blogger in live stream, prosecutor arriving with siren flash)
- Victory Courtyard (all cars restored, Maxim smiles with car keys & 3 legal rules)
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
# 1. BRAND-NEW CHARACTERS FOR "ФАЛЬШИВЫЙ ЭВАКУАТОР"
# ---------------------------------------------------------------------------

def render_maxim(
    mood: str = "confident",
    mouth_state: str = "closed",
    gesture: str = "relax",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    holding_phone: bool = False,
    holding_keys: bool = False,
    scale: float = 0.93,
) -> Image.Image:
    """Maxim — smart young driver in dark navy vest over light-blue shirt."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(30, 41, 59), hair_style="slicked",
        mood=mood, mouth_state=mouth_state, gesture=("hold_phone" if holding_phone else gesture),
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2

    # Collared light-blue shirt visible under dark vest V-neck
    d.polygon([(cx - 24, 250), (cx, 310), (cx + 24, 250)], fill=(219, 234, 254, 255), outline=INK, width=2)
    d.line([(cx, 260), (cx, 310)], fill=(147, 197, 253, 255), width=2)

    # Silver wristwatch on left wrist
    d.rectangle([(cx - 78, 342), (cx - 64, 356)], fill=(203, 213, 225, 255), outline=INK, width=2)

    # Key fob in hand
    if holding_keys:
        hx = cx + 80 if facing == "right" else cx - 80
        hy = 345
        d.rounded_rectangle([(hx - 10, hy - 6), (hx + 10, hy + 20)], radius=4, fill=(15, 23, 42, 255), outline=INK, width=2)
        d.ellipse([hx - 4, hy - 14, hx + 4, hy - 4], outline=(203, 213, 225, 255), width=2)

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_tow_driver(
    mood: str = "smug",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "left",
    holding_crowbar: bool = True,
    scale: float = 0.95,
) -> Image.Image:
    """Tow Truck Driver — burly guy in neon-orange reflective vest & dark work cap."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(249, 115, 22), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    shift = 8 if facing == "right" else -8

    # Dark work cap with visor
    d.chord([cx - 74, 110, cx + 74, 185], start=180, end=360, fill=(30, 41, 59, 255), outline=INK, width=4)
    if facing == "right":
        d.polygon([(cx + 60, 150), (cx + 105, 154), (cx + 90, 168), (cx + 55, 165)], fill=(30, 41, 59, 255), outline=INK)
    else:
        d.polygon([(cx - 60, 150), (cx - 105, 154), (cx - 90, 168), (cx - 55, 165)], fill=(30, 41, 59, 255), outline=INK)

    # Silver reflective safety stripes on neon-orange vest
    d.rectangle([(cx - 52, 290), (cx + 52, 308)], fill=(241, 245, 249, 255), outline=INK, width=2)
    d.rectangle([(cx - 52, 335), (cx + 52, 353)], fill=(241, 245, 249, 255), outline=INK, width=2)

    # Stubble beard
    d.arc([cx - 52 + shift, 204, cx + 52 + shift, 258], start=20, end=160, fill=(40, 36, 32, 255), width=10)

    # Heavy steel crowbar or tow hook in hand
    if holding_crowbar:
        hx = cx - 85 if facing == "left" else cx + 85
        hy = 345
        d.line([(hx - 15, hy - 45), (hx + 10, hy + 45)], fill=(148, 163, 184, 255), width=8)
        d.arc([hx - 28, hy - 55, hx - 4, hy - 35], start=180, end=360, fill=(100, 116, 139, 255), width=5)

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_rude_cashier(
    mood: str = "shady",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    facing: str = "right",
    scale: float = 0.94,
) -> Image.Image:
    """Rude Cashier — angry woman in guard booth with glasses & knit shawl."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(136, 19, 55), hair_style="messy",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2

    # Glasses on nose
    d.ellipse([cx - 32, 175, cx - 12, 195], outline=INK, width=3)
    d.ellipse([cx + 12, 175, cx + 32, 195], outline=INK, width=3)
    d.line([(cx - 12, 185), (cx + 12, 185)], fill=INK, width=3)

    # Thick patterned knit shawl over shoulders
    d.polygon([(cx - 62, 250), (cx, 320), (cx + 62, 250), (cx + 50, 360), (cx - 50, 360)], fill=(159, 18, 57, 255), outline=INK, width=3)

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_blogger(
    mood: str = "confident",
    mouth_state: str = "open",
    gesture: str = "point_right",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    scale: float = 0.93,
) -> Image.Image:
    """TV Blogger / Journalist — stylish reporter in graphite jacket with live microphone."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(51, 65, 85), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2

    # Red "LIVE / ПРЯМОЙ ЭФИР" badge on chest
    d.rounded_rectangle([(cx - 40, 275), (cx + 25, 300)], radius=3, fill=(220, 38, 38, 255), outline=INK, width=2)
    d.text((cx - 36, 280), "LIVE", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 12))

    # Handheld condenser reporter microphone in hand!
    hx = cx + 80 if facing == "right" else cx - 80
    hy = 330
    d.rectangle([(hx - 6, hy - 10), (hx + 6, hy + 35)], fill=(15, 23, 42, 255), outline=INK, width=2)
    # Red foam mic windshield cube with "TV"
    d.rectangle([(hx - 14, hy - 34), (hx + 14, hy - 10)], fill=(220, 38, 38, 255), outline=INK, width=2)
    d.text((hx - 10, hy - 28), "TV", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 10))

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_prosecutor(
    mood: str = "alert",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    scale: float = 0.94,
) -> Image.Image:
    """Prosecutor Inspector — deep navy uniform with gold insignia & case warrant."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(15, 23, 42), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2

    # Gold prosecutor epaulets on shoulders
    d.rectangle([(cx - 62, 240), (cx - 40, 256)], fill=(234, 179, 8, 255), outline=INK, width=2)
    d.rectangle([(cx + 40, 240), (cx + 62, 256)], fill=(234, 179, 8, 255), outline=INK, width=2)

    # Blue prosecutor lapels & gold buttons
    d.polygon([(cx - 22, 250), (cx, 310), (cx + 22, 250)], fill=(30, 58, 138, 255), outline=INK, width=2)
    for by in [320, 345, 370]:
        d.ellipse([cx - 4, by, cx + 4, by + 8], fill=(234, 179, 8, 255))

    # Official warrant folder in hand
    hx = cx + 80 if facing == "right" else cx - 80
    hy = 340
    d.rounded_rectangle([(hx - 20, hy - 30), (hx + 24, hy + 30)], radius=4, fill=(30, 58, 138, 255), outline=INK, width=2)
    d.rectangle([(hx - 14, hy - 14), (hx + 18, hy + 8)], fill=(255, 255, 255, 255))
    d.text((hx - 12, hy - 10), "ОРДЕР", fill=INK, font=_font(FONT_BOLD, 8))

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 2. VEHICLE & PROPS SPRITES
# ---------------------------------------------------------------------------

def build_tow_truck_sprite(with_car_on_bed: bool = False) -> Image.Image:
    """Heavy yellow recovery tow truck with flatbed, hydraulic ramp & orange lightbar."""
    S = 2
    W, H = 640 * S, 280 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    wheel_y = 205 * S
    # Heavy rear flatbed platform (slanted steel deck)
    d.polygon([(30 * S, 140 * S), (420 * S, 140 * S), (420 * S, wheel_y), (30 * S, wheel_y)], fill=(71, 85, 105, 255), outline=INK, width=4 * S)
    d.polygon([(10 * S, 180 * S), (60 * S, 140 * S), (60 * S, wheel_y), (10 * S, wheel_y)], fill=(51, 65, 85, 255), outline=INK, width=3 * S)

    # Yellow Cab Front
    cab_color = (250, 204, 21, 255)
    d.rounded_rectangle([(400 * S, 80 * S), (610 * S, wheel_y)], radius=16 * S, fill=cab_color, outline=INK, width=5 * S)
    # Cab windshield & side window
    d.polygon([(420 * S, 95 * S), (520 * S, 95 * S), (550 * S, 145 * S), (420 * S, 145 * S)], fill=(219, 234, 254, 255), outline=INK, width=3 * S)
    # Headlight
    d.rounded_rectangle([(585 * S, 155 * S), (610 * S, 185 * S)], radius=4 * S, fill=(254, 240, 138, 255), outline=INK, width=3 * S)

    # Flashing orange lightbar on cab roof
    d.rounded_rectangle([(460 * S, 62 * S), (540 * S, 80 * S)], radius=6 * S, fill=(249, 115, 22, 255), outline=INK, width=3 * S)
    d.ellipse([470 * S, 66 * S, 490 * S, 76 * S], fill=(255, 255, 255, 255))
    d.ellipse([510 * S, 66 * S, 530 * S, 76 * S], fill=(255, 255, 255, 255))

    # Heavy Wheels with mudguards
    for wx in [120 * S, 260 * S, 530 * S]:
        d.ellipse([wx - 36 * S, wheel_y - 28 * S, wx + 36 * S, wheel_y + 44 * S], fill=(30, 41, 59, 255), outline=INK, width=5 * S)
        d.ellipse([wx - 16 * S, wheel_y - 8 * S, wx + 16 * S, wheel_y + 24 * S], fill=(148, 163, 184, 255), outline=INK, width=3 * S)

    # Optional Car being towed on the flatbed
    if with_car_on_bed:
        _draw_car(d, cx=220 * S, wheel_y=138 * S, S=int(S * 0.8), body_color=(37, 99, 235), split_gap=0)

    return img.resize((640, 280), Image.Resampling.LANCZOS)


def build_maxim_sedan_sprite() -> Image.Image:
    """Maxim's sleek royal-blue city sedan sprite."""
    S = 2
    W, H = 540 * S, 240 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _draw_car(d, cx=270 * S, wheel_y=176 * S, S=S, body_color=(37, 99, 235), split_gap=0)
    return img.resize((540, 240), Image.Resampling.LANCZOS)


def build_portable_sign_sprite() -> Image.Image:
    """Portable road sign: 3.27 'No Parking' + 8.24 'Tow Truck' on makeshift post."""
    S = 2
    W, H = 180 * S, 320 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 90 * S

    # Steel vertical post
    d.rectangle([(cx - 5 * S, 40 * S), (cx + 5 * S, 280 * S)], fill=(148, 163, 184, 255), outline=INK, width=2 * S)
    # Makeshift portable heavy concrete base block
    d.polygon([(cx - 45 * S, 280 * S), (cx + 45 * S, 280 * S), (cx + 55 * S, 310 * S), (cx - 55 * S, 310 * S)], fill=(100, 116, 139, 255), outline=INK, width=3 * S)

    # Sign 3.27: "Остановка запрещена" (Blue circle with red border and red cross)
    r = 44 * S
    cy = 60 * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(37, 99, 235, 255), outline=(220, 38, 38, 255), width=8 * S)
    # Red cross lines
    d.line([(cx - 30 * S, cy - 30 * S), (cx + 30 * S, cy + 30 * S)], fill=(220, 38, 38, 255), width=8 * S)
    d.line([(cx - 30 * S, cy + 30 * S), (cx + 30 * S, cy - 30 * S)], fill=(220, 38, 38, 255), width=8 * S)

    # Plate 8.24: "Работает эвакуатор" (White rectangle with black tow truck icon)
    d.rounded_rectangle([(cx - 42 * S, 115 * S), (cx + 42 * S, 165 * S)], radius=4 * S, fill=(255, 255, 255, 255), outline=INK, width=3 * S)
    # Miniature tow silhouette
    d.rectangle([(cx - 28 * S, 135 * S), (cx + 10 * S, 155 * S)], fill=INK)
    d.polygon([(cx + 10 * S, 140 * S), (cx + 25 * S, 140 * S), (cx + 28 * S, 155 * S), (cx + 10 * S, 155 * S)], fill=INK)
    d.line([(cx - 15 * S, 135 * S), (cx - 32 * S, 124 * S)], fill=INK, width=2 * S)

    return img.resize((180, 320), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 3. 2X-SUPERSAMPLED BACKGROUND BUILDER (8 UNIQUE LOCATIONS)
# ---------------------------------------------------------------------------

def build_evacuator_backgrounds() -> Dict[str, Image.Image]:
    """Generates all high-res backgrounds for the fake tow truck / impound lot story."""
    S = 2
    W, H = 1080 * S, 1920 * S
    bgs = {}

    # ------------------------------------------------------------------
    # LOC 1: NIGHT COURTYARD (03:00 Peaceful Residential Yard + Lamppost)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Dark blue night sky
    for y in range(0, floor_y, 4):
        rat = y / floor_y
        d.rectangle([(0, y), (W, y + 4)], fill=(int(10 + rat * 15), int(15 + rat * 20), int(30 + rat * 30), 255))

    # Multi-story apartment buildings with warm glowing windows
    for bx, bw, bh in [(30, 260, 800), (330, 340, 920), (710, 340, 780)]:
        d.rectangle([(bx * S, floor_y - bh * S), ((bx + bw) * S, floor_y)], fill=(30, 41, 59, 255), outline=INK, width=4 * S)
        # Windows
        for wy in range(floor_y - (bh - 60) * S, floor_y - 80 * S, 70 * S):
            for wx in range((bx + 30) * S, (bx + bw - 40) * S, 60 * S):
                is_lit = (wx + wy) % 5 == 0
                win_c = (254, 240, 138, 220) if is_lit else (51, 65, 85, 255)
                d.rounded_rectangle([(wx, wy), (wx + 34 * S, wy + 44 * S)], radius=3 * S, fill=win_c, outline=INK, width=2 * S)

    # Street lamppost casting warm yellow glow
    lx = 860 * S
    d.line([(lx, 380 * S), (lx, floor_y)], fill=(100, 116, 139, 255), width=6 * S)
    d.polygon([(lx - 40 * S, 380 * S), (lx + 40 * S, 380 * S), (lx + 20 * S, 350 * S), (lx - 20 * S, 350 * S)], fill=(250, 204, 21, 255), outline=INK)
    cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cone).polygon([(lx - 30 * S, 380 * S), (lx + 30 * S, 380 * S), (W, floor_y), (480 * S, floor_y)], fill=(254, 240, 138, 25))
    img = Image.alpha_composite(img, cone)
    d = ImageDraw.Draw(img)

    # Dark asphalt parking bays with white painted lines
    d.rectangle([(0, floor_y), (W, H)], fill=(30, 32, 40, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    for px in range(80 * S, W, 220 * S):
        d.line([(px, floor_y), (px + 60 * S, H)], fill=(148, 163, 184, 180), width=4 * S)

    bgs["night_courtyard"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 2: MORNING EMPTY COURTYARD (08:00 Daylight, 15 Cars Missing!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (224, 242, 254, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Pale morning sky
    for y in range(0, floor_y, 4):
        rat = y / floor_y
        d.rectangle([(0, y), (W, y + 4)], fill=(int(186 + rat * 20), int(230 + rat * 15), int(253), 255))

    # Apartment buildings in daylight
    for bx, bw, bh in [(30, 260, 800), (330, 340, 920), (710, 340, 780)]:
        d.rectangle([(bx * S, floor_y - bh * S), ((bx + bw) * S, floor_y)], fill=(203, 213, 225, 255), outline=INK, width=4 * S)
        for wy in range(floor_y - (bh - 60) * S, floor_y - 80 * S, 70 * S):
            for wx in range((bx + 30) * S, (bx + bw - 40) * S, 60 * S):
                d.rounded_rectangle([(wx, wy), (wx + 34 * S, wy + 44 * S)], radius=3 * S, fill=(147, 197, 253, 220), outline=INK, width=2 * S)

    # Trees & green lawn
    d.rectangle([(60 * S, floor_y - 40 * S), (380 * S, floor_y)], fill=(34, 197, 94, 255), outline=INK, width=3 * S)

    # Freshly placed portable sign standing right on the lawn!
    psign = build_portable_sign_sprite()
    psign_lg = psign.resize((int(psign.width * 1.5), int(psign.height * 1.5)), Image.Resampling.LANCZOS)
    img.paste(psign_lg, (140 * S, floor_y - 280 * S), psign_lg)
    d = ImageDraw.Draw(img)

    # Empty asphalt parking slots with tire skid marks!
    d.rectangle([(0, floor_y), (W, H)], fill=(226, 232, 240, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    for px in range(80 * S, W, 220 * S):
        d.line([(px, floor_y), (px + 60 * S, H)], fill=(255, 255, 255, 255), width=5 * S)
    # Skid marks
    for sx in [320 * S, 580 * S, 840 * S]:
        d.line([(sx, floor_y + 40 * S), (sx + 20 * S, floor_y + 140 * S)], fill=(71, 85, 105, 160), width=8 * S)

    bgs["morning_courtyard"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 3: FAKE IMPOUND LOT (Barbed Wire Fence + Seized Cars Behind)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (51, 65, 85, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Gloomy grey industrial overcast sky
    for y in range(0, floor_y, 4):
        rat = y / floor_y
        d.rectangle([(0, y), (W, y + 4)], fill=(int(100 - rat * 30), int(116 - rat * 25), int(139 - rat * 20), 255))

    # Concrete slabs perimeter wall with barbed wire
    d.rectangle([(0, 480 * S), (W, floor_y)], fill=(148, 163, 184, 255), outline=INK, width=5 * S)
    for sx in range(0, W, 180 * S):
        d.line([(sx, 480 * S), (sx, floor_y)], fill=(100, 116, 139, 255), width=3 * S)
    # Barbed wire coil
    d.line([(0, 450 * S), (W, 450 * S)], fill=(71, 85, 105, 255), width=4 * S)
    for bx in range(0, W, 50 * S):
        d.arc([bx, 420 * S, bx + 60 * S, 480 * S], start=0, end=360, fill=(71, 85, 105, 255), width=3 * S)

    # Crooked sign on wall: "СПЕЦИАЛИЗИРОВАННАЯ ШТРАФСТОЯНКА № 12"
    d.rounded_rectangle([(180 * S, 540 * S), (900 * S, 680 * S)], radius=12 * S, fill=(220, 38, 38, 255), outline=INK, width=5 * S)
    f_sh = _font(FONT_IMPACT, 42 * S)
    sht = "СПЕЦСТОЯНКА № 12"
    shb = f_sh.getbbox(sht)
    d.text(((W - (shb[2] - shb[0])) // 2, 565 * S), sht, fill=(255, 255, 255, 255), font=f_sh)
    f_sub = _font(FONT_BOLD, 22 * S)
    sut = "ООО «ЭВАКУАЦИЯ-ПЛЮС» • ВХОД СТРОГО ПО ПРОПУСКАМ"
    sub = f_sub.getbbox(sut)
    d.text(((W - (sub[2] - sub[0])) // 2, 630 * S), sut, fill=(254, 240, 138, 255), font=f_sub)

    # Row of seized cars visible behind chain-link gate
    _draw_car(d, cx=320 * S, wheel_y=1040 * S, S=S, body_color=(220, 38, 38), split_gap=0)
    _draw_car(d, cx=740 * S, wheel_y=1040 * S, S=S, body_color=(37, 99, 235), split_gap=0)

    # Muddy gravel ground
    d.rectangle([(0, floor_y), (W, H)], fill=(71, 85, 105, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    for mx in range(120 * S, W, 260 * S):
        d.ellipse([mx, floor_y + 40 * S, mx + 160 * S, floor_y + 110 * S], fill=(51, 65, 85, 180))

    bgs["fake_impound_lot"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 4: GUARD BOOTH & CASHIER WINDOW (Bars + "60 000 ₽ ТОЛЬКО НАЛ")
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (45, 55, 72, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Corrugated metal wall of guard trailer
    d.rectangle([(0, 0), (W, floor_y)], fill=(74, 85, 104, 255))
    for rx in range(0, W, 50 * S):
        d.line([(rx, 0), (rx, floor_y)], fill=(45, 55, 72, 255), width=3 * S)

    # Heavy steel cashier window with thick iron bars
    win_x1, win_y1 = 220 * S, 420 * S
    win_x2, win_y2 = 860 * S, 940 * S
    d.rectangle([(win_x1, win_y1), (win_x2, win_y2)], fill=(26, 32, 44, 255), outline=INK, width=6 * S)

    # Inside booth: dim incandescent orange glow
    d.rectangle([(win_x1 + 16 * S, win_y1 + 16 * S), (win_x2 - 16 * S, win_y2 - 16 * S)], fill=(67, 56, 202, 180))

    # Heavy vertical iron bars across window!
    for bx in range(win_x1 + 60 * S, win_x2, 70 * S):
        d.line([(bx, win_y1), (bx, win_y2)], fill=(203, 213, 225, 255), width=8 * S)

    # Cardboard notice taped to window: "ОПЛАТА 60 000 ₽ ТОЛЬКО НАЛИЧНЫМИ БЕЗ ЧЕКА"
    d.rounded_rectangle([(180 * S, 980 * S), (900 * S, 1160 * S)], radius=12 * S, fill=(254, 243, 199, 255), outline=(220, 38, 38, 255), width=5 * S)
    f_not1 = _font(FONT_IMPACT, 38 * S)
    f_not2 = _font(FONT_BOLD, 26 * S)
    nt1 = "ОПЛАТА: 60 000 ₽ (ТОЛЬКО НАЛИЧНЫЕ!)"
    nb1 = f_not1.getbbox(nt1)
    d.text(((W - (nb1[2] - nb1[0])) // 2, 1005 * S), nt1, fill=(220, 38, 38, 255), font=f_not1)

    nt2 = "БЕЗ ЧЕКОВ • КАРТЫ НЕ ПРИНИМАЕМ • СРОК 3 ДНЯ"
    nb2 = f_not2.getbbox(nt2)
    d.text(((W - (nb2[2] - nb2[0])) // 2, 1075 * S), nt2, fill=(15, 23, 42, 255), font=f_not2)

    # Concrete ground
    d.rectangle([(0, floor_y), (W, H)], fill=(203, 213, 225, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)

    bgs["guard_booth"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 5: INTERCOM NIGHT-CAM SCREEN (03:14:22 Tow Driver Caught on Cam!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (10, 15, 20, 255))
    d = ImageDraw.Draw(img)

    # Smartphone / Security Monitor Frame
    mon_w, mon_h = 920 * S, 1540 * S
    mx = (W - mon_w) // 2
    my = 180 * S
    d.rounded_rectangle([(mx, my), (mx + mon_w, my + mon_h)], radius=36 * S, fill=(15, 23, 42, 255), outline=(56, 189, 248, 255), width=6 * S)

    # Night-vision green-tinted surveillance video feed
    d.rectangle([(mx + 20 * S, my + 80 * S), (mx + mon_w - 20 * S, my + mon_h - 40 * S)], fill=(6, 30, 20, 255))

    # OSD Header: "УМНЫЙ ДОМОФОН • ПОДЪЕЗД 2 • КАМЕРА №1 [LIVE]"
    f_osd = _font(FONT_BOLD, 22 * S)
    d.text((mx + 40 * S, my + 30 * S), "🔴 REC  УМНЫЙ ДОМОФОН • ПОДЪЕЗД №2", fill=(239, 68, 68, 255), font=f_osd)
    d.text((mx + mon_w - 240 * S, my + 30 * S), "03:14:22 HD", fill=(34, 197, 94, 255), font=f_osd)

    # Silhouette of the driver hammering the sign in the center of the feed
    d.ellipse([460 * S, 580 * S, 620 * S, 740 * S], fill=(34, 197, 94, 180), outline=(74, 222, 128, 255), width=4 * S)
    # Sledgehammer in hands
    d.line([(480 * S, 640 * S), (420 * S, 520 * S)], fill=(74, 222, 128, 255), width=8 * S)
    d.rectangle([(400 * S, 500 * S), (440 * S, 540 * S)], fill=(74, 222, 128, 255))
    # Portable sign being hammered
    d.ellipse([640 * S, 680 * S, 780 * S, 820 * S], outline=(239, 68, 68, 255), width=6 * S)
    d.line([(710 * S, 820 * S), (710 * S, 1100 * S)], fill=(74, 222, 128, 255), width=6 * S)

    # Big Red Targeting Box around the Driver's Face: "ЛИЦО ОПОЗНАНО!"
    d.rectangle([(420 * S, 540 * S), (660 * S, 780 * S)], outline=(239, 68, 68, 255), width=6 * S)
    d.text((430 * S, 500 * S), "УЛИКА! ВОДИТЕЛЬ ЭВАКУАТОРА", fill=(239, 68, 68, 255), font=_font(FONT_BOLD, 22 * S))

    # Giant Stamp: "САМИ ПОСТАВИЛИ ЗНАК В 03:14!"
    d.rounded_rectangle([(140 * S, 1360 * S), (940 * S, 1500 * S)], radius=18 * S, fill=(220, 38, 38, 245), outline=(255, 255, 255, 255), width=6 * S)
    f_st = _font(FONT_IMPACT, 44 * S)
    stt = "УЛИКА: САМИ ПОСТАВИЛИ ЗНАК!"
    stb = f_st.getbbox(stt)
    d.text(((W - (stb[2] - stb[0])) // 2, 1395 * S), stt, fill=(255, 255, 255, 255), font=f_st)

    bgs["intercom_screen"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 6: LIVE BROADCAST & PROSECUTOR RAID
    # ------------------------------------------------------------------
    img = bgs["fake_impound_lot"].copy()
    img = img.resize((W, H), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(img)

    # TV Broadcast Header Bar
    d.rectangle([(0, 200 * S), (W, 300 * S)], fill=(220, 38, 38, 240))
    f_tv = _font(FONT_IMPACT, 38 * S)
    tvt = "🔴 В ЭФИРЕ: ШТУРМ НЕЛЕГАЛЬНОЙ СТОЯНКИ"
    tvb = f_tv.getbbox(tvt)
    d.text(((W - (tvb[2] - tvb[0])) // 2, 225 * S), tvt, fill=(255, 255, 255, 255), font=f_tv)

    # Blue-and-White Police Crime Scene Tape across foreground
    d.polygon([(0, 680 * S), (W, 760 * S), (W, 820 * S), (0, 740 * S)], fill=(30, 58, 138, 240), outline=INK)
    for sx in range(0, W + 200 * S, 120 * S):
        d.polygon([(sx, 680 * S + int(sx * 0.07)), (sx + 50 * S, 680 * S + int((sx + 50 * S) * 0.07)), (sx + 50 * S, 740 * S + int((sx + 50 * S) * 0.07)), (sx, 740 * S + int(sx * 0.07))], fill=(255, 255, 255, 240))
    d.text((260 * S, 740 * S), "ПРОКУРАТУРА РФ • СТОЯНКА ОПЕЧАТАНА • СТ. 159 УК РФ", fill=INK, font=_font(FONT_BOLD, 22 * S))

    bgs["live_broadcast"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 7: VICTORY COURTYARD (Sunny Morning + Cars Restored)
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

    # Apartment buildings in daylight
    for bx, bw, bh in [(30, 260, 800), (330, 340, 920), (710, 340, 780)]:
        d.rectangle([(bx * S, floor_y - bh * S), ((bx + bw) * S, floor_y)], fill=(203, 213, 225, 255), outline=INK, width=4 * S)

    # Clean sunlit courtyard floor
    d.rectangle([(0, floor_y), (W, H)], fill=(241, 245, 249, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)

    bgs["victory_courtyard"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    return bgs


# ---------------------------------------------------------------------------
# 4. STORY EPISODES DATA (5 FULL-LENGTH EPISODES)
# ---------------------------------------------------------------------------

EVACUATOR_EPISODES = {
    1: {
        "filename": "evacuator_ep1_sign.mp4",
        "title": "Фальшивый эвакуатор • Часть 1: Знак в 3 часа ночи",
        "chapters": [
            {
                "scene_id": "ev1_s1",
                "loc": "night_courtyard",
                "sentences": [
                    "Максим припарковал свой седан в родном дворе, где все жильцы спокойно ставили машины последние пять лет.",
                    "Во дворе было тихо, разметка чистая, и никаких запрещающих знаков здесь никогда не было.",
                ],
                "hud_bal": "00:30 • ДВОР",
                "hud_st": "ЗАКОННАЯ ПАРКОВКА",
                "theme": "green",
                "pill": "СПАЛЬНЫЙ РАЙОН • ТИХИЙ ДВОР",
                "sfx": "coin",
            },
            {
                "scene_id": "ev1_s2",
                "loc": "night_courtyard",
                "sentences": [
                    "Но ровно в три часа ночи во двор бесшумно въехал жёлтый эвакуатор с выключенными фарами.",
                    "Двое мужчин в жилетах выгрузили переносной знак «Остановка запрещена» и кувалдой вбили его прямо в газон!",
                ],
                "hud_bal": "03:14 НОЧИ",
                "hud_st": "АФЕРА В ТЕМНОТЕ!",
                "theme": "danger",
                "pill": "УСТАНОВКА ФАЛЬШИВОГО ЗНАКА",
                "sfx": "whoosh",
            },
            {
                "scene_id": "ev1_s3",
                "loc": "night_courtyard",
                "sentences": [
                    "Сразу после этого началась ночная облава: наглый водитель цеплял машины одну за другой и увозил в неизвестном направлении.",
                    "За сорок минут со двора вывезли пятнадцать автомобилей спящих жильцов!",
                ],
                "hud_bal": "15 МАШИН УКРАДЕНО",
                "hud_st": "МАССОВЫЙ ВЫВОЗ",
                "theme": "danger",
                "pill": "РЕЙД ЭВАКУАТОРОВ • 15 АВТО",
                "sfx": "boom",
            },
            {
                "scene_id": "ev1_s4",
                "loc": "morning_courtyard",
                "sentences": [
                    "В восемь утра Максим вышел на работу и остолбенел: весь двор был абсолютно пуст, а на газоне красовался свежий знак эвакуации!",
                    "«Куда делись наши машины?!» — в панике закричали соседи. Смотри вторую часть!",
                ],
                "hud_bal": "08:00 • ШОК!",
                "hud_st": "ДВОР ПУСТ!",
                "theme": "danger",
                "pill": "УТРО • ПУСТОЙ ДВОР",
                "sfx": "boom",
            },
        ],
    },
    2: {
        "filename": "evacuator_ep2_lot.mp4",
        "title": "Фальшивый эвакуатор • Часть 2: Счёт на 60 000 рублей",
        "chapters": [
            {
                "scene_id": "ev2_s1",
                "loc": "fake_impound_lot",
                "sentences": [
                    "Часть вторая. Через городскую справочную соседи с трудом выяснили адрес: глухой пустырь в промзоне за бетонным забором.",
                    "Приехав туда, люди обомлели — за колючей проволокой стояли все пятнадцать машин из их двора!",
                ],
                "hud_bal": "ПРОМЗОНА",
                "hud_st": "СТОЯНКА НАЙДЕНА",
                "theme": "alert",
                "pill": "СПЕЦСТОЯНКА В ПРОМЗОНЕ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "ev2_s2",
                "loc": "guard_booth",
                "sentences": [
                    "Максим подошёл к будке охраны, но в зарешеченном окошке сидела злобная кассирша.",
                    "Она швырнула на прилавок бумажку: «Эвакуация пятнадцать тысяч, хранение сорок пять. С каждого по шестьдесят тысяч рублей!»",
                ],
                "hud_bal": "60 000 ₽",
                "hud_st": "СЧЁТ ЗА ВЫКУП!",
                "theme": "danger",
                "pill": "КАССА • ТРЕБОВАНИЕ ДЕНЕГ",
                "sfx": "boom",
            },
            {
                "scene_id": "ev2_s3",
                "loc": "guard_booth",
                "sentences": [
                    "«Какие шестьдесят тысяч?! Дайте чек и протокол ГИБДД!» — возмутился Максим.",
                    "Но кассирша нагло оскалилась: «Только наличными без чека! Не заплатите за трое суток — пустим ваши тачки с молотка!»",
                ],
                "hud_bal": "БЕЗ ЧЕКА!",
                "hud_st": "ТОЛЬКО НАЛИЧКА!",
                "theme": "danger",
                "pill": "ШАНТАЖ • ПРОДАЖА АВТО",
                "sfx": "whoosh",
            },
            {
                "scene_id": "ev2_s4",
                "loc": "fake_impound_lot",
                "sentences": [
                    "Рядом стоял наглый водитель эвакуатора с монтировкой в руках и хохотал: «Платите, лохи, вы нарушили правила!»",
                    "Люди были в отчаянии... Но Максим придумал, как поймать их с поличным! Продолжение в третьей части!",
                ],
                "hud_bal": "ТУПИК...",
                "hud_st": "УГРОЗЫ СИЛОЙ",
                "theme": "danger",
                "pill": "ТУПИК • ПЛАН МАКСИМА",
                "sfx": "boom",
            },
        ],
    },
    3: {
        "filename": "evacuator_ep3_evidence.mp4",
        "title": "Фальшивый эвакуатор • Часть 3: Ночная запись домофона",
        "chapters": [
            {
                "scene_id": "ev3_s1",
                "loc": "morning_courtyard",
                "sentences": [
                    "Часть третья. Максим вернулся во двор. Соседи уже хотели собирать последние деньги, чтобы не потерять машины.",
                    "Но Максим поднял голову и увидел объектив умного домофона прямо над вторым подъездом!",
                ],
                "hud_bal": "УМНЫЙ ДОМОФОН",
                "hud_st": "ПОИСК ЗАПИСИ",
                "theme": "alert",
                "pill": "АРХИВ ВИДЕО • ПОДЪЕЗД №2",
                "sfx": "coin",
            },
            {
                "scene_id": "ev3_s2",
                "loc": "intercom_screen",
                "sentences": [
                    "Максим открыл приложение на смартфоне и перемотал ночной архив ровно на три часа четырнадцать минут.",
                    "И камера в высоком разрешении выдала сенсацию: тот самый наглый водитель эвакуатора лично вбивает знак кувалдой!",
                ],
                "hud_bal": "03:14:22",
                "hud_st": "ЛИЦО ОПОЗНАНО!",
                "theme": "danger",
                "pill": "КАМЕРА • МОМЕНТ ПРЕСТУПЛЕНИЯ",
                "sfx": "boom",
            },
            {
                "scene_id": "ev3_s3",
                "loc": "intercom_screen",
                "sentences": [
                    "На видео было видно всё: номер эвакуатора, лица мошенников и как они смеются, устанавливая фальшивую ловушку!",
                    "Это была чистая статья сто пятьдесят девятая — мошенничество, совершённое организованной группой!",
                ],
                "hud_bal": "СТ. 159 УК РФ",
                "hud_st": "ПОЛНЫЙ КОМПРОМАТ",
                "theme": "danger",
                "pill": "ОРГАНИЗОВАННАЯ ГРУППА",
                "sfx": "whoosh",
            },
            {
                "scene_id": "ev3_s4",
                "loc": "morning_courtyard",
                "sentences": [
                    "Максим тут же набрал знакомого журналиста-расследователя и переслал ему файл.",
                    "«Выезжаю со съёмочной группой, запускаем прямой эфир!» — ответил блогер. В четвёртой части начнётся штурм!",
                ],
                "hud_bal": "ВЫЕЗД ТВ",
                "hud_st": "ПРЯМОЙ ЭФИР!",
                "theme": "green",
                "pill": "ЖУРНАЛИСТЫ ЕДУТ НА СТОЯНКУ",
                "sfx": "phone",
            },
        ],
    },
    4: {
        "filename": "evacuator_ep4_live.mp4",
        "title": "Фальшивый эвакуатор • Часть 4: Прямой эфир и штурм прокуратуры",
        "chapters": [
            {
                "scene_id": "ev4_s1",
                "loc": "live_broadcast",
                "sentences": [
                    "Часть четвёртая. Журналист с микрофоном и камерой подъехал к воротам нелегальной стоянки и врубил трансляцию на миллион зрителей!",
                    "«Друзья, прямо сейчас мы раскрываем наглейшую схему вымогательства миллионов рублей у простых водителей!»",
                ],
                "hud_bal": "1 200 000 ЗРИТЕЛЕЙ",
                "hud_st": "ПРЯМОЙ ЭФИР!",
                "theme": "danger",
                "pill": "ТРАНСЛЯЦИЯ В ИНТЕРНЕТ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "ev4_s2",
                "loc": "guard_booth",
                "sentences": [
                    "Блогер сунул микрофон прямо в решётку будки и показал кассирше запись домофона на планшете.",
                    "Увидев своё начальство на видео, женщина побледнела и в панике попыталась захлопнуть железные ставни!",
                ],
                "hud_bal": "ПАНИКА В БУДКЕ!",
                "hud_st": "УЛИКИ В ЛИЦО",
                "theme": "danger",
                "pill": "КАССИРША ЗАХЛОПНУЛА ОКНО",
                "sfx": "boom",
            },
            {
                "scene_id": "ev4_s3",
                "loc": "live_broadcast",
                "sentences": [
                    "Водитель эвакуатора запрыгнул в кабину и попытался сбежать, но разъярённые жильцы намертво перекрыли выезд своими телами!",
                    "А в следующую секунду улицу оглушил вой сирен!",
                ],
                "hud_bal": "ПОБЕГ СОРВАН!",
                "hud_st": "ВЫЕЗД ПЕРЕКРЫТ",
                "theme": "danger",
                "pill": "ЖИТЕЛИ ПЕРЕКРЫЛИ ВЫЕЗД",
                "sfx": "whoosh",
            },
            {
                "scene_id": "ev4_s4",
                "loc": "live_broadcast",
                "sentences": [
                    "К воротам стоянки на полной скорости подлетел микроавтобус прокуратуры и следственного комитета!",
                    "«Всем оставаться на местах, работает прокуратура!» — скомандовал следователь. Смотри развязку в финале!",
                ],
                "hud_bal": "ПРОКУРАТУРА!",
                "hud_st": "ШТУРМ СТОЯНКИ!",
                "theme": "danger",
                "pill": "РЕЙД ПРОКУРАТУРЫ И СК",
                "sfx": "boom",
            },
        ],
    },
    5: {
        "filename": "evacuator_ep5_finale.mp4",
        "title": "Фальшивый эвакуатор • Часть 5: Разгром стоянки и 3 правила",
        "chapters": [
            {
                "scene_id": "ev5_s1",
                "loc": "live_broadcast",
                "sentences": [
                    "Финал истории! В ходе обыска в сейфе будки нашли двенадцать миллионов рублей неучтённой наличности и пачки поддельных протоколов.",
                    "Стоянку опечатали, а организаторам банды грозит до десяти лет тюрьмы за мошенничество и самоуправство!",
                ],
                "hud_bal": "12 МЛН НАЛИЧНЫМИ",
                "hud_st": "ДО 10 ЛЕТ ТЮРЬМЫ",
                "theme": "danger",
                "pill": "ОБЫСК • АРЕСТ ОРГАНИЗАТОРОВ",
                "sfx": "boom",
            },
            {
                "scene_id": "ev5_s2",
                "loc": "fake_impound_lot",
                "sentences": [
                    "Ворота стоянки распахнули настежь, и следователи лично вернули все пятнадцать машин жильцам — без единой копейки выкупа!",
                    "Максим пожал руку прокурору и поблагодарил блогера за огласку.",
                ],
                "hud_bal": "15 АВТО СПАСЕНО!",
                "hud_st": "0 РУБЛЕЙ ВЫКУПА",
                "theme": "green",
                "pill": "СПРАВЕДЛИВОСТЬ • АВТО ВЕРНУЛИ",
                "sfx": "coin",
            },
            {
                "scene_id": "ev5_s3",
                "loc": "victory_courtyard",
                "sentences": [
                    "Фальшивый дорожный знак во дворе коммунальщики спилили в тот же день.",
                    "Но чтобы никогда не попасть в такую ловушку, запомните три главных правила юридической защиты!",
                ],
                "hud_bal": "ПОБЕДА!",
                "hud_st": "ЗНАК ЛИКВИДИРОВАН",
                "theme": "green",
                "pill": "ГЛАВНЫЕ ПРАВИЛА ВОДИТЕЛЯ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "ev5_s4",
                "loc": "victory_courtyard",
                "sentences": [
                    "Первое: проверяйте дислокацию знаков в ЦОДД или ГИБДД — самодельный знак законен ровно на ноль процентов!",
                    "Второе: всегда требуйте протокол задержания и акт приёмки. И третье: никогда не платите наличкой в карман! Сохрани и отправь соседям!",
                ],
                "hud_bal": "СТ. 330 УК РФ",
                "hud_st": "НЕ ПЛАТИ НАЛ!",
                "theme": "green",
                "pill": "ЗАЩИТИ СВОЮ МАШИНУ И ПРАВА!",
                "sfx": "coin",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# 5. MASTER EPISODE RENDERER
# ---------------------------------------------------------------------------

def render_evacuator_episode(
    ep_num: int,
    out_dir: Path = Path("output/story_evacuator"),
    speaker: str = "f5",
    fps: int = 30,
    shared_bgs: Optional[Dict[str, Image.Image]] = None,
) -> Path:
    ep = EVACUATOR_EPISODES[ep_num]
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
    voice_wav = work_dir / f"voice_evacuator_ep{ep_num}_{speaker}.wav"
    cached_words = work_dir / f"words_f5_voice_evacuator_ep{ep_num}_{speaker}.json"

    if speaker == "f5" and voice_wav.exists() and cached_words.exists():
        print(f"[EVACUATOR EP{ep_num}] 1. Используем кэшированную GPU-озвучку F5-TTS...")
        voice_file = voice_wav
        meta = json.loads(cached_words.read_text(encoding="utf-8"))
        words = meta["words"]
        duration = float(meta["duration"])
    elif speaker == "f5" and is_f5_available():
        print(f"[EVACUATOR EP{ep_num}] 1. Синтезируем живую озвучку '{ep['title']}' (F5-TTS RTX 4050)...")
        voice_file, words, duration = synthesize_f5_script(all_sentences, out_wav=voice_wav, speed=1.07)
    else:
        print(f"[EVACUATOR EP{ep_num}] 1. Синтезируем Silero v5.6 ({speaker})...")
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
    ass_path = work_dir / f"evacuator_ep{ep_num}.ass"
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
    bgs = shared_bgs if shared_bgs is not None else build_evacuator_backgrounds()
    maxim_sedan = build_maxim_sedan_sprite()
    tow_truck_empty = build_tow_truck_sprite(with_car_on_bed=False)
    tow_truck_loaded = build_tow_truck_sprite(with_car_on_bed=True)
    portable_sign = build_portable_sign_sprite()
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
        # EPISODE 1: ЗНАК В 3 ЧАСА НОЧИ
        # ================================================================
        if sid == "ev1_s1":
            # Maxim locks blue sedan in peaceful night courtyard
            frame = paste_obj(frame, maxim_sedan, 340, 990)
            maxim = render_maxim(mood="confident", mouth_state=mouth, gesture="relax", blink=blink, facing="right", holding_keys=True, scale=0.92)
            frame = paste_char(frame, maxim, 260, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Пять лет тут паркуюсь — места всегда есть!»", anchor_x=320, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "ev1_s2":
            # 03:00 Night: Yellow tow truck arrives, tow driver hammers portable sign into lawn
            frame = paste_obj(frame, tow_truck_empty, 360, 970)
            frame = paste_obj(frame, portable_sign, 220, 990)
            driver = render_tow_driver(mood="shady", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", holding_crowbar=True, scale=0.94)
            frame = paste_char(frame, driver, 820, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Вбивай знак в газон! Утром снимем куш!»", anchor_x=780, anchor_y=800, align="right", pop_scale=pop_late)

        elif sid == "ev1_s3":
            # Tow truck loading sedan and driving off with blinking orange light
            drive_p = max(0.0, (t_local - 1.2) / max(1.0, ch_dur - 1.2))
            tt_x = int(220 + drive_p * 900)
            frame = paste_obj(frame, tow_truck_loaded, tt_x, 970)
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "УВЕЗЛИ 15 МАШИН!", t_local - 0.15, center=(540, 560))

        elif sid == "ev1_s4":
            # 08:00 Morning: Empty courtyard, fresh sign, Maxim in shock
            maxim = render_maxim(mood="shocked", mouth_state=mouth, gesture="hands_on_head", blink=False, facing="right", scale=0.95)
            frame = paste_char(frame, maxim, 380, 1300)
            frame = camera.apply(frame, zoom=1.02 + 0.06 * p_ch, focal_point=(520, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«ГДЕ МОЯ МАШИНА?! ОТКУДА ЗДЕСЬ ЭТОТ ЗНАК?!»", anchor_x=430, anchor_y=800, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 2: СЧЁТ НА 60 000 РУБЛЕЙ
        # ================================================================
        elif sid == "ev2_s1":
            # Industrial impound lot with barbed wire
            maxim = render_maxim(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.93)
            frame = paste_char(frame, maxim, 280, 1305)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Вот они! Все машины со двора загнали сюда!»", anchor_x=340, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "ev2_s2":
            # Guard booth: rude cashier behind window bars demanding 60k
            cashier = render_rude_cashier(mood="shady", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", scale=0.94)
            maxim = render_maxim(mood="shocked", mouth_state="closed", gesture="relax", blink=False, facing="right", scale=0.92)
            frame = paste_char(frame, maxim, 260, 1305)
            frame = paste_char(frame, cashier, 840, 1305)
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            frame = draw_animated_stamp(frame, "СЧЁТ: 60 000 ₽!", t_local - 0.20, center=(540, 560))

        elif sid == "ev2_s3":
            # Cashier demands cash only: "No card, no receipt!"
            cashier = render_rude_cashier(mood="shady", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", scale=0.94)
            maxim = render_maxim(mood="alert", mouth_state="closed", gesture="point_right", blink=blink, facing="right", scale=0.92)
            frame = paste_char(frame, maxim, 270, 1305)
            frame = paste_char(frame, cashier, 840, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Только наличка без чека! Иначе пустим с молотка!»", anchor_x=800, anchor_y=790, align="right", pop_scale=pop_late)

        elif sid == "ev2_s4":
            # Tow driver laughing with crowbar, Maxim determined
            driver = render_tow_driver(mood="smug", mouth_state="closed", gesture="relax", blink=blink, facing="left", holding_crowbar=True, scale=0.95)
            maxim = render_maxim(mood="alert", mouth_state=mouth, gesture="hold_phone", blink=blink, facing="right", scale=0.93)
            frame = paste_char(frame, maxim, 270, 1305)
            frame = paste_char(frame, driver, 830, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Ни копейки не получите! Я найду на вас управу!»", anchor_x=330, anchor_y=800, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 3: НОЧНАЯ ЗАПИСЬ ДОМОФОНА
        # ================================================================
        elif sid == "ev3_s1":
            # Maxim spots smart intercom camera on entrance wall
            maxim = render_maxim(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.93)
            frame = paste_char(frame, maxim, 340, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Стойте! На подъезде же висит умный домофон!»", anchor_x=400, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "ev3_s2":
            # Intercom night-cam screen: zooming into driver's face hammering sign!
            frame = camera.apply(frame, zoom=1.00 + 0.06 * p_ch, focal_point=(540, 960), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Попался! Сам ставит знак в 03:14 ночи!»", anchor_x=340, anchor_y=380, align="left", pop_scale=pop_late)

        elif sid == "ev3_s3":
            # Intercom screen with evidence stamp
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 960), t=t)
            frame = draw_animated_stamp(frame, "СТ. 159 УК РФ: МОШЕННИЧЕСТВО!", t_local - 0.20, center=(540, 680))

        elif sid == "ev3_s4":
            # Maxim calling journalist on phone
            maxim = render_maxim(mood="confident", mouth_state=mouth, gesture="hold_phone", blink=blink, facing="right", holding_phone=True, scale=0.94)
            frame = paste_char(frame, maxim, 340, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Алексей, у меня железные улики! Врубай эфир!»", anchor_x=400, anchor_y=800, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 4: ПРЯМОЙ ЭФИР И ШТУРМ ПРОКУРАТУРЫ
        # ================================================================
        elif sid == "ev4_s1":
            # Blogger live on scene with mic in hand
            blogger = render_blogger(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            maxim = render_maxim(mood="confident", mouth_state="closed", gesture="relax", blink=blink, facing="right", scale=0.91)
            frame = paste_char(frame, blogger, 320, 1305)
            frame = paste_char(frame, maxim, 780, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1000), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«В прямом эфире разоблачаем банду стоянки!»", anchor_x=380, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "ev4_s2":
            # Guard booth: blogger shoves mic, cashier slams window shut in horror
            blogger = render_blogger(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            cashier = render_rude_cashier(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="left", scale=0.92)
            frame = paste_char(frame, blogger, 270, 1305)
            frame = paste_char(frame, cashier, 840, 1305)
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Посмотрите на экран! Узнаёте своего водителя?!»", anchor_x=340, anchor_y=790, align="left", pop_scale=pop_late)

        elif sid == "ev4_s3":
            # Tow driver trying to escape, residents blocking
            driver = render_tow_driver(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="right", holding_crowbar=False, scale=0.93)
            maxim = render_maxim(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", scale=0.93)
            frame = paste_char(frame, driver, 340, 1305)
            frame = paste_char(frame, maxim, 800, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Куда побежал?! Стоять на месте!»", anchor_x=760, anchor_y=800, align="right", pop_scale=pop_late)

        elif sid == "ev4_s4":
            # Prosecutor arriving with siren strobes!
            prosecutor = render_prosecutor(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.95)
            driver = render_tow_driver(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="left", holding_crowbar=False, scale=0.93)
            frame = paste_char(frame, prosecutor, 290, 1305)
            frame = paste_char(frame, driver, 840, 1305)
            frame = draw_siren_flash(frame, t)
            shake = ((1.0 - t_local / 0.5) ** 1.4) if t_local <= 0.5 else 0.0
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 1020), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "ПРОКУРАТУРА! РУКИ НА КАПОТ!", t_local - 0.15, center=(540, 520))

        # ================================================================
        # EPISODE 5: РАЗГРОМ СТОЯНКИ И 3 ПРАВИЛА
        # ================================================================
        elif sid == "ev5_s1":
            # Search of lot: safe opened with 12M cash, handcuffs
            prosecutor = render_prosecutor(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            cashier = render_rude_cashier(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="left", scale=0.92)
            frame = paste_char(frame, prosecutor, 290, 1305)
            frame = paste_char(frame, cashier, 820, 1305)
            frame = draw_siren_flash(frame, t)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "СТ. 159 + СТ. 330: АРЕСТ!", t_local - 0.20, center=(540, 520))

        elif sid == "ev5_s2":
            # Impound lot gates opened: all cars returned free!
            frame = paste_obj(frame, maxim_sedan, 270, 990)
            prosecutor = render_prosecutor(mood="confident", mouth_state="closed", gesture="thumbs_up", blink=blink, facing="right", scale=0.92)
            maxim = render_maxim(mood="confident", mouth_state=mouth, gesture="relax", blink=blink, facing="left", holding_keys=True, scale=0.92)
            frame = paste_char(frame, prosecutor, 260, 1305)
            frame = paste_char(frame, maxim, 830, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Все 15 машин освобождены! Справедливость есть!»", anchor_x=320, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "ev5_s3":
            # Victory courtyard: Maxim next to blue sedan smiling
            frame = paste_obj(frame, maxim_sedan, 380, 990)
            maxim = render_maxim(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            frame = paste_char(frame, maxim, 280, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Запомните 3 правила против автоловушек!»", anchor_x=340, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "ev5_s4":
            # Finale: Maxim gives thumbs up, legal checklist stamp
            frame = paste_obj(frame, maxim_sedan, 380, 990)
            maxim = render_maxim(mood="confident", mouth_state=mouth, gesture="thumbs_up", blink=blink, facing="right", scale=0.95)
            frame = paste_char(frame, maxim, 270, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "ПРОВЕРЯЙ ДИСЛОКАЦИЮ В ГИБДД!", t_local - 0.15, center=(540, 520))

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
    print(f"[EVACUATOR EP{ep_num}] 2. Рендерим анимацию ({ep['title']})...")
    total_frames = int(duration * fps)
    raw_video = work_dir / f"raw_evacuator_ep{ep_num}.mp4"

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

    print(f"[EVACUATOR EP{ep_num}] 3. Финальная сборка MP4 (субтитры ASS + аудио)...")
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


def render_all_evacuator_episodes(speaker: str = "f5", fps: int = 30) -> List[Path]:
    print("=" * 65)
    print("🚛 ФАЛЬШИВЫЙ ЭВАКУАТОР И ШТРАФСТОЯНКА В ПРОМЗОНЕ")
    print(f"   Движок: v3 PRO • Озвучка: {speaker.upper()} • Выход: output/story_evacuator/")
    print("=" * 65)
    shared_bgs = build_evacuator_backgrounds()
    outputs = []
    for ep_num in range(1, 6):
        out = render_evacuator_episode(ep_num, speaker=speaker, fps=fps, shared_bgs=shared_bgs)
        outputs.append(out)
    print("=" * 65)
    print("🎉 ВСЕ 5 СЕРИЙ УСПЕШНО СГЕНЕРИРОВАНЫ В output/story_evacuator/")
    print("=" * 65)
    return outputs


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate 5-part Fake Tow Truck / Impound Lot animated series.")
    parser.add_argument("--ep", type=int, default=0, help="Episode number (1-5), or 0 for all 5.")
    parser.add_argument("--speaker", type=str, default="f5", help="Voice engine: f5 (GPU) or eugene/aidar")
    args = parser.parse_args()

    bgs = build_evacuator_backgrounds()
    episodes = [args.ep] if args.ep in (1, 2, 3, 4, 5) else [1, 2, 3, 4, 5]

    for ep_num in episodes:
        render_evacuator_episode(ep_num=ep_num, speaker=args.speaker, shared_bgs=bgs)


if __name__ == "__main__":
    main()
