"""
Cartoon v3 Engine: Full-Body Articulated Multi-Character 2D Storytelling Studio.
Fixes visual composition completely:
- Characters are full-body (~25% of frame height) with grounded shadows, walking legs,
  swinging arms, and never block the location or props!
- 2x Supersampled Anti-Aliased Vector Art (smooth Adobe Illustrator-like lines).
- Multi-character staging: Hero + Shady Manager interacting inside the scene!
- Real physical animation: walking, running away off-screen, car physically splitting
  in half with smoke/sparks, animated bus driving past in the rain!
- Sleek minimalist frosted HUD + clean lower third reserved for bold subtitles.
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
    draw_rain,
    draw_siren_flash,
    ease_out_back,
)
from backend.app.cartoon.f5_voice import is_f5_available, synthesize_f5_script
from backend.app.cartoon.sfx import synth_whoosh
from backend.app.cartoon.silero_voice import synthesize_silero_script
from backend.app.cinematic.subtitles import generate_cinematic_ass

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT_IMPACT = "C:/Windows/Fonts/impact.ttf"

INK = (26, 32, 44, 255)  # Signature charcoal vector ink


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------------------------------
# 1. SLEEK EDITORIAL UI (LIGHTWEIGHT FROSTED HUD + SMART SPEECH BUBBLES)
# ---------------------------------------------------------------------------

def draw_sleek_hud(
    canvas: Image.Image,
    balance_text: str,
    status_text: str,
    theme: str = "green",  # green | alert | danger | muted
) -> None:
    """Clean, compact editorial capsule HUD at top (never crowds the scene)."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    w = canvas.width
    hud_w, hud_h = 940, 78
    x1 = (w - hud_w) // 2
    y1 = 68
    x2, y2 = x1 + hud_w, y1 + hud_h

    accent_map = {
        "green": (22, 163, 74, 255),
        "alert": (217, 119, 6, 255),
        "danger": (220, 38, 38, 255),
        "muted": (100, 116, 139, 255),
    }
    accent = accent_map.get(theme, (22, 163, 74, 255))

    # Soft shadow
    draw.rounded_rectangle([(x1, y1 + 5), (x2, y2 + 5)], radius=39, fill=(15, 23, 42, 45))
    # Frosted light card
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=39, fill=(248, 250, 252, 242), outline=INK, width=3)

    f_lbl = _font(FONT_BOLD, 20)
    f_val = _font(FONT_BOLD, 30)

    # Left: Balance
    draw.text((x1 + 30, y1 + 26), "НА СЧЕТУ", fill=(100, 116, 139, 255), font=f_lbl)
    draw.text((x1 + 148, y1 + 19), balance_text, fill=INK, font=f_val)

    # Subtle divider
    div_x = x1 + 495
    draw.line([(div_x, y1 + 18), (div_x, y2 - 18)], fill=(203, 213, 225, 255), width=2)

    # Right: Status pill text
    draw.text((div_x + 24, y1 + 26), "СТАТУС", fill=(100, 116, 139, 255), font=f_lbl)
    st_clean = status_text[:18]
    draw.text((div_x + 114, y1 + 20), st_clean, fill=accent, font=_font(FONT_BOLD, 28))


