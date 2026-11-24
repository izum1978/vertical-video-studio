"""
Cartoon Motion & Particle Effects Engine.
Adds kinetic energy to every frame:
- Floating & falling cash banknotes ('money')
- Atmospheric slanted raindrops ('rain')
- Emergency red/blue flashing side lights ('sirens')
- Comic/Anime radial shock speedlines ('impact_lines')
- Animated slamming rubber stamp ('stamp')
- Fast Whip-Pan / Slide transitions between locations
- Spring easing functions for bouncy character entrances & bubble pop-ins
"""

import math
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

FONT_IMPACT = "C:/Windows/Fonts/impact.ttf"


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_IMPACT, size)
    except Exception:
        return ImageFont.load_default()


def ease_out_back(x: float) -> float:
    """Springy overshoot easing (0.0 -> 1.0) for lively cartoon pop-ins."""
    x = max(0.0, min(1.0, x))
    c1 = 1.70158
    c3 = c1 + 1.0
    return 1.0 + c3 * ((x - 1.0) ** 3) + c1 * ((x - 1.0) ** 2)


def ease_in_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 4 * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2


def draw_money_rain(frame: Image.Image, t: float) -> Image.Image:
    """Draws animated falling/swaying green banknotes."""
    w, h = frame.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 14 deterministic banknotes with different speeds, phases, and sizes
    for i in range(14):
        seed = i * 97.3
        speed = 210 + (i % 5) * 55
        start_y = (i * 157) % (h + 200)
        y = ((start_y + t * speed) % (h + 200)) - 100
        base_x = (i * 83 + 50) % (w - 100)
        x = base_x + math.sin(t * 2.5 + seed) * 55
        angle = math.sin(t * 3.0 + seed) * 0.6

        bw, bh = 68, 34
        # Rotated rectangle corners
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        pts = []
        for dx, dy in [(-bw / 2, -bh / 2), (bw / 2, -bh / 2), (bw / 2, bh / 2), (-bw / 2, bh / 2)]:
            rx = x + dx * cos_a - dy * sin_a
            ry = y + dx * sin_a + dy * cos_a
            pts.append((rx, ry))

        draw.polygon(pts, fill=(34, 197, 94, 190), outline=(20, 83, 45, 220))
        # Center bill dot
        draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(187, 247, 208, 210))

    return Image.alpha_composite(frame, overlay)


def draw_rain(frame: Image.Image, t: float) -> Image.Image:
    """Draws atmospheric slanted rain streaks across the night scene."""
    w, h = frame.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for i in range(55):
        speed = 1350 + (i % 6) * 180
        start_y = (i * 211) % (h + 200)
        y = ((start_y + t * speed) % (h + 200)) - 100
        x = ((i * 73 + t * 220) % (w + 150)) - 75
        length = 38 + (i % 4) * 14
        alpha = 90 + (i % 3) * 40
        draw.line([(x, y), (x - 10, y + length)], fill=(186, 230, 253, alpha), width=2)

    return Image.alpha_composite(frame, overlay)


def draw_siren_flash(frame: Image.Image, t: float) -> Image.Image:
    """Draws alternating red/blue police or emergency siren side flashes."""
    w, h = frame.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Pulse 3.5 times per second
    pulse = math.sin(t * math.pi * 7.0)
    if pulse > 0:
        alpha = int(pulse * 85)
        draw.rectangle([(0, 0), (160, h)], fill=(239, 68, 68, alpha))
        draw.rectangle([(w - 160, 0), (w, h)], fill=(239, 68, 68, int(alpha * 0.4)))
    else:
        alpha = int((-pulse) * 85)
        draw.rectangle([(w - 160, 0), (w, h)], fill=(59, 130, 246, alpha))
        draw.rectangle([(0, 0), (160, h)], fill=(59, 130, 246, int(alpha * 0.4)))

    return Image.alpha_composite(frame, overlay)


def draw_impact_speedlines(frame: Image.Image, t: float) -> Image.Image:
    """Draws dynamic comic/anime radial impact lines around the frame edges."""
    w, h = frame.size
    cx, cy = w // 2, h // 2 + 120
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Jitter angle slightly at 15 fps for authentic hand-drawn comic energy
    jitter = int(t * 15) * 3.7
    for i in range(28):
        angle = math.radians(i * (360.0 / 28.0) + (jitter % 12))
        inner_r = 460 + ((i * 37 + int(t * 20) * 19) % 130)
        outer_r = 1250
        x1 = cx + math.cos(angle) * inner_r
        y1 = cy + math.sin(angle) * inner_r
        x2 = cx + math.cos(angle) * outer_r
        y2 = cy + math.sin(angle) * outer_r
        width = 4 + (i % 3) * 3
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 110), width=width)

    return Image.alpha_composite(frame, overlay)


