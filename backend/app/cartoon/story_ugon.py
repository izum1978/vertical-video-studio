"""
Standalone 5-Part Animated Mini-Series: "УГОН НА «УДОЧКУ»" (v3 PRO Engine).
100% Brand-New Characters & Brand-New 2x-Supersampled Locations (independent story!):

Characters:
- Igor (bearded courier/driver in olive-green jacket)
- Hacker #1 & #2 (black hoodies + black balaclavas + glowing radio-relay "fishing rod" antenna!)
- Chop-Shop Boss (greasy dark vest, cap, wrench)
- Criminal Detective (tan/beige trench coat + crimson detective ID badge)
- SWAT Officer (tactical black helmet, visor, armored vest)

Locations:
- Mall Coffee Shop ("COFFEE TO GO" + pastry counter + animated green radio relay waves!)
- Mall Underground Parking ("СЕКТОР B • МЕСТО 42" + Igor's silver crossover SUV)
- Dark Glowing GPS Tracker Map (pulsing red tracking dot -> red "ГЛУШИЛКА GPS!" alert)
- Industrial Night Gate (chain-link fence, red-white barrier, factory chimneys)
- Underground Chop-Shop Hangar (corrugated steel hangar, engine hoist, 3 stolen cars inside!)
- Golden Sunrise Plaza (warm sunrise sky, reunited Igor with his silver crossover)
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
from backend.app.cartoon.v3_part2 import draw_rec_camera_overlay
from backend.app.cinematic.subtitles import generate_cinematic_ass

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


# ---------------------------------------------------------------------------
# 1. BRAND-NEW CHARACTERS FOR "УГОН НА УДОЧКУ"
# ---------------------------------------------------------------------------

def render_igor(
    mood: str = "confident",
    mouth_state: str = "closed",
    gesture: str = "relax",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    holding_coffee: bool = False,
    scale: float = 0.93,
) -> Image.Image:
    """Igor — bearded driver in olive-green utility jacket."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(77, 110, 62), hair_style="messy",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    shift = 8 if facing == "right" else -8
    # Neat short brown-charcoal beard along chin!
    d.arc([cx - 58 + shift // 2, 198, cx + 58 + shift // 2, 260], start=18, end=162, fill=(58, 44, 36, 255), width=16)

    # Optional hot takeaway coffee cup in right hand!
    if holding_coffee:
        hx = cx + 86 if facing == "right" else cx - 86
        hy = 340
        d.polygon([(hx - 14, hy + 24), (hx + 14, hy + 24), (hx + 18, hy - 14), (hx - 18, hy - 14)], fill=(254, 243, 199, 255), outline=INK)
        d.rectangle([(hx - 20, hy - 20), (hx + 20, hy - 12)], fill=(255, 255, 255, 255), outline=INK, width=2)
        d.rectangle([(hx - 15, hy - 2), (hx + 15, hy + 10)], fill=(180, 83, 9, 255))

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_hacker_masked(
    mood: str = "shady",
    mouth_state: str = "closed",
    gesture: str = "hold_phone",
    with_backpack_antenna: bool = False,
    walk_phase: float = 0.0,
    facing: str = "left",
    scale: float = 0.92,
) -> Image.Image:
    """Car Thief / Relay Hacker in black hoodie + black balaclava ski-mask + optional relay antenna!"""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(28, 32, 40), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=False, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    shift = 10 if facing == "right" else -10

    # Black balaclava covering head except eye-slit!
    d.ellipse([cx - 75, 114, cx + 75, 264], fill=(22, 26, 34, 255), outline=INK, width=5)
    # Pale skin eye-slit cutout
    d.rounded_rectangle([(cx - 48 + shift, 168), (cx + 48 + shift, 204)], radius=14, fill=(250, 245, 240, 255), outline=INK, width=3)
    # Eyes inside balaclava slit
    ex_l, ex_r, ey = cx - 22 + shift, cx + 22 + shift, 186
    if mood == "shocked":
        d.ellipse([ex_l - 12, ey - 12, ex_l + 12, ey + 12], fill=(255, 255, 255, 255), outline=INK, width=3)
        d.ellipse([ex_r - 12, ey - 12, ex_r + 12, ey + 12], fill=(255, 255, 255, 255), outline=INK, width=3)
        d.ellipse([ex_l - 4, ey - 4, ex_l + 4, ey + 4], fill=INK)
        d.ellipse([ex_r - 4, ey - 4, ex_r + 4, ey + 4], fill=INK)
    else:
        d.ellipse([ex_l - 6, ey - 6, ex_l + 6, ey + 6], fill=INK)
        d.ellipse([ex_r - 6, ey - 6, ex_r + 6, ey + 6], fill=INK)

    # Backpack + Relay Antenna sticking up with glowing green LED tip!
    if with_backpack_antenna:
        bx = cx - 64 if facing == "right" else cx + 32
        d.rounded_rectangle([(bx, 272), (bx + 36, 390)], radius=8, fill=(15, 23, 42, 255), outline=INK, width=3)
        ax = bx + 18
        d.line([(ax, 272), (ax, 145)], fill=(148, 163, 184, 255), width=5)
        d.ellipse([ax - 10, 135, ax + 10, 155], fill=(34, 197, 94, 255), outline=INK, width=3)

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_detective(
    mood: str = "confident",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    scale: float = 0.94,
) -> Image.Image:
    """Criminal Investigation Detective in warm tan trench coat & red badge."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(188, 152, 108), hair_style="slicked",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    # Coat lapel + dark tie + red police detective ID badge!
    d.polygon([(cx - 24, 266), (cx, 330), (cx + 24, 266)], fill=(248, 250, 252, 255), outline=INK)
    d.polygon([(cx - 6, 276), (cx + 6, 276), (cx + 8, 345), (cx, 355), (cx - 8, 345)], fill=(30, 41, 59, 255))
    d.rounded_rectangle([(cx + 20, 300), (cx + 48, 324)], radius=4, fill=(220, 38, 38, 255), outline=INK, width=2)
    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_swat_officer(
    gesture: str = "point_right",
    walk_phase: float = 0.0,
    facing: str = "right",
    scale: float = 0.95,
) -> Image.Image:
    """Tactical SWAT / OMON Officer in black helmet, tinted visor, armored vest."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(24, 30, 42), hair_style="undercut",
        mood="alert", mouth_state="closed", gesture=gesture,
        blink=False, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    shift = 10 if facing == "right" else -10
    # Tactical helmet + dark glass visor
    d.chord([cx - 82, 104, cx + 82, 215], start=180, end=360, fill=(30, 41, 59, 255), outline=INK, width=5)
    d.rounded_rectangle([(cx - 56 + shift, 152), (cx + 56 + shift, 206)], radius=12, fill=(15, 23, 42, 240), outline=(148, 163, 184, 255), width=4)
    # Armored vest chest plate + yellow "ОМОН" tag
    d.rounded_rectangle([(cx - 52, 286), (cx + 52, 388)], radius=10, fill=(36, 44, 58, 255), outline=INK, width=4)
    d.rectangle([(cx - 38, 308), (cx + 38, 326)], fill=(250, 204, 21, 255), outline=INK, width=2)
    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def build_crossover_sprite(
    body_color: Tuple[int, int, int] = (148, 163, 184),
    headlights_flash: bool = False,
) -> Image.Image:
    """Igor's sleek silver-teal crossover SUV sprite."""
    S = 2
    W, H = 560 * S, 250 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _draw_car(d, cx=280 * S, wheel_y=182 * S, S=S, body_color=body_color, split_gap=0)
    # Roof rails for crossover look!
    d.line([(205 * S, 42 * S), (355 * S, 42 * S)], fill=INK, width=6 * S)
    if headlights_flash:
        # Bright glowing headlight beam flash when unlocked by relay!
        d.polygon([(520 * S, 130 * S), (560 * S, 90 * S), (560 * S, 185 * S), (520 * S, 155 * S)], fill=(254, 240, 138, 190))
    return img.resize((560, 250), Image.Resampling.LANCZOS)


def build_swat_van_sprite() -> Image.Image:
    """Dark tactical SWAT van sprite with flashing red/blue lightbar."""
    S = 2
    W, H = 580 * S, 270 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink_w = 5 * S
    d.rounded_rectangle([(20 * S, 36 * S), (560 * S, 215 * S)], radius=18 * S, fill=(24, 30, 44, 255), outline=INK, width=ink_w)
    # Armored blue stripe + text
    d.rectangle([(24 * S, 140 * S), (556 * S, 166 * S)], fill=(37, 99, 235, 255))
    d.text((170 * S, 82 * S), "СПЕЦНАЗ", fill=(250, 204, 21, 255), font=_font(FONT_IMPACT, 44 * S))
    # Roof siren lightbar
    d.rounded_rectangle([(240 * S, 12 * S), (290 * S, 36 * S)], radius=6 * S, fill=(239, 68, 68, 255), outline=INK, width=3 * S)
    d.rounded_rectangle([(290 * S, 12 * S), (340 * S, 36 * S)], radius=6 * S, fill=(59, 130, 246, 255), outline=INK, width=3 * S)
    # Heavy wheels
    for wx in [135 * S, 445 * S]:
        d.ellipse([wx - 40 * S, 180 * S, wx + 40 * S, 258 * S], fill=(15, 20, 30, 255), outline=INK, width=ink_w)
        d.ellipse([wx - 18 * S, 202 * S, wx + 18 * S, 236 * S], fill=(148, 163, 184, 255), outline=INK, width=3 * S)
    return img.resize((580, 270), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 2. 6 BRAND-NEW 2x-SUPERSAMPLED LOCATIONS FOR "УГОН НА УДОЧКУ"
# ---------------------------------------------------------------------------

def build_ugon_backgrounds() -> Dict[str, Image.Image]:
    S = 2
    W, H = 1080 * S, 1920 * S
    bgs = {}

    # ------------------------------------------------------------------
    # LOC 1: MALL COFFEE SHOP ("COFFEE TO GO")
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (242, 235, 224, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Warm café brick/cream wall
    d.rectangle([(0, 0), (W, floor_y)], fill=(244, 236, 224, 255))
    # Dark chalkboard menu above counter
    d.rounded_rectangle([(150 * S, 270 * S), (930 * S, 515 * S)], radius=18 * S, fill=(30, 41, 59, 255), outline=(146, 84, 46, 255), width=8 * S)
    f_c1 = _font(FONT_IMPACT, 56 * S)
    ct1 = "COFFEE TO GO • ТЦ ГАЛЕРЕЯ"
    cbb1 = f_c1.getbbox(ct1)
    d.text(((W - (cbb1[2] - cbb1[0])) // 2, 305 * S), ct1, fill=(254, 240, 138, 255), font=f_c1)
    f_c2 = _font(FONT_BOLD, 28 * S)
    ct2 = "АМЕРИКАНО 190₽  •  КАПУЧИНО 240₽  •  ЛАТТЕ 260₽"
    cbb2 = f_c2.getbbox(ct2)
    d.text(((W - (cbb2[2] - cbb2[0])) // 2, 415 * S), ct2, fill=(226, 232, 240, 255), font=f_c2)

    # Café Counter + Espresso Machine on Left!
    d.rounded_rectangle([(60 * S, 960 * S), (460 * S, floor_y)], radius=12 * S, fill=(146, 92, 54, 255), outline=INK, width=5 * S)
    d.rectangle([(48 * S, 944 * S), (472 * S, 970 * S)], fill=(248, 250, 252, 255), outline=INK, width=4 * S)
    # Silver Espresso Machine
    d.rounded_rectangle([(110 * S, 810 * S), (290 * S, 944 * S)], radius=12 * S, fill=(148, 163, 184, 255), outline=INK, width=5 * S)
    d.rectangle([(140 * S, 845 * S), (260 * S, 900 * S)], fill=(30, 41, 59, 255), outline=INK, width=3 * S)

    # Clean Mall Tile Floor
    d.rectangle([(0, floor_y), (W, H)], fill=(236, 232, 226, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["mall_cafe"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 2: MALL UNDERGROUND PARKING ("СЕКТОР B • МЕСТО 42")
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (206, 214, 224, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S
    d.rectangle([(0, 0), (W, floor_y)], fill=(196, 206, 218, 255))

    # Concrete pillars with blue mall sector stripe "B-42"
    for px in [115 * S, 965 * S]:
        d.rectangle([(px - 52 * S, 200 * S), (px + 52 * S, floor_y)], fill=(148, 163, 184, 255), outline=INK, width=5 * S)
        d.rectangle([(px - 52 * S, 560 * S), (px + 52 * S, 680 * S)], fill=(37, 99, 235, 255), outline=INK, width=4 * S)
        d.text((px - 36 * S, 598 * S), "B-42", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 34 * S))

    # Ceiling Parking Sign + Green LED indicator
    d.rounded_rectangle([(230 * S, 270 * S), (850 * S, 360 * S)], radius=16 * S, fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=5 * S)
    f_mp = _font(FONT_BOLD, 40 * S)
    mpt = "ПАРКИНГ ТЦ • СЕКТОР B-42"
    mpb = f_mp.getbbox(mpt)
    d.text(((W - (mpb[2] - mpb[0])) // 2, 290 * S), mpt, fill=(255, 255, 255, 255), font=f_mp)

    # Clean Parking Concrete Floor + Yellow Bay Box
    d.rectangle([(0, floor_y), (W, H)], fill=(224, 226, 230, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    d.line([(220 * S, floor_y), (140 * S, 1420 * S)], fill=(250, 204, 21, 255), width=10 * S)
    d.line([(860 * S, floor_y), (940 * S, 1420 * S)], fill=(250, 204, 21, 255), width=10 * S)

    bgs["mall_parking"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 3: DARK GLOWING GPS TRACKER RADAR MAP (Live & Jammed!)
    # ------------------------------------------------------------------
    for mode in ["gps_live", "gps_jammed"]:
        img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
        d = ImageDraw.Draw(img)
        floor_y = 1245 * S
        d.rectangle([(0, 0), (W, floor_y)], fill=(18, 26, 44, 255))

        # Big Tablet/Map Radar Frame
        mx1, my1, mx2, my2 = 110 * S, 270 * S, 970 * S, 780 * S
        brd = (34, 197, 94, 255) if mode == "gps_live" else (239, 68, 68, 255)
        d.rounded_rectangle([(mx1, my1), (mx2, my2)], radius=24 * S, fill=(10, 18, 30, 255), outline=brd, width=6 * S)

        # Glowing cyan city street grid inside map!
        for gx in range(mx1 + 70 * S, mx2, 110 * S):
            d.line([(gx, my1 + 65 * S), (gx, my2 - 65 * S)], fill=(30, 58, 90, 200), width=3 * S)
        for gy in range(my1 + 90 * S, my2 - 60 * S, 90 * S):
            d.line([(mx1 + 25 * S, gy), (mx2 - 25 * S, gy)], fill=(30, 58, 90, 200), width=3 * S)

        # Glowing GPS route path from Mall (left) to Industrial Zone (right)!
        route = [(210 * S, 640 * S), (390 * S, 560 * S), (580 * S, 510 * S), (810 * S, 430 * S)]
        d.line(route, fill=(56, 189, 248, 255), width=8 * S, joint="curve")
        # Pulsing target circles at destination
        tx, ty = 810 * S, 430 * S
        t_col = (239, 68, 68, 255)
        d.ellipse([tx - 62 * S, ty - 62 * S, tx + 62 * S, ty + 62 * S], outline=t_col, width=4 * S)
        d.ellipse([tx - 34 * S, ty - 34 * S, tx + 34 * S, ty + 34 * S], outline=t_col, width=4 * S)
        d.ellipse([tx - 16 * S, ty - 16 * S, tx + 16 * S, ty + 16 * S], fill=t_col)

        if mode == "gps_live":
            d.text((mx1 + 32 * S, my1 + 22 * S), "GPS-МАЯК АКТИВЕН  |  95 КМ/Ч  |  ПРОМЗОНА", fill=(74, 222, 128, 255), font=_font(FONT_BOLD, 26 * S))
            d.text((mx1 + 140 * S, my2 - 58 * S), "ЦЕЛЬ ДВИЖЕТСЯ К СКЛАДУ №7!", fill=(254, 240, 138, 255), font=_font(FONT_BOLD, 30 * S))
        else:
            d.text((mx1 + 32 * S, my1 + 22 * S), "ВНИМАНИЕ: ВКЛЮЧЕНА ГЛУШИЛКА GPS!", fill=(248, 113, 113, 255), font=_font(FONT_BOLD, 28 * S))
            d.rounded_rectangle([(230 * S, 455 * S), (850 * S, 585 * S)], radius=16 * S, fill=(127, 29, 29, 235), outline=(248, 113, 113, 255), width=5 * S)
            d.text((285 * S, 488 * S), "СИГНАЛ ПОТЕРЯН • СКЛАД №7", fill=(255, 255, 255, 255), font=_font(FONT_IMPACT, 42 * S))

        d.rectangle([(0, floor_y), (W, H)], fill=(228, 230, 235, 255))
        d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
        bgs[mode] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 4: INDUSTRIAL NIGHT GATE (Barrier + Factory Chimneys + Fence)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (24, 34, 52, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S
    # Moody night sky
    for y in range(0, floor_y, 4):
        rat = y / floor_y
        d.rectangle([(0, y), (W, y + 4)], fill=(int(18 + rat * 22), int(26 + rat * 26), int(44 + rat * 36), 255))

    # Factory silhouettes + smokestacks
    d.rectangle([(80 * S, 640 * S), (460 * S, floor_y)], fill=(36, 46, 62, 255), outline=INK, width=4 * S)
    d.rectangle([(140 * S, 420 * S), (200 * S, 640 * S)], fill=(46, 56, 72, 255), outline=INK, width=4 * S)
    d.rectangle([(640 * S, 690 * S), (1020 * S, floor_y)], fill=(36, 46, 62, 255), outline=INK, width=4 * S)

    # Industrial Gate Sign: "ПРОМЗОНА • СКЛАД №7"
    d.rounded_rectangle([(240 * S, 275 * S), (840 * S, 360 * S)], radius=14 * S, fill=(15, 23, 42, 245), outline=(250, 204, 21, 255), width=5 * S)
    f_ig = _font(FONT_BOLD, 40 * S)
    igt = "ПРОМЗОНА • АНГАР №7"
    igb = f_ig.getbbox(igt)
    d.text(((W - (igb[2] - igb[0])) // 2, 294 * S), igt, fill=(254, 240, 138, 255), font=f_ig)

    # Red-White Striped Security Barrier Gate!
    d.rectangle([(120 * S, 1010 * S), (175 * S, floor_y)], fill=(220, 38, 38, 255), outline=INK, width=4 * S)
    d.rectangle([(150 * S, 1020 * S), (920 * S, 1054 * S)], fill=(255, 255, 255, 255), outline=INK, width=4 * S)
    for sx in range(180 * S, 890 * S, 110 * S):
        d.rectangle([(sx, 1022 * S), (sx + 55 * S, 1052 * S)], fill=(220, 38, 38, 255))

    # Clean light asphalt floor for characters & subtitles
    d.rectangle([(0, floor_y), (W, H)], fill=(216, 220, 226, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["industrial_gate"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 5: UNDERGROUND CHOP-SHOP HANGAR (Corrugated Steel + Multiple Cars!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (44, 48, 56, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S
    d.rectangle([(0, 0), (W, floor_y)], fill=(52, 58, 68, 255))
    # Corrugated steel vertical ribs
    for rx in range(0, W, 64 * S):
        d.line([(rx, 0), (rx, floor_y)], fill=(40, 46, 54, 255), width=4 * S)

    # Hanging industrial factory lamps casting warm light cones
    for lx in [270 * S, 810 * S]:
        d.line([(lx, 180 * S), (lx, 285 * S)], fill=INK, width=6 * S)
        d.polygon([(lx - 58 * S, 325 * S), (lx + 58 * S, 325 * S), (lx + 26 * S, 285 * S), (lx - 26 * S, 285 * S)], fill=(100, 116, 139, 255), outline=INK)
        cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(cone).polygon([(lx - 48 * S, 325 * S), (lx + 48 * S, 325 * S), (lx + 240 * S, floor_y), (lx - 240 * S, floor_y)], fill=(254, 240, 138, 24))
        img = Image.alpha_composite(img, cone)
        d = ImageDraw.Draw(img)

    # Stack of stolen car tires on left + Hangar Banner
    d.rounded_rectangle([(240 * S, 260 * S), (840 * S, 345 * S)], radius=14 * S, fill=(30, 41, 59, 255), outline=(239, 68, 68, 255), width=5 * S)
    f_ch = _font(FONT_BOLD, 38 * S)
    cht = "ПОДПОЛЬНАЯ РАЗБОРКА • 8 АВТО"
    chb = f_ch.getbbox(cht)
    d.text(((W - (chb[2] - chb[0])) // 2, 278 * S), cht, fill=(254, 202, 202, 255), font=f_ch)

    # Background stolen car silhouettes (red & blue) parked in the back of the hangar!
    _draw_car(d, cx=320 * S, wheel_y=990 * S, S=S, body_color=(185, 28, 28), split_gap=0)
    _draw_car(d, cx=780 * S, wheel_y=990 * S, S=S, body_color=(37, 99, 235), split_gap=0)

    # Concrete garage floor
    d.rectangle([(0, floor_y), (W, H)], fill=(224, 224, 222, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["chop_shop"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 6: GOLDEN SUNRISE PLAZA (Warm Finale Sky + Reunited Car!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (254, 215, 170, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S
    # Warm golden-peach sunrise sky gradient!
    for y in range(0, floor_y, 4):
        rat = y / floor_y
        c = (int(253), int(186 + rat * 52), int(116 + rat * 85), 255)
        d.rectangle([(0, y), (W, y + 4)], fill=c)

    # Rising bright sun
    d.ellipse([780 * S, 260 * S, 940 * S, 420 * S], fill=(254, 249, 195, 255), outline=(250, 204, 21, 255), width=6 * S)
    # Soft warm city skyline
    for bx, bw, bh in [(30, 180, 380), (240, 200, 480), (650, 210, 440), (880, 170, 360)]:
        d.rectangle([(bx * S, floor_y - bh * S), ((bx + bw) * S, floor_y)], fill=(148, 132, 138, 210), outline=INK, width=4 * S)

    # Clean sunlit plaza floor
    d.rectangle([(0, floor_y), (W, H)], fill=(244, 238, 228, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["dawn_plaza"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    return bgs


def draw_radio_waves(canvas: Image.Image, cx: int, cy: int, t: float) -> Image.Image:
    """Draws animated expanding glowing green radio-relay waves from hacker's backpack!"""
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for k in range(3):
        phase = (t * 1.8 + k * 0.33) % 1.0
        r = int(20 + phase * 180)
        alpha = int((1.0 - phase) * 230)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(34, 197, 94, alpha), width=6)
    return Image.alpha_composite(canvas, overlay)


# ---------------------------------------------------------------------------
# 3. ALL 5 STANDALONE EPISODES OF "УГОН НА «УДОЧКУ»"
# ---------------------------------------------------------------------------

UGON_EPISODES = {
    1: {
        "filename": "ugon_ep1_cafe.mp4",
        "title": "Угон на «удочку» • Часть 1: 18 секунд в кофейне",
        "chapters": [
            {
                "scene_id": "u1_s1",
                "loc": "mall_parking",
                "sentences": [
                    "Я заехал в торговый центр буквально на пять минут — взять горячий кофе после тяжёлой смены.",
                    "Закрыл свой кроссовер с кнопки и спокойно пошёл внутрь.",
                ],
                "hud_bal": "2 500 000 ₽",
                "hud_st": "АВТО НА ПАРКОВКЕ",
                "theme": "green",
                "pill": "ПАРКИНГ ТЦ • МЕСТО B-42",
                "sfx": "whoosh",
            },
            {
                "scene_id": "u1_s2",
                "loc": "mall_cafe",
                "sentences": [
                    "В очереди за кофе ко мне вплотную встал странный парень с чёрным рюкзаком.",
                    "Я даже не догадывался, что внутри у него спрятана мощная антенна-удочка!",
                ],
                "hud_bal": "2 500 000 ₽",
                "hud_st": "СКАН КЛЮЧА!",
                "theme": "alert",
                "pill": "КОФЕЙНЯ ТЦ • ПЕРЕХВАТ СИГНАЛА",
                "sfx": "phone",
            },
            {
                "scene_id": "u1_s3",
                "loc": "mall_parking",
                "sentences": [
                    "Антенна перехватила сигнал моего ключа через две бетонные стены и передала подельнику на парковку!",
                    "Машина открылась сама и уехала ровно за восемнадцать секунд!",
                ],
                "hud_bal": "0 ₽ (УГНАНА!)",
                "hud_st": "УГОН ЗА 18 СЕК!",
                "theme": "danger",
                "pill": "БЕСКЛЮЧЕВОЙ УГОН НА «УДОЧКУ»",
                "sfx": "boom",
            },
            {
                "scene_id": "u1_s4",
                "loc": "mall_parking",
                "sentences": [
                    "Я спустился со стаканом кофе, а на моём месте — пусто!",
                    "Но угонщики забыли проверить одно секретное место в салоне... Продолжение во второй части!",
                ],
                "hud_bal": "2 500 000 ₽ ?",
                "hud_st": "МАШИНА ИСЧЕЗЛА!",
                "theme": "danger",
                "pill": "ПУСТОЕ МЕСТО B-42 • ИНТРИГА",
                "sfx": "drip",
            },
        ],
    },
    2: {
        "filename": "ugon_ep2_gps.mp4",
        "title": "Угон на «удочку» • Часть 2: Секретный маячок и глушилка",
        "chapters": [
            {
                "scene_id": "u2_s1",
                "loc": "mall_parking",
                "sentences": [
                    "Часть вторая. Охрана парковки только развела руками, а я спокойно достал телефон.",
                    "Ещё полгода назад я спрятал под обшивкой заднего сиденья копеечный автономный маячок!",
                ],
                "hud_bal": "МАЯК: 3 000 ₽",
                "hud_st": "ЗАПУСК ПОИСКА!",
                "theme": "green",
                "pill": "СЕКРЕТНЫЙ GPS-МАЯК В САЛОНЕ",
                "sfx": "coin",
            },
            {
                "scene_id": "u2_s2",
                "loc": "gps_live",
                "sentences": [
                    "Открываю приложение — и вот она! Красная точка живая!",
                    "На скорости девяносто пять километров в час машина уходит на окраину города, в старую промзону!",
                ],
                "hud_bal": "95 КМ/Ч",
                "hud_st": "СИГНАЛ ПОЙМАН!",
                "theme": "green",
                "pill": "ТРЕКЕР В РЕАЛЬНОМ ВРЕМЕНИ",
                "sfx": "phone",
            },
            {
                "scene_id": "u2_s3",
                "loc": "industrial_gate",
                "sentences": [
                    "Я тут же набрал знакомого детектива уголовного розыска и скинул ему живую геолокацию.",
                    "Через пять минут мы уже мчались в промзону, пока сигнал не пропал!",
                ],
                "hud_bal": "14 КМ ДО ЦЕЛИ",
                "hud_st": "ПОГОНЯ В НОЧИ!",
                "theme": "alert",
                "pill": "УГОЛОВНЫЙ РОЗЫСК • ВЫЕЗД",
                "sfx": "whoosh",
            },
            {
                "scene_id": "u2_s4",
                "loc": "gps_jammed",
                "sentences": [
                    "И вдруг точка резко остановилась у заброшенного завода... а через секунду экран покраснел!",
                    "Угонщики включили глушилку! Последний адрес — склад номер семь. Смотри третью часть!",
                ],
                "hud_bal": "СИГНАЛ: 0%",
                "hud_st": "ГЛУШИЛКА GPS!",
                "theme": "danger",
                "pill": "ПОСЛЕДНЯЯ ТОЧКА • СКЛАД №7",
                "sfx": "boom",
            },
        ],
    },
    3: {
        "filename": "ugon_ep3_hangar.mp4",
        "title": "Угон на «удочку» • Часть 3: Заброшенный ангар №7",
        "chapters": [
            {
                "scene_id": "u3_s1",
                "loc": "industrial_gate",
                "sentences": [
                    "Часть третья. Мы подъехали к ночной промзоне с выключенными фарами.",
                    "Вокруг тишина, и только из щелей седьмого ангара пробивался яркий свет сварки!",
                ],
                "hud_bal": "23:45",
                "hud_st": "РАЗВЕДКА У СКЛАДА",
                "theme": "alert",
                "pill": "ПРОМЗОНА • ЗАБРОШЕННЫЙ АНГАР №7",
                "sfx": "whoosh",
            },
            {
                "scene_id": "u3_s2",
                "loc": "chop_shop",
                "sentences": [
                    "Детектив заглянул в окно и обомлел. Внутри стояла не только моя машина!",
                    "Там было сразу восемь угнанных кроссоверов, которые уже готовили к разбору на запчасти!",
                ],
                "hud_bal": "8 УГНАННЫХ АВТО",
                "hud_st": "ЛОГОВО НАЙДЕНО!",
                "theme": "danger",
                "pill": "ПОДПОЛЬНАЯ РАЗБОРКА • 20 МЛН ₽",
                "sfx": "boom",
            },
            {
                "scene_id": "u3_s3",
                "loc": "chop_shop",
                "sentences": [
                    "И в эту секунду их механик нашёл мой маячок под сиденьем!",
                    "В ангаре поднялась паника — они начали срочно перегонять машины к чёрному выезду!",
                ],
                "hud_bal": "МАЯК РАСКРЫТ!",
                "hud_st": "ПОПЫТКА ПОБЕГА!",
                "theme": "danger",
                "pill": "ТРЕВОГА В АНГАРЕ • БАНДА БЕЖИТ",
                "sfx": "boom",
            },
            {
                "scene_id": "u3_s4",
                "loc": "industrial_gate",
                "sentences": [
                    "Ждать было нельзя ни секунды! Детектив вызвал группу захвата по рации!",
                    "А мы перекрыли единственный выезд через шлагбаум! Жёсткий штурм — в четвёртой части!",
                ],
                "hud_bal": "СПЕЦНАЗ В ПУТИ",
                "hud_st": "ВЫЕЗД ПЕРЕКРЫТ!",
                "theme": "alert",
                "pill": "ВЫЗОВ ГРУППЫ ЗАХВАТА",
                "sfx": "phone",
            },
        ],
    },
    4: {
        "filename": "ugon_ep4_raid.mp4",
        "title": "Угон на «удочку» • Часть 4: Ночной штурм ангара",
        "chapters": [
            {
                "scene_id": "u4_s1",
                "loc": "industrial_gate",
                "sentences": [
                    "Часть четвёртая. Ворота ангара распахнулись, и угонщики рванули прямо на шлагбаум!",
                    "Но в ту же секунду дорогу намертво перекрыл фургон спецназа!",
                ],
                "hud_bal": "ОПЕРАЦИЯ",
                "hud_st": "БЛОКПОСТ НА ВЫЕЗДЕ!",
                "theme": "danger",
                "pill": "ПРОМЗОНА • ПЕРЕХВАТ СПЕЦНАЗА",
                "sfx": "boom",
            },
            {
                "scene_id": "u4_s2",
                "loc": "chop_shop",
                "sentences": [
                    "Спецназ ворвался внутрь ангара ровно за четыре секунды!",
                    "Никто из банды даже не успел добежать до запасного выхода!",
                ],
                "hud_bal": "4 СЕКУНДЫ",
                "hud_st": "ШТУРМ АНГАРА!",
                "theme": "danger",
                "pill": "ЗАХВАТ ПОДПОЛЬНОЙ РАЗБОРКИ",
                "sfx": "boom",
            },
            {
                "scene_id": "u4_s3",
                "loc": "chop_shop",
                "sentences": [
                    "В углу нашли тот самый рюкзак с антенной-удочкой, глушилки и десятки перебитых номеров.",
                    "Оказалось, эта банда угнала больше тридцати машин за полгода!",
                ],
                "hud_bal": "30+ УГОНОВ",
                "hud_st": "УЛИКИ ИЗЪЯТЫ!",
                "theme": "alert",
                "pill": "ВЕЩДОКИ • АНТЕННА-РЕТРАНСЛЯТОР",
                "sfx": "phone",
            },
            {
                "scene_id": "u4_s4",
                "loc": "chop_shop",
                "sentences": [
                    "Я подбежал к своему кроссоверу — болгарка лежала прямо рядом с капотом, но его не успели распилить!",
                    "Как наказали банду и как защитить свою машину — в финальной пятой части!",
                ],
                "hud_bal": "2 500 000 ₽",
                "hud_st": "АВТО СПАСЕНО!",
                "theme": "green",
                "pill": "СПАСЕНА В ПОСЛЕДНЮЮ МИНУТУ",
                "sfx": "coin",
            },
        ],
    },
    5: {
        "filename": "ugon_ep5_finale.mp4",
        "title": "Угон на «удочку» • Часть 5 (Финал): 8 спасённых машин и секрет защиты",
        "chapters": [
            {
                "scene_id": "u5_s1",
                "loc": "chop_shop",
                "sentences": [
                    "Пятая, финальная часть. К утру вся банда угонщиков и хозяин разборки дали признательные показания.",
                    "За хищение тридцати машин им грозит до десяти лет реального срока!",
                ],
                "hud_bal": "ДО 10 ЛЕТ",
                "hud_st": "БАНДА ЗА РЕШЁТКОЙ!",
                "theme": "danger",
                "pill": "УТРО • АНГАР ОПЕЧАТАН",
                "sfx": "boom",
            },
            {
                "scene_id": "u5_s2",
                "loc": "mall_parking",
                "sentences": [
                    "Самое крутое — восемь семей получили назад свои угнанные машины целыми и невредимыми!",
                    "Детектив лично пожал мне руку за самую быструю наводку за весь год.",
                ],
                "hud_bal": "8 СЕМЕЙ СПАСЕНО",
                "hud_st": "МАШИНЫ ВЕРНУЛИ!",
                "theme": "green",
                "pill": "ВОЗВРАТ УГНАННЫХ АВТО",
                "sfx": "coin",
            },
            {
                "scene_id": "u5_s3",
                "loc": "dawn_plaza",
                "sentences": [
                    "Моя машина осталась при мне, а копеечный маячок за три тысячи рублей спас имущества на двадцать миллионов!",
                    "На рассвете я наконец спокойно допил свой кофе.",
                ],
                "hud_bal": "2 500 000 ₽",
                "hud_st": "МАШИНА ДОМА!",
                "theme": "green",
                "pill": "РАССВЕТ • СЧАСТЛИВЫЙ ФИНАЛ",
                "sfx": "coin",
            },
            {
                "scene_id": "u5_s4",
                "loc": "mall_cafe",
                "sentences": [
                    "Запомните защиту от удочки: храните ключ в экранирующем чехле Фарадея и прячьте автономный маячок!",
                    "Ставьте лайк и пишите в комментариях, какую криминальную схему разобрать в следующей истории!",
                ],
                "hud_bal": "ЗАЩИТА 100%",
                "hud_st": "ЧЕХОЛ + МАЯК!",
                "theme": "green",
                "pill": "ГЛАВНЫЙ СОВЕТ ВОДИТЕЛЯМ",
                "sfx": "coin",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# 4. MASTER EPISODE RENDERER & BATCH RUNNER
# ---------------------------------------------------------------------------

def render_ugon_episode(
    ep_num: int,
    out_dir: Path = Path("output/story_ugon_udochka"),
    speaker: str = "f5",
    fps: int = 30,
    shared_bgs: Optional[Dict[str, Image.Image]] = None,
) -> Path:
    ep = UGON_EPISODES[ep_num]
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

    # 1. Live Voiceover via F5-TTS Russian GPU (cached per episode!)
    voice_wav = work_dir / f"voice_ugon_ep{ep_num}_{speaker}.wav"
    cached_words = work_dir / f"words_f5_voice_ugon_ep{ep_num}_{speaker}.json"

    if speaker == "f5" and voice_wav.exists() and cached_words.exists():
        print(f"[UGON EP{ep_num}] 1. Используем кэшированную GPU-озвучку F5-TTS...")
        voice_file = voice_wav
        meta = json.loads(cached_words.read_text(encoding="utf-8"))
        words = meta["words"]
        duration = float(meta["duration"])
    elif speaker == "f5" and is_f5_available():
        print(f"[UGON EP{ep_num}] 1. Синтезируем живую озвучку '{ep['title']}' (F5-TTS RTX 4050)...")
        voice_file, words, duration = synthesize_f5_script(all_sentences, out_wav=voice_wav, speed=1.07)
    else:
        print(f"[UGON EP{ep_num}] 1. Синтезируем Silero v5.6 ({speaker})...")
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
    ass_path = work_dir / f"ugon_ep{ep_num}.ass"
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

    # 4. Load / Reuse Backgrounds & Movable Vehicles
    bgs = shared_bgs if shared_bgs is not None else build_ugon_backgrounds()
    igor_car = build_crossover_sprite((148, 163, 184), headlights_flash=False)
    igor_car_flash = build_crossover_sprite((148, 163, 184), headlights_flash=True)
    swat_van = build_swat_van_sprite()
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
        # EPISODE 1: 18 СЕКУНД В КОФЕЙНЕ
        # ================================================================
        if sid == "u1_s1":
            # Igor's silver crossover parked in B-42, Igor walks off right toward mall!
            frame = paste_obj(frame, igor_car, 260, 995)
            ix = int(560 + p_ch * 220)
            igor = render_igor(mood="confident", mouth_state=mouth, gesture="relax", blink=blink, walk_phase=t * 10.0, facing="right", scale=0.92)
            frame = paste_char(frame, igor, ix, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1060), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Возьму кофе — и сразу домой!»", anchor_x=ix - 20, anchor_y=800, align="right", pop_scale=pop_late)

        elif sid == "u1_s2":
            # Café queue: Igor stands at counter, Masked Hacker #1 creeps right behind him scanning key!
            igor = render_igor(mood="confident", mouth_state="closed", gesture="relax", blink=blink, facing="left", holding_coffee=True, scale=0.93)
            hx = int(950 - ease_out_back(min(1.0, t_local / 1.4)) * 230)
            hacker = render_hacker_masked(mood="shady", mouth_state="closed", gesture="hold_phone", with_backpack_antenna=True, walk_phase=(t * 10.0 if t_local < 1.3 else 0.0), facing="left", scale=0.92)
            frame = paste_char(frame, igor, 510, 1300)
            frame = paste_char(frame, hacker, hx, 1305)
            # Expanding green radio waves from hacker's backpack antenna!
            frame = draw_radio_waves(frame, hx + 46, 945, t)
            frame = camera.apply(frame, zoom=1.01 + 0.06 * p_ch, focal_point=(580, 1020), t=t)
            if t_local > 0.5:
                draw_smart_bubble(frame, "«Сигнал ключа пойман! Передаю вниз!»", anchor_x=hx - 20, anchor_y=800, align="right", pop_scale=pop_late)

        elif sid == "u1_s3":
            # Downstairs in parking: Hacker #2 unlocks & drives Igor's car away to the right!
            drive_p = max(0.0, (t_local - 1.5) / max(1.0, ch_dur - 1.5))
            car_x = int(250 + drive_p * 950)
            car_img = igor_car_flash if (int(t * 6) % 2 == 0 and t_local < 1.8) else igor_car
            frame = paste_obj(frame, car_img, car_x, 995)
            if t_local < 1.7:
                h2 = render_hacker_masked(mood="shady", gesture="hold_phone", with_backpack_antenna=True, facing="right", scale=0.90)
                frame = paste_char(frame, h2, 230, 1300)
                frame = draw_radio_waves(frame, 180, 945, t)
            shake = ((1.0 - t_local / 0.5) ** 1.4) if t_local <= 0.5 else 0.0
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 1050), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "УГОН: 18 СЕК!", t_local - 0.15, center=(540, 560))

        elif sid == "u1_s4":
            # Empty B-42 bay! Igor returns with coffee and grabs his head in pure horror!
            igor = render_igor(mood="shocked", mouth_state=mouth, gesture="hands_on_head", blink=False, facing="right", scale=0.95)
            frame = paste_char(frame, igor, 360, 1300)
            frame = camera.apply(frame, zoom=1.02 + 0.06 * p_ch, focal_point=(520, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«ГДЕ МОЯ МАШИНА?! СТОЙТЕ... МАЯЧОК!»", anchor_x=400, anchor_y=800, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 2: СЕКРЕТНЫЙ МАЯЧОК И ГЛУШИЛКА
        # ================================================================
        elif sid == "u2_s1":
            igor = render_igor(mood="smug", mouth_state=mouth, gesture="hold_phone", blink=blink, facing="right", scale=0.95)
            frame = paste_char(frame, igor, 380, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Под сиденьем спрятан GPS-маячок!»", anchor_x=420, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "u2_s2":
            # Dark Glowing GPS Map Radar with pulsing live dot!
            igor = render_igor(mood="smug", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.92)
            frame = paste_char(frame, igor, 290, 1315)
            frame = draw_radio_waves(frame, 810, 430, t)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 940), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Вижу! Уходят в промзону на 95 км/ч!»", anchor_x=340, anchor_y=840, align="left", pop_scale=pop_late)

        elif sid == "u2_s3":
            # Night industrial gate — Igor + Detective in tan trench coat!
            igor = render_igor(mood="alert", mouth_state="closed", gesture="hold_phone", blink=blink, facing="right", scale=0.90)
            det = render_detective(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", scale=0.94)
            frame = paste_char(frame, igor, 265, 1310)
            frame = paste_char(frame, det, 815, 1310)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1040), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Скидывай координаты — выезжаем!»", anchor_x=790, anchor_y=810, align="right", pop_scale=pop_late)

        elif sid == "u2_s4":
            # GPS Jammer Alert Cliffhanger!
            igor = render_igor(mood="shocked", mouth_state=mouth, gesture="hands_on_head", blink=False, facing="right", scale=0.92)
            det = render_detective(mood="alert", mouth_state="closed", gesture="hold_phone", blink=blink, facing="left", scale=0.92)
            frame = paste_char(frame, igor, 260, 1315)
            frame = paste_char(frame, det, 825, 1315)
            shake = ((1.0 - t_local / 0.55) ** 1.4) if t_local <= 0.55 else 0.0
            frame = camera.apply(frame, zoom=1.03 + 0.06 * p_ch, focal_point=(540, 960), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "ГЛУШИЛКА!", t_local - 0.15, center=(540, 860))

        # ================================================================
        # EPISODE 3: ЗАБРОШЕННЫЙ АНГАР №7
        # ================================================================
        elif sid == "u3_s1":
            igor = render_igor(mood="alert", mouth_state="closed", gesture="point_right", blink=blink, facing="right", scale=0.90)
            det = render_detective(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.93)
            frame = paste_char(frame, det, 330, 1305)
            frame = paste_char(frame, igor, 180, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1040), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Тихо! В седьмом ангаре горит свет!»", anchor_x=360, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "u3_s2":
            # Inside the Chop-Shop Hangar with Igor's crossover + 2 more stolen cars!
            frame = paste_obj(frame, igor_car, 260, 1020)
            h1 = render_hacker_masked(mood="shady", mouth_state="closed", gesture="point_left", with_backpack_antenna=True, facing="left", scale=0.88)
            frame = paste_char(frame, h1, 860, 1305)
            frame = camera.apply(frame, zoom=1.02 + 0.06 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_rec_camera_overlay(frame, t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Восемь угнанных машин в одном ангаре!»", anchor_x=540, anchor_y=800, align="center", pop_scale=pop_late)

        elif sid == "u3_s3":
            # Thief finds the GPS tracker -> PANIC!
            frame = paste_obj(frame, igor_car, 260, 1020)
            h1 = render_hacker_masked(mood="shocked", mouth_state=mouth, gesture="hands_on_head", facing="left", scale=0.90)
            h2 = render_hacker_masked(mood="shocked", mouth_state="open", gesture="run", walk_phase=t * 18.0, facing="right", scale=0.88)
            frame = paste_char(frame, h1, 240, 1305)
            frame = paste_char(frame, h2, int(740 + p_ch * 180), 1305)
            shake = ((1.0 - t_local / 0.55) ** 1.4) if t_local <= 0.55 else 0.0
            frame = camera.apply(frame, zoom=1.04 + 0.06 * p_ch, focal_point=(540, 1040), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "ТРЕВОГА!", t_local - 0.15, center=(540, 560))
            if t_local > 0.4:
                draw_smart_bubble(frame, "«ТУТ МАЯЧОК! СРОЧНО СВАЛИВАЕМ!»", anchor_x=290, anchor_y=810, align="left", pop_scale=pop_late)

        elif sid == "u3_s4":
            # Detective calls SWAT + SWAT van pulls up!
            vx = int(1120 - ease_out_back(min(1.0, t_local / 1.3)) * 580)
            frame = paste_obj(frame, swat_van, vx, 985)
            det = render_detective(mood="alert", mouth_state=mouth, gesture="hold_phone", blink=blink, facing="right", scale=0.93)
            igor = render_igor(mood="alert", mouth_state="closed", gesture="point_right", blink=blink, facing="right", scale=0.90)
            frame = paste_char(frame, igor, 185, 1310)
            frame = paste_char(frame, det, 390, 1310)
            frame = draw_siren_flash(frame, t)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1040), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Группа захвата, перекрываем выезд!»", anchor_x=410, anchor_y=810, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 4: НОЧНОЙ ШТУРМ АНГАРА
        # ================================================================
        elif sid == "u4_s1":
            # SWAT van blocks the barrier gate!
            frame = paste_obj(frame, swat_van, 470, 990)
            frame = paste_obj(frame, igor_car_flash, -20, 1020)
            swat = render_swat_officer(gesture="point_left", facing="left", scale=0.94)
            frame = paste_char(frame, swat, 830, 1315)
            frame = draw_siren_flash(frame, t)
            shake = ((1.0 - t_local / 0.55) ** 1.4) if t_local <= 0.55 else 0.0
            frame = camera.apply(frame, zoom=1.03 + 0.06 * p_ch, focal_point=(540, 1040), shake_intensity=shake, t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«СТОЯТЬ! ВЫХОДИМ ИЗ МАШИНЫ!»", anchor_x=800, anchor_y=810, align="right", pop_scale=pop_late)

        elif sid == "u4_s2":
            # SWAT storms the chop-shop hangar!
            sw1_x = int(60 + ease_out_back(min(1.0, t_local / 0.9)) * 165)
            sw1 = render_swat_officer(gesture="point_right", walk_phase=(t * 16.0 if t_local < 0.85 else 0.0), facing="right", scale=0.95)
            h1 = render_hacker_masked(mood="shocked", gesture="hands_on_head", facing="left", scale=0.90)
            h2 = render_hacker_masked(mood="shocked", gesture="hands_on_head", facing="left", scale=0.88)
            frame = paste_char(frame, sw1, sw1_x, 1310)
            frame = paste_char(frame, h1, 610, 1310)
            frame = paste_char(frame, h2, 875, 1310)
            frame = draw_siren_flash(frame, t)
            shake = ((1.0 - t_local / 0.6) ** 1.4) if t_local <= 0.6 else 0.0
            frame = camera.apply(frame, zoom=1.04 + 0.06 * p_ch, focal_point=(540, 1020), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "ШТУРМ!", t_local - 0.12, center=(540, 540))

        elif sid == "u4_s3":
            # Detective seizes the relay backpack antenna!
            det = render_detective(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.93)
            h1 = render_hacker_masked(mood="shocked", gesture="hands_on_head", with_backpack_antenna=True, facing="left", scale=0.90)
            frame = paste_char(frame, det, 260, 1310)
            frame = paste_char(frame, h1, 800, 1310)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Вот она — та самая антенна-удочка!»", anchor_x=310, anchor_y=810, align="left", pop_scale=pop_late)

        elif sid == "u4_s4":
            # Igor reunited with his intact silver crossover!
            frame = paste_obj(frame, igor_car, 420, 1015)
            igor = render_igor(mood="smug", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            frame = paste_char(frame, igor, 240, 1310)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1040), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Успели! Даже царапины не поставили!»", anchor_x=290, anchor_y=810, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 5 (FINALE): 8 СПАСЁННЫХ МАШИН И СЕКРЕТ ЗАЩИТЫ
        # ================================================================
        elif sid == "u5_s1":
            # Sealed hangar + SWAT arresting both thieves!
            swat = render_swat_officer(gesture="point_right", facing="right", scale=0.94)
            h1 = render_hacker_masked(mood="shocked", gesture="hands_on_head", facing="left", scale=0.90)
            h2 = render_hacker_masked(mood="shocked", gesture="hands_on_head", facing="left", scale=0.88)
            frame = paste_char(frame, swat, 210, 1310)
            frame = paste_char(frame, h1, 610, 1310)
            frame = paste_char(frame, h2, 875, 1310)
            shake = ((1.0 - t_local / 0.5) ** 1.4) if t_local <= 0.5 else 0.0
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 1020), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "ДО 10 ЛЕТ!", t_local - 0.15, center=(540, 540))

        elif sid == "u5_s2":
            # 8 cars returned — Detective shakes Igor's hand!
            frame = paste_obj(frame, igor_car, 260, 995)
            igor = render_igor(mood="smug", mouth_state="closed", gesture="point_right", blink=blink, facing="right", scale=0.92)
            det = render_detective(mood="smug", mouth_state=mouth, gesture="point_left", blink=blink, facing="left", scale=0.94)
            frame = paste_char(frame, igor, 250, 1310)
            frame = paste_char(frame, det, 825, 1310)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1040), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Спасибо! Восемь семей спасены!»", anchor_x=800, anchor_y=810, align="right", pop_scale=pop_late)

        elif sid == "u5_s3":
            # Golden sunrise finale — Igor peacefully drinks coffee next to his silver crossover!
            frame = draw_money_rain(frame, t)
            frame = paste_obj(frame, igor_car, 420, 1020)
            igor = render_igor(mood="smug", mouth_state=mouth, gesture="relax", blink=blink, facing="right", holding_coffee=True, scale=0.95)
            frame = paste_char(frame, igor, 260, 1315)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1040), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Маячок за 3 000 ₽ спас 20 миллионов!»", anchor_x=310, anchor_y=810, align="left", pop_scale=pop_late)

        else:  # u5_s4 — Protection Life-Hack Finale!
            igor = render_igor(mood="smug", mouth_state=mouth, gesture="hold_phone", blink=blink, facing="right", holding_coffee=True, scale=0.95)
            frame = paste_char(frame, igor, 540, 1315)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Чехол Фарадея + маячок = 100% защита!»", anchor_x=540, anchor_y=800, align="center", pop_scale=pop_late)

        draw_sleek_hud(frame, balance_text=ch["hud_bal"], status_text=ch["hud_st"], theme=ch["theme"])
        draw_compact_pill(frame, text=ch["pill"])
        return frame

    print(f"[UGON EP{ep_num}] 2. Рендерим анимацию ({ep['title']})...")
    total_frames = int(duration * fps)
    raw_video = work_dir / f"raw_ugon_ep{ep_num}.mp4"

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

    print(f"[UGON EP{ep_num}] 3. Финальная сборка MP4...")
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


def render_all_ugon_episodes(speaker: str = "f5", fps: int = 30) -> List[Path]:
    print("=" * 64)
    print("  NEW STORY: 'УГОН НА УДОЧКУ' — BATCH RENDER ALL 5 EPISODES")
    print("=" * 64)
    shared_bgs = build_ugon_backgrounds()
    outputs = []
    for ep_num in range(1, 6):
        out = render_ugon_episode(ep_num, speaker=speaker, fps=fps, shared_bgs=shared_bgs)
        outputs.append(out)
    print("=" * 64)
    print("  ALL 5 EPISODES OF 'УГОН НА УДОЧКУ' COMPLETED SUCCESSFULLY!")
    print("=" * 64)
    return outputs
