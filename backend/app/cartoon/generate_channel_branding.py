"""
Generates high-resolution YouTube channel packaging assets for Anatoly Kuertov:
- Avatar (1000x1000 px PNG) with circular safe-zone preview
- Banner (2048x1152 px PNG) with exact mobile/desktop Safe-Area (1235x338 px)
"""

import math
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from backend.app.cartoon.v3_engine import (
    FONT_BOLD,
    FONT_IMPACT,
    INK,
    _draw_car,
    _font,
    render_full_body_character,
)

OUTPUT_DIR = Path("output/channel_branding")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def draw_glow_circle(d: ImageDraw.Draw, cx: int, cy: int, r: int, color: tuple, width: int = 4, blur: int = 8):
    for i in range(width + blur, 0, -2):
        alpha = int(color[3] * (1.0 - i / (width + blur))) if len(color) > 3 else int(180 * (1.0 - i / (width + blur)))
        c = (color[0], color[1], color[2], alpha)
        d.ellipse([cx - r - i, cy - r - i, cx + r + i, cy + r + i], outline=c, width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)


# ---------------------------------------------------------------------------
# 1. AVATAR 1: HERO STORYTELLER (1000x1000)
# ---------------------------------------------------------------------------

def generate_avatar_hero() -> Path:
    W, H = 1000, 1000
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    d = ImageDraw.Draw(img)

    # 1. Dark vibrant radial background gradient (Deep slate-violet to midnight black)
    cx, cy = W // 2, H // 2
    for r in range(500, 0, -4):
        rat = r / 500.0
        # Center glow (electric indigo/cyan) -> outer midnight
        cr = int(30 + (1.0 - rat) * 55)
        cg = int(27 + (1.0 - rat) * 65)
        cb = int(75 + (1.0 - rat) * 140)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb, 255))

    # 2. Glowing circular neon rim (Electric Cyan & Neon Gold)
    draw_glow_circle(d, cx, cy, 470, (56, 189, 248, 255), width=6, blur=14)
    draw_glow_circle(d, cx, cy, 460, (234, 179, 8, 220), width=4, blur=8)

    # 3. Dynamic background speed rays / geometric accents
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        x2 = cx + int(460 * math.cos(rad))
        y2 = cy + int(460 * math.sin(rad))
        d.line([(cx, cy), (x2, y2)], fill=(255, 255, 255, 18), width=3)

    # 4. Stylized Hero Character: Anatoly Kuertov
    # We render a full-body character and crop/scale as a charismatic bust portrait!
    char_base = render_full_body_character(
        outfit="hoodie",
        outfit_color=(30, 41, 59),
        hair_style="slicked",
        mood="confident",
        mouth_state="closed",
        gesture="relax",
        blink=False,
        facing="right",
        scale=1.0,
    )
    # Add neat stylish beard + leather jacket lapels + popped collar
    cd = ImageDraw.Draw(char_base, "RGBA")
    ccx = char_base.width // 2
    # Beard along jaw
    cd.arc([ccx - 56, 202, ccx + 56, 260], start=18, end=162, fill=(55, 42, 34, 255), width=16)
    # Gold necklace chain peek
    cd.arc([ccx - 24, 250, ccx + 24, 290], start=20, end=160, fill=(234, 179, 8, 255), width=4)
    # Jacket dark leather shoulders
    cd.polygon([(ccx - 90, 320), (ccx - 55, 250), (ccx - 30, 340)], fill=(15, 23, 42, 255), outline=INK, width=3)
    cd.polygon([(ccx + 90, 320), (ccx + 55, 250), (ccx + 30, 340)], fill=(15, 23, 42, 255), outline=INK, width=3)

    # Scale character up for tight charismatic bust composition
    # Bust crop: head around y=100..450 in char_base (char_base is ~480x780 at scale 1.0)
    char_scaled = char_base.resize((int(char_base.width * 2.1), int(char_base.height * 2.1)), Image.Resampling.LANCZOS)
    # Paste character positioned in center
    char_x = (W - char_scaled.width) // 2
    char_y = 130
    img.paste(char_scaled, (char_x, char_y), char_scaled)

    # 5. Bottom branded badge: "АК" Monogram in gold/cyan capsule
    d = ImageDraw.Draw(img)
    badge_w, badge_h = 320, 84
    bx = (W - badge_w) // 2
    by = 780
    d.rounded_rectangle([(bx - 3, by - 3), (bx + badge_w + 3, by + badge_h + 3)], radius=42, fill=(56, 189, 248, 255))
    d.rounded_rectangle([(bx, by), (bx + badge_w, by + badge_h)], radius=40, fill=(15, 23, 42, 245), outline=(234, 179, 8, 255), width=4)

    f_mon = _font(FONT_IMPACT, 48)
    mt = "КУЕРТОВ"
    mb = f_mon.getbbox(mt)
    d.text(((W - (mb[2] - mb[0])) // 2, by + 12), mt, fill=(255, 255, 255, 255), font=f_mon)

    # Save Avatar
    out_path = OUTPUT_DIR / "avatar_kuertov_hero.png"
    img.save(out_path, "PNG")
    print(f"[OK] Создан аватар: {out_path} ({W}x{H})")
    return out_path


# ---------------------------------------------------------------------------
# 2. AVATAR 2: AUTO CRIME & STORIES (1000x1000)
# ---------------------------------------------------------------------------

def generate_avatar_auto() -> Path:
    W, H = 1000, 1000
    img = Image.new("RGBA", (W, H), (10, 15, 26, 255))
    d = ImageDraw.Draw(img)

    cx, cy = W // 2, H // 2
    # Radial dark red / crimson glow
    for r in range(500, 0, -4):
        rat = r / 500.0
        cr = int(24 + (1.0 - rat) * 110)
        cg = int(10 + (1.0 - rat) * 20)
        cb = int(20 + (1.0 - rat) * 35)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb, 255))

    # Glowing neon red/amber ring
    draw_glow_circle(d, cx, cy, 470, (239, 68, 68, 255), width=6, blur=14)
    draw_glow_circle(d, cx, cy, 460, (249, 115, 22, 220), width=4, blur=8)

    # Stylized Sports Car / Crossover vector in center
    S = 2
    car_layer = Image.new("RGBA", (580 * S, 260 * S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(car_layer)
    _draw_car(cd, cx=290 * S, wheel_y=190 * S, S=S, body_color=(220, 38, 38), split_gap=0)
    # Headlight glowing beam
    cd.polygon([(520 * S, 130 * S), (580 * S, 90 * S), (580 * S, 200 * S), (520 * S, 160 * S)], fill=(254, 240, 138, 190))
    car_scaled = car_layer.resize((760, 340), Image.Resampling.LANCZOS)
    img.paste(car_scaled, (120, 330), car_scaled)

    # Bold Typography: "АК" Top & "ИСТОРИИ" Bottom
    d = ImageDraw.Draw(img)
    f_ak = _font(FONT_IMPACT, 110)
    akt = "АК"
    akb = f_ak.getbbox(akt)
    d.text(((W - (akb[2] - akb[0])) // 2, 190), akt, fill=(254, 240, 138, 255), font=f_ak)

    # Bottom capsule: "АВТО-ИСТОРИИ"
    bw, bh = 480, 88
    bx = (W - bw) // 2
    by = 720
    d.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=44, fill=(220, 38, 38, 240), outline=(255, 255, 255, 255), width=4)
    f_sub = _font(FONT_BOLD, 38)
    sbt = "АВТО-ИСТОРИИ"
    sbb = f_sub.getbbox(sbt)
    d.text(((W - (sbb[2] - sbb[0])) // 2, by + 18), sbt, fill=(255, 255, 255, 255), font=f_sub)

    out_path = OUTPUT_DIR / "avatar_auto_stories.png"
    img.save(out_path, "PNG")
    print(f"[OK] Создан аватар: {out_path} ({W}x{H})")
    return out_path


# ---------------------------------------------------------------------------
# 3. YOUTUBE BANNER: CINEMATIC MASTERPIECE (2048x1152)
# ---------------------------------------------------------------------------

def generate_banner_cinematic() -> Path:
    """
    YouTube Official Banner Specs:
    - Canvas Size: 2048 x 1152 px
    - Exact Safe Area (Visible on Mobile & Desktop):
      Width: 1235 px, Height: 338 px
      Centered at x = 406..1641, y = 407..745
    """
    W, H = 2048, 1152
    img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
    d = ImageDraw.Draw(img)

    # Safe Area Coordinates
    safe_w, safe_h = 1235, 338
    safe_x1 = (W - safe_w) // 2  # 406
    safe_y1 = (H - safe_h) // 2  # 407
    safe_x2 = safe_x1 + safe_w   # 1641
    safe_y2 = safe_y1 + safe_h   # 745

    # 1. Background Sky: Moody Night City with Deep Violet/Navy Gradient
    for y in range(0, H, 4):
        rat = y / float(H)
        cr = int(10 + rat * 18)
        cg = int(14 + rat * 20)
        cb = int(28 + rat * 36)
        d.rectangle([(0, y), (W, y + 4)], fill=(cr, cg, cb, 255))

    # 2. Distant Glowing Skyscrapers & Neon City Grid
    # Left towers
    for bx, bw, bh in [(60, 150, 520), (240, 180, 640), (450, 160, 480)]:
        d.rectangle([(bx, H - bh), (bx + bw, H)], fill=(20, 28, 42, 255), outline=(38, 48, 65, 255), width=2)
        # Windows
        for wy in range(H - bh + 40, H - 100, 45):
            for wx in range(bx + 18, bx + bw - 18, 32):
                if (wx + wy) % 3 == 0:
                    d.rectangle([(wx, wy), (wx + 16, wy + 24)], fill=(254, 240, 138, 150))

    # Right towers
    for bx, bw, bh in [(1460, 170, 500), (1670, 200, 680), (1900, 130, 540)]:
        d.rectangle([(bx, H - bh), (bx + bw, H)], fill=(20, 28, 42, 255), outline=(38, 48, 65, 255), width=2)
        for wy in range(H - bh + 40, H - 100, 45):
            for wx in range(bx + 18, bx + bw - 18, 32):
                if (wx + wy) % 4 == 0:
                    d.rectangle([(wx, wy), (wx + 16, wy + 24)], fill=(56, 189, 248, 150))

    # 3. Horizontal Cinematic Neon Light-Beams across Safe Area
    d.line([(0, safe_y1), (W, safe_y1)], fill=(56, 189, 248, 70), width=2)
    d.line([(0, safe_y2), (W, safe_y2)], fill=(239, 68, 68, 70), width=2)

    # Soft radial glow right behind the main title
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W // 2 - 420, H // 2 - 180, W // 2 + 420, H // 2 + 180], fill=(79, 70, 229, 65))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)

    # 4. Left Element: Sleek Sports Car positioned dynamically
    # Positioned so front bumper ends at x = 710, beautifully framing the title without overlap
    car_layer = Image.new("RGBA", (580 * 2, 260 * 2), (0, 0, 0, 0))
    _draw_car(ImageDraw.Draw(car_layer), cx=290 * 2, wheel_y=190 * 2, S=2, body_color=(220, 38, 38), split_gap=0)
    # Bright LED headlights beam towards the center
    ImageDraw.Draw(car_layer).polygon([(520 * 2, 130 * 2), (580 * 2, 80 * 2), (580 * 2, 210 * 2), (520 * 2, 160 * 2)], fill=(254, 240, 138, 210))
    car_res = car_layer.resize((430, 192), Image.Resampling.LANCZOS)
    img.paste(car_res, (280, safe_y1 + 86), car_res)

    # 5. Right Element: Character (Anatoly Kuertov)
    # Positioned at x = 1340..1700 facing left towards the title with ample margin
    char_base = render_full_body_character(
        outfit="hoodie", outfit_color=(30, 41, 59), hair_style="slicked",
        mood="confident", mouth_state="closed", gesture="relax",
        blink=False, facing="left", scale=1.0,
    )
    cd = ImageDraw.Draw(char_base, "RGBA")
    ccx = char_base.width // 2
    # Beard
    cd.arc([ccx - 56, 202, ccx + 56, 260], start=18, end=162, fill=(55, 42, 34, 255), width=16)
    # Gold chain peek
    cd.arc([ccx - 24, 250, ccx + 24, 290], start=20, end=160, fill=(234, 179, 8, 255), width=4)
    # Leather jacket collar
    cd.polygon([(ccx - 85, 320), (ccx - 55, 250), (ccx - 30, 340)], fill=(15, 23, 42, 255), outline=INK, width=3)
    cd.polygon([(ccx + 85, 320), (ccx + 55, 250), (ccx + 30, 340)], fill=(15, 23, 42, 255), outline=INK, width=3)
    # Scale for safe area height
    char_scaled = char_base.resize((int(char_base.width * 0.90), int(char_base.height * 0.90)), Image.Resampling.LANCZOS)
    img.paste(char_scaled, (1340, safe_y1 + 18), char_scaled)

    # 6. Central Typography inside Safe Area (Guaranteed visible on phones!)
    title_cx = W // 2  # 1024

    # Top Tagline Pill
    pill_w, pill_h = 390, 38
    px = title_cx - pill_w // 2
    py = safe_y1 + 22
    d.rounded_rectangle([(px, py), (px + pill_w, py + pill_h)], radius=19, fill=(220, 38, 38, 240), outline=(255, 255, 255, 255), width=2)
    f_pill = _font(FONT_BOLD, 19)
    plt = "КРИМИНАЛЬНЫЕ АВТО-ИСТОРИИ"
    plb = f_pill.getbbox(plt)
    d.text((title_cx - (plb[2] - plb[0]) // 2, py + 8), plt, fill=(255, 255, 255, 255), font=f_pill)

    # Main Huge Title: "АНАТОЛИЙ КУЕРТОВ" (Impact 74)
    f_main = _font(FONT_IMPACT, 74)
    mtt = "АНАТОЛИЙ КУЕРТОВ"
    mtb = f_main.getbbox(mtt)
    mt_w = mtb[2] - mtb[0]
    mt_x = title_cx - mt_w // 2
    mt_y = safe_y1 + 76

    # 3D Drop Shadow
    for sx, sy in [(4, 4), (3, 3), (2, 2)]:
        d.text((mt_x + sx, mt_y + sy), mtt, fill=(15, 23, 42, 255), font=f_main)
    # Bright White with Gold Underline
    d.text((mt_x, mt_y), mtt, fill=(255, 255, 255, 255), font=f_main)

    # Subtitle: "АФЕРЫ • РАЗВОДЫ • ПЕРЕКУПЫ • РАЗОБЛАЧЕНИЯ"
    f_sub = _font(FONT_BOLD, 22)
    sbt = "АФЕРЫ • РАЗВОДЫ • ПЕРЕКУПЫ • РАЗОБЛАЧЕНИЯ"
    sbb = f_sub.getbbox(sbt)
    sb_w = sbb[2] - sbb[0]
    d.text((title_cx - sb_w // 2, safe_y1 + 182), sbt, fill=(250, 204, 21, 255), font=f_sub)

    # Bottom Badges: "НОВЫЕ СЕРИИ КАЖДЫЙ ДЕНЬ" & "ПОДПИШИСЬ НА КАНАЛ"
    b_y = safe_y1 + 242

    # Left Badge
    d.rounded_rectangle([(title_cx - 275, b_y), (title_cx - 15, b_y + 44)], radius=12, fill=(30, 41, 59, 230), outline=(56, 189, 248, 255), width=2)
    d.text((title_cx - 260, b_y + 11), "🔥 НОВЫЕ СЕРИИ КАЖДЫЙ ДЕНЬ", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 16))

    # Right Badge
    d.rounded_rectangle([(title_cx + 15, b_y), (title_cx + 275, b_y + 44)], radius=12, fill=(220, 38, 38, 240), outline=(255, 255, 255, 255), width=2)
    d.text((title_cx + 40, b_y + 11), "▶ ПОДПИШИСЬ НА КАНАЛ", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 17))

    # Save Banner
    out_path = OUTPUT_DIR / "banner_kuertov_stories.png"
    img.save(out_path, "PNG")
    print(f"[OK] Создан баннер: {out_path} ({W}x{H})")
    return out_path
    sb_w = sbb[2] - sbb[0]
    d.text((title_cx - sb_w // 2, safe_y1 + 185), sbt, fill=(250, 204, 21, 255), font=f_sub)

    # Bottom Badges: "НОВЫЕ СЕРИИ КАЖДЫЙ ДЕНЬ" & "YOUTUBE SHORTS"
    b_y = safe_y1 + 242

    # Left Badge
    d.rounded_rectangle([(title_cx - 290, b_y), (title_cx - 10, b_y + 46)], radius=12, fill=(30, 41, 59, 230), outline=(56, 189, 248, 255), width=2)
    d.text((title_cx - 275, b_y + 11), "🔥 НОВЫЕ СЕРИИ КАЖДЫЙ ДЕНЬ", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 17))

    # Right Badge
    d.rounded_rectangle([(title_cx + 10, b_y), (title_cx + 290, b_y + 46)], radius=12, fill=(220, 38, 38, 240), outline=(255, 255, 255, 255), width=2)
    d.text((title_cx + 38, b_y + 11), "▶ ПОДПИШИСЬ НА КАНАЛ", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 18))

    # Save Banner
    out_path = OUTPUT_DIR / "banner_kuertov_stories.png"
    img.save(out_path, "PNG")
    print(f"[OK] Создан баннер: {out_path} ({W}x{H})")
    return out_path


# ---------------------------------------------------------------------------
# 4. YOUTUBE BANNER: MINIMAL DARK LUXURY (2048x1152)
# ---------------------------------------------------------------------------

def generate_banner_minimal() -> Path:
    W, H = 2048, 1152
    img = Image.new("RGBA", (W, H), (12, 16, 24, 255))
    d = ImageDraw.Draw(img)

    safe_w, safe_h = 1235, 338
    safe_x1 = (W - safe_w) // 2
    safe_y1 = (H - safe_h) // 2
    safe_x2 = safe_x1 + safe_w
    safe_y2 = safe_y1 + safe_h

    # Subtle carbon grid pattern
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(20, 26, 38, 255), width=1)
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(20, 26, 38, 255), width=1)

    # Gold rim border lines across safe area
    d.line([(safe_x1, safe_y1), (safe_x2, safe_y1)], fill=(234, 179, 8, 120), width=2)
    d.line([(safe_x1, safe_y2), (safe_x2, safe_y2)], fill=(234, 179, 8, 120), width=2)

    cx = W // 2
    cy = H // 2

    # Title
    f_main = _font(FONT_IMPACT, 92)
    mtt = "АНАТОЛИЙ КУЕРТОВ"
    mtb = f_main.getbbox(mtt)
    d.text((cx - (mtb[2] - mtb[0]) // 2, safe_y1 + 60), mtt, fill=(255, 255, 255, 255), font=f_main)

    # Gold accent line
    d.line([(cx - 240, safe_y1 + 175), (cx + 240, safe_y1 + 175)], fill=(234, 179, 8, 255), width=4)

    # Subtitle
    f_sub = _font(FONT_BOLD, 28)
    sbt = "АВТО-РАССЛЕДОВАНИЯ • КРИМИНАЛЬНЫЕ ИСТОРИИ"
    sbb = f_sub.getbbox(sbt)
    d.text((cx - (sbb[2] - sbb[0]) // 2, safe_y1 + 205), sbt, fill=(203, 213, 225, 255), font=f_sub)

    out_path = OUTPUT_DIR / "banner_dark_minimal.png"
    img.save(out_path, "PNG")
    print(f"[OK] Создан баннер минимал: {out_path} ({W}x{H})")
    return out_path


def main():
    print("\n" + "=" * 60)
    print("🎨 ГЕНЕРАЦИЯ ОФОРМЛЕНИЯ YOUTUBE КАНАЛА ДЛЯ АНАТОЛИЯ КУЕРТОВА")
    print("=" * 60)

    generate_avatar_hero()
    generate_avatar_auto()
    generate_banner_cinematic()
    generate_banner_minimal()

    print("=" * 60)
    print("🎉 ВСЕ МАКЕТЫ ГОТОВЫ В output/channel_branding/")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