def draw_animated_stamp(
    frame: Image.Image,
    text: str,
    t_local: float,
    center: Tuple[int, int] = (540, 460),
) -> Image.Image:
    """Slams a tilted red rubber stamp onto the screen with spring scale impact.
    Auto-fits text so it never clips or overflows the stamp's double border."""
    if t_local < 0.0:
        return frame

    # Scale slams from 2.4x down to 1.0x in 0.22s
    p = min(1.0, t_local / 0.22)
    scale = 2.4 - 1.4 * ease_out_back(p)
    scale = max(0.95, scale)

    # Auto-fit font size to guarantee text fits cleanly inside border
    sz = 68
    while sz >= 42:
        font = _get_font(sz)
        bb = font.getbbox(text)
        tw = bb[2] - bb[0]
        th = bb[3] - bb[1]
        if tw <= 720:
            break
        sz -= 2

    # Dynamic stamp dimensions with generous margins
    sw = max(520, min(840, tw + 80))
    sh = max(130, th + 54)

    stamp_img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stamp_img)

    # Double border red ink stamp with clean inner clearance
    red = (239, 68, 68, 240)
    sdraw.rounded_rectangle([(8, 8), (sw - 8, sh - 8)], radius=18, fill=(127, 29, 29, 185), outline=red, width=10)
    sdraw.rounded_rectangle([(20, 20), (sw - 20, sh - 20)], radius=10, outline=red, width=4)

    # Center text inside inner box
    tx = (sw - tw) // 2
    ty = (sh - th) // 2 - 6
    sdraw.text((tx, ty), text, fill=(254, 226, 226, 255), font=font)

    # Rotate & scale
    rotated = stamp_img.rotate(11, expand=True, resample=Image.Resampling.BICUBIC)
    rw, rh = int(rotated.width * scale), int(rotated.height * scale)
    if rw > 0 and rh > 0:
        scaled = rotated.resize((rw, rh), Image.Resampling.BILINEAR)
        px = center[0] - rw // 2
        py = center[1] - rh // 2
        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        overlay.paste(scaled, (px, py))
        return Image.alpha_composite(frame, overlay)
    return frame


def apply_whip_transition(prev_frame: Image.Image, next_frame: Image.Image, progress: float) -> Image.Image:
    """Fast horizontal whip-pan slide transition between two scenes."""
    w, h = prev_frame.size
    eased = ease_in_out_cubic(progress)
    shift = int(w * eased)

    out = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    # Previous scene slides out left
    out.paste(prev_frame, (-shift, 0))
    # Next scene slides in from right
    out.paste(next_frame, (w - shift, 0))
    return out


def draw_sweat_drops(frame: Image.Image, x: int, y: int, t: float) -> Image.Image:
    """Draws nervous cartoon blue sweat droplets popping and dripping near a character's temple."""
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    drop_y1 = y + int((t * 40) % 25)
    drop_y2 = y + 14 + int(((t + 0.3) * 35) % 20)
    # Droplet 1
    d.polygon([(x, drop_y1 - 10), (x - 7, drop_y1 + 4), (x + 7, drop_y1 + 4)], fill=(56, 189, 248, 230))
    d.ellipse([x - 7, drop_y1 - 3, x + 7, drop_y1 + 11], fill=(56, 189, 248, 230), outline=(2, 132, 199, 255), width=2)
    # Droplet 2
    d.polygon([(x + 18, drop_y2 - 7), (x + 13, drop_y2 + 3), (x + 23, drop_y2 + 3)], fill=(56, 189, 248, 200))
    d.ellipse([x + 13, drop_y2 - 2, x + 23, drop_y2 + 8], fill=(56, 189, 248, 200), outline=(2, 132, 199, 255), width=2)
    return Image.alpha_composite(frame, overlay)


def draw_anger_mark(frame: Image.Image, cx: int, cy: int, scale: float = 1.0) -> Image.Image:
    """Draws dynamic anime/cartoon red anger vein cross mark (💢) popping over an enraged character."""
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    s = int(24 * scale)
    red = (239, 68, 68, 245)
    w = max(3, int(5 * scale))
    d.arc([cx - s, cy - s, cx, cy], start=180, end=360, fill=red, width=w)
    d.arc([cx, cy - s, cx + s, cy], start=180, end=360, fill=red, width=w)
    d.arc([cx - s, cy, cx, cy + s], start=0, end=180, fill=red, width=w)
    d.arc([cx, cy, cx + s, cy + s], start=0, end=180, fill=red, width=w)
    return Image.alpha_composite(frame, overlay)


def draw_door_burst_particles(frame: Image.Image, t_local: float) -> Image.Image:
    """Explosive wooden splinter particles & entry shockwave when doors are kicked open."""
    if t_local > 0.65 or t_local < 0.0:
        return frame
    w, h = frame.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    prog = t_local / 0.65
    alpha = int((1.0 - prog) * 230)

    # White impact entry flash
    if prog < 0.25:
        flash_a = int((1.0 - prog / 0.25) * 140)
        d.rectangle([(0, 0), (w, h)], fill=(255, 255, 255, flash_a))

    # Flying wood splinter particles bursting from doorway (x=160, y=1150)
    origin_x, origin_y = 180, 1150
    for i in range(24):
        angle = -0.5 + (i * 0.04)  # flying towards right
        speed = 380 + (i * 47) % 600
        dist = speed * prog
        px = origin_x + int(math.cos(angle) * dist)
        py = origin_y + int(math.sin(angle) * dist) + int(550 * (prog ** 2))
        pw = 8 + (i % 3) * 6
        ph = 14 + (i % 4) * 8
        d.rectangle([(px, py), (px + pw, py + ph)], fill=(180, 83, 9, alpha), outline=(120, 53, 15, alpha), width=2)

    return Image.alpha_composite(frame, overlay)
