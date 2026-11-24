"""
Standalone 5-Part Animated Mini-Series:
"АВТОСЕРВИС-ЛОВУШКА: СЧЁТ НА 480 000 ₽ ЗА ЗАМЕНУ МАСЛА" (v3 PRO Engine).

100% Brand-New Characters & Brand-New 2x-Supersampled Locations:

Characters:
- Anya (stylish girl driver in mustard-yellow sweater with high ponytail)
- Master Priemshik (sneaky foreman in greasy coveralls with badge & wrench)
- Trainee Mechanic (young apprentice in orange overalls secretly filming on phone)
- Service Director (arrogant boss in black leather jacket with gold chain & 480k invoice)
- OBEP Police Captain (police investigator in navy uniform with white "ОБЭП" badge)

Locations:
- Service Reception (promo banner "АКЦИЯ: ЗАМЕНА МАСЛА 4 990 ₽")
- Service Lift Bay (2-post hydraulic lift, red hatchback, red tool cart, oil barrels)
- Disassembled Engine Bay (exposed pipes, missing catalytic converter, oil drip pan)
- Rusty Graveyard Back Alley (piles of rusted exhausts, brake rotors, damp brick wall)
- Glowing Avito Smartphone Screen (listing of stolen cat for 85k with yellow sticker)
- Director's Office (desk with 480 250 ₽ bill, safe, diplomas)
- Locked Service Gates (heavy roller door with massive padlock)
- Police Raid Bay (red/blue siren flashes, "ОПЕЧАТАНО" police tape, evidence boxes)
- Daylight Plaza (sunny city square with Anya's restored red hatchback)
"""

import json
import math
import subprocess
import sys
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
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
    draw_anger_mark,
    draw_animated_stamp,
    draw_door_burst_particles,
    draw_money_rain,
    draw_siren_flash,
    draw_sweat_drops,
    ease_out_back,
)
from backend.app.cartoon.f5_voice import is_f5_available, synthesize_f5_script
from backend.app.cartoon.sfx import synth_police_siren, synth_suspense_bed, synth_whoosh
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
# 1. BRAND-NEW CHARACTERS FOR "АВТОСЕРВИС-ЛОВУШКА"
# ---------------------------------------------------------------------------

