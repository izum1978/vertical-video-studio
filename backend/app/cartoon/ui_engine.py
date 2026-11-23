"""
Cartoon UI Engine: Renders 2D Explainer graphics (HUD, Location tags, Speech bubbles).
Matches the viral 2D storytelling / explainer video aesthetic.
"""

import math
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_IMPACT = "C:/Windows/Fonts/impact.ttf"


def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def draw_top_hud(
    canvas: Image.Image,
    balance_text: str = "330 000 ₽",
    status_text: str = "ПАВИЛЬОН ТВОЙ",
    y_offset: int = 80,
    width: int = 960,
    height: int = 120,
    theme: str = "green",  # "green", "alert", "danger", "muted"
) -> None:
    """Renders the top gaming-style HUD status bar with mood-aware colors."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    canvas_w, canvas_h = canvas.size

    hud_x = (canvas_w - width) // 2
    hud_y = y_offset

    # Theme palette
    if theme == "danger":
        border_col = (239, 68, 68, 255)
        badge_fill = (153, 27, 27, 240)
        badge_outline = (248, 113, 113, 255)
        bal_label_col = (254, 202, 202)
        status_label_col = (248, 113, 113)
    elif theme == "alert":
        border_col = (251, 146, 60, 255)
        badge_fill = (154, 52, 18, 235)
        badge_outline = (253, 186, 116, 255)
        bal_label_col = (254, 215, 170)
        status_label_col = (251, 191, 36)
    elif theme == "muted":
        border_col = (148, 163, 184, 255)
        badge_fill = (51, 65, 85, 235)
        badge_outline = (148, 163, 184, 255)
        bal_label_col = (203, 213, 225)
        status_label_col = (148, 163, 184)
    else:  # green
        border_col = (255, 215, 0, 255)
        badge_fill = (22, 101, 52, 230)
        badge_outline = (74, 222, 128, 255)
        bal_label_col = (187, 247, 208)
        status_label_col = (251, 191, 36)

    # Shadow
    draw.rounded_rectangle(
        [(hud_x + 4, hud_y + 8), (hud_x + width + 4, hud_y + height + 8)],
        radius=30,
        fill=(0, 0, 0, 110),
    )

    # Main dark capsule container
    draw.rounded_rectangle(
        [(hud_x, hud_y), (hud_x + width, hud_y + height)],
        radius=30,
        fill=(15, 20, 32, 245),
        outline=border_col,
        width=4,
    )

    # Left Section: Balance Badge
    badge_w = 460
    badge_x = hud_x + 18
    badge_y = hud_y + 16
    badge_h = height - 32

    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
        radius=20,
        fill=badge_fill,
        outline=badge_outline,
        width=2,
    )

    font_label = get_font(FONT_BOLD, 22)
    font_val = get_font(FONT_BOLD, 34)

    # Currency Label
    draw.text((badge_x + 22, badge_y + 8), "НА СЧЕТУ:", fill=bal_label_col, font=font_label)
    draw.text((badge_x + 22, badge_y + 38), balance_text, fill=(255, 255, 255), font=font_val)

    # Vertical Divider
    div_x = hud_x + badge_w + 35
    draw.line(
        [(div_x, hud_y + 20), (div_x, hud_y + height - 20)],
        fill=(71, 85, 105, 200),
        width=3,
    )

    # Right Section: Status / Mission Goal
    goal_x = div_x + 25
    goal_y = hud_y + 18
    font_status_label = get_font(FONT_BOLD, 22)
    font_status_val = get_font(FONT_BOLD, 30)

    draw.text((goal_x, goal_y + 6), "СТАТУС:", fill=status_label_col, font=font_status_label)
    display_status = status_text if len(status_text) <= 21 else status_text[:19] + ".."
    draw.text((goal_x, goal_y + 38), display_status, fill=(255, 255, 255), font=font_status_val)


def draw_location_pill(
    canvas: Image.Image,
    text: str = "ларёк с шаурмой 24/7 у остановки",
    y_pos: int = 225,
    font_size: int = 28,
) -> None:
    """Renders location/time badge pill below the HUD."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    canvas_w, canvas_h = canvas.size

    font = get_font(FONT_BOLD, font_size)
    full_text = f"( {text} )"
    bbox = font.getbbox(full_text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    pill_w = text_w + 60
    pill_h = text_h + 30
    pill_x = (canvas_w - pill_w) // 2

    # Drop shadow
    draw.rounded_rectangle(
        [(pill_x + 3, y_pos + 4), (pill_x + pill_w + 3, y_pos + pill_h + 4)],
        radius=pill_h // 2,
        fill=(0, 0, 0, 90),
    )

    # Pill background
    draw.rounded_rectangle(
        [(pill_x, y_pos), (pill_x + pill_w, y_pos + pill_h)],
        radius=pill_h // 2,
        fill=(30, 41, 59, 235),  # Slate dark
        outline=(148, 163, 184, 220),
        width=2,
    )

    draw.text((pill_x + 30, y_pos + 12), full_text, fill=(241, 245, 249), font=font)


def draw_speech_bubble(
    canvas: Image.Image,
    text: str,
    box_rect: Tuple[int, int, int, int],  # (x1, y1, x2, y2)
    tail_tip: Tuple[int, int],  # (x, y) where the tail points (e.g. character mouth)
    font_size: int = 34,
    bg_color: Tuple[int, int, int] = (255, 255, 255),
    border_color: Tuple[int, int, int] = (20, 20, 25),
) -> None:
    """Renders a comic speech bubble with a directional tail pointing at the speaker."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    x1, y1, x2, y2 = box_rect

    # Outer border expansion for tail
    tx, ty = tail_tip

    # Draw tail triangle
    # Base of tail on the bottom or side of box
    tail_base_left = (x1 + (x2 - x1) // 3, y2)
    tail_base_right = (x1 + (x2 - x1) // 3 + 45, y2)

    # Shadow
    draw.rounded_rectangle([(x1 + 4, y1 + 6), (x2 + 4, y2 + 6)], radius=28, fill=(0, 0, 0, 70))
    draw.polygon(
        [(tail_base_left[0] + 4, tail_base_left[1] + 6),
         (tail_base_right[0] + 4, tail_base_right[1] + 6),
         (tx + 4, ty + 6)],
        fill=(0, 0, 0, 70),
    )

    # Tail outline & fill
    draw.polygon([tail_base_left, tail_base_right, (tx, ty)], fill=bg_color, outline=border_color)
    draw.line([tail_base_left, (tx, ty)], fill=border_color, width=4)
    draw.line([tail_base_right, (tx, ty)], fill=border_color, width=4)

    # Bubble body
    draw.rounded_rectangle([box_rect[0], box_rect[1], box_rect[2], box_rect[3]], radius=28, fill=bg_color, outline=border_color, width=4)
    # Overwrite the interior seam where tail connects
    draw.line([(tail_base_left[0] + 4, y2), (tail_base_right[0] - 4, y2)], fill=bg_color, width=6)

    # Wrap text and draw
    font = get_font(FONT_BOLD, font_size)
    words = text.split(" ")
    lines = []
    cur_line = []
    max_w = (x2 - x1) - 48

    for word in words:
        test_line = " ".join(cur_line + [word])
        w = font.getbbox(test_line)[2] - font.getbbox(test_line)[0]
        if w > max_w and cur_line:
            lines.append(" ".join(cur_line))
            cur_line = [word]
        else:
            cur_line.append(word)
    if cur_line:
        lines.append(" ".join(cur_line))

    # Center text vertically
    line_h = font_size + 10
    total_h = len(lines) * line_h
    start_y = y1 + ((y2 - y1) - total_h) // 2

    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        lw = bbox[2] - bbox[0]
        lx = x1 + ((x2 - x1) - lw) // 2
        draw.text((lx, start_y + i * line_h), line, fill=(15, 23, 42), font=font)


def draw_floating_badge(
    canvas: Image.Image,
    text: str = "?!",
    center_pos: Tuple[int, int] = (540, 800),
    badge_color: Tuple[int, int, int] = (239, 68, 68),  # Red alert
    size: int = 80,
) -> None:
    """Draws an expressive alert badge (like ?!, shock, anger) near the character."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    cx, cy = center_pos
    r = size // 2

    # Glow / shadow
    draw.ellipse([(cx - r - 4, cy - r - 4), (cx + r + 4, cy + r + 4)], fill=(0, 0, 0, 80))
    # Badge circle
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=badge_color, outline=(255, 255, 255), width=4)

    font = get_font(FONT_IMPACT, int(size * 0.6))
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - 4), text, fill=(255, 255, 255), font=font)