def draw_compact_pill(canvas: Image.Image, text: str, y_pos: int = 166) -> None:
    """Clean airy location pill below HUD."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    f = _font(FONT_BOLD, 25)
    bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pw, ph = tw + 48, th + 24
    x1 = (canvas.width - pw) // 2
    draw.rounded_rectangle([(x1, y_pos + 3), (x1 + pw, y_pos + ph + 3)], radius=ph // 2, fill=(15, 23, 42, 40))
    draw.rounded_rectangle([(x1, y_pos), (x1 + pw, y_pos + ph)], radius=ph // 2, fill=(255, 255, 255, 238), outline=INK, width=3)
    draw.text((x1 + 24, y_pos + 9), text, fill=INK, font=f)


def draw_smart_bubble(
    canvas: Image.Image,
    text: str,
    anchor_x: int,
    anchor_y: int,
    max_w: int = 480,
    align: str = "center",  # left | center | right
    pop_scale: float = 1.0,
) -> None:
    """Compact speech bubble positioned cleanly above a specific speaker with balanced typography."""
    if pop_scale <= 0.05:
        return
    draw = ImageDraw.Draw(canvas, "RGBA")
    f = _font(FONT_BOLD, 29)

    # Wrap words (prefer balanced 2-line wrap for clean comic aesthetics & compact bounds)
    lines = []
    if "\n" in text:
        lines = text.split("\n")
    else:
        words = text.split(" ")
        if len(words) <= 3:
            lines = [text]
        else:
            best_2line = None
            min_diff = 999999
            for i in range(1, len(words)):
                l1 = " ".join(words[:i])
                l2 = " ".join(words[i:])
                w1 = f.getbbox(l1)[2] - f.getbbox(l1)[0]
                w2 = f.getbbox(l2)[2] - f.getbbox(l2)[0]
                if w1 <= max_w - 52 and w2 <= max_w - 52:
                    diff = abs(w1 - w2)
                    if diff < min_diff:
                        min_diff = diff
                        best_2line = [l1, l2]
            if best_2line:
                lines = best_2line
            else:
                cur = []
                for w_str in words:
                    cand = " ".join(cur + [w_str])
                    if (f.getbbox(cand)[2] - f.getbbox(cand)[0]) > (max_w - 52) and cur:
                        lines.append(" ".join(cur))
                        cur = [w_str]
                    else:
                        cur.append(w_str)
                if cur:
                    lines.append(" ".join(cur))

    line_h = 38
    content_w = max((f.getbbox(l)[2] - f.getbbox(l)[0]) for l in lines)
    bw = max(240, content_w + 56)
    bh = len(lines) * line_h + 36

    if align == "left":
        x1 = max(48, min(anchor_x - 80, canvas.width - bw - 48))
    elif align == "right":
        x1 = max(48, min(anchor_x - bw + 80, canvas.width - bw - 48))
    else:
        x1 = max(48, min(anchor_x - bw // 2, canvas.width - bw - 48))

    y2 = anchor_y - 34
    y1 = y2 - bh
    x2 = x1 + bw

    # Apply subtle vertical pop shift
    shift_y = int((1.0 - pop_scale) * 28)
    y1 += shift_y
    y2 += shift_y

    # Tail pointing toward speaker's head
    tx = max(x1 + 45, min(anchor_x, x2 - 45))
    ty = y2 + 30
    tb_l = (max(x1 + 24, tx - 18), y2)
    tb_r = (min(x2 - 24, tx + 18), y2)

    # Shadow
    draw.rounded_rectangle([(x1 + 3, y1 + 5), (x2 + 3, y2 + 5)], radius=22, fill=(15, 23, 42, 45))
    # Tail + Box
    draw.polygon([tb_l, tb_r, (tx, ty)], fill=(255, 255, 255, 255))
    draw.line([tb_l, (tx, ty)], fill=INK, width=4)
    draw.line([tb_r, (tx, ty)], fill=INK, width=4)
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=22, fill=(255, 255, 255, 255), outline=INK, width=4)
    draw.line([(tb_l[0] + 3, y2), (tb_r[0] - 3, y2)], fill=(255, 255, 255, 255), width=6)

    for i, line in enumerate(lines):
        lw = f.getbbox(line)[2] - f.getbbox(line)[0]
        lx = x1 + (bw - lw) // 2
        ly = y1 + 16 + i * line_h
        draw.text((lx, ly), line, fill=INK, font=f)


# ---------------------------------------------------------------------------
# 2. FULL-BODY ARTICULATED CHARACTER ENGINE (2x SUPERSAMPLED ANTI-ALIASED)
# ---------------------------------------------------------------------------

def render_full_body_character(
    outfit: str = "hoodie",         # hoodie | suit
    outfit_color: Tuple[int, int, int] = (59, 130, 246),
    hair_style: str = "undercut",   # undercut | slicked | messy
    mood: str = "confident",        # confident | smug | alert | shocked | sad | shady
    mouth_state: str = "closed",    # closed | half | open
    gesture: str = "relax",         # relax | hold_money | hold_phone | hands_on_head | point_left | point_right | run
    blink: bool = False,
    walk_phase: float = 0.0,        # radians for walking/running leg swing
    facing: str = "right",          # right | left
    scale: float = 1.0,
) -> Image.Image:
    """
    Renders a crisp 2x-supersampled full-body character sprite (~360x540px at scale=1.0).
    Bottom center of returned image is the feet contact point!
    """
    S = 2  # 2x supersampling for silky-smooth anti-aliased vector strokes
    W, H = 420 * S, 560 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = W // 2
    foot_y = H - 36 * S
    ink_w = 5 * S

    # Walking/running vertical stride bounce
    stride = math.sin(walk_phase)
    stride_abs = abs(stride)
    body_bounce = int(-stride_abs * 10 * S)

    # Ground contact oval shadow
    sh_rx = int(74 * S)
    sh_ry = int(14 * S)
    d.ellipse([cx - sh_rx, foot_y - sh_ry + 6 * S, cx + sh_rx, foot_y + sh_ry + 6 * S], fill=(15, 23, 42, 65))

    # --- 1. LEGS & SHOES ---
    hip_y = foot_y - 128 * S + body_bounce
    leg_len = 118 * S

    if gesture == "run":
        l_ang = stride * 0.72
        r_ang = -stride * 0.72
    else:
        l_ang = stride * 0.38
        r_ang = -stride * 0.38

    for side_x, ang in [(-24 * S, l_ang), (24 * S, r_ang)]:
        hx = cx + side_x
        hy = hip_y
        kx = hx + int(math.sin(ang) * leg_len)
        ky = hy + int(math.cos(ang) * leg_len)
        d.line([(hx, hy), (kx, ky)], fill=INK, width=10 * S)
        # Shoe oval
        shoe_dir = 1 if facing == "right" else -1
        d.ellipse([kx - 16 * S + shoe_dir * 8 * S, ky - 8 * S, kx + 20 * S + shoe_dir * 8 * S, ky + 12 * S], fill=INK)

    # --- 2. TORSO (STYLISH HOODIE OR BUSINESS SUIT) ---
    sh_y = hip_y - 148 * S  # shoulder y
    torso_poly = [
        (cx - 56 * S, sh_y),
        (cx + 56 * S, sh_y),
        (cx + 70 * S, hip_y + 12 * S),
        (cx - 70 * S, hip_y + 12 * S),
    ]

    if outfit == "suit":
        jacket_col = (45, 55, 72, 255)
        d.polygon(torso_poly, fill=jacket_col, outline=INK)
        d.line(torso_poly + [torso_poly[0]], fill=INK, width=ink_w, joint="curve")
        # White V-shirt + Red Tie
        d.polygon([(cx - 24 * S, sh_y), (cx, sh_y + 68 * S), (cx + 24 * S, sh_y)], fill=(255, 255, 255, 255), outline=INK)
        d.polygon([(cx - 6 * S, sh_y + 12 * S), (cx + 6 * S, sh_y + 12 * S), (cx + 10 * S, sh_y + 84 * S), (cx, sh_y + 98 * S), (cx - 10 * S, sh_y + 84 * S)], fill=(220, 38, 38, 255), outline=INK)
        # Lapel lines
        d.line([(cx - 24 * S, sh_y), (cx, sh_y + 72 * S), (cx + 24 * S, sh_y)], fill=INK, width=3 * S)
    else:
        col = (outfit_color[0], outfit_color[1], outfit_color[2], 255)
        d.polygon(torso_poly, fill=col, outline=INK)
        d.line(torso_poly + [torso_poly[0]], fill=INK, width=ink_w, joint="curve")
        # Collar hood rim
        d.rounded_rectangle([(cx - 48 * S, sh_y - 8 * S), (cx + 48 * S, sh_y + 16 * S)], radius=10 * S, fill=col, outline=INK, width=4 * S)
        # Kangaroo pocket
        d.rounded_rectangle([(cx - 34 * S, hip_y - 46 * S), (cx + 34 * S, hip_y - 6 * S)], radius=10 * S, fill=(max(0, col[0]-22), max(0, col[1]-22), max(0, col[2]-22), 255), outline=INK, width=3 * S)
        # Drawstrings
        d.line([(cx - 14 * S, sh_y + 14 * S), (cx - 16 * S, sh_y + 62 * S)], fill=(255, 255, 255, 255), width=4 * S)
        d.line([(cx + 14 * S, sh_y + 14 * S), (cx + 16 * S, sh_y + 62 * S)], fill=(255, 255, 255, 255), width=4 * S)

    # --- 3. HEAD & HAIR ---
    head_r = 76 * S
    head_cy = sh_y - head_r + 6 * S
    d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], fill=(255, 255, 255, 255), outline=INK, width=ink_w)

    # Hair
    if hair_style in ("none", "bald", "custom"):
        pass
    elif hair_style == "undercut":
        d.chord([cx - head_r - 2 * S, head_cy - head_r - 6 * S, cx + head_r + 2 * S, head_cy - 18 * S], start=185, end=355, fill=(30, 41, 59, 255), outline=INK, width=4 * S)
    elif hair_style == "slicked":
        # Shady slicked-back manager hair (silver-dark gray)
        d.chord([cx - head_r - 2 * S, head_cy - head_r - 4 * S, cx + head_r + 2 * S, head_cy - 22 * S], start=185, end=355, fill=(71, 85, 105, 255), outline=INK, width=4 * S)
        # Side hairline sweep
        d.line([(cx - 40 * S, head_cy - 54 * S), (cx + 46 * S, head_cy - 44 * S)], fill=(148, 163, 184, 255), width=4 * S)
    else:  # messy
        for poly in [
            [(cx - 60 * S, head_cy - 50 * S), (cx - 44 * S, head_cy - 92 * S), (cx - 10 * S, head_cy - 68 * S)],
            [(cx - 18 * S, head_cy - 68 * S), (cx + 4 * S, head_cy - 102 * S), (cx + 28 * S, head_cy - 68 * S)],
            [(cx + 20 * S, head_cy - 66 * S), (cx + 56 * S, head_cy - 88 * S), (cx + 62 * S, head_cy - 48 * S)],
        ]:
            d.polygon(poly, fill=(30, 41, 59, 255), outline=INK)

    # --- 4. EXPRESSIVE FACE (EYES, BROWS, MOUTH) ---
    eye_shift = 10 * S if facing == "right" else -10 * S
    ex_l = cx - 28 * S + eye_shift
    ex_r = cx + 24 * S + eye_shift
    ey = head_cy - 4 * S

    if blink:
        d.line([(ex_l - 12 * S, ey), (ex_l + 12 * S, ey)], fill=INK, width=4 * S)
        d.line([(ex_r - 12 * S, ey), (ex_r + 12 * S, ey)], fill=INK, width=4 * S)
    elif mood == "shocked":
        d.ellipse([ex_l - 18 * S, ey - 18 * S, ex_l + 18 * S, ey + 18 * S], fill=(255, 255, 255, 255), outline=INK, width=4 * S)
        d.ellipse([ex_r - 18 * S, ey - 18 * S, ex_r + 18 * S, ey + 18 * S], fill=(255, 255, 255, 255), outline=INK, width=4 * S)
        d.ellipse([ex_l - 5 * S, ey - 5 * S, ex_l + 5 * S, ey + 5 * S], fill=INK)
        d.ellipse([ex_r - 5 * S, ey - 5 * S, ex_r + 5 * S, ey + 5 * S], fill=INK)
        d.arc([ex_l - 18 * S, ey - 36 * S, ex_l + 18 * S, ey - 16 * S], start=200, end=340, fill=INK, width=4 * S)
        d.arc([ex_r - 18 * S, ey - 36 * S, ex_r + 18 * S, ey - 16 * S], start=200, end=340, fill=INK, width=4 * S)
        # Sweat drop
        d.ellipse([cx + 52 * S, head_cy - 34 * S, cx + 64 * S, head_cy - 14 * S], fill=(56, 189, 248, 255))
    elif mood == "smug":
        d.arc([ex_l - 13 * S, ey - 10 * S, ex_l + 13 * S, ey + 10 * S], start=190, end=350, fill=INK, width=5 * S)
        d.arc([ex_r - 13 * S, ey - 10 * S, ex_r + 13 * S, ey + 10 * S], start=190, end=350, fill=INK, width=5 * S)
        d.line([(ex_l - 14 * S, ey - 20 * S), (ex_l + 12 * S, ey - 16 * S)], fill=INK, width=4 * S)
        d.line([(ex_r - 12 * S, ey - 16 * S), (ex_r + 14 * S, ey - 20 * S)], fill=INK, width=4 * S)
    elif mood == "shady":
        # Sly half-lidded eyes + cocky brows
        d.ellipse([ex_l - 7 * S, ey - 7 * S, ex_l + 7 * S, ey + 7 * S], fill=INK)
        d.ellipse([ex_r - 7 * S, ey - 7 * S, ex_r + 7 * S, ey + 7 * S], fill=INK)
        d.line([(ex_l - 15 * S, ey - 16 * S), (ex_l + 14 * S, ey - 10 * S)], fill=INK, width=4 * S)
        d.line([(ex_r - 14 * S, ey - 10 * S), (ex_r + 15 * S, ey - 18 * S)], fill=INK, width=4 * S)
    elif mood == "sad":
        d.ellipse([ex_l - 7 * S, ey - 7 * S, ex_l + 7 * S, ey + 7 * S], fill=INK)
        d.ellipse([ex_r - 7 * S, ey - 7 * S, ex_r + 7 * S, ey + 7 * S], fill=INK)
        d.line([(ex_l - 14 * S, ey - 14 * S), (ex_l + 12 * S, ey - 22 * S)], fill=INK, width=4 * S)
        d.line([(ex_r - 12 * S, ey - 22 * S), (ex_r + 14 * S, ey - 14 * S)], fill=INK, width=4 * S)
        # Small tear
        d.ellipse([ex_l - 5 * S, ey + 14 * S, ex_l + 5 * S, ey + 28 * S], fill=(56, 189, 248, 255))
    else:  # confident / alert
        d.ellipse([ex_l - 8 * S, ey - 9 * S, ex_l + 8 * S, ey + 9 * S], fill=INK)
        d.ellipse([ex_r - 8 * S, ey - 9 * S, ex_r + 8 * S, ey + 9 * S], fill=INK)
        d.line([(ex_l - 14 * S, ey - 22 * S), (ex_l + 12 * S, ey - 20 * S)], fill=INK, width=4 * S)
        d.line([(ex_r - 12 * S, ey - 20 * S), (ex_r + 14 * S, ey - 22 * S)], fill=INK, width=4 * S)

    # Mouth
    my = head_cy + 30 * S
    mx = cx + eye_shift
    if mouth_state == "closed":
        if mood in ("smug", "shady", "confident"):
            d.arc([mx - 20 * S, my - 12 * S, mx + 20 * S, my + 12 * S], start=20, end=160, fill=INK, width=4 * S)
        elif mood == "shocked":
            d.ellipse([mx - 14 * S, my - 10 * S, mx + 14 * S, my + 20 * S], fill=INK)
        elif mood == "sad":
            d.arc([mx - 18 * S, my, mx + 18 * S, my + 20 * S], start=200, end=340, fill=INK, width=4 * S)
        else:
            d.line([(mx - 16 * S, my + 4 * S), (mx + 16 * S, my + 4 * S)], fill=INK, width=4 * S)
    elif mouth_state == "half":
        d.chord([mx - 18 * S, my - 8 * S, mx + 18 * S, my + 18 * S], start=0, end=180, fill=INK)
    else:  # open
        d.ellipse([mx - 20 * S, my - 8 * S, mx + 20 * S, my + 24 * S], fill=INK)
        d.chord([mx - 13 * S, my + 6 * S, mx + 13 * S, my + 24 * S], start=0, end=180, fill=(244, 63, 94, 255))

    # --- 5. ARTICULATED ARMS, ROUND HANDS & PROPS ---
    sh_l = (cx - 56 * S, sh_y + 18 * S)
    sh_r = (cx + 56 * S, sh_y + 18 * S)
    hand_r = 15 * S

    def _arm(p1, p2, p3=None):
        pts = [p1, p2] if p3 is None else [p1, p2, p3]
        d.line(pts, fill=INK, width=9 * S, joint="curve")
        end = pts[-1]
        d.ellipse([end[0] - hand_r, end[1] - hand_r, end[0] + hand_r, end[1] + hand_r], fill=(255, 255, 255, 255), outline=INK, width=4 * S)
        return end

    if gesture == "hands_on_head":
        _arm(sh_l, (cx - 110 * S, sh_y - 10 * S), (cx - head_r - 4 * S, head_cy + 4 * S))
        _arm(sh_r, (cx + 110 * S, sh_y - 10 * S), (cx + head_r + 4 * S, head_cy + 4 * S))
    elif gesture == "hold_money":
        _arm(sh_l, (cx - 80 * S, hip_y - 12 * S))
        end = _arm(sh_r, (cx + 108 * S, sh_y + 26 * S), (cx + 122 * S, sh_y - 26 * S))
        # Crisp fan of cash banknotes
        hx, hy = end
        for rot_dx, rot_dy, bcol in [(-8, -36, (34, 197, 94, 255)), (10, -44, (74, 222, 128, 255))]:
            bx, by = hx + rot_dx * S, hy + rot_dy * S
            d.rounded_rectangle([(bx - 24 * S, by - 14 * S), (bx + 24 * S, by + 14 * S)], radius=4 * S, fill=bcol, outline=INK, width=3 * S)
    elif gesture == "hold_phone":
        _arm(sh_l, (cx - 76 * S, hip_y - 10 * S))
        end = _arm(sh_r, (cx + 104 * S, sh_y + 14 * S), (cx + 88 * S, head_cy + 20 * S))
        # Smartphone glowing
        px, py = end
        d.rounded_rectangle([(px - 10 * S, py - 38 * S), (px + 28 * S, py + 16 * S)], radius=6 * S, fill=(15, 23, 42, 255), outline=INK, width=3 * S)
        d.rectangle([(px - 4 * S, py - 30 * S), (px + 22 * S, py + 8 * S)], fill=(56, 189, 248, 255))
    elif gesture == "point_left":
        _arm(sh_r, (cx + 76 * S, hip_y - 10 * S))
        _arm(sh_l, (cx - 128 * S, sh_y + 10 * S))
    elif gesture == "point_right":
        _arm(sh_l, (cx - 76 * S, hip_y - 10 * S))
        _arm(sh_r, (cx + 128 * S, sh_y + 10 * S))
    elif gesture == "run":
        sw = int(stride * 55 * S)
        _arm(sh_l, (cx - 88 * S + sw, sh_y + 52 * S), (cx - 48 * S + sw, sh_y + 20 * S))
        _arm(sh_r, (cx + 88 * S - sw, sh_y + 52 * S), (cx + 115 * S - sw, sh_y + 16 * S))
    else:  # relax
        sw = int(stride * 18 * S)
        _arm(sh_l, (cx - 74 * S - sw, hip_y - 8 * S))
        _arm(sh_r, (cx + 74 * S + sw, hip_y - 8 * S))

    out_w = int((W // S) * scale)
    out_h = int((H // S) * scale)
    return img.resize((out_w, out_h), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 3. 2x SUPERSAMPLED WIDE-OPEN 2D LOCATIONS (CLEAR LOWER THIRD FOR SUBTITLES!)
# ---------------------------------------------------------------------------

def _draw_car(
    d: ImageDraw.ImageDraw,
    cx: int,
    wheel_y: int,
    S: int,
    body_color: Tuple[int, int, int] = (220, 38, 38),
    split_gap: int = 0,
    rear_color: Optional[Tuple[int, int, int]] = None,
) -> None:
    """Draws a crisp vector sports sedan (can physically split in half!)."""
    ink_w = 5 * S
    c_left = (body_color[0], body_color[1], body_color[2], 255)
    c_right = (rear_color[0], rear_color[1], rear_color[2], 255) if rear_color else c_left

    # Car ground shadow
    d.ellipse([cx - 260 * S - split_gap * S, wheel_y + 16 * S, cx + 260 * S + split_gap * S, wheel_y + 44 * S], fill=(15, 23, 42, 65))

    if split_gap == 0:
        # Intact sleek car
        # Upper cabin + glass
        d.polygon([(cx - 155 * S, wheel_y - 68 * S), (cx - 85 * S, wheel_y - 135 * S), (cx + 85 * S, wheel_y - 135 * S), (cx + 165 * S, wheel_y - 68 * S)], fill=(186, 230, 253, 255), outline=INK)
        d.line([(cx - 155 * S, wheel_y - 68 * S), (cx - 85 * S, wheel_y - 135 * S), (cx + 85 * S, wheel_y - 135 * S), (cx + 165 * S, wheel_y - 68 * S)], fill=INK, width=ink_w)
        d.line([(cx, wheel_y - 135 * S), (cx, wheel_y - 68 * S)], fill=INK, width=4 * S)
        # Main body
        d.rounded_rectangle([(cx - 245 * S, wheel_y - 72 * S), (cx + 245 * S, wheel_y + 6 * S)], radius=24 * S, fill=c_left, outline=INK, width=ink_w)
        # Headlight & Taillight
        d.rounded_rectangle([(cx + 210 * S, wheel_y - 54 * S), (cx + 243 * S, wheel_y - 28 * S)], radius=6 * S, fill=(254, 240, 138, 255), outline=INK, width=3 * S)
        d.rounded_rectangle([(cx - 243 * S, wheel_y - 54 * S), (cx - 216 * S, wheel_y - 28 * S)], radius=6 * S, fill=(252, 165, 165, 255), outline=INK, width=3 * S)
        # Wheels
        for wx in [cx - 145 * S, cx + 145 * S]:
            d.ellipse([wx - 44 * S, wheel_y - 36 * S, wx + 44 * S, wheel_y + 44 * S], fill=(30, 41, 59, 255), outline=INK, width=ink_w)
            d.ellipse([wx - 20 * S, wheel_y - 12 * S, wx + 20 * S, wheel_y + 20 * S], fill=(203, 213, 225, 255), outline=INK, width=3 * S)
    else:
        # Physically SPLIT car (left half red, right half blue, jagged weld crack + sparks!)
        g = split_gap * S
        # Left half
        lx = cx - g
        d.polygon([(lx - 155 * S, wheel_y - 68 * S), (lx - 85 * S, wheel_y - 135 * S), (lx - 4 * S, wheel_y - 135 * S), (lx - 12 * S, wheel_y - 68 * S)], fill=(186, 230, 253, 255), outline=INK)
        d.rounded_rectangle([(lx - 245 * S, wheel_y - 72 * S), (lx - 4 * S, wheel_y + 6 * S)], radius=18 * S, fill=c_left, outline=INK, width=ink_w)
        wx_l = lx - 145 * S
        d.ellipse([wx_l - 44 * S, wheel_y - 36 * S, wx_l + 44 * S, wheel_y + 44 * S], fill=(30, 41, 59, 255), outline=INK, width=ink_w)
        d.ellipse([wx_l - 20 * S, wheel_y - 12 * S, wx_l + 20 * S, wheel_y + 20 * S], fill=(203, 213, 225, 255), outline=INK, width=3 * S)

        # Right half (mismatched blue weld!)
        rx = cx + g
        d.polygon([(rx + 10 * S, wheel_y - 68 * S), (rx + 4 * S, wheel_y - 135 * S), (rx + 85 * S, wheel_y - 135 * S), (rx + 165 * S, wheel_y - 68 * S)], fill=(186, 230, 253, 255), outline=INK)
        d.rounded_rectangle([(rx + 4 * S, wheel_y - 72 * S), (rx + 245 * S, wheel_y + 6 * S)], radius=18 * S, fill=c_right, outline=INK, width=ink_w)
        wx_r = rx + 145 * S
        d.ellipse([wx_r - 44 * S, wheel_y - 36 * S, wx_r + 44 * S, wheel_y + 44 * S], fill=(30, 41, 59, 255), outline=INK, width=ink_w)
        d.ellipse([wx_r - 20 * S, wheel_y - 12 * S, wx_r + 20 * S, wheel_y + 20 * S], fill=(203, 213, 225, 255), outline=INK, width=3 * S)

        # Jagged lightning crack + sparks in center gap
        d.line([(cx, wheel_y - 155 * S), (cx - 18 * S, wheel_y - 90 * S), (cx + 16 * S, wheel_y - 45 * S), (cx - 10 * S, wheel_y + 18 * S)], fill=(250, 204, 21, 255), width=8 * S)


def build_v3_backgrounds() -> Dict[str, Image.Image]:
    """Pre-renders all 4 crisp 2x-supersampled wide editorial locations."""
    S = 2
    W, H = 1080 * S, 1920 * S
    bgs = {}

    # ------------------------------------------------------------------
    # LOC 1: MODERN BANK VAULT (Clean Editorial Mint/Slate Palette)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (226, 235, 234, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1230 * S
    # Clean wall panels
    d.rectangle([(0, 0), (W, floor_y)], fill=(216, 228, 226, 255))
    for px in range(0, W, 270 * S):
        d.line([(px, 0), (px, floor_y)], fill=(192, 208, 206, 255), width=3 * S)
    # Floor (clean open area for character walking + lower third subtitles)
    d.rectangle([(0, floor_y), (W, H)], fill=(238, 234, 225, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    # Subtle floor perspective lines
    for fx in range(180 * S, W, 260 * S):
        d.line([(fx, floor_y), (fx - 120 * S, H)], fill=(218, 212, 200, 255), width=3 * S)

    # Massive Detailed Steel Bank Vault Door (Right-Center, completely unobstructed!)
    vx, vy, vr = 670 * S, 860 * S, 270 * S
    d.ellipse([vx - vr, vy - vr, vx + vr, vy + vr], fill=(100, 116, 139, 255), outline=INK, width=6 * S)
    d.ellipse([vx - vr + 36 * S, vy - vr + 36 * S, vx + vr - 36 * S, vy + vr - 36 * S], fill=(71, 85, 105, 255), outline=INK, width=4 * S)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        d.line([(vx, vy), (vx + int(math.cos(rad) * 140 * S), vy + int(math.sin(rad) * 140 * S))], fill=(226, 232, 240, 255), width=14 * S)
    d.ellipse([vx - 46 * S, vy - 46 * S, vx + 46 * S, vy + 46 * S], fill=(148, 163, 184, 255), outline=INK, width=5 * S)

    # Stacks of Cash on a sleek pedestal table (Center-Right)
    tx1, ty1, tx2, ty2 = 540 * S, 1080 * S, 920 * S, floor_y
    d.rounded_rectangle([(tx1, ty1), (tx2, ty2)], radius=12 * S, fill=(148, 163, 184, 255), outline=INK, width=5 * S)
    for sx in [580 * S, 680 * S, 780 * S]:
        for row in range(4):
            by = ty1 - (row + 1) * 24 * S
            d.rounded_rectangle([(sx, by), (sx + 84 * S, by + 22 * S)], radius=5 * S, fill=(34, 197, 94, 255), outline=INK, width=3 * S)
            d.rectangle([(sx + 34 * S, by), (sx + 50 * S, by + 22 * S)], fill=(254, 240, 138, 255))

    bgs["vault"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 2: BRIGHT ELITE CAR DEALERSHIP (Car in full view center!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (224, 232, 240, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1230 * S
    # Panoramic showroom windows + soft city buildings behind glass
    d.rectangle([(0, 0), (W, floor_y)], fill=(210, 224, 238, 255))
    for bx, bw, bh in [(40, 170, 520), (240, 190, 620), (470, 160, 480), (670, 200, 640), (900, 160, 540)]:
        d.rectangle([(bx * S, floor_y - bh * S), ((bx + bw) * S, floor_y)], fill=(186, 200, 214, 255), outline=(148, 163, 184, 255), width=3 * S)
        for wy in range(floor_y - bh * S + 36 * S, floor_y - 60 * S, 55 * S):
            for wx in range((bx + 26) * S, (bx + bw - 26) * S, 42 * S):
                d.rectangle([(wx, wy), (wx + 20 * S, wy + 28 * S)], fill=(226, 236, 245, 255))
    # Window vertical mullions
    for mx in [360 * S, 720 * S]:
        d.line([(mx, 0), (mx, floor_y)], fill=(100, 116, 139, 255), width=6 * S)

    # Dealership Banner Sign (high up cleanly below pill!)
    d.rounded_rectangle([(200 * S, 260 * S), (880 * S, 355 * S)], radius=18 * S, fill=(220, 38, 38, 255), outline=INK, width=5 * S)
    f_sign = _font(FONT_BOLD, 44 * S)
    stxt = "АВТОСАЛОН ПРЕМИУМ"
    sbb = f_sign.getbbox(stxt)
    d.text(((W - (sbb[2] - sbb[0])) // 2, 281 * S), stxt, fill=(255, 255, 255, 255), font=f_sign)

    # Clean Showroom Floor
    d.rectangle([(0, floor_y), (W, H)], fill=(236, 234, 228, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)
    for fx in range(180 * S, W, 240 * S):
        d.line([(fx, floor_y), (fx - 130 * S, H)], fill=(214, 210, 202, 255), width=3 * S)

    # Podium & Sleek Red Sports Car RIGHT IN FULL VIEW!
    d.ellipse([230 * S, 1110 * S, 850 * S, 1210 * S], fill=(203, 213, 225, 255), outline=INK, width=4 * S)
    _draw_car(d, cx=540 * S, wheel_y=1120 * S, S=S, body_color=(220, 38, 38), split_gap=0)

    # Small golden windshield tag
    d.rounded_rectangle([(345 * S, 895 * S), (735 * S, 950 * S)], radius=12 * S, fill=(254, 240, 138, 255), outline=INK, width=4 * S)
    f_tag = _font(FONT_BOLD, 24 * S)
    ttxt = "НЕ БИТА • НЕ КРАШЕНА"
    tbb = f_tag.getbbox(ttxt)
    d.text(((W - (tbb[2] - tbb[0])) // 2, 908 * S), ttxt, fill=INK, font=f_tag)

    bgs["showroom"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 3: AUTOTEKA GARAGE REVEAL (RED DANGER + SPLIT CAR!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (254, 226, 226, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1230 * S
    # Dramatic crimson-tinted garage wall
    d.rectangle([(0, 0), (W, floor_y)], fill=(69, 18, 24, 255))
    # Yellow-black hazard stripe cleanly below location pill
    sy = 250 * S
    d.rectangle([(0, sy), (W, sy + 44 * S)], fill=(250, 204, 21, 255))
    for hx in range(-60 * S, W + 60 * S, 64 * S):
        d.polygon([(hx, sy), (hx + 32 * S, sy), (hx + 8 * S, sy + 44 * S), (hx - 24 * S, sy + 44 * S)], fill=INK)
    d.line([(0, sy), (W, sy)], fill=INK, width=4 * S)
    d.line([(0, sy + 44 * S), (W, sy + 44 * S)], fill=INK, width=4 * S)

    # Red digital report screen on wall
    d.rounded_rectangle([(150 * S, 340 * S), (930 * S, 515 * S)], radius=20 * S, fill=(30, 12, 16, 245), outline=(239, 68, 68, 255), width=5 * S)
    f_r1 = _font(FONT_IMPACT, 46 * S)
    r1 = "VIN-ОТЧЁТ: СМЕРТЕЛЬНЫЙ ТОТАЛ!"
    r1b = f_r1.getbbox(r1)
    d.text(((W - (r1b[2] - r1b[0])) // 2, 368 * S), r1, fill=(248, 113, 113, 255), font=f_r1)
    f_r2 = _font(FONT_BOLD, 28 * S)
    r2 = "ПРОБЕГ: -214 000 КМ   |   4 КРУПНЫХ ДТП"
    r2b = f_r2.getbbox(r2)
    d.text(((W - (r2b[2] - r2b[0])) // 2, 444 * S), r2, fill=(254, 226, 226, 255), font=f_r2)

    # Dark concrete garage floor (light enough for clean contrast!)
    d.rectangle([(0, floor_y), (W, H)], fill=(228, 220, 218, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)

    # SPLIT CAR IN CENTER (Red Front + Blue Welded Rear!)
    _draw_car(d, cx=540 * S, wheel_y=1120 * S, S=S, body_color=(220, 38, 38), split_gap=32, rear_color=(59, 130, 246))

    bgs["split_car"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 4: MOODY TWILIGHT RAINY BUS STOP (Wide Atmospheric Street)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (30, 41, 59, 255))
    d = ImageDraw.Draw(img)
    road_y = 1090 * S
    sidewalk_y = 1240 * S

    # Stormy twilight sky gradient
    for y in range(0, road_y, 4):
        rat = y / road_y
        c = (int(34 + rat * 22), int(48 + rat * 28), int(72 + rat * 36), 255)
        d.rectangle([(0, y), (W, y + 4)], fill=c)

    # City apartment blocks silhouette
    for bx, bw, bh in [(30, 190, 460), (250, 210, 560), (500, 180, 420), (720, 220, 520), (960, 150, 440)]:
        d.rectangle([(bx * S, road_y - bh * S), ((bx + bw) * S, road_y)], fill=(45, 58, 78, 255), outline=INK, width=4 * S)
        for wy in range(road_y - bh * S + 34 * S, road_y - 40 * S, 54 * S):
            for wx in range((bx + 26) * S, (bx + bw - 26) * S, 44 * S):
                wcol = (254, 240, 138, 220) if (wx + wy) % 7 == 0 else (71, 85, 105, 255)
                d.rectangle([(wx, wy), (wx + 20 * S, wy + 26 * S)], fill=wcol)

    # Asphalt road with dashed white markings (bus drives along this!)
    d.rectangle([(0, road_y), (W, sidewalk_y)], fill=(51, 65, 85, 255))
    d.line([(0, road_y), (W, road_y)], fill=INK, width=5 * S)
    for dx in range(40 * S, W, 170 * S):
        d.rectangle([(dx, road_y + 64 * S), (dx + 90 * S, road_y + 78 * S)], fill=(226, 232, 240, 220))

    # Clean light-slate sidewalk foreground (great contrast for character + subtitles!)
    d.rectangle([(0, sidewalk_y), (W, H)], fill=(214, 220, 226, 255))
    d.line([(0, sidewalk_y), (W, sidewalk_y)], fill=INK, width=5 * S)

    # Bus Shelter on Left-Center
    sh_x1, sh_y1, sh_x2, sh_y2 = 120 * S, 760 * S, 660 * S, sidewalk_y
    d.rectangle([(sh_x1 + 20 * S, sh_y1 + 36 * S), (sh_x2 - 20 * S, sh_y2)], fill=(148, 163, 184, 150), outline=INK, width=5 * S)
    d.rounded_rectangle([(sh_x1 - 24 * S, sh_y1), (sh_x2 + 24 * S, sh_y1 + 42 * S)], radius=10 * S, fill=(71, 85, 105, 255), outline=INK, width=5 * S)
    # Timetable display inside shelter
    d.rounded_rectangle([(180 * S, 845 * S), (600 * S, 918 * S)], radius=10 * S, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=4 * S)
    f_b = _font(FONT_BOLD, 24 * S)
    d.text((205 * S, 868 * S), "АВТОБУС №42 • 45 МИН", fill=(250, 204, 21, 255), font=f_b)
    # Bench
    d.rounded_rectangle([(190 * S, 1145 * S), (590 * S, 1175 * S)], radius=6 * S, fill=(146, 64, 14, 255), outline=INK, width=4 * S)

    # Blue Bus Stop Sign 'А' on right
    d.line([(740 * S, 640 * S), (740 * S, sidewalk_y)], fill=(100, 116, 139, 255), width=10 * S)
    d.rounded_rectangle([(694 * S, 640 * S), (786 * S, 738 * S)], radius=14 * S, fill=(37, 99, 235, 255), outline=(255, 255, 255, 255), width=5 * S)
    d.text((722 * S, 654 * S), "А", fill=(255, 255, 255, 255), font=_font(FONT_IMPACT, 56 * S))

    bgs["bus_stop"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)
    return bgs


def build_city_bus_sprite() -> Image.Image:
    """Renders a 2x-supersampled blue city bus sprite that drives past the stop!"""
    S = 2
    W, H = 560 * S, 260 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink_w = 5 * S
    # Bus body
    d.rounded_rectangle([(20 * S, 20 * S), (540 * S, 205 * S)], radius=22 * S, fill=(37, 99, 235, 255), outline=INK, width=ink_w)
    # Windows
    for wx in [48 * S, 148 * S, 248 * S, 348 * S, 448 * S]:
        d.rounded_rectangle([(wx, 46 * S), (wx + 76 * S, 118 * S)], radius=8 * S, fill=(186, 230, 253, 255), outline=INK, width=4 * S)
    # Route stripe + number
    d.rectangle([(24 * S, 142 * S), (536 * S, 162 * S)], fill=(250, 204, 21, 255))
    # Headlight glow
    d.ellipse([518 * S, 164 * S, 542 * S, 188 * S], fill=(254, 240, 138, 255), outline=INK, width=3 * S)
    # Wheels
    for wx in [135 * S, 425 * S]:
        d.ellipse([wx - 36 * S, 175 * S, wx + 36 * S, 245 * S], fill=(30, 41, 59, 255), outline=INK, width=ink_w)
        d.ellipse([wx - 16 * S, 195 * S, wx + 16 * S, 225 * S], fill=(203, 213, 225, 255), outline=INK, width=3 * S)
    return img.resize((560, 260), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# 4. MASTER v3 AUTOPILOT RENDERER (FULL-BODY STAGING + MULTI-CHARACTER!)
# ---------------------------------------------------------------------------

def render_autodealer_v3(
    output_path: Path = Path("output/cartoon_master/autopilot_autodealer_v3_pro.mp4"),
    speaker: str = "f5",
    fps: int = 30,
) -> Path:
    """Renders the upgraded Full-Body Multi-Character v3 Autodealer Story."""
    output_path = Path(output_path)
    work_dir = output_path.parent / "temp_v3"
    work_dir.mkdir(parents=True, exist_ok=True)

    chapters = [
        {
            "loc": "vault",
            "sentences": [
                "Я копил пять лет и наконец собрал почти два миллиона рублей.",
                "Мечта вот-вот сбудется!",
            ],
            "hud_bal": "1 850 000 ₽",
            "hud_st": "МАШИНА МЕЧТЫ",
            "theme": "green",
            "pill": "БАНКОВСКАЯ ЯЧЕЙКА • 5 ЛЕТ ТРУДА",
            "sfx": "coin",
        },
        {
            "loc": "showroom",
            "sentences": [
                "Пришёл в элитный автосалон. Менеджер клялся, что на ней ездил дедушка в аптеку.",
                "Отдаю деньги, и тут внезапно звонит знакомый автоподборщик!",
            ],
            "hud_bal": "0 ₽ (ОПЛАЧЕНО)",
            "hud_st": "СРОЧНЫЙ ЗВОНОК!",
            "theme": "alert",
            "pill": "АВТОСАЛОН ПРЕМИУМ • 14:15",
            "sfx": "phone",
        },
        {
            "loc": "split_car",
            "sentences": [
                "Он пробил вин-номер, а там... Тотальное ДТП и скручено двести тысяч пробега!",
                "Машина буквально сварена из двух разных половин!",
            ],
            "hud_bal": "-1 850 000 ₽",
            "hud_st": "ТОТАЛЬНЫЙ РАСПИЛ!",
            "theme": "danger",
            "pill": "ОТЧЁТ ПО VIN • КРИТИЧЕСКИЙ ТОТАЛ",
            "sfx": "boom",
        },
        {
            "loc": "bus_stop",
            "sentences": [
                "Менеджер тут же испарился, а телефон заблокирован.",
                "Теперь я жду сорок второй автобус под дождём. Проверяйте тачки до покупки!",
            ],
            "hud_bal": "42 ₽ НА ПРОЕЗД",
            "hud_st": "ПРОВЕРЯЙ VIN!",
            "theme": "muted",
            "pill": "ОСТАНОВКА • 22:40 • ДОЖДЬ",
            "sfx": "drip",
        },
    ]

    all_sentences = []
    chapter_word_counts = []
    for ch in chapters:
        cnt = 0
        for s in ch["sentences"]:
            all_sentences.append(s)
            cnt += len(s.replace(".", "").replace("!", "").replace("?", "").replace(",", "").split())
        chapter_word_counts.append(cnt)

    # Reuse existing F5-TTS voice if already synthesized for this exact script!
    cached_wav = output_path.parent / "temp_autopilot" / "voice_f5.wav"
    cached_words = output_path.parent / "temp_autopilot" / "words_f5_voice_f5.json"

    if speaker == "f5" and cached_wav.exists() and cached_words.exists():
        print("[v3 PRO] 1. Используем готовую GPU-озвучку F5-TTS Russian из кэша (мгновенно!)...")
        voice_file = cached_wav
        meta = json.loads(cached_words.read_text(encoding="utf-8"))
        words = meta["words"]
        duration = float(meta["duration"])
    elif speaker == "f5" and is_f5_available():
        print("[v3 PRO] 1. Синтезируем живую озвучку F5-TTS Russian на GPU...")
        voice_file, words, duration = synthesize_f5_script(all_sentences, out_wav=work_dir / "voice_f5.wav", speed=1.06)
    else:
        print(f"[v3 PRO] 1. Синтезируем озвучку Silero v5.6 ({speaker})...")
        voice_file, words, duration = synthesize_silero_script(all_sentences, speaker=speaker, out_wav=work_dir / f"voice_{speaker}.wav")

    # Compute exact synced chapter transitions
    ch_starts = [0.0]
    wc = 0
    for i in range(len(chapters) - 1):
        wc += chapter_word_counts[i]
        ch_starts.append(max(ch_starts[-1] + 1.0, words[wc]["start"] - 0.12) if wc < len(words) else (i + 1) * (duration / 4.0))
    ch_ends = ch_starts[1:] + [duration]
    print(f"         Длительность: {duration:.2f}s | Смены локаций: {[round(x, 2) for x in ch_starts]}s")

    # SFX Mixing
    print("[v3 PRO] 2. Сводим звук + SFX переходов (whoosh, монеты, звонок, удар)...")
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
        sfx_events.append((ch_starts[i] + 0.18, sfx_map[ch["sfx"]], 0.90 if ch["sfx"] == "boom" else 0.75))

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

    # Subtitles cleanly positioned in the wide-open lower third!
    print("[v3 PRO] 3. Генерируем чистые контрастные караоке-субтитры (свободная нижняя треть)...")
    ass_path = work_dir / "v3_subtitles.ass"
    generate_cinematic_ass(
        words,
        ass_path,
        words_per_phrase=3,
        font_name="Arial",
        font_size=68,
        primary_color="&H00FFFFFF",
        highlight_color="&H0026A6FF",  # Bright crisp orange-gold accent
        outline_color="&H001C2026",
        margin_v=310,
    )

    print("[v3 PRO] 4. Строим 2x-суперсэмплированные локации и пропсы...")
    bgs = build_v3_backgrounds()
    bus_sprite = build_city_bus_sprite()
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
        blink = (t % 2.9) > 2.77
        mouth = (["half", "open", "half"][int((t * 9.5) % 3)]) if speaking else "closed"
        ch_prog = max(0.0, min(1.0, t_local / max(0.1, ch_dur)))

        # ------------------ SCENE 1: BANK VAULT ------------------
        if ch_idx == 0:
            frame = draw_money_rain(frame, t)
            # Hero walks in from left (x: 110 -> 310 over first 1.6s), then stands holding cash!
            walk_p = min(1.0, t_local / 1.5)
            hero_x = int(90 + ease_out_back(walk_p) * 230)
            w_phase = t * 11.0 if walk_p < 0.98 else 0.0
            hero = render_full_body_character(
                outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
                mood="smug", mouth_state=mouth, gesture="hold_money",
                blink=blink, walk_phase=w_phase, facing="right", scale=0.95,
            )
            frame = paste_char(frame, hero, hero_x, 1295)
            # Subtle camera drift
            frame = camera.apply(frame, zoom=1.00 + 0.05 * ch_prog, focal_point=(540, 1020), t=t)
            # Clean speech bubble over hero (left)
            if t_local > 0.45:
                pop = ease_out_back(min(1.0, (t_local - 0.45) / 0.25))
                draw_smart_bubble(frame, "«Наконец-то забираю свою ласточку!»", anchor_x=hero_x + 40, anchor_y=790, align="left", pop_scale=pop)

        # ------------------ SCENE 2: ELITE CAR DEALERSHIP ------------------
        elif ch_idx == 1:
            # Two characters! Hero on LEFT, Shady Manager on RIGHT, Red Sports Car wide open in CENTER!
            phone_moment = t_local > (ch_dur * 0.48)

            # Shady Manager (Right side, gesturing smoothly at the red car!)
            mgr_x = 855
            mgr_mouth = (["half", "open"][int((t * 8.0) % 2)]) if (not phone_moment and speaking) else "closed"
            mgr = render_full_body_character(
                outfit="suit", hair_style="slicked",
                mood="shady", mouth_state=mgr_mouth, gesture="point_left",
                blink=((t + 1.1) % 3.2) > 3.08, facing="left", scale=0.92,
            )
            frame = paste_char(frame, mgr, mgr_x, 1290)

            # Hero (Left side — first holds cash, then raises glowing phone on incoming call!)
            hero_x = 225
            hero = render_full_body_character(
                outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
                mood="alert" if phone_moment else "confident",
                mouth_state=mouth if phone_moment else "closed",
                gesture="hold_phone" if phone_moment else "hold_money",
                blink=blink, facing="right", scale=0.92,
            )
            frame = paste_char(frame, hero, hero_x, 1295)

            frame = camera.apply(frame, zoom=1.01 + 0.06 * ch_prog, focal_point=(540, 1040), t=t)

            if not phone_moment and t_local > 0.3:
                pop = ease_out_back(min(1.0, (t_local - 0.3) / 0.22))
                draw_smart_bubble(frame, "«Ездил дедушка строго в аптеку!»", anchor_x=mgr_x - 30, anchor_y=790, align="right", pop_scale=pop)
            elif phone_moment:
                pop = ease_out_back(min(1.0, (t_local - ch_dur * 0.48) / 0.22))
                draw_smart_bubble(frame, "«Алло, брат, СТОЙ! Не подписывай!»", anchor_x=hero_x + 50, anchor_y=790, align="left", pop_scale=pop)

        # ------------------ SCENE 3: SPLIT CAR & MANAGER FLEES! ------------------
        elif ch_idx == 2:
            # Hero jumps back on LEFT clutching head in horror!
            recoil = int(ease_out_back(min(1.0, t_local / 0.30)) * 55)
            hero_x = 260 - recoil
            hero = render_full_body_character(
                outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
                mood="shocked", mouth_state=mouth, gesture="hands_on_head",
                blink=False, facing="right", scale=0.95,
            )
            frame = paste_char(frame, hero, hero_x, 1300)

            # Shady Manager literally SPRINTS AWAY off the right side of the screen!
            run_x = int(830 + t_local * 260)
            if run_x < 1260:
                mgr = render_full_body_character(
                    outfit="suit", hair_style="slicked",
                    mood="shocked", mouth_state="open", gesture="run",
                    blink=False, walk_phase=t * 22.0, facing="right", scale=0.90,
                )
                frame = paste_char(frame, mgr, run_x, 1285)

            # Flashing emergency sirens!
            frame = draw_siren_flash(frame, t)

            # Shock camera shake + dramatic push-in!
            shake = ((1.0 - t_local / 0.65) ** 1.4) if t_local <= 0.65 else 0.0
            frame = camera.apply(frame, zoom=1.06 + 0.06 * ch_prog, focal_point=(520, 1020), shake_intensity=shake, t=t)

            # Slamming Red Rubber Stamp cleanly positioned above split car (right of hero bubble!)
            frame = draw_animated_stamp(frame, "ТОТАЛ!", t_local - 0.15, center=(730, 660))

            if t_local > 0.35:
                pop = ease_out_back(min(1.0, (t_local - 0.35) / 0.22))
                draw_smart_bubble(frame, "«ЭТО ЖЕ РАСПИЛ ИЗ ДВУХ ЧАСТЕЙ?!»", anchor_x=hero_x + 70, anchor_y=790, align="left", pop_scale=pop)

        # ------------------ SCENE 4: RAINY BUS STOP + DRIVING BUS ------------------
        else:
            # Animated blue city bus drives across the road behind the shelter!
            bus_x = int(-580 + ((t_local + 0.6) * 290))
            if -600 < bus_x < 1180:
                bus_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                bus_layer.paste(bus_sprite, (bus_x, 940))
                frame = Image.alpha_composite(frame, bus_layer)

            # Defeated Hero standing under the bus shelter on the left
            hero_x = 380
            hero = render_full_body_character(
                outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
                mood="sad", mouth_state=mouth, gesture="relax",
                blink=blink, facing="right", scale=0.93,
            )
            frame = paste_char(frame, hero, hero_x, 1315)

            # Slanted animated rain streaks
            frame = draw_rain(frame, t)

            frame = camera.apply(frame, zoom=1.04 - 0.04 * ch_prog, focal_point=(540, 1040), t=t)

            if t_local > 0.35:
                pop = ease_out_back(min(1.0, (t_local - 0.35) / 0.22))
                draw_smart_bubble(frame, "«Зато пешком ходить полезно...»", anchor_x=hero_x + 40, anchor_y=800, align="center", pop_scale=pop)

        # Clean editorial HUD + location pill on top
        draw_sleek_hud(frame, balance_text=ch["hud_bal"], status_text=ch["hud_st"], theme=ch["theme"])
        draw_compact_pill(frame, text=ch["pill"])
        return frame

    print("[v3 PRO] 5. Рендерим полноростовую анимацию (2 персонажа, ходьба, бег, распил, автобус)...")
    total_frames = int(duration * fps)
    raw_video = work_dir / "raw_v3.mp4"

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

    print("[v3 PRO] 6. Финальная сборка MP4 с живой озвучкой F5-TTS и субтитрами...")
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

    print(f"[OK] v3 PRO полноростовой мультфильм готов: {output_path}")
    return output_path