def render_anya(
    mood: str = "confident",
    mouth_state: str = "closed",
    gesture: str = "relax",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    holding_keys: bool = False,
    holding_phone: bool = False,
    scale: float = 0.92,
) -> Image.Image:
    """
    Anya — stylish girl driver in mustard-yellow knit sweater & high ponytail:
    - 2x supersampled vector rendering (silky smooth curves)
    - Voluminous silky chestnut hair with high flowing ponytail & red scrunchie
    - Expressive feminine anime/cartoon eyes with twin sparkle highlights & delicate lashes
    - No jagged male spikes, no weird Frankenstein unibrow!
    """
    S = 2  # 2x Supersampling
    W, H = 420 * S, 560 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = W // 2
    foot_y = H - 36 * S
    ink_w = 5 * S

    # Walking bounce
    stride = math.sin(walk_phase)
    stride_abs = abs(stride)
    body_bounce = int(-stride_abs * 10 * S)

    # Shadow on ground
    sh_rx = int(70 * S)
    sh_ry = int(14 * S)
    d.ellipse([cx - sh_rx, foot_y - sh_ry + 6 * S, cx + sh_rx, foot_y + sh_ry + 6 * S], fill=(15, 23, 42, 60))

    # --- 1. LEGS & SLIM JEANS & SNEAKERS ---
    hip_y = foot_y - 128 * S + body_bounce
    leg_len = 118 * S

    if gesture == "run":
        l_ang = stride * 0.72
        r_ang = -stride * 0.72
    else:
        l_ang = stride * 0.35
        r_ang = -stride * 0.35

    def _leg(hip_x, angle, is_front=True):
        knee_x = int(hip_x + math.sin(angle) * (leg_len * 0.52))
        knee_y = int(hip_y + math.cos(angle) * (leg_len * 0.52))
        ankle_x = int(knee_x + math.sin(angle * 0.8) * (leg_len * 0.48))
        ankle_y = int(knee_y + math.cos(angle * 0.8) * (leg_len * 0.48))

        # Slim dark denim jeans leg
        d.line([(hip_x, hip_y), (knee_x, knee_y), (ankle_x, ankle_y)], fill=(30, 41, 59, 255), width=8 * S, joint="curve")
        d.line([(hip_x, hip_y), (knee_x, knee_y), (ankle_x, ankle_y)], fill=INK, width=10 * S, joint="curve")
        d.line([(hip_x, hip_y), (knee_x, knee_y), (ankle_x, ankle_y)], fill=(30, 41, 59, 255), width=7 * S, joint="curve")

        # White stylish sneaker shoe with mustard accent
        s_dir = 1 if facing == "right" else -1
        sx1 = ankle_x - 12 * S
        sx2 = ankle_x + 28 * S * s_dir
        if s_dir == -1:
            sx1, sx2 = sx2, ankle_x + 12 * S
        sy1 = ankle_y - 4 * S
        sy2 = ankle_y + 14 * S
        # Sole
        d.rounded_rectangle([(min(sx1, sx2) - 4 * S, sy2 - 6 * S), (max(sx1, sx2) + 4 * S, sy2 + 2 * S)], radius=4 * S, fill=(241, 245, 249, 255), outline=INK, width=3 * S)
        # Upper
        d.rounded_rectangle([(min(sx1, sx2), sy1), (max(sx1, sx2), sy2 - 2 * S)], radius=6 * S, fill=(255, 255, 255, 255), outline=INK, width=3 * S)
        # Accent stripe
        d.line([(min(sx1, sx2) + 8 * S, sy1 + 5 * S), (max(sx1, sx2) - 8 * S, sy1 + 5 * S)], fill=(245, 158, 11, 255), width=3 * S)

    _leg(cx - 18 * S, l_ang, is_front=False)
    _leg(cx + 18 * S, r_ang, is_front=True)

    # --- 2. MUSTARD-YELLOW SWEATER / HOODIE (FEMININE CUT) ---
    body_top_y = hip_y - 125 * S
    sh_y = body_top_y + 20 * S

    sweater_color = (245, 158, 11, 255)       # warm vibrant mustard
    sweater_shadow = (217, 119, 6, 255)       # rich dark amber fold

    body_poly = [
        (cx - 48 * S, body_top_y + 18 * S),   # left shoulder
        (cx + 48 * S, body_top_y + 18 * S),   # right shoulder
        (cx + 56 * S, hip_y + 4 * S),         # right hip
        (cx - 56 * S, hip_y + 4 * S),         # left hip
    ]
    d.polygon(body_poly, fill=sweater_color, outline=INK)
    # Sweater ribbing hem at bottom
    d.rounded_rectangle([(cx - 58 * S, hip_y - 4 * S), (cx + 58 * S, hip_y + 10 * S)], radius=5 * S, fill=sweater_shadow, outline=INK, width=3 * S)

    # Front kangaroo pouch
    d.rounded_rectangle([(cx - 32 * S, hip_y - 56 * S), (cx + 32 * S, hip_y - 16 * S)], radius=8 * S, fill=(234, 140, 8, 255), outline=INK, width=3 * S)

    # Hoodie collar & hanging white drawstrings
    d.chord([cx - 42 * S, body_top_y + 2 * S, cx + 42 * S, body_top_y + 42 * S], start=0, end=180, fill=(234, 140, 8, 255), outline=INK, width=3 * S)
    d.line([(cx - 12 * S, body_top_y + 36 * S), (cx - 14 * S, body_top_y + 82 * S)], fill=(255, 255, 255, 255), width=4 * S)
    d.line([(cx + 12 * S, body_top_y + 36 * S), (cx + 14 * S, body_top_y + 82 * S)], fill=(255, 255, 255, 255), width=4 * S)

    # --- 3. HEAD & SILKY HAIR ---
    head_r = 74 * S
    head_cy = sh_y - head_r + 4 * S

    hair_base = (78, 46, 32, 255)      # rich dark chestnut
    hair_highlight = (130, 85, 60, 255)# soft shine

    p_dir = -1 if facing == "right" else 1
    pt_x = cx + int(52 * S * p_dir)
    pt_y = head_cy - 48 * S

    # 3A. PONYTAIL (BEHIND HEAD)
    if facing == "right":
        d.ellipse([pt_x - 14 * S, pt_y - 14 * S, pt_x + 14 * S, pt_y + 14 * S], fill=(239, 68, 68, 255), outline=INK, width=3 * S)
        pts_pony = [
            (pt_x - 4 * S, pt_y - 6 * S),
            (pt_x - 38 * S, pt_y - 32 * S),
            (pt_x - 72 * S, pt_y + 20 * S),
            (pt_x - 76 * S, pt_y + 120 * S),
            (pt_x - 56 * S, pt_y + 190 * S),
            (pt_x - 42 * S, pt_y + 160 * S),
            (pt_x - 40 * S, pt_y + 80 * S),
            (pt_x - 10 * S, pt_y + 10 * S),
        ]
        d.polygon(pts_pony, fill=hair_base, outline=INK)
        d.line([(pt_x - 30 * S, pt_y - 18 * S), (pt_x - 60 * S, pt_y + 60 * S), (pt_x - 52 * S, pt_y + 140 * S)], fill=hair_highlight, width=4 * S)
    else:
        d.ellipse([pt_x - 14 * S, pt_y - 14 * S, pt_x + 14 * S, pt_y + 14 * S], fill=(239, 68, 68, 255), outline=INK, width=3 * S)
        pts_pony = [
            (pt_x + 4 * S, pt_y - 6 * S),
            (pt_x + 38 * S, pt_y - 32 * S),
            (pt_x + 72 * S, pt_y + 20 * S),
            (pt_x + 76 * S, pt_y + 120 * S),
            (pt_x + 56 * S, pt_y + 190 * S),
            (pt_x + 42 * S, pt_y + 160 * S),
            (pt_x + 40 * S, pt_y + 80 * S),
            (pt_x + 10 * S, pt_y + 10 * S),
        ]
        d.polygon(pts_pony, fill=hair_base, outline=INK)
        d.line([(pt_x + 30 * S, pt_y - 18 * S), (pt_x + 60 * S, pt_y + 60 * S), (pt_x + 52 * S, pt_y + 140 * S)], fill=hair_highlight, width=4 * S)

    # 3B. HEAD BASE (SMOOTH PORCELAIN / PEACH OVAL)
    d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], fill=(255, 255, 255, 255), outline=INK, width=ink_w)

    # 3C. HAIR CROWN & STYLISH BANGS
    d.chord([cx - head_r - 4 * S, head_cy - head_r - 10 * S, cx + head_r + 4 * S, head_cy - 12 * S], start=185, end=355, fill=hair_base, outline=INK, width=4 * S)
    d.arc([cx - head_r + 14 * S, head_cy - head_r + 4 * S, cx + head_r - 14 * S, head_cy - 36 * S], start=195, end=345, fill=hair_highlight, width=6 * S)

    if facing == "right":
        d.chord([cx - 44 * S, head_cy - 50 * S, cx + 56 * S, head_cy - 6 * S], start=180, end=340, fill=hair_base, outline=INK, width=3 * S)
        d.line([(cx - 52 * S, head_cy - 20 * S), (cx - 58 * S, head_cy + 25 * S), (cx - 52 * S, head_cy + 45 * S)], fill=hair_base, width=6 * S)
    else:
        d.chord([cx - 56 * S, head_cy - 50 * S, cx + 44 * S, head_cy - 6 * S], start=200, end=360, fill=hair_base, outline=INK, width=3 * S)
        d.line([(cx + 52 * S, head_cy - 20 * S), (cx + 58 * S, head_cy + 25 * S), (cx + 52 * S, head_cy + 45 * S)], fill=hair_base, width=6 * S)

    # --- 4. FEMININE EXPRESSIVE EYES, BROWS & MOUTH ---
    eye_shift = 10 * S if facing == "right" else -10 * S
    ex_l = cx - 26 * S + eye_shift
    ex_r = cx + 24 * S + eye_shift
    ey = head_cy - 4 * S

    # Cheerful rosy cheek blush
    d.ellipse([ex_l - 18 * S, ey + 22 * S, ex_l + 8 * S, ey + 38 * S], fill=(251, 113, 133, 115))
    d.ellipse([ex_r - 8 * S, ey + 22 * S, ex_r + 18 * S, ey + 38 * S], fill=(251, 113, 133, 115))

    def _draw_feminine_eye(x, y, rad_w=12, rad_h=15, is_shock=False):
        d.ellipse([x - rad_w * S, y - rad_h * S, x + rad_w * S, y + rad_h * S], fill=(255, 255, 255, 255), outline=INK, width=3 * S)
        p_r = 7 if is_shock else 9
        d.ellipse([x - p_r * S, y - p_r * S, x + p_r * S, y + p_r * S], fill=(30, 41, 59, 255))
        d.ellipse([x - p_r * S + 2 * S, y - p_r * S + 2 * S, x - p_r * S + 8 * S, y - p_r * S + 8 * S], fill=(255, 255, 255, 255))
        d.ellipse([x + 1 * S, y + 1 * S, x + 5 * S, y + 5 * S], fill=(255, 255, 255, 255))
        d.arc([x - (rad_w + 3) * S, y - (rad_h + 3) * S, x + (rad_w + 3) * S, y + 2 * S], start=190, end=350, fill=INK, width=4 * S)
        flick_dir = 1 if x > cx else -1
        d.line([(x + rad_w * S * flick_dir, y - rad_h * S + 4 * S), (x + (rad_w + 6) * S * flick_dir, y - rad_h * S - 3 * S)], fill=INK, width=3 * S)

    if blink:
        d.arc([ex_l - 12 * S, ey - 4 * S, ex_l + 12 * S, ey + 10 * S], start=190, end=350, fill=INK, width=4 * S)
        d.arc([ex_r - 12 * S, ey - 4 * S, ex_r + 12 * S, ey + 10 * S], start=190, end=350, fill=INK, width=4 * S)
    elif mood == "shocked":
        _draw_feminine_eye(ex_l, ey - 2 * S, rad_w=14, rad_h=16, is_shock=True)
        _draw_feminine_eye(ex_r, ey - 2 * S, rad_w=14, rad_h=16, is_shock=True)
        d.arc([ex_l - 14 * S, ey - 32 * S, ex_l + 14 * S, ey - 12 * S], start=190, end=350, fill=hair_base, width=4 * S)
        d.arc([ex_r - 14 * S, ey - 32 * S, ex_r + 14 * S, ey - 12 * S], start=190, end=350, fill=hair_base, width=4 * S)
        d.ellipse([cx + 52 * S, head_cy - 28 * S, cx + 62 * S, head_cy - 12 * S], fill=(56, 189, 248, 255), outline=INK, width=2 * S)
    elif mood == "sad":
        _draw_feminine_eye(ex_l, ey, rad_w=12, rad_h=14)
        _draw_feminine_eye(ex_r, ey, rad_w=12, rad_h=14)
        d.line([(ex_l - 12 * S, ey - 20 * S), (ex_l + 12 * S, ey - 28 * S)], fill=hair_base, width=4 * S)
        d.line([(ex_r - 12 * S, ey - 28 * S), (ex_r + 12 * S, ey - 20 * S)], fill=hair_base, width=4 * S)
        d.ellipse([ex_l - 4 * S, ey + 18 * S, ex_l + 4 * S, ey + 28 * S], fill=(56, 189, 248, 255))
    elif mood == "smug":
        _draw_feminine_eye(ex_l, ey - 2 * S, rad_w=12, rad_h=13)
        _draw_feminine_eye(ex_r, ey - 2 * S, rad_w=12, rad_h=13)
        d.line([(ex_l - 12 * S, ey - 22 * S), (ex_l + 12 * S, ey - 18 * S)], fill=hair_base, width=4 * S)
        d.line([(ex_r - 12 * S, ey - 18 * S), (ex_r + 12 * S, ey - 24 * S)], fill=hair_base, width=4 * S)
    else:  # confident / normal
        _draw_feminine_eye(ex_l, ey, rad_w=12, rad_h=14)
        _draw_feminine_eye(ex_r, ey, rad_w=12, rad_h=14)
        d.arc([ex_l - 12 * S, ey - 28 * S, ex_l + 12 * S, ey - 12 * S], start=200, end=340, fill=hair_base, width=4 * S)
        d.arc([ex_r - 12 * S, ey - 28 * S, ex_r + 12 * S, ey - 12 * S], start=200, end=340, fill=hair_base, width=4 * S)

    # Mouth
    my = head_cy + 28 * S
    mx = cx + eye_shift
    if mouth_state == "closed":
        if mood in ("confident", "smug"):
            d.arc([mx - 14 * S, my - 8 * S, mx + 14 * S, my + 8 * S], start=20, end=160, fill=INK, width=4 * S)
        elif mood == "shocked":
            d.ellipse([mx - 10 * S, my - 6 * S, mx + 10 * S, my + 14 * S], fill=INK)
            d.chord([mx - 7 * S, my + 2 * S, mx + 7 * S, my + 14 * S], start=0, end=180, fill=(244, 63, 94, 255))
        elif mood == "sad":
            d.arc([mx - 12 * S, my + 4 * S, mx + 12 * S, my + 16 * S], start=200, end=340, fill=INK, width=4 * S)
        else:
            d.line([(mx - 10 * S, my), (mx + 10 * S, my)], fill=INK, width=3 * S)
    elif mouth_state == "half":
        d.chord([mx - 14 * S, my - 6 * S, mx + 14 * S, my + 14 * S], start=0, end=180, fill=INK)
        d.chord([mx - 9 * S, my + 3 * S, mx + 9 * S, my + 14 * S], start=0, end=180, fill=(244, 63, 94, 255))
    else:  # open
        d.ellipse([mx - 15 * S, my - 6 * S, mx + 15 * S, my + 18 * S], fill=INK)
        d.chord([mx - 10 * S, my + 4 * S, mx + 10 * S, my + 18 * S], start=0, end=180, fill=(244, 63, 94, 255))

    # --- 5. ARTICULATED ARMS, PROPS & SLEEVES ---
    sh_l = (cx - 48 * S, sh_y + 16 * S)
    sh_r = (cx + 48 * S, sh_y + 16 * S)
    hand_r = 13 * S

    def _arm(p1, p2, p3=None):
        pts = [p1, p2] if p3 is None else [p1, p2, p3]
        d.line(pts, fill=INK, width=9 * S, joint="curve")
        d.line(pts, fill=sweater_color, width=7 * S, joint="curve")
        end = pts[-1]
        d.ellipse([end[0] - hand_r, end[1] - hand_r, end[0] + hand_r, end[1] + hand_r], fill=(255, 255, 255, 255), outline=INK, width=3 * S)
        return end

    if gesture == "hands_on_head":
        _arm(sh_l, (cx - 96 * S, sh_y - 10 * S), (cx - head_r + 4 * S, head_cy + 4 * S))
        _arm(sh_r, (cx + 96 * S, sh_y - 10 * S), (cx + head_r - 4 * S, head_cy + 4 * S))
    elif gesture in ("hold_phone", "holding_phone") or holding_phone:
        _arm(sh_l, (cx - 68 * S, hip_y - 10 * S))
        end = _arm(sh_r, (cx + 88 * S, sh_y + 14 * S), (cx + 74 * S, head_cy + 22 * S))
        px, py = end
        d.rounded_rectangle([(px - 10 * S, py - 36 * S), (px + 24 * S, py + 14 * S)], radius=6 * S, fill=(15, 23, 42, 255), outline=INK, width=3 * S)
        d.rectangle([(px - 4 * S, py - 28 * S), (px + 18 * S, py + 8 * S)], fill=(56, 189, 248, 255))
    elif gesture in ("hold_keys", "holding_keys") or holding_keys:
        _arm(sh_l, (cx - 68 * S, hip_y - 10 * S))
        end = _arm(sh_r, (cx + 80 * S, sh_y + 24 * S), (cx + 88 * S, sh_y + 70 * S))
        hx, hy = end
        d.rounded_rectangle([(hx - 10 * S, hy - 4 * S), (hx + 10 * S, hy + 22 * S)], radius=5 * S, fill=(30, 41, 59, 255), outline=INK, width=2 * S)
        d.ellipse([hx - 5 * S, hy - 14 * S, hx + 5 * S, hy - 4 * S], outline=(203, 213, 225, 255), width=2 * S)
        d.rectangle([(hx + 4 * S, hy - 16), (hx + 14 * S, hy - 13)], fill=(226, 232, 240, 255))
    elif gesture == "point_right":
        _arm(sh_l, (cx - 68 * S, hip_y - 8 * S))
        _arm(sh_r, (cx + 115 * S, sh_y + 10 * S))
    elif gesture == "point_left":
        _arm(sh_r, (cx + 68 * S, hip_y - 8 * S))
        _arm(sh_l, (cx - 115 * S, sh_y + 10 * S))
    elif gesture == "thumbs_up":
        _arm(sh_l, (cx - 68 * S, hip_y - 8 * S))
        end = _arm(sh_r, (cx + 90 * S, sh_y + 12 * S), (cx + 85 * S, sh_y - 20 * S))
        tx, ty = end
        d.rounded_rectangle([(tx - 6 * S, ty - 18 * S), (tx + 6 * S, ty)], radius=4 * S, fill=(255, 255, 255, 255), outline=INK, width=3 * S)
    else:  # relax
        sw = int(stride * 16 * S)
        _arm(sh_l, (cx - 66 * S - sw, hip_y - 6 * S))
        _arm(sh_r, (cx + 66 * S + sw, hip_y - 6 * S))

    out_w = int((W // S) * scale)
    out_h = int((H // S) * scale)
    return img.resize((out_w, out_h), Image.Resampling.LANCZOS)


def render_master(
    mood: str = "smug",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "left",
    holding_wrench: bool = True,
    scale: float = 0.94,
) -> Image.Image:
    """Master Priemshik — greasy cynical foreman in dark-slate overalls with badge & wrench."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(45, 58, 76), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    shift = 8 if facing == "right" else -8

    # Dark stubble along chin & greasy oil smudge on cheek
    d.arc([cx - 52 + shift, 202, cx + 52 + shift, 256], start=20, end=160, fill=(40, 36, 32, 255), width=10)
    d.ellipse([cx + 28 + shift, 192, cx + 46 + shift, 206], fill=(55, 65, 81, 160))

    # White breast badge "МАСТЕР"
    d.rounded_rectangle([(cx - 42, 280), (cx + 12, 305)], radius=3, fill=(241, 245, 249, 255), outline=INK, width=2)
    f_badge = _font(FONT_BOLD, 11)
    d.text((cx - 38, 285), "МАСТЕР", fill=INK, font=f_badge)

    # Yellow grease pencil behind ear
    d.line([(cx + 46 + shift, 150), (cx + 62 + shift, 138)], fill=(250, 204, 21, 255), width=5)

    # Heavy red pipe wrench in hand
    if holding_wrench:
        hx = cx - 85 if facing == "left" else cx + 85
        hy = 345
        d.line([(hx, hy - 45), (hx, hy + 40)], fill=(220, 38, 38, 255), width=10)
        d.rectangle([(hx - 14, hy - 55), (hx + 14, hy - 40)], fill=(100, 116, 139, 255), outline=INK, width=2)
        d.rectangle([(hx - 18, hy - 65), (hx + 4, hy - 50)], fill=(71, 85, 105, 255), outline=INK, width=2)

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_trainee(
    mood: str = "alert",
    mouth_state: str = "closed",
    gesture: str = "hold_phone",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    holding_usb: bool = False,
    scale: float = 0.91,
) -> Image.Image:
    """Trainee Mechanic — young guy in bright orange dungarees with backwards cap, secretly helping."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(234, 88, 12), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    shift = 8 if facing == "right" else -8

    # Backwards baseball cap: dome covering crown + visor sticking backward!
    d.chord([cx - 72, 108, cx + 72, 185], start=180, end=360, fill=(30, 41, 59, 255), outline=INK, width=4)
    # Cap visor sticking out back
    if facing == "right":
        d.polygon([(cx - 68, 148), (cx - 105, 142), (cx - 95, 158), (cx - 64, 158)], fill=(30, 41, 59, 255), outline=INK)
    else:
        d.polygon([(cx + 68, 148), (cx + 105, 142), (cx + 95, 158), (cx + 64, 158)], fill=(30, 41, 59, 255), outline=INK)

    # Smudge of oil on nose tip
    d.ellipse([cx + shift - 4, 196, cx + shift + 6, 204], fill=(75, 85, 99, 150))

    # Flash drive in hand
    if holding_usb:
        hx = cx + 80 if facing == "right" else cx - 80
        hy = 340
        d.rounded_rectangle([(hx - 8, hy - 14), (hx + 8, hy + 14)], radius=3, fill=(16, 185, 129, 255), outline=INK, width=2)
        d.rectangle([(hx - 5, hy - 22), (hx + 5, hy - 14)], fill=(226, 232, 240, 255))

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_director(
    mood: str = "smug",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    holding_bill: bool = True,
    scale: float = 0.94,
) -> Image.Image:
    """Service Director — sleazy boss in black leather jacket with gold chain & printed bill."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(24, 24, 28), hair_style="slicked",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2

    # Chunky gold chain on chest
    d.arc([cx - 28, 250, cx + 28, 305], start=20, end=160, fill=(234, 179, 8, 255), width=6)
    d.ellipse([cx - 6, 302, cx + 6, 318], fill=(234, 179, 8, 255), outline=INK, width=2)

    # Gold watch on left wrist
    d.rectangle([(cx - 78, 342), (cx - 64, 356)], fill=(234, 179, 8, 255), outline=INK, width=2)

    # Large printed A4 invoice in hand: "480 250 ₽"
    if holding_bill:
        hx = cx + 80 if facing == "right" else cx - 80
        hy = 320
        d.rectangle([(hx - 24, hy - 40), (hx + 40, hy + 45)], fill=(255, 255, 255, 255), outline=INK, width=3)
        # Red title + lines
        d.rectangle([(hx - 18, hy - 34), (hx + 34, hy - 24)], fill=(220, 38, 38, 255))
        for ly in range(hy - 14, hy + 20, 8):
            d.line([(hx - 18, ly), (hx + 32, ly)], fill=(148, 163, 184, 255), width=2)
        # Bold total amount
        f_amt = _font(FONT_BOLD, 11)
        d.text((hx - 20, hy + 26), "480 250 ₽", fill=(220, 38, 38, 255), font=f_amt)

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def render_obep_captain(
    mood: str = "alert",
    mouth_state: str = "closed",
    gesture: str = "point_right",
    blink: bool = False,
    walk_phase: float = 0.0,
    facing: str = "right",
    holding_badge: bool = True,
    scale: float = 0.94,
) -> Image.Image:
    """OBEP Police Captain in navy blue uniform with white 'ОБЭП' badge & case folder."""
    base = render_full_body_character(
        outfit="hoodie", outfit_color=(24, 34, 54), hair_style="undercut",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=blink, walk_phase=walk_phase, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2

    # Gold police shoulder epaulets
    d.rectangle([(cx - 62, 240), (cx - 40, 256)], fill=(234, 179, 8, 255), outline=INK, width=2)
    d.rectangle([(cx + 40, 240), (cx + 62, 256)], fill=(234, 179, 8, 255), outline=INK, width=2)

    # White crisp reflective "ОБЭП" patch on chest
    d.rounded_rectangle([(cx - 36, 276), (cx + 36, 304)], radius=4, fill=(255, 255, 255, 255), outline=INK, width=2)
    f_p = _font(FONT_BOLD, 14)
    d.text((cx - 24, 280), "ОБЭП", fill=(24, 34, 54, 255), font=f_p)

    # Red official criminal case folder in hand
    if holding_badge:
        hx = cx + 80 if facing == "right" else cx - 80
        hy = 340
        d.rounded_rectangle([(hx - 20, hy - 30), (hx + 24, hy + 30)], radius=4, fill=(185, 28, 28, 255), outline=INK, width=2)
        d.rectangle([(hx - 14, hy - 14), (hx + 18, hy + 8)], fill=(255, 255, 255, 255))
        d.text((hx - 10, hy - 10), "ДЕЛО", fill=INK, font=_font(FONT_BOLD, 9))

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 2. VEHICLE & PROPS SPRITES
# ---------------------------------------------------------------------------

def build_anya_car_sprite(
    body_color: Tuple[int, int, int] = (220, 38, 38),
    damaged: bool = False,
) -> Image.Image:
    """Anya's bright red compact hatchback sprite."""
    S = 2
    W, H = 540 * S, 240 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _draw_car(d, cx=270 * S, wheel_y=176 * S, S=S, body_color=body_color, split_gap=0)
    # Hatchback sleek rear spoiler
    d.polygon([(110 * S, 58 * S), (145 * S, 58 * S), (120 * S, 75 * S)], fill=INK)

    if damaged:
        # Front bumper removed & dangling wire / missing grill!
        d.rectangle([(420 * S, 110 * S), (520 * S, 180 * S)], fill=(40, 40, 40, 220), outline=INK, width=3 * S)
        d.line([(450 * S, 170 * S), (465 * S, 210 * S)], fill=(234, 179, 8, 255), width=4 * S)
        d.line([(475 * S, 170 * S), (485 * S, 215 * S)], fill=(220, 38, 38, 255), width=4 * S)

    return img.resize((540, 240), Image.Resampling.LANCZOS)


def build_catalytic_converter_sprite() -> Image.Image:
    """Original metallic catalytic converter with bright yellow inspection sticker."""
    S = 2
    W, H = 340 * S, 180 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 170 * S, 90 * S
    # Exhaust pipes left and right
    d.rectangle([(20 * S, cy - 14 * S), (cx - 70 * S, cy + 14 * S)], fill=(148, 163, 184, 255), outline=INK, width=3 * S)
    d.rectangle([(cx + 70 * S, cy - 14 * S), (W - 20 * S, cy + 14 * S)], fill=(148, 163, 184, 255), outline=INK, width=3 * S)
    # Flanges
    d.rounded_rectangle([(15 * S, cy - 24 * S), (30 * S, cy + 24 * S)], radius=4 * S, fill=(100, 116, 139, 255), outline=INK, width=3 * S)
    d.rounded_rectangle([(W - 30 * S, cy - 24 * S), (W - 15 * S, cy + 24 * S)], radius=4 * S, fill=(100, 116, 139, 255), outline=INK, width=3 * S)
    # Bulging metallic catalyst body
    d.rounded_rectangle([(cx - 85 * S, cy - 48 * S), (cx + 85 * S, cy + 48 * S)], radius=24 * S, fill=(203, 213, 225, 255), outline=INK, width=5 * S)
    d.line([(cx - 70 * S, cy - 22 * S), (cx + 70 * S, cy - 22 * S)], fill=(241, 245, 249, 255), width=6 * S)

    # Yellow service sticker with "№ 42-А" (Anya's unique proof mark!)
    d.rounded_rectangle([(cx - 35 * S, cy - 22 * S), (cx + 35 * S, cy + 22 * S)], radius=4 * S, fill=(250, 204, 21, 255), outline=INK, width=3 * S)
    f_stk = _font(FONT_BOLD, 15 * S)
    stk_t = "№ 42-А"
    sb = f_stk.getbbox(stk_t)
    tw = sb[2] - sb[0]
    th = sb[3] - sb[1]
    d.text((cx - tw // 2, cy - th // 2 - sb[1]), stk_t, fill=INK, font=f_stk)

    return img.resize((340, 180), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 3. 2X-SUPERSAMPLED BACKGROUND BUILDER (9 UNIQUE LOCATIONS)
# ---------------------------------------------------------------------------

def build_autoservice_backgrounds() -> Dict[str, Image.Image]:
    """Generates all required high-res backgrounds for the auto service story."""
    S = 2
    W, H = 1080 * S, 1920 * S
    bgs = {}

    # ------------------------------------------------------------------
    # LOC 1: SERVICE RECEPTION (Promo Banner 4 990 ₽ + Glass entrance)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (241, 245, 249, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Light modern tiled wall
    for y in range(0, floor_y, 48 * S):
        d.line([(0, y), (W, y)], fill=(226, 232, 240, 255), width=2 * S)
    for x in range(0, W, 96 * S):
        d.line([(x, 0), (x, floor_y)], fill=(226, 232, 240, 255), width=2 * S)

    # Glass window accents high on wall
    d.rectangle([(80 * S, 240 * S), (1000 * S, 310 * S)], fill=(219, 234, 254, 180), outline=(191, 219, 254, 255), width=3 * S)

    # HUGE PROMO LIGHTBOX BANNER (MOUNTED HIGH AT Y = 330..580 SO IT IS 100% VISIBLE & NEVER COVERED BY REPLICA!)
    b_y1, b_y2 = 330 * S, 580 * S
    d.rounded_rectangle([(100 * S, b_y1), (980 * S, b_y2)], radius=18 * S, fill=(220, 38, 38, 255), outline=INK, width=6 * S)
    d.rounded_rectangle([(114 * S, b_y1 + 12 * S), (966 * S, b_y2 - 12 * S)], radius=12 * S, fill=(255, 255, 255, 255))
    f_tit = _font(FONT_IMPACT, 44 * S)
    f_sub = _font(FONT_BOLD, 26 * S)
    f_prc = _font(FONT_IMPACT, 68 * S)

    t1 = "🔥 АКЦИЯ ДЛЯ НОВЫХ КЛИЕНТОВ! 🔥"
    b1 = f_tit.getbbox(t1)
    d.text(((W - (b1[2] - b1[0])) // 2, b_y1 + 24 * S), t1, fill=(220, 38, 38, 255), font=f_tit)

    t2 = "ЗАМЕНА МАСЛА + ДИАГНОСТИКА ПОДВЕСКИ"
    b2 = f_sub.getbbox(t2)
    d.text(((W - (b2[2] - b2[0])) // 2, b_y1 + 92 * S), t2, fill=(30, 41, 59, 255), font=f_sub)

    t3 = "ВСЕГО 4 990 ₽"
    b3 = f_prc.getbbox(t3)
    d.text(((W - (b3[2] - b3[0])) // 2, b_y1 + 144 * S), t3, fill=(22, 163, 74, 255), font=f_prc)

    # Clean service desk counter
    d.rectangle([(620 * S, 960 * S), (1080 * S, floor_y)], fill=(71, 85, 105, 255), outline=INK, width=5 * S)
    d.rectangle([(590 * S, 940 * S), (1080 * S, 970 * S)], fill=(148, 163, 184, 255), outline=INK, width=4 * S)

    # Polished showroom floor
    d.rectangle([(0, floor_y), (W, H)], fill=(226, 232, 240, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["service_reception"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 2: SERVICE LIFT BAY (Two-Post Lift + Oil Barrels + Tool Cart)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (51, 65, 85, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Darker industrial garage wall with steel girders
    d.rectangle([(0, 0), (W, floor_y)], fill=(51, 65, 85, 255))
    for gy in [180 * S, 380 * S]:
        d.rectangle([(0, gy), (W, gy + 32 * S)], fill=(30, 41, 59, 255), outline=INK, width=3 * S)

    # Fluorescent shop lights hanging
    for lx in [260 * S, 820 * S]:
        d.line([(lx, 100 * S), (lx, 220 * S)], fill=INK, width=4 * S)
        d.rectangle([(lx - 90 * S, 220 * S), (lx + 90 * S, 244 * S)], fill=(255, 255, 255, 255), outline=INK, width=3 * S)
        # Soft downward light cone
        cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(cone).polygon([(lx - 80 * S, 244 * S), (lx + 80 * S, 244 * S), (lx + 320 * S, floor_y), (lx - 320 * S, floor_y)], fill=(255, 255, 255, 20))
        img = Image.alpha_composite(img, cone)
        d = ImageDraw.Draw(img)

    # Heavy Blue 2-Post Hydraulic Lift
    lift_col_color = (37, 99, 235, 255)
    # Left post
    d.rectangle([(180 * S, 320 * S), (240 * S, floor_y)], fill=lift_col_color, outline=INK, width=5 * S)
    d.rectangle([(160 * S, floor_y - 20 * S), (260 * S, floor_y)], fill=(30, 41, 59, 255), outline=INK, width=4 * S)
    # Right post
    d.rectangle([(840 * S, 320 * S), (900 * S, floor_y)], fill=lift_col_color, outline=INK, width=5 * S)
    d.rectangle([(820 * S, floor_y - 20 * S), (920 * S, floor_y)], fill=(30, 41, 59, 255), outline=INK, width=4 * S)
    # Lift crossbeam on top
    d.rectangle([(220 * S, 360 * S), (860 * S, 400 * S)], fill=lift_col_color, outline=INK, width=4 * S)

    # Red Hazet Tool Cart on left
    d.rounded_rectangle([(60 * S, 960 * S), (150 * S, floor_y - 10 * S)], radius=8 * S, fill=(220, 38, 38, 255), outline=INK, width=4 * S)
    for dy in range(990 * S, 1180 * S, 48 * S):
        d.line([(66 * S, dy), (144 * S, dy)], fill=(30, 41, 59, 255), width=3 * S)
        d.ellipse([100 * S, dy + 14 * S, 110 * S, dy + 24 * S], fill=(226, 232, 240, 255))

    # Blue Castrol Oil Drums on right
    d.rounded_rectangle([(930 * S, 940 * S), (1020 * S, floor_y)], radius=6 * S, fill=(14, 116, 144, 255), outline=INK, width=4 * S)
    d.ellipse([930 * S, 930 * S, 1020 * S, 960 * S], fill=(6, 182, 212, 255), outline=INK, width=3 * S)
    d.text((945 * S, 1030 * S), "OIL", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 18 * S))

    # Garage epoxy floor with oil stains
    d.rectangle([(0, floor_y), (W, H)], fill=(203, 213, 225, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    d.ellipse([420 * S, floor_y + 40 * S, 640 * S, floor_y + 110 * S], fill=(71, 85, 105, 140))
    bgs["service_lift"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 3: DISASSEMBLED ENGINE BAY (Horror of stripped car on lift)
    # ------------------------------------------------------------------
    img = bgs["service_lift"].copy()
    img = img.resize((W, H), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(img)

    # Red car hoisted high on the lift arms!
    car_elev_y = 680 * S
    # Lift horizontal arms holding car
    d.rectangle([(220 * S, car_elev_y + 110 * S), (860 * S, car_elev_y + 135 * S)], fill=(234, 179, 8, 255), outline=INK, width=4 * S)
    # Car body elevated
    _draw_car(d, cx=540 * S, wheel_y=car_elev_y + 90 * S, S=S, body_color=(220, 38, 38), split_gap=0)

    # Disassembled front: bumper removed, radiator hollow!
    d.rectangle([(710 * S, car_elev_y + 10 * S), (820 * S, car_elev_y + 95 * S)], fill=(24, 24, 28, 240), outline=INK, width=4 * S)
    d.line([(740 * S, car_elev_y + 90 * S), (750 * S, car_elev_y + 140 * S)], fill=(234, 88, 12, 255), width=5 * S)
    d.line([(780 * S, car_elev_y + 90 * S), (770 * S, car_elev_y + 145 * S)], fill=(56, 189, 248, 255), width=5 * S)

    # Cut catalytic converter exhaust pipe dangling under car with open empty gap!
    d.line([(420 * S, car_elev_y + 115 * S), (490 * S, car_elev_y + 115 * S)], fill=(148, 163, 184, 255), width=8 * S)
    d.line([(620 * S, car_elev_y + 115 * S), (700 * S, car_elev_y + 115 * S)], fill=(148, 163, 184, 255), width=8 * S)
    # Dotted red box showing missing catalytic converter!
    d.rectangle([(495 * S, car_elev_y + 90 * S), (615 * S, car_elev_y + 140 * S)], outline=(239, 68, 68, 255), width=4 * S)
    d.text((505 * S, car_elev_y + 98 * S), "СНЯТО!", fill=(239, 68, 68, 255), font=_font(FONT_BOLD, 18 * S))

    # Telescopic oil drain funnel on floor under car
    d.polygon([(510 * S, 940 * S), (570 * S, 940 * S), (550 * S, 990 * S), (530 * S, 990 * S)], fill=(30, 41, 59, 255), outline=INK, width=3 * S)
    d.line([(540 * S, 990 * S), (540 * S, floor_y)], fill=(30, 41, 59, 255), width=8 * S)

    # Large fresh dark oil puddle on floor
    d.ellipse([460 * S, floor_y + 20 * S, 620 * S, floor_y + 80 * S], fill=(15, 23, 42, 220))
    bgs["engine_disassembled"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 4: RUSTY GRAVEYARD BACK ALLEY (Scrap heap of old exhausts & tires)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (30, 32, 38, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Dark gloomy brick wall with grime
    for y in range(0, floor_y, 36 * S):
        d.line([(0, y), (W, y)], fill=(44, 48, 56, 255), width=2 * S)
    # Barbed wire coil along top of wall
    d.line([(0, 180 * S), (W, 180 * S)], fill=(148, 163, 184, 255), width=3 * S)
    for bx in range(0, W, 40 * S):
        d.arc([bx, 155 * S, bx + 50 * S, 205 * S], start=0, end=360, fill=(100, 116, 139, 255), width=2 * S)

    # Dim yellow sodium security lamp
    d.rectangle([(840 * S, 240 * S), (900 * S, 300 * S)], fill=(245, 158, 11, 255), outline=INK, width=4 * S)
    cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(cone).polygon([(840 * S, 300 * S), (900 * S, 300 * S), (W, floor_y), (480 * S, floor_y)], fill=(245, 158, 11, 25))
    img = Image.alpha_composite(img, cone)
    d = ImageDraw.Draw(img)

    # Huge Scrap Pile: rusty orange mufflers, pipes, brake rotors
    # Rusty mufflers
    for mx, my, rot in [(200, 1100, 20), (320, 1060, -35), (420, 1120, 10), (140, 1150, -15)]:
        d.rounded_rectangle([(mx * S, my * S), ((mx + 140) * S, (my + 45) * S)], radius=10 * S, fill=(180, 83, 9, 255), outline=INK, width=3 * S)
        d.line([((mx - 25) * S, (my + 22) * S), ((mx + 165) * S, (my + 22) * S)], fill=(120, 53, 15, 255), width=6 * S)

    # Stacks of worn bald tires on left
    for ty in [1160, 1110, 1060, 1010]:
        d.rounded_rectangle([(40 * S, ty * S), (160 * S, (ty + 44) * S)], radius=12 * S, fill=(24, 28, 36, 255), outline=INK, width=4 * S)
        d.ellipse([70 * S, (ty + 10) * S, 130 * S, (ty + 34) * S], fill=(45, 50, 60, 255))

    # Wet asphalt ground reflecting sodium light
    d.rectangle([(0, floor_y), (W, H)], fill=(28, 30, 36, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    d.ellipse([340 * S, floor_y + 40 * S, 720 * S, floor_y + 110 * S], fill=(40, 44, 52, 200))
    bgs["rusty_graveyard"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 5: AVITO SMARTPHONE SCREEN (Glowing UI with Stolen Part & Yellow Sticker!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    d = ImageDraw.Draw(img)

    # Giant smartphone chassis in center
    ph_w, ph_h = 820 * S, 1520 * S
    ph_x = (W - ph_w) // 2
    ph_y = 180 * S
    d.rounded_rectangle([(ph_x, ph_y), (ph_x + ph_w, ph_y + ph_h)], radius=56 * S, fill=(24, 28, 36, 255), outline=(71, 85, 105, 255), width=8 * S)
    # Screen inner bezel
    d.rounded_rectangle([(ph_x + 18 * S, ph_y + 18 * S), (ph_x + ph_w - 18 * S, ph_y + ph_h - 18 * S)], radius=42 * S, fill=(255, 255, 255, 255))

    # Avito Header bar
    d.rectangle([(ph_x + 18 * S, ph_y + 18 * S), (ph_x + ph_w - 18 * S, ph_y + 130 * S)], fill=(0, 170, 255, 255))
    f_av_h = _font(FONT_BOLD, 36 * S)
    d.text((ph_x + 50 * S, ph_y + 54 * S), "Авито • Автозапчасти", fill=(255, 255, 255, 255), font=f_av_h)

    # Search query box
    d.rounded_rectangle([(ph_x + 40 * S, ph_y + 150 * S), (ph_x + ph_w - 40 * S, ph_y + 215 * S)], radius=10 * S, fill=(241, 245, 249, 255), outline=(203, 213, 225, 255), width=2 * S)
    f_q = _font(FONT_BOLD, 22 * S)
    d.text((ph_x + 60 * S, ph_y + 172 * S), "🔍  Оригинальный катализатор Kia/Hyundai", fill=(100, 116, 139, 255), font=f_q)

    # Big Listing Card
    card_y = ph_y + 245 * S
    d.rounded_rectangle([(ph_x + 40 * S, card_y), (ph_x + ph_w - 40 * S, card_y + 860 * S)], radius=16 * S, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=4 * S)

    # Photo area of the part
    photo_box = [(ph_x + 60 * S, card_y + 20 * S), (ph_x + ph_w - 60 * S, card_y + 440 * S)]
    d.rounded_rectangle(photo_box, radius=12 * S, fill=(241, 245, 249, 255))
    cat_spr = build_catalytic_converter_sprite()
    scale = 2.4
    cat_w = int(cat_spr.width * scale)
    cat_h = int(cat_spr.height * scale)
    cat_spr_lg = cat_spr.resize((cat_w, cat_h), Image.Resampling.LANCZOS)

    cx_target = ph_x + ph_w // 2
    cy_target = card_y + 220 * S
    cat_x = cx_target - cat_w // 2
    cat_y = cy_target - cat_h // 2
    img.paste(cat_spr_lg, (cat_x, cat_y), cat_spr_lg)
    d = ImageDraw.Draw(img)

    # Red callout circle centered directly on the yellow sticker
    stk_x = cx_target
    stk_y = cy_target
    r = 75 * S
    d.ellipse([stk_x - r, stk_y - r, stk_x + r, stk_y + r], outline=(239, 68, 68, 255), width=6 * S)

    # Pointer arrow & badge "ЕЁ НАКЛЕЙКА!"
    pt_x = stk_x + int(r * 0.707)
    pt_y = stk_y + int(r * 0.707)
    bg_x = pt_x + 40 * S
    bg_y = pt_y + 30 * S
    badge_w = 230 * S
    badge_h = 56 * S
    d.polygon([(pt_x, pt_y), (bg_x + 20 * S, bg_y + 10 * S), (bg_x, bg_y + 35 * S)], fill=(239, 68, 68, 255))
    d.rounded_rectangle([(bg_x, bg_y), (bg_x + badge_w, bg_y + badge_h)], radius=10 * S, fill=(239, 68, 68, 255))
    f_badge = _font(FONT_BOLD, 22 * S)
    badge_txt = "ЕЁ НАКЛЕЙКА!"
    bb_b = f_badge.getbbox(badge_txt)
    tx = bg_x + (badge_w - (bb_b[2] - bb_b[0])) // 2
    ty = bg_y + (badge_h - (bb_b[3] - bb_b[1])) // 2 - bb_b[1]
    d.text((tx, ty), badge_txt, fill=(255, 255, 255, 255), font=f_badge)

    # Listing Details
    f_price = _font(FONT_IMPACT, 52 * S)
    d.text((ph_x + 60 * S, card_y + 465 * S), "85 000 ₽", fill=(15, 23, 42, 255), font=f_price)

    f_desc = _font(FONT_BOLD, 26 * S)
    d.text((ph_x + 60 * S, card_y + 535 * S), "Катализатор Kia Rio 1.6 • ИДЕАЛ", fill=(30, 41, 59, 255), font=f_desc)
    d.text((ph_x + 60 * S, card_y + 580 * S), "Снят час назад с живой машины!", fill=(100, 116, 139, 255), font=_font(FONT_BOLD, 22 * S))
    d.text((ph_x + 60 * S, card_y + 620 * S), "Продавец: СТО-Мастер • В наличии", fill=(22, 163, 74, 255), font=_font(FONT_BOLD, 22 * S))

    # Blue "Позвонить / Написать" button
    d.rounded_rectangle([(ph_x + 60 * S, card_y + 680 * S), (ph_x + ph_w - 60 * S, card_y + 780 * S)], radius=12 * S, fill=(0, 170, 255, 255))
    f_btn = _font(FONT_BOLD, 30 * S)
    bt = "Написать продавцу"
    bb = f_btn.getbbox(bt)
    d.text(((W - (bb[2] - bb[0])) // 2, card_y + 710 * S), bt, fill=(255, 255, 255, 255), font=f_btn)

    # Red stamp overlay: "ПОЛИЧНОЕ!"
    d.rounded_rectangle([(180 * S, 1420 * S), (900 * S, 1540 * S)], radius=18 * S, fill=(220, 38, 38, 245), outline=(255, 255, 255, 255), width=6 * S)
    f_stmp = _font(FONT_IMPACT, 48 * S)
    st = "УЛИКА! НАШЛА СВОЙ КАТАЛИЗАТОР!"
    sb = f_stmp.getbbox(st)
    d.text(((W - (sb[2] - sb[0])) // 2, 1450 * S), st, fill=(255, 255, 255, 255), font=f_stmp)

    bgs["avito_screen"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 6: DIRECTOR'S OFFICE (Desk with 480 250 ₽ bill + safe)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (248, 250, 252, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Office wall with wooden paneling lower half
    d.rectangle([(0, 0), (W, floor_y)], fill=(241, 245, 249, 255))
    d.rectangle([(0, 680 * S), (W, floor_y)], fill=(120, 53, 15, 255), outline=INK, width=4 * S)

    # Fake framed certificates / diplomas on wall
    for cx in [220 * S, 480 * S, 740 * S]:
        d.rectangle([(cx, 340 * S), (cx + 180 * S, 460 * S)], fill=(254, 243, 199, 255), outline=INK, width=4 * S)
        d.line([(cx + 20 * S, 370 * S), (cx + 160 * S, 370 * S)], fill=(180, 83, 9, 255), width=3 * S)
        d.line([(cx + 20 * S, 400 * S), (cx + 140 * S, 400 * S)], fill=(148, 163, 184, 255), width=2 * S)

    # Heavy Director's Desk in foreground
    d.rectangle([(160 * S, 940 * S), (920 * S, floor_y)], fill=(69, 26, 3, 255), outline=INK, width=5 * S)
    d.rectangle([(120 * S, 920 * S), (960 * S, 955 * S)], fill=(120, 53, 15, 255), outline=INK, width=4 * S)

    # Gigantic printed Invoice Sheet lying on desk
    d.rounded_rectangle([(320 * S, 780 * S), (760 * S, 935 * S)], radius=6 * S, fill=(255, 255, 255, 255), outline=INK, width=4 * S)
    d.rectangle([(335 * S, 795 * S), (745 * S, 825 * S)], fill=(220, 38, 38, 255))
    d.text((345 * S, 802 * S), "ЗАКАЗ-НАРЯД № 714", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 18 * S))
    d.text((340 * S, 840 * S), "Дефектовка ДВС и турбины: 480 250 ₽", fill=INK, font=_font(FONT_BOLD, 18 * S))
    d.rounded_rectangle([(560 * S, 875 * S), (745 * S, 925 * S)], radius=4 * S, fill=(220, 38, 38, 255))
    d.text((570 * S, 888 * S), "К ОПЛАТЕ!", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 18 * S))

    # Carpet floor
    d.rectangle([(0, floor_y), (W, H)], fill=(226, 232, 240, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["director_office"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 7: SERVICE GATES LOCKED (Roller Shutter + Heavy Padlock)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (40, 44, 52, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Dark steel garage frontage
    d.rectangle([(0, 0), (W, floor_y)], fill=(30, 41, 59, 255))

    # Heavy Closed Corrugated Roller Gate
    d.rectangle([(140 * S, 340 * S), (940 * S, floor_y)], fill=(71, 85, 105, 255), outline=INK, width=6 * S)
    for ry in range(350 * S, floor_y, 32 * S):
        d.line([(145 * S, ry), (935 * S, ry)], fill=(51, 65, 85, 255), width=3 * S)

    # Massive Steel Chain & Padlock on Gate
    d.rectangle([(500 * S, floor_y - 120 * S), (580 * S, floor_y - 30 * S)], fill=(234, 179, 8, 255), outline=INK, width=5 * S)
    d.arc([515 * S, floor_y - 170 * S, 565 * S, floor_y - 110 * S], start=180, end=360, fill=(148, 163, 184, 255), width=8 * S)

    # Red warning sign: "ВЫЕЗД ЗАБЛОКИРОВАН"
    d.rounded_rectangle([(240 * S, 560 * S), (840 * S, 680 * S)], radius=14 * S, fill=(220, 38, 38, 255), outline=INK, width=5 * S)
    f_gat = _font(FONT_IMPACT, 42 * S)
    gt = "ВЫЕЗД ЗАБЛОКИРОВАН!"
    gb = f_gat.getbbox(gt)
    d.text(((W - (gb[2] - gb[0])) // 2, 595 * S), gt, fill=(255, 255, 255, 255), font=f_gat)

    # Ground
    d.rectangle([(0, floor_y), (W, H)], fill=(203, 213, 225, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["service_gates"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 8: POLICE RAID BAY (Red/Blue Strobe flashes + OBEP Sealed Tape)
    # ------------------------------------------------------------------
    img = bgs["service_lift"].copy()
    img = img.resize((W, H), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(img)

    # Police Crime Scene Red-White barrier tape across foreground!
    d.polygon([(0, 680 * S), (W, 780 * S), (W, 830 * S), (0, 730 * S)], fill=(220, 38, 38, 240), outline=INK)
    for sx in range(0, W + 200 * S, 120 * S):
        d.polygon([(sx, 680 * S + int(sx * 0.08)), (sx + 50 * S, 680 * S + int((sx + 50 * S) * 0.08)), (sx + 50 * S, 730 * S + int((sx + 50 * S) * 0.08)), (sx, 730 * S + int(sx * 0.08))], fill=(255, 255, 255, 240))
    f_tape = _font(FONT_BOLD, 22 * S)
    d.text((260 * S, 735 * S), "ОБЭП • СЕРВИС ОПЕЧАТАН • СТ. 159 УК РФ", fill=INK, font=f_tape)

    # Cardboard evidence boxes with recovered car parts on floor
    d.rectangle([(160 * S, floor_y - 90 * S), (300 * S, floor_y)], fill=(180, 83, 9, 255), outline=INK, width=4 * S)
    d.text((180 * S, floor_y - 65 * S), "УЛИКИ", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 18 * S))

    bgs["police_raid"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 9: DAYLIGHT PLAZA (Warm Sunny Finale + Restored Hatchback)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (224, 242, 254, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1235 * S

    # Fresh blue sky gradient
    for y in range(0, floor_y, 4):
        rat = y / floor_y
        d.rectangle([(0, y), (W, y + 4)], fill=(int(186 - rat * 30), int(230 - rat * 20), int(253 - rat * 10), 255))

    # Bright morning sun
    d.ellipse([780 * S, 180 * S, 940 * S, 340 * S], fill=(254, 240, 138, 255), outline=(250, 204, 21, 255), width=6 * S)

    # Modern city skyline backdrop
    for bx, bw, bh in [(40, 190, 420), (260, 220, 520), (520, 180, 380), (740, 240, 480)]:
        d.rectangle([(bx * S, floor_y - bh * S), ((bx + bw) * S, floor_y)], fill=(148, 163, 184, 180), outline=INK, width=4 * S)

    # Clean sunlit plaza floor
    d.rectangle([(0, floor_y), (W, H)], fill=(241, 245, 249, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    bgs["daylight_plaza"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    return bgs


# ---------------------------------------------------------------------------
# 4. STORY EPISODES DATA (5 FULL-LENGTH EPISODES)
# ---------------------------------------------------------------------------

AUTOSERVICE_EPISODES = {
    1: {
        "filename": "autoservice_ep1_trap.mp4",
        "title": "Автосервис-ловушка • Часть 1: Замена масла за 4 990 ₽",
        "chapters": [
            {
                "scene_id": "as1_s1",
                "loc": "service_reception",
                "sentences": [
                    "Аня приехала в автосервис по яркой рекламе: замена масла и бесплатная диагностика всего за четыре тысячи девятьсот девяносто рублей.",
                    "Наглый приёмщик расплылся в улыбке: «Оставляйте ключи, попейте кофе часик — сделаем всё в лучшем виде!»",
                ],
                "hud_bal": "4 990 ₽",
                "hud_st": "ПРИЁМКА АВТО",
                "theme": "crypto",
                "pill": "СТО «АВТО-ЭКСПРЕСС» • ПРИЁМКА",
                "sfx": "coin",
            },
            {
                "scene_id": "as1_s2",
                "loc": "service_lift",
                "sentences": [
                    "Но как только девушка вышла за дверь, улыбка мастера мгновенно исчезла.",
                    "Он подозвал механиков и скомандовал: «Поднимайте на подъёмник! Снимайте оригинальный катализатор — клиентка неопытная, разведём по полной!»",
                ],
                "hud_bal": "РАЗБОРКА ДВС",
                "hud_st": "СХЕМА АВТОСЕРВИСА!",
                "theme": "danger",
                "pill": "РЕМЗОНА • СНЯТИЕ ДЕТАЛЕЙ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "as1_s3",
                "loc": "service_lift",
                "sentences": [
                    "За сорок минут новенькую машину буквально раскидали по винтикам, а снятые запчасти тайком вынесли на склад.",
                    "Вместо них приготовили ржавый хлам со свалки заднего двора!",
                ],
                "hud_bal": "ДЕТАЛИ СНЯТЫ",
                "hud_st": "ПОДМЕНА НА ХЛАМ",
                "theme": "danger",
                "pill": "СКЛАД ЗАПЧАСТЕЙ • ПОДМЕНА",
                "sfx": "boom",
            },
            {
                "scene_id": "as1_s4",
                "loc": "engine_disassembled",
                "sentences": [
                    "Спустя час Аня вернулась со стаканчиком кофе и зашла в ремзону... Но её машина висела без морды, а весь пол был залит маслом!",
                    "«Что вы сделали с моей машиной?!» — в ужасе закричала она. Смотри вторую часть!",
                ],
                "hud_bal": "ШОК КЛИЕНТА!",
                "hud_st": "ДВИГАТЕЛЬ РАЗОБРАН!",
                "theme": "danger",
                "pill": "РЕМЗОНА • МАШИНА РАЗОБРАНА",
                "sfx": "boom",
            },
        ],
    },
    2: {
        "filename": "autoservice_ep2_bill.mp4",
        "title": "Автосервис-ловушка • Часть 2: Счёт на 480 000 рублей",
        "chapters": [
            {
                "scene_id": "as2_s1",
                "loc": "engine_disassembled",
                "sentences": [
                    "Часть вторая. Мастер подошёл к Ане и с наглым видом потряс перед её лицом кривой ржавой железкой.",
                    "«Девушка, молитесь, что вообще доехали! У вас двигатель заклинил, турбина рассыпалась, а катализатор сгорел дотла!»",
                ],
                "hud_bal": "«ТОТАЛЬНЫЙ ИЗНОС»",
                "hud_st": "ЛОЖЬ МАСТЕРА!",
                "theme": "danger",
                "pill": "ДЕФЕКТОВКА • ОБМАН КЛИЕНТА",
                "sfx": "whoosh",
            },
            {
                "scene_id": "as2_s2",
                "loc": "director_office",
                "sentences": [
                    "«Мы разобрали всё ради вашей же безопасности! — заявил он и повёл её в кабинет директора.",
                    "Там ей с порога швырнули на стол распечатанный заказ-наряд на четыреста восемьдесят тысяч двести пятьдесят рублей!»",
                ],
                "hud_bal": "480 250 ₽",
                "hud_st": "ЗАКАЗ-НАРЯД №714",
                "theme": "danger",
                "pill": "КАССА • СЧЁТ НА 480 000 ₽",
                "sfx": "boom",
            },
            {
                "scene_id": "as2_s3",
                "loc": "director_office",
                "sentences": [
                    "Аня замерла: «Какая разборка?! Я заказывала только замену масла за пять тысяч! Верните мою машину!»",
                    "Но директор вальяжно усмехнулся: «У нас в договоре мелким шрифтом написано — аварийная дефектовка платная. Плати или забирай запчасти в мешках!»",
                ],
                "hud_bal": "ШАНТАЖ",
                "hud_st": "«ПЛАТИ ИЛИ В МЕШКАХ!»",
                "theme": "danger",
                "pill": "КАБИНЕТ ДИРЕКТОРА • ТРЕБОВАНИЕ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "as2_s4",
                "loc": "service_gates",
                "sentences": [
                    "В эту секунду ворота автосервиса с грохотом опустились на замок. Машину взяли в заложники!",
                    "Каждый день простоя — три тысячи рублей! В слезах Аня выбежала на улицу... Продолжение в третьей части!",
                ],
                "hud_bal": "ВОРОТА ЗАПЕРТЫ!",
                "hud_st": "3 000 ₽ / ДЕНЬ",
                "theme": "danger",
                "pill": "АВТО В ЗАЛОЖНИКАХ • ШАНТАЖ",
                "sfx": "boom",
            },
        ],
    },
    3: {
        "filename": "autoservice_ep3_avito.mp4",
        "title": "Автосервис-ловушка • Часть 3: Улика на Авито и тайный свидетель",
        "chapters": [
            {
                "scene_id": "as3_s1",
                "loc": "rusty_graveyard",
                "sentences": [
                    "Часть третья. Аня стояла на заднем дворе сервиса возле огромной горы ржавых запчастей и плакала.",
                    "Таких денег у неё не было, а доказать обман казалось невозможным.",
                ],
                "hud_bal": "ТУПИК...",
                "hud_st": "ЗАДНИЙ ДВОР СТО",
                "theme": "alert",
                "pill": "КЛАДБИЩЕ ЗАПЧАСТЕЙ • БЕЗВЫХОДНОСТЬ",
                "sfx": "drip",
            },
            {
                "scene_id": "as3_s2",
                "loc": "rusty_graveyard",
                "sentences": [
                    "Вдруг из боковой двери тихо вышел молодой стажёр-механик в оранжевом комбинезоне.",
                    "«Девушка, не плачьте и ни в коем случае не платите им ни рубля! — прошептал парень. — Ваша машина была абсолютно здорова!»",
                ],
                "hud_bal": "СТАЖЁР СТО",
                "hud_st": "«ВАС РАЗВОДЯТ!»",
                "theme": "alert",
                "pill": "ТАЙНЫЙ СВИДЕТЕЛЬ • РАСКРЫТИЕ СХЕМЫ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "as3_s3",
                "loc": "avito_screen",
                "sentences": [
                    "Он достал свой телефон и открыл Авито: «Смотрите! Ровно сорок минут назад наш приёмщик выставил ваш катализатор за восемьдесят пять тысяч рублей!»",
                    "Аня пригляделась и ахнула: на фото в объявлении чётко виднелась её жёлтая сервисная наклейка с прошлого техосмотра!",
                ],
                "hud_bal": "УЛИКА НА АВИТО!",
                "hud_st": "85 000 ₽",
                "theme": "danger",
                "pill": "АВИТО • СВОЙ КАТАЛИЗАТОР В ПРОДАЖЕ!",
                "sfx": "boom",
            },
            {
                "scene_id": "as3_s4",
                "loc": "rusty_graveyard",
                "sentences": [
                    "«И самое главное — я тайно записал на телефон, как они снимали ваши детали и ставили этот ржавый хлам!» — сказал стажёр и передал ей флешку.",
                    "Теперь у Ани были железные доказательства. В четвёртой части начнётся расплата!",
                ],
                "hud_bal": "ФЛЕШКА С ВИДЕО",
                "hud_st": "ПОЛНЫЙ КОМПРОМАТ!",
                "theme": "crypto",
                "pill": "ЖЕЛЕЗНЫЕ УЛИКИ • ПЛАН ВОЗМЕЗДИЯ",
                "sfx": "coin",
            },
        ],
    },
    4: {
        "filename": "autoservice_ep4_confrontation.mp4",
        "title": "Автосервис-ловушка • Часть 4: Очная ставка и штурм ОБЭП",
        "chapters": [
            {
                "scene_id": "as4_s1",
                "loc": "director_office",
                "sentences": [
                    "Часть четвёртая. Аня решительным шагом вернулась в кабинет директора автосервиса.",
                    "Тот довольно пересчитывал пачку денег: «Ну что, принесла четыреста восемьдесят тысяч? Или ключи на стол и машина уходит в утиль?»",
                ],
                "hud_bal": "ШАНТАЖ 480К",
                "hud_st": "ДИРЕКТОР ЖДЁТ ДЕНЬГИ",
                "theme": "alert",
                "pill": "КАБИНЕТ ДИРЕКТОРА • РАЗГОВОР",
                "sfx": "whoosh",
            },
            {
                "scene_id": "as4_s2",
                "loc": "director_office",
                "sentences": [
                    "Аня молча положила на стол телефон с включённым диктофоном и показала распечатку объявления с Авито.",
                    "«Вы украли мой катализатор, подсунули гниль со свалки и вымогаете полмиллиона рублей!»",
                ],
                "hud_bal": "ПРЕДЪЯВА!",
                "hud_st": "ДИКТОФОН + АВИТО",
                "theme": "danger",
                "pill": "ОЧНАЯ СТАВКА • УЛИКИ НА СТОЛЕ",
                "sfx": "boom",
            },
            {
                "scene_id": "as4_s3",
                "loc": "director_office",
                "sentences": [
                    "Директор вскочил и злобно закричал: «Да кому ты пожалуешься?! Ментам? У меня здесь всё схвачено, ты отсюда пешком уйдёшь!»",
                    "Но Аня лишь спокойно улыбнулась: «А вы это следователям скажите... Они слушают наш разговор за дверью».",
                ],
                "hud_bal": "«У МЕНЯ ВСЁ СХВАЧЕНО!»",
                "hud_st": "ПРЯМОЙ ЭФИР",
                "theme": "danger",
                "pill": "ПРЯМАЯ ТРАНСЛЯЦИЯ В ПОЛИЦИЮ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "as4_s4",
                "loc": "police_raid",
                "sentences": [
                    "В ту же секунду входные двери с грохотом распахнулись! В сервис ворвалась группа отдела экономической безопасности!",
                    "«ОБЭП! Руки на стол, работает полиция!» — скомандовал капитан. Смотри развязку в финале!",
                ],
                "hud_bal": "ОБЭП РАБОТАЕТ!",
                "hud_st": "ОБЛАВА НА СТО!",
                "theme": "danger",
                "pill": "ОТДЕЛ ЭКОНОМИЧЕСКОЙ БЕЗОПАСНОСТИ",
                "sfx": "boom",
            },
        ],
    },
    5: {
        "filename": "autoservice_ep5_finale.mp4",
        "title": "Автосервис-ловушка • Часть 5: Разгром разводил и 3 правила водителя",
        "chapters": [
            {
                "scene_id": "as5_s1",
                "loc": "police_raid",
                "sentences": [
                    "Финал истории! В ходе обыска в подсобках сервиса полиция нашла шестьдесят украденных катализаторов и целый склад поддельных накладных.",
                    "На ворота СТО наложили пломбы, а директора и наглого мастера увели в наручниках — им грозит до десяти лет по статье мошенничество!",
                ],
                "hud_bal": "СТ. 159 УК РФ",
                "hud_st": "ДО 10 ЛЕТ ТЮРЬМЫ",
                "theme": "danger",
                "pill": "ОБЫСК СТО • 60 КРАДЕНЫХ ДЕТАЛЕЙ",
                "sfx": "boom",
            },
            {
                "scene_id": "as5_s2",
                "loc": "service_lift",
                "sentences": [
                    "Под надзором криминалистов честный стажёр лично установил все родные детали Ани обратно на автомобиль.",
                    "Капитан полиции вернул девушке ключи и поблагодарил за смелость!",
                ],
                "hud_bal": "АВТО СОБРАНО!",
                "hud_st": "РОДНЫЕ ДЕТАЛИ НА МЕСТЕ",
                "theme": "crypto",
                "pill": "ВОЗВРАТ АВТОМОБИЛЯ • СПРАВЕДЛИВОСТЬ",
                "sfx": "coin",
            },
            {
                "scene_id": "as5_s3",
                "loc": "daylight_plaza",
                "sentences": [
                    "Аня забрала свою машину, не заплатив ни копейки вымогателям, а стажёра пригласили работать в официальный дилерский центр.",
                    "Но чтобы никогда не попасть в такой капкан, запомните три главных правила каждого водителя!",
                ],
                "hud_bal": "ПОБЕДА!",
                "hud_st": "0 РУБЛЕЙ РАЗВОДИЛАМ",
                "theme": "crypto",
                "pill": "ГЛАВНЫЙ ЛАЙФХАК ДЛЯ ВОДИТЕЛЕЙ",
                "sfx": "whoosh",
            },
            {
                "scene_id": "as5_s4",
                "loc": "daylight_plaza",
                "sentences": [
                    "Первое: всегда требуйте личного присутствия в ремзоне — по тридцать второй статье закона о защите прав потребителей это ваше право!",
                    "Второе: никогда не подписывайте пустые акты без лимита стоимости. А при любом шантаже — сразу звоните сто двенадцать! Сохраняй и перешли друзьям!",
                ],
                "hud_bal": "СТ. 32 ЗОЗПП",
                "hud_st": "ЗВОНИТЕ 112!",
                "theme": "crypto",
                "pill": "ЗАЩИТИ СЕБЯ И СВОЙ АВТОМОБИЛЬ!",
                "sfx": "coin",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# 5. MASTER EPISODE RENDERER
# ---------------------------------------------------------------------------

def render_autoservice_episode(
    ep_num: int,
    out_dir: Path = Path("output/story_autoservice"),
    speaker: str = "f5",
    fps: int = 30,
    shared_bgs: Optional[Dict[str, Image.Image]] = None,
) -> Path:
    ep = AUTOSERVICE_EPISODES[ep_num]
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
    voice_wav = work_dir / f"voice_autoservice_ep{ep_num}_{speaker}.wav"
    cached_words = work_dir / f"words_f5_voice_autoservice_ep{ep_num}_{speaker}.json"

    if speaker == "f5" and voice_wav.exists() and cached_words.exists():
        print(f"[AUTOSERVICE EP{ep_num}] 1. Используем кэшированную GPU-озвучку F5-TTS...")
        voice_file = voice_wav
        meta = json.loads(cached_words.read_text(encoding="utf-8"))
        words = meta["words"]
        duration = float(meta["duration"])
    elif speaker == "f5" and is_f5_available():
        print(f"[AUTOSERVICE EP{ep_num}] 1. Синтезируем живую озвучку '{ep['title']}' (F5-TTS RTX 4050)...")
        voice_file, words, duration = synthesize_f5_script(all_sentences, out_wav=voice_wav, speed=1.07)
    else:
        print(f"[AUTOSERVICE EP{ep_num}] 1. Синтезируем Silero v5.6 ({speaker})...")
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

    # --- NEXT-GEN SOUND DESIGN (EPISODE 4 BETA) ---
    if ep_num == 4:
        # 1. Suspense beat background music with audio ducking
        bed_path = synth_suspense_bed(sfx_dir / "suspense_bed.wav", duration + 1.0)
        with wave.open(str(bed_path), "rb") as wf:
            bed_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

        v_len = min(len(vs), total_samples)
        hop = sr // 10  # 100ms chunks
        duck_gain = np.full(total_samples, 0.22, dtype=np.float32)
        for k in range(0, v_len, hop):
            block = np.abs(vs[k:min(k + hop, v_len)])
            if len(block) > 0 and np.mean(block) > 0.035:
                duck_gain[k:min(k + hop, total_samples)] = 0.09  # quiet ducking during speech

        b_len = min(len(bed_data), total_samples)
        master[:b_len] += bed_data[:b_len] * duck_gain[:b_len]

        # 2. Rich Foley events from backend/assets/sfx/
        assets_sfx = PROJECT_ROOT / "backend" / "assets" / "sfx"
        if (assets_sfx / "clock_tick.wav").exists():
            sfx_events.append((ch_starts[0] + 0.25, assets_sfx / "clock_tick.wav", 0.40))
        if (assets_sfx / "impact.wav").exists():
            sfx_events.append((ch_starts[1] + 0.35, assets_sfx / "impact.wav", 0.70))
        if (assets_sfx / "heartbeat.wav").exists():
            sfx_events.append((ch_starts[1] + 0.55, assets_sfx / "heartbeat.wav", 0.55))
        if (assets_sfx / "tension_riser.wav").exists():
            sfx_events.append((ch_starts[2] + 0.15, assets_sfx / "tension_riser.wav", 0.65))
        if (assets_sfx / "door_slam.wav").exists():
            sfx_events.append((ch_starts[3], assets_sfx / "door_slam.wav", 0.90))
        if (assets_sfx / "sub_boom.wav").exists():
            sfx_events.append((ch_starts[3] + 0.04, assets_sfx / "sub_boom.wav", 0.85))

        # Police siren during scene 4:
        siren_dur = duration - ch_starts[3] + 0.5
        siren_path = synth_police_siren(sfx_dir / "police_siren.wav", siren_dur)
        sfx_events.append((ch_starts[3], siren_path, 0.28))

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
    ass_path = work_dir / f"autoservice_ep{ep_num}.ass"
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
    bgs = shared_bgs if shared_bgs is not None else build_autoservice_backgrounds()
    anya_car = build_anya_car_sprite((220, 38, 38), damaged=False)
    anya_car_dmg = build_anya_car_sprite((220, 38, 38), damaged=True)
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
        # EPISODE 1: ЗАМЕНА МАСЛА ЗА 4 990 ₽
        # ================================================================
        if sid == "as1_s1":
            # Anya arrives at reception, hands keys to smiling master
            anya = render_anya(mood="confident", mouth_state=mouth, gesture="relax", blink=blink, facing="right", holding_keys=True, scale=0.92)
            master = render_master(mood="smug", mouth_state="closed", gesture="relax", blink=blink, facing="left", holding_wrench=False, scale=0.94)
            frame = paste_char(frame, anya, 340, 1300)
            frame = paste_char(frame, master, 800, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Замена масла за 4 990 ₽?\nПопейте кофе часик!»", anchor_x=760, anchor_y=800, align="right", pop_scale=pop_late)

        elif sid == "as1_s2":
            # Service lift: Car on lift, master points to exhaust, trainee looks shocked
            frame = paste_obj(frame, anya_car, 270, 980)
            master = render_master(mood="shady", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", holding_wrench=True, scale=0.94)
            trainee = render_trainee(mood="alert", mouth_state="closed", gesture="relax", blink=blink, facing="left", scale=0.91)
            frame = paste_char(frame, master, 260, 1305)
            frame = paste_char(frame, trainee, 860, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.5:
                draw_smart_bubble(frame, "«Снимайте катализатор!\nРазведём клиентку!»", anchor_x=310, anchor_y=810, align="left", pop_scale=pop_late)

        elif sid == "as1_s3":
            # Sparks flying under car, trainee secretly takes photo on phone
            frame = paste_obj(frame, anya_car_dmg, 270, 980)
            trainee = render_trainee(mood="alert", mouth_state="closed", gesture="hold_phone", blink=blink, facing="left", scale=0.92)
            frame = paste_char(frame, trainee, 840, 1305)
            # Trainee phone flash / screen glow
            flash_p = max(0.0, 1.0 - (t_local % 1.5) / 0.3)
            if flash_p > 0.1:
                ov = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                ImageDraw.Draw(ov).ellipse([780, 1040, 840, 1100], fill=(255, 255, 255, int(flash_p * 180)))
                frame = Image.alpha_composite(frame, ov)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "ПОДМЕНА ДЕТАЛЕЙ!", t_local - 0.15, center=(540, 560))

        elif sid == "as1_s4":
            # Anya returns with coffee cup and grabs head in pure horror
            anya = render_anya(mood="shocked", mouth_state=mouth, gesture="hands_on_head", blink=False, facing="right", scale=0.95)
            master = render_master(mood="smug", mouth_state="closed", gesture="relax", blink=blink, facing="left", holding_wrench=True, scale=0.93)
            frame = paste_char(frame, anya, 320, 1300)
            frame = paste_char(frame, master, 840, 1300)
            frame = camera.apply(frame, zoom=1.02 + 0.06 * p_ch, focal_point=(520, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«ЧТО С МОЕЙ МАШИНОЙ?!\nГДЕ МОТОР?!»", anchor_x=380, anchor_y=800, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 2: СЧЁТ НА 480 000 РУБЛЕЙ
        # ================================================================
        elif sid == "as2_s1":
            # Master shoving rusty iron into Anya's face
            master = render_master(mood="shady", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", holding_wrench=True, scale=0.95)
            anya = render_anya(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="left", scale=0.92)
            frame = paste_char(frame, master, 300, 1305)
            frame = paste_char(frame, anya, 820, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Молитесь, что доехали! Двигатель стуканул!»", anchor_x=350, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "as2_s2":
            # Director's office: Director slams invoice 480 250 ₽ onto desk
            dir_boss = render_director(mood="smug", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", holding_bill=True, scale=0.95)
            anya = render_anya(mood="shocked", mouth_state="closed", gesture="relax", blink=False, facing="right", scale=0.92)
            frame = paste_char(frame, anya, 270, 1305)
            frame = paste_char(frame, dir_boss, 840, 1305)
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            frame = draw_animated_stamp(frame, "СЧЁТ: 480 250 ₽!", t_local - 0.20, center=(540, 560))

        elif sid == "as2_s3":
            # Director leans forward: "Pay or take in bags!"
            dir_boss = render_director(mood="shady", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", holding_bill=True, scale=0.95)
            anya = render_anya(mood="alert", mouth_state="closed", gesture="point_right", blink=blink, facing="right", scale=0.92)
            frame = paste_char(frame, anya, 280, 1305)
            frame = paste_char(frame, dir_boss, 830, 1305)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Плати 480к, или забирай\nмотор в мешках!»", anchor_x=790, anchor_y=790, align="right", pop_scale=pop_late)

        elif sid == "as2_s4":
            # Locked service gates! Anya in tears outside
            anya = render_anya(mood="sad", mouth_state=mouth, gesture="hands_on_head", blink=blink, facing="right", scale=0.93)
            frame = paste_char(frame, anya, 350, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "ВОРОТА ЗАПЕРТЫ!", t_local - 0.15, center=(540, 520))

        # ================================================================
        # EPISODE 3: УЛИКА НА АВИТО И ТАЙНЫЙ СВИДЕТЕЛЬ
        # ================================================================
        elif sid == "as3_s1":
            # Back alley scrap yard: Anya crying near pile of rusty exhausts
            anya = render_anya(mood="sad", mouth_state=mouth, gesture="relax", blink=blink, facing="right", scale=0.93)
            frame = paste_char(frame, anya, 360, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Что мне делать?!\nМашину не отдают...»", anchor_x=410, anchor_y=810, align="left", pop_scale=pop_late)

        elif sid == "as3_s2":
            # Trainee steps out: "Don't cry, don't pay them!"
            trainee = render_trainee(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.92)
            anya = render_anya(mood="sad", mouth_state="closed", gesture="relax", blink=blink, facing="left", scale=0.92)
            frame = paste_char(frame, trainee, 280, 1305)
            frame = paste_char(frame, anya, 810, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Девушка, тихо! Вас\nразводят — тачка здорова!»", anchor_x=340, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "as3_s3":
            # Glowing Avito screen — zoom in on yellow sticker!
            frame = camera.apply(frame, zoom=1.00 + 0.06 * p_ch, focal_point=(540, 960), t=t)
            if t_local > 0.4:
                # Placed cleanly below listing card (y=1230..1350) so Avito header, photo & sticker are never blocked!
                draw_smart_bubble(frame, "«Смотрите! Ваш катализатор\nна Авито за 85 000 ₽!»", anchor_x=540, anchor_y=1380, align="center", pop_scale=pop_late)

        elif sid == "as3_s4":
            # Trainee hands USB flash drive with secret recording to determined Anya!
            trainee = render_trainee(mood="confident", mouth_state="closed", gesture="point_right", blink=blink, facing="right", holding_usb=True, scale=0.92)
            anya = render_anya(mood="confident", mouth_state=mouth, gesture="hold_phone", blink=blink, facing="left", scale=0.93)
            frame = paste_char(frame, trainee, 290, 1305)
            frame = paste_char(frame, anya, 810, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Вот видео подмены!\nТеперь пора наказывать!»", anchor_x=340, anchor_y=800, align="left", pop_scale=pop_late)

        # ================================================================
        # EPISODE 4: ОЧНАЯ СТАВКА И ШТУРМ ОБЭП (BETA NEXT-GEN)
        # ================================================================
        elif sid == "as4_s1":
            # Director counting cash: "Did you bring 480k?"
            bob_a = int(math.sin(t * 3.1) * 3)
            bob_d = int(math.sin(t * 2.8 + 1.2) * 3)
            talk_d = int(math.sin(t * 7.5) * 3.5) if mouth != "closed" else 0
            dir_boss = render_director(mood="smug", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", holding_bill=False, scale=0.95)
            anya = render_anya(mood="confident", mouth_state="closed", gesture="relax", blink=blink, facing="right", scale=0.92)
            frame = paste_char(frame, anya, 270, 1305 + bob_a)
            frame = paste_char(frame, dir_boss, 840, 1305 + bob_d + talk_d)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Ну что, принесла 480 тысяч?\nИли тачка в утиль?»", anchor_x=790, anchor_y=790, align="right", pop_scale=pop_late)

        elif sid == "as4_s2":
            # Anya slams phone with voice recorder & Avito sheet on desk
            bob_a = int(math.sin(t * 3.1) * 3)
            bob_d = int(math.sin(t * 2.8 + 1.2) * 3)
            talk_a = int(math.sin(t * 7.5) * 3.5) if mouth != "closed" else 0
            anya = render_anya(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", holding_phone=True, scale=0.94)
            dir_boss = render_director(mood="shocked", mouth_state="closed", gesture="relax", blink=False, facing="left", holding_bill=True, scale=0.94)
            frame = paste_char(frame, anya, 280, 1305 + bob_a + talk_a)
            frame = paste_char(frame, dir_boss, 830, 1305 + bob_d)
            # Director cold sweat beads dripping in shock!
            frame = draw_sweat_drops(frame, 895, 1010, t_local)
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Вы украли мой катализатор\nи вымогаете деньги!»", anchor_x=340, anchor_y=790, align="left", pop_scale=pop_late)

        elif sid == "as4_s3":
            # Director rages: "Who are you gonna complain to?!", Anya smiles
            bob_a = int(math.sin(t * 3.1) * 3)
            # Director shaking with furious rage
            rage_x = int(math.sin(t * 28.0) * 4)
            rage_y = int(math.cos(t * 22.0) * 2)
            talk_d = int(math.sin(t * 9.0) * 4) if mouth != "closed" else 0
            dir_boss = render_director(mood="shady", mouth_state=mouth, gesture="point_right", blink=blink, facing="left", scale=0.95)
            anya = render_anya(mood="smug", mouth_state="closed", gesture="point_right", blink=blink, facing="right", scale=0.92)
            frame = paste_char(frame, anya, 270, 1305 + bob_a)
            frame = paste_char(frame, dir_boss, 840 + rage_x, 1305 + rage_y + talk_d)
            # Cartoon red anger cross 💢 popping over director's head
            frame = draw_anger_mark(frame, 865 + rage_x, 990, scale=1.15)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 980), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«А вы следователям ОБЭП\nэто скажите за дверью!»", anchor_x=340, anchor_y=790, align="left", pop_scale=pop_late)

        elif sid == "as4_s4":
            # Police raid! OBEP Captain storms in with squad
            bob_c = int(math.sin(t * 3.1) * 3)
            bob_d = int(math.sin(t * 2.8 + 1.2) * 3)
            talk_c = int(math.sin(t * 8.0) * 4) if mouth != "closed" else 0
            captain = render_obep_captain(mood="alert", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.95)
            dir_boss = render_director(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="left", holding_bill=False, scale=0.93)
            frame = paste_char(frame, captain, 290, 1305 + bob_c + talk_c)
            frame = paste_char(frame, dir_boss, 840, 1305 + bob_d)
            # Panic sweat on director's forehead
            frame = draw_sweat_drops(frame, 895, 1010, t_local)
            # Explosive door splinter burst particles in first 0.65s!
            frame = draw_door_burst_particles(frame, t_local)
            # Flashing blue & red police lights
            frame = draw_siren_flash(frame, t)
            shake = ((1.0 - t_local / 0.5) ** 1.4) if t_local <= 0.5 else 0.0
            frame = camera.apply(frame, zoom=1.02 + 0.05 * p_ch, focal_point=(540, 1020), shake_intensity=shake, t=t)
            frame = draw_animated_stamp(frame, "ОБЭП! РУКИ НА СТОЛ!", t_local - 0.15, center=(540, 520))
            if t_local > ch_dur - 2.5:
                draw_compact_pill(frame, "СМОТРИ ФИНАЛ: ЧАСТЬ 5 — РАЗВЯЗКА В СЛЕДУЮЩЕЙ СЕРИИ!", y_pos=1620)

        # ================================================================
        # EPISODE 5: РАЗГРОМ РАЗВОДИЛ И 3 ПРАВИЛА
        # ================================================================
        elif sid == "as5_s1":
            # Police search: evidence boxes, director handcuffed
            captain = render_obep_captain(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            master = render_master(mood="shocked", mouth_state="closed", gesture="hands_on_head", blink=False, facing="left", holding_wrench=False, scale=0.92)
            frame = paste_char(frame, captain, 290, 1305)
            frame = paste_char(frame, master, 820, 1305)
            frame = draw_siren_flash(frame, t)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "СТ. 159 УК РФ: АРЕСТ!", t_local - 0.20, center=(540, 520))

        elif sid == "as5_s2":
            # Service lift: Car fully reassembled, honest trainee & captain hand keys to Anya!
            frame = paste_obj(frame, anya_car, 270, 980)
            trainee = render_trainee(mood="confident", mouth_state="closed", gesture="thumbs_up", blink=blink, facing="right", scale=0.91)
            anya = render_anya(mood="confident", mouth_state=mouth, gesture="relax", blink=blink, facing="left", holding_keys=True, scale=0.92)
            frame = paste_char(frame, trainee, 260, 1305)
            frame = paste_char(frame, anya, 830, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.45:
                draw_smart_bubble(frame, "«Все родные детали на месте!\nСчастливого пути!»", anchor_x=320, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "as5_s3":
            # Daylight plaza: Anya next to red car smiling, introducing 3 rules
            frame = paste_obj(frame, anya_car, 380, 990)
            anya = render_anya(mood="confident", mouth_state=mouth, gesture="point_right", blink=blink, facing="right", scale=0.94)
            frame = paste_char(frame, anya, 280, 1300)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            if t_local > 0.4:
                draw_smart_bubble(frame, "«Запомните 3 главных\nправила водителя!»", anchor_x=340, anchor_y=800, align="left", pop_scale=pop_late)

        elif sid == "as5_s4":
            # Finale: Anya gives thumbs up, 3 rules checklist displayed
            frame = paste_obj(frame, anya_car, 380, 990)
            anya = render_anya(mood="confident", mouth_state=mouth, gesture="thumbs_up", blink=blink, facing="right", scale=0.95)
            frame = paste_char(frame, anya, 270, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * p_ch, focal_point=(540, 1020), t=t)
            frame = draw_animated_stamp(frame, "СТ. 32 ЗОЗПП: ЗВОНИ 112!", t_local - 0.15, center=(540, 520))

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
    print(f"[AUTOSERVICE EP{ep_num}] 2. Рендерим анимацию ({ep['title']})...")
    total_frames = int(duration * fps)
    raw_video = work_dir / f"raw_autoservice_ep{ep_num}.mp4"

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

    print(f"[AUTOSERVICE EP{ep_num}] 3. Финальная сборка MP4 (субтитры ASS + аудио)...")
    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
    res = subprocess.run([
        FFMPEG_BIN, "-y",
        "-i", str(raw_video),
        "-i", str(master_audio),
        "-vf", f"ass='{ass_escaped}'",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(output_path),
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        subprocess.run([FFMPEG_BIN, "-y", "-i", str(raw_video), "-i", str(master_audio), "-c:v", "copy", "-c:a", "aac", str(output_path)], check=True)

    print(f"[OK] Серия {ep_num}/5 готова -> {output_path} ({duration:.2f}s, {output_path.stat().st_size / 1024 / 1024:.2f} MB)")
    return output_path


def render_all_autoservice_episodes(speaker: str = "f5", fps: int = 30) -> List[Path]:
    print("=" * 65)
    print("🎬 АВТОСЕРВИС-ЛОВУШКА: СЧЁТ НА 480 000 ₽ ЗА ЗАМЕНУ МАСЛА")
    print(f"   Движок: v3 PRO • Озвучка: {speaker.upper()} • Выход: output/story_autoservice/")
    print("=" * 65)
    shared_bgs = build_autoservice_backgrounds()
    outputs = []
    for ep_num in range(1, 6):
        out = render_autoservice_episode(ep_num, speaker=speaker, fps=fps, shared_bgs=shared_bgs)
        outputs.append(out)
    print("=" * 65)
    print("🎉 ВСЕ 5 СЕРИЙ УСПЕШНО СГЕНЕРИРОВАНЫ В output/story_autoservice/")
    print("=" * 65)
    return outputs


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate 5-part Auto Service Scam animated series.")
    parser.add_argument("--ep", type=int, default=0, help="Episode number (1-5), or 0 for all 5.")
    parser.add_argument("--speaker", type=str, default="f5", help="Voice engine: f5 (GPU) or eugene/aidar")
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("🎬 АВТОСЕРВИС-ЛОВУШКА: СЧЁТ НА 480 000 ₽ ЗА ЗАМЕНУ МАСЛА")
    print(f"   Движок: v3 PRO • Озвучка: {args.speaker.upper()} • Выход: output/story_autoservice/")
    print("=" * 65 + "\n")

    bgs = build_autoservice_backgrounds()
    episodes = [args.ep] if args.ep in (1, 2, 3, 4, 5) else [1, 2, 3, 4, 5]

    for ep_num in episodes:
        render_autoservice_episode(ep_num=ep_num, speaker=args.speaker, shared_bgs=bgs)

    print("\n" + "=" * 65)
    print("🎉 ВСЕ СЕРИИ УСПЕШНО СГЕНЕРИРОВАНЫ В output/story_autoservice/")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
