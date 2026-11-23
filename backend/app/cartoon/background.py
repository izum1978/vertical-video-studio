"""
Cartoon Background Generator (2D Vector Locations).
Creates atmospheric 2D vector backgrounds (Night Street Kiosk, Courtroom, Office, City)
in clean 1080x1920 9:16 vertical resolution.
"""

from typing import Tuple
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_IMPACT = "C:/Windows/Fonts/impact.ttf"


def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def render_night_kiosk_location(size: Tuple[int, int] = (1080, 1920)) -> Image.Image:
    """Renders a stylized 2D vector night street food kiosk location."""
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 1. Sky Gradient (Deep Navy to Indigo Night)
    for y in range(0, int(h * 0.65)):
        ratio = y / (h * 0.65)
        r = int(10 + ratio * 15)
        g = int(15 + ratio * 20)
        b = int(35 + ratio * 45)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Glowing Moon & Stars
    draw.ellipse([820, 180, 920, 280], fill=(254, 240, 138, 240))
    draw.ellipse([800, 160, 900, 260], fill=(15, 23, 42, 255))  # Crescent shape

    # Distant Stars
    stars = [(120, 160), (280, 240), (450, 180), (620, 220), (750, 140), (980, 320), (180, 380), (390, 410)]
    for sx, sy in stars:
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255, 180))

    # 2. Distant City Skyline Silhouettes
    skyline_y = 580
    buildings = [
        (40, 320, 160), (180, 260, 140), (300, 380, 180), (460, 300, 150),
        (590, 420, 170), (740, 280, 160), (880, 360, 180)
    ]
    for bx, by, bw in buildings:
        # Building silhouette
        draw.rectangle([(bx, skyline_y - by), (bx + bw, skyline_y + 100)], fill=(20, 26, 42, 255))
        # Illuminated windows
        for wy in range(skyline_y - by + 30, skyline_y + 80, 45):
            for wx in range(bx + 20, bx + bw - 20, 35):
                if (wx + wy) % 7 == 0:
                    draw.rectangle([(wx, wy), (wx + 16, wy + 24)], fill=(253, 224, 71, 200))

    # 3. Ground / Asphalt Street
    ground_y = 660
    draw.rectangle([(0, ground_y), (w, h)], fill=(24, 30, 42, 255))

    # Street pavement curb line
    draw.rectangle([(0, ground_y), (w, ground_y + 35)], fill=(51, 65, 85, 255))
    draw.line([(0, ground_y), (w, ground_y)], fill=(100, 116, 139, 255), width=3)

    # Wet road reflections
    draw.ellipse([140, ground_y + 300, 940, ground_y + 440], fill=(30, 41, 59, 120))

    # 4. Street Kiosk Pavilion
    kx, ky = 120, 480
    kw, kh = 840, 560

    # Kiosk Main Walls
    draw.rectangle([(kx, ky), (kx + kw, ky + kh)], fill=(30, 41, 59, 255), outline=(15, 23, 42, 255), width=6)

    # Large Glass Counter / Service Window
    win_x, win_y = kx + 80, ky + 140
    win_w, win_h = kw - 160, kh - 220
    # Warm glowing interior
    draw.rectangle([(win_x, win_y), (win_x + win_w, win_y + win_h)], fill=(254, 215, 170, 230), outline=(15, 23, 42, 255), width=5)

    # Interior silhouettes: Shawarma vertical rotisserie spit
    spit_x = win_x + win_w // 2 - 25
    draw.line([(spit_x + 25, win_y + 20), (spit_x + 25, win_y + win_h - 20)], fill=(120, 53, 15, 255), width=6)
    draw.rounded_rectangle([(spit_x, win_y + 50), (spit_x + 50, win_y + win_h - 60)], radius=25, fill=(180, 83, 9, 255))

    # Service counter shelf
    shelf_y = win_y + win_h - 15
    draw.rounded_rectangle([(win_x - 30, shelf_y), (win_x + win_w + 30, shelf_y + 35)], radius=10, fill=(71, 85, 105, 255), outline=(15, 23, 42, 255), width=4)

    # Striped Awning / Roof (Red & White Stripes)
    roof_y = ky - 30
    roof_h = 130
    draw.polygon(
        [(kx - 50, roof_y + roof_h), (kx + kw + 50, roof_y + roof_h), (kx + kw, roof_y), (kx, roof_y)],
        fill=(220, 38, 38, 255),
        outline=(15, 23, 42, 255),
    )
    # White stripes
    stripe_w = (kw + 100) // 9
    for i in range(1, 9, 2):
        sx = (kx - 50) + i * stripe_w
        draw.polygon(
            [(sx, roof_y + roof_h), (sx + stripe_w, roof_y + roof_h), (sx + stripe_w - 6, roof_y), (sx - 6, roof_y)],
            fill=(248, 250, 252, 255),
        )

    # Neon Signboard above roof: 'ШАУРМА 24/7'
    sign_w, sign_h = 560, 95
    sign_x = (w - sign_w) // 2
    sign_y = roof_y - 85
    # Sign background
    draw.rounded_rectangle([(sign_x, sign_y), (sign_x + sign_w, sign_y + sign_h)], radius=20, fill=(15, 23, 42, 255), outline=(239, 68, 68, 255), width=5)
    # Neon text
    font_sign = get_font(FONT_IMPACT, 52)
    text = "ШАУРМА 24/7"
    t_bbox = font_sign.getbbox(text)
    tw = t_bbox[2] - t_bbox[0]
    draw.text((sign_x + (sign_w - tw) // 2, sign_y + 12), text, fill=(254, 240, 138, 255), font=font_sign)

    # 5. Street Light Lamp Post (casting cone of light)
    lamp_x = 900
    draw.line([(lamp_x, 320), (lamp_x, ground_y + 200)], fill=(71, 85, 105, 255), width=12)
    draw.arc([lamp_x - 120, 240, lamp_x, 360], start=270, end=360, fill=(71, 85, 105, 255), width=12)
    # Lamp head
    draw.polygon([(lamp_x - 140, 310), (lamp_x - 80, 310), (lamp_x - 60, 335), (lamp_x - 160, 335)], fill=(251, 191, 36, 255))

    # Warm light beam polygon onto the ground
    light_beam = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    light_draw = ImageDraw.Draw(light_beam)
    light_draw.polygon(
        [(lamp_x - 110, 335), (200, h), (1050, h)],
        fill=(253, 230, 138, 38),  # Soft warm translucent cone
    )
    img = Image.alpha_composite(img, light_beam)

    return img


def render_dealership_location(is_scam: bool = False, size: Tuple[int, int] = (1080, 1920)) -> Image.Image:
    """Renders 2D vector Car Dealership / Showroom location."""
    w, h = size
    img = Image.new("RGBA", (w, h), (18, 22, 32, 255))
    draw = ImageDraw.Draw(img)

    # 1. Showroom Glass Wall & Ceiling lights
    for y in range(0, 680):
        ratio = y / 680.0
        r = int(15 + ratio * 20)
        g = int(22 + ratio * 25)
        b = int(38 + ratio * 40)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Overhead LED square light fixtures
    for lx in [200, 540, 880]:
        draw.rounded_rectangle([(lx - 110, 140), (lx + 110, 220)], radius=12, fill=(248, 250, 252, 240), outline=(203, 213, 225, 255), width=3)
        # Light cone downwards
        cone = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(cone)
        cdraw.polygon([(lx - 100, 220), (lx + 100, 220), (lx + 220, 780), (lx - 220, 780)], fill=(255, 255, 255, 18))
        img = Image.alpha_composite(img, cone)
        draw = ImageDraw.Draw(img)

    # Neon Sign: 'АВТОСАЛОН ПРЕМИУМ' vs 'АВТОХЛАМ 24/7'
    sign_w, sign_h = 620, 95
    sign_x = (w - sign_w) // 2
    sign_y = 260
    draw.rounded_rectangle([(sign_x, sign_y), (sign_x + sign_w, sign_y + sign_h)], radius=20, fill=(15, 23, 42, 255), outline=(239, 68, 68, 255) if is_scam else (56, 189, 248, 255), width=4)
    font_sign = get_font(FONT_IMPACT, 44)
    sign_txt = "АВТОХЛАМ И ТОТАЛ" if is_scam else "АВТОСАЛОН ПРЕМИУМ"
    t_bb = font_sign.getbbox(sign_txt)
    draw.text((sign_x + (sign_w - (t_bb[2] - t_bb[0])) // 2, sign_y + 18), sign_txt, fill=(255, 255, 255), font=font_sign)

    # 2. Glossy Tile Showroom Floor
    floor_y = 680
    draw.rectangle([(0, floor_y), (w, h)], fill=(30, 41, 59, 255))
    # Tile perspective lines
    for tx in range(-200, w + 400, 160):
        draw.line([(tx, floor_y), (tx + (tx - 540) * 1.5, h)], fill=(51, 65, 85, 160), width=2)
    for ty in [740, 830, 960, 1140, 1400]:
        draw.line([(0, ty), (w, ty)], fill=(51, 65, 85, 160), width=2)

    # 3. Sports Car Silhouette on display
    car_y = 520
    # Car body
    car_color = (220, 38, 38, 255) if not is_scam else (71, 85, 105, 255)
    # Roof and windshield
    draw.polygon([(340, car_y + 50), (460, car_y), (620, car_y), (740, car_y + 50)], fill=(15, 23, 42, 230), outline=(15, 20, 30, 255), width=4)
    # Main chassis
    draw.rounded_rectangle([(200, car_y + 50), (880, car_y + 130)], radius=20, fill=car_color, outline=(15, 20, 30, 255), width=5)
    # Wheels
    draw.ellipse([270, car_y + 100, 370, car_y + 190], fill=(15, 23, 42, 255), outline=(148, 163, 184, 255), width=6)
    draw.ellipse([710, car_y + 100, 810, car_y + 190], fill=(15, 23, 42, 255), outline=(148, 163, 184, 255), width=6)
    # Wheel rims
    draw.ellipse([300, car_y + 130, 340, car_y + 165], fill=(203, 213, 225, 255))
    draw.ellipse([740, car_y + 130, 780, car_y + 165], fill=(203, 213, 225, 255))

    # Price Banner on Car: 'НЕ БИТА, НЕ КРАШЕНА' vs 'РАСПИЛ ИЗ ДВУХ ЧАСТЕЙ'
    banner_w, banner_h = 480, 60
    bx = (w - banner_w) // 2
    by = car_y + 40
    draw.rounded_rectangle([(bx, by), (bx + banner_w, by + banner_h)], radius=12, fill=(234, 179, 8, 245) if not is_scam else (220, 38, 38, 245), outline=(15, 23, 42, 255), width=3)
    font_ban = get_font(FONT_BOLD, 24)
    b_txt = "РАСПИЛ СО СМОТАННЫМ ПРОБЕГОМ!" if is_scam else "ОДИН ВЛАДЕЛЕЦ • НЕ БИТА НЕ КРАШЕНА"
    bb_box = font_ban.getbbox(b_txt)
    draw.text((bx + (banner_w - (bb_box[2] - bb_box[0])) // 2, by + 12), b_txt, fill=(15, 23, 42) if not is_scam else (255, 255, 255), font=font_ban)

    return img


def render_office_location(is_climax: bool = False, size: Tuple[int, int] = (1080, 1920)) -> Image.Image:
    """Renders 2D vector Executive Office with city skyscrapers view."""
    w, h = size
    img = Image.new("RGBA", (w, h), (24, 28, 42, 255))
    draw = ImageDraw.Draw(img)

    # 1. Sky & Skyscrapers through floor-to-ceiling panoramic window
    for y in range(0, 720):
        ratio = y / 720.0
        r = int(18 + ratio * 20)
        g = int(24 + ratio * 28)
        b = int(45 + ratio * 45)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Skyscrapers outside
    skyline_y = 660
    towers = [(80, 420, 160), (280, 340, 180), (500, 480, 190), (730, 310, 170), (940, 400, 120)]
    for tx, th_val, tw_val in towers:
        draw.rectangle([(tx, skyline_y - th_val), (tx + tw_val, skyline_y + 40)], fill=(15, 20, 32, 255))
        for wy in range(skyline_y - th_val + 25, skyline_y, 40):
            for wx in range(tx + 20, tx + tw_val - 20, 35):
                draw.rectangle([(wx, wy), (wx + 15, wy + 20)], fill=(254, 240, 138, 190) if (wx + wy) % 5 == 0 else (71, 85, 105, 160))

    # Window frames
    draw.line([(360, 0), (360, 720)], fill=(51, 65, 85, 255), width=8)
    draw.line([(720, 0), (720, 720)], fill=(51, 65, 85, 255), width=8)
    draw.line([(0, 720), (w, 720)], fill=(51, 65, 85, 255), width=12)

    # 2. Executive Office Wall & Flooring
    draw.rectangle([(0, 720), (w, h)], fill=(20, 24, 33, 255))

    # Performance Board on Left Wall
    draw.rounded_rectangle([(80, 380), (340, 640)], radius=12, fill=(248, 250, 252, 240), outline=(15, 23, 42, 255), width=4)
    font_board = get_font(FONT_BOLD, 22)
    draw.text((105, 400), "KPI / ПРИБЫЛЬ", fill=(15, 23, 42), font=font_board)
    # Rising green chart vs crashing red chart
    c_col = (220, 38, 38, 255) if is_climax else (34, 197, 94, 255)
    points = [(110, 580), (160, 540), (220, 500), (280, 460), (320, 430)] if not is_climax else [(110, 440), (160, 470), (220, 520), (280, 570), (320, 610)]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=c_col, width=5)

    # Executive Desk
    desk_y = 800
    draw.rounded_rectangle([(120, desk_y), (960, desk_y + 130)], radius=16, fill=(45, 55, 72, 255), outline=(15, 23, 42, 255), width=5)
    # Laptop
    draw.rectangle([(440, desk_y - 80), (640, desk_y)], fill=(148, 163, 184, 255), outline=(15, 23, 42, 255), width=3)
    draw.rectangle([(450, desk_y - 72), (630, desk_y - 8)], fill=(15, 23, 42, 255))

    # Documents folder: 'ДОГОВОР' or 'ЗАЯВЛЕНИЕ НА УВОЛЬНЕНИЕ'
    draw.polygon([(200, desk_y + 15), (320, desk_y + 15), (340, desk_y + 85), (220, desk_y + 85)], fill=(254, 243, 199, 255), outline=(180, 83, 9, 255), width=3)
    font_doc = get_font(FONT_BOLD, 14)
    draw.text((230, desk_y + 45), "ОТКАЗАНО" if is_climax else "ДОГОВОР", fill=(220, 38, 38) if is_climax else (30, 41, 59), font=font_doc)

    return img


def render_bank_vault_location(size: Tuple[int, int] = (1080, 1920)) -> Image.Image:
    """Renders 2D vector Bank Vault / Savings scene with stacks of cash and gold bars."""
    w, h = size
    img = Image.new("RGBA", (w, h), (12, 24, 22, 255))
    draw = ImageDraw.Draw(img)

    # 1. Emerald luxury vault gradient
    for y in range(0, 740):
        ratio = y / 740.0
        r = int(8 + ratio * 14)
        g = int(28 + ratio * 38)
        b = int(24 + ratio * 30)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Huge metallic round bank vault door in background
    vx, vy, vr = 540, 480, 320
    draw.ellipse([vx - vr, vy - vr, vx + vr, vy + vr], fill=(51, 65, 85, 255), outline=(148, 163, 184, 255), width=14)
    draw.ellipse([vx - vr + 45, vy - vr + 45, vx + vr - 45, vy + vr - 45], fill=(30, 41, 59, 255), outline=(100, 116, 139, 255), width=6)
    # Vault wheel spokes
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        x2 = vx + int(math.cos(rad) * 160)
        y2 = vy + int(math.sin(rad) * 160)
        draw.line([(vx, vy), (x2, y2)], fill=(203, 213, 225, 255), width=14)
    draw.ellipse([vx - 55, vy - 55, vx + 55, vy + 55], fill=(148, 163, 184, 255), outline=(15, 23, 42, 255), width=6)

    # 2. Polished marble floor / table
    floor_y = 740
    draw.rectangle([(0, floor_y), (w, h)], fill=(15, 28, 26, 255))
    draw.line([(0, floor_y), (w, floor_y)], fill=(52, 211, 153, 200), width=4)

    # Stacks of cash & gold bars on left and right
    for stack_x in [110, 210, 770, 870]:
        for stack_i in range(4):
            by = floor_y - 25 - stack_i * 28
            draw.rounded_rectangle([(stack_x, by), (stack_x + 110, by + 26)], radius=6, fill=(34, 197, 94, 255), outline=(20, 83, 45, 255), width=3)
            # Paper strap
            draw.rectangle([(stack_x + 42, by), (stack_x + 68, by + 26)], fill=(254, 240, 138, 255))

    return img


def render_crash_report_location(size: Tuple[int, int] = (1080, 1920)) -> Image.Image:
    """Renders 2D vector Crash Scene / Red Autoteka Report Screen with wrecked car & danger tape."""
    w, h = size
    img = Image.new("RGBA", (w, h), (35, 10, 14, 255))
    draw = ImageDraw.Draw(img)

    # 1. Alarming crimson dark gradient
    for y in range(0, 760):
        ratio = y / 760.0
        r = int(55 + ratio * 45)
        g = int(10 + ratio * 12)
        b = int(14 + ratio * 16)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Hazard yellow-black caution stripe across top
    stripe_y = 260
    draw.rectangle([(0, stripe_y), (w, stripe_y + 52)], fill=(234, 179, 8, 255))
    for sx in range(-60, w + 60, 70):
        draw.polygon([(sx, stripe_y), (sx + 35, stripe_y), (sx + 10, stripe_y + 52), (sx - 25, stripe_y + 52)], fill=(15, 23, 42, 255))

    # Giant digital report card in background
    card_x1, card_y1, card_x2, card_y2 = 100, 340, 980, 760
    draw.rounded_rectangle([(card_x1, card_y1), (card_x2, card_y2)], radius=24, fill=(18, 12, 18, 245), outline=(239, 68, 68, 255), width=6)

    font_hdr = get_font(FONT_IMPACT, 44)
    hdr_txt = "ОТЧЁТ ПО VIN: НАЙДЕН ТОТАЛ!"
    bb = font_hdr.getbbox(hdr_txt)
    draw.text(((w - (bb[2] - bb[0])) // 2, card_y1 + 22), hdr_txt, fill=(248, 113, 113), font=font_hdr)

    # Wrecked split car icon inside card (two halves separated by jagged crack!)
    cy = card_y1 + 190
    # Left half (red)
    draw.rounded_rectangle([(190, cy), (490, cy + 95)], radius=16, fill=(220, 38, 38, 255), outline=(255, 255, 255, 220), width=4)
    draw.ellipse([240, cy + 65, 330, cy + 145], fill=(15, 23, 42, 255), outline=(203, 213, 225, 255), width=5)
    # Right half (blue - mismatched weld!)
    draw.rounded_rectangle([(570, cy + 12), (880, cy + 102)], radius=16, fill=(59, 130, 246, 255), outline=(255, 255, 255, 220), width=4)
    draw.ellipse([740, cy + 72, 830, cy + 152], fill=(15, 23, 42, 255), outline=(203, 213, 225, 255), width=5)
    # Lightning weld crack between halves
    draw.line([(530, cy - 30), (505, cy + 35), (550, cy + 65), (520, cy + 145)], fill=(250, 204, 21, 255), width=8)

    # Red alert badges inside report
    font_sub = get_font(FONT_BOLD, 30)
    draw.text((155, card_y1 + 350), "[!] ПРОБЕГ СКРУЧЕН: -214 000 КМ  |  ДТП: 4 РАЗА", fill=(254, 202, 202), font=font_sub)

    # Dark asphalt ground
    draw.rectangle([(0, 760), (w, h)], fill=(20, 14, 18, 255))
    return img


def render_rainy_bus_stop_location(size: Tuple[int, int] = (1080, 1920)) -> Image.Image:
    """Renders 2D vector Moody Night Bus Stop in the Rain (for broke/reality-check endings)."""
    w, h = size
    img = Image.new("RGBA", (w, h), (15, 23, 38, 255))
    draw = ImageDraw.Draw(img)

    # 1. Moody stormy blue-gray night sky
    for y in range(0, 720):
        ratio = y / 720.0
        r = int(15 + ratio * 16)
        g = int(23 + ratio * 24)
        b = int(38 + ratio * 34)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Storm clouds
    for cx, cy, cr in [(200, 200, 110), (340, 180, 130), (760, 210, 120), (910, 190, 100)]:
        draw.ellipse([cx - cr, cy - cr // 2, cx + cr, cy + cr // 2], fill=(30, 41, 59, 230))

    # Distant muted apartment blocks
    for bx, bh, bw in [(20, 260, 180), (220, 320, 190), (680, 290, 180), (880, 340, 190)]:
        draw.rectangle([(bx, 720 - bh), (bx + bw, 720)], fill=(20, 28, 42, 255))
        for wy in range(720 - bh + 30, 700, 45):
            for wx in range(bx + 25, bx + bw - 25, 40):
                if (wx * 3 + wy) % 11 == 0:
                    draw.rectangle([(wx, wy), (wx + 16, wy + 22)], fill=(148, 163, 184, 150))

    # 2. Bus Stop Shelter in Center
    sx1, sy1, sx2, sy2 = 140, 390, 940, 750
    # Glass back panel
    draw.rectangle([(sx1 + 20, sy1 + 30), (sx2 - 20, sy2)], fill=(51, 65, 85, 160), outline=(100, 116, 139, 255), width=4)
    # Metal shelter roof
    draw.rounded_rectangle([(sx1 - 20, sy1), (sx2 + 20, sy1 + 42)], radius=10, fill=(71, 85, 105, 255), outline=(15, 23, 42, 255), width=4)
    # Support pillars
    draw.rectangle([(sx1 + 10, sy1 + 42), (sx1 + 32, sy2 + 80)], fill=(71, 85, 105, 255))
    draw.rectangle([(sx2 - 32, sy1 + 42), (sx2 - 10, sy2 + 80)], fill=(71, 85, 105, 255))

    # Blue Bus Stop Sign 'А' on pole (right)
    draw.line([(970, 290), (970, 820)], fill=(148, 163, 184, 255), width=10)
    draw.rounded_rectangle([(925, 290), (1015, 390)], radius=12, fill=(37, 99, 235, 255), outline=(255, 255, 255, 255), width=4)
    font_a = get_font(FONT_IMPACT, 56)
    draw.text((954, 305), "А", fill=(255, 255, 255), font=font_a)

    # Glowing Schedule Display inside shelter
    draw.rounded_rectangle([(240, 460), (840, 540)], radius=12, fill=(15, 23, 42, 240), outline=(56, 189, 248, 220), width=3)
    font_bus = get_font(FONT_BOLD, 30)
    draw.text((285, 482), "АВТОБУС №42 • ПРИБЫТИЕ: 45 МИН", fill=(250, 204, 21), font=font_bus)

    # Wooden Bench
    draw.rectangle([(260, 680), (820, 715)], fill=(120, 53, 15, 255), outline=(15, 23, 42, 255), width=3)

    # 3. Wet Asphalt & Street Curb
    draw.rectangle([(0, 750), (w, h)], fill=(18, 24, 34, 255))
    draw.rectangle([(0, 750), (w, 780)], fill=(40, 52, 70, 255))
    draw.line([(0, 750), (w, 750)], fill=(100, 116, 139, 200), width=3)

    return img
