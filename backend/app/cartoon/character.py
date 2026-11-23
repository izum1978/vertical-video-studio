"""
Cartoon Character Generator (2D Vector Character Rig v2).
Features:
- Modular facial expressions (confident, smug, alert, shocked, devastated, angry)
- Lip-sync mouth flaps (closed, half, open)
- Modular hairstyles (bald/bean, messy bedhead, modern undercut)
- Modular outfits (hoodie in custom colors, business suit with tie, casual tee)
- Modular arm gestures & props:
    * 'relax': arms down
    * 'hands_on_head': clutching head in horror/panic
    * 'holding_phone': holding glowing smartphone
    * 'holding_money': holding fan of cash banknotes
    * 'pointing': pointing finger
Output: 1080x1920 transparent RGBA.
"""

from typing import Optional, Tuple
from PIL import Image, ImageDraw


class CharacterRig:
    def __init__(self, base_scale: float = 1.0):
        self.scale = base_scale

    def render(
        self,
        mood: str = "confident",
        mouth_state: str = "closed",
        gesture: str = "relax",  # "relax", "hands_on_head", "holding_phone", "holding_money", "pointing"
        outfit: str = "hoodie",  # "hoodie", "suit", "casual"
        outfit_color: Tuple[int, int, int] = (249, 115, 22),  # Default orange
        hair_style: str = "messy",  # "bald", "messy", "undercut"
        blink: bool = False,
        offset_y: int = 0,
        size: Tuple[int, int] = (1080, 1920),
    ) -> Image.Image:
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx = 540
        cy = 1200 + offset_y
        outline_col = (18, 22, 30, 255)
        outline_w = 8
        skin_col = (250, 247, 242, 255)

        # -------------------------------------------------------------
        # 1. TORSO & OUTFIT
        # -------------------------------------------------------------
        body_top_y = cy + 190

        if outfit == "suit":
            # Dark business suit jacket
            draw.polygon(
                [
                    (cx - 290, 1920),
                    (cx - 270, body_top_y + 120),
                    (cx - 160, body_top_y),
                    (cx + 160, body_top_y),
                    (cx + 270, body_top_y + 120),
                    (cx + 290, 1920),
                ],
                fill=(30, 41, 59, 255),
                outline=outline_col,
            )
            # White shirt V-neck
            draw.polygon([(cx - 70, body_top_y), (cx, body_top_y + 180), (cx + 70, body_top_y)], fill=(255, 255, 255, 255), outline=outline_col)
            # Red tie
            draw.polygon([(cx - 16, body_top_y + 30), (cx + 16, body_top_y + 30), (cx + 24, body_top_y + 220), (cx, body_top_y + 260), (cx - 24, body_top_y + 220)], fill=(220, 38, 38, 255), outline=outline_col)

        else:
            # Hoodie / Casual (Custom Color)
            col_rgba = (outfit_color[0], outfit_color[1], outfit_color[2], 255)
            draw.polygon(
                [
                    (cx - 290, 1920),
                    (cx - 270, body_top_y + 120),
                    (cx - 160, body_top_y),
                    (cx + 160, body_top_y),
                    (cx + 270, body_top_y + 120),
                    (cx + 290, 1920),
                ],
                fill=col_rgba,
                outline=outline_col,
            )
            # Inner neck shirt
            draw.polygon([(cx - 120, body_top_y), (cx, body_top_y + 110), (cx + 120, body_top_y)], fill=(30, 41, 59, 255), outline=outline_col)
            # White drawstrings
            draw.line([(cx - 45, body_top_y + 60), (cx - 45, body_top_y + 220)], fill=(255, 255, 255), width=7)
            draw.line([(cx + 45, body_top_y + 60), (cx + 45, body_top_y + 220)], fill=(255, 255, 255), width=7)

        # -------------------------------------------------------------
        # 2. HEAD (BEAN SHAPE)
        # -------------------------------------------------------------
        head_w, head_h = 210, 240
        head_box = [cx - head_w, cy - head_h, cx + head_w, cy + head_h]
        draw.ellipse(head_box, fill=skin_col, outline=outline_col, width=outline_w)

        # Subtle cheeks
        draw.ellipse([cx - 170, cy + 30, cx - 110, cy + 70], fill=(254, 205, 211, 160))
        draw.ellipse([cx + 110, cy + 30, cx + 170, cy + 70], fill=(254, 205, 211, 160))

        # -------------------------------------------------------------
        # 3. HAIRSTYLE
        # -------------------------------------------------------------
        hair_col = (30, 41, 59, 255)
        if hair_style == "messy":
            tufts = [
                [(cx - 160, cy - 180), (cx - 190, cy - 250), (cx - 120, cy - 210)],
                [(cx - 120, cy - 210), (cx - 130, cy - 290), (cx - 50, cy - 230)],
                [(cx - 50, cy - 230), (cx, cy - 310), (cx + 50, cy - 230)],
                [(cx + 50, cy - 230), (cx + 130, cy - 290), (cx + 120, cy - 210)],
                [(cx + 120, cy - 210), (cx + 190, cy - 250), (cx + 160, cy - 180)],
            ]
            for t_poly in tufts:
                draw.polygon(t_poly, fill=hair_col, outline=outline_col)
        elif hair_style == "undercut":
            # Modern side sweep
            draw.chord([cx - 190, cy - 250, cx + 190, cy - 110], start=180, end=360, fill=hair_col, outline=outline_col)

        # -------------------------------------------------------------
        # 4. EYES & BROWS BY MOOD
        # -------------------------------------------------------------
        eye_y = cy - 20

        if blink:
            # Closed blinking eyelids
            draw.line([(cx - 100, eye_y), (cx - 40, eye_y)], fill=outline_col, width=8)
            draw.line([(cx + 40, eye_y), (cx + 100, eye_y)], fill=outline_col, width=8)
            draw.arc([cx - 105, eye_y - 60, cx - 35, eye_y - 30], start=200, end=340, fill=outline_col, width=7)
            draw.arc([cx + 35, eye_y - 60, cx + 105, eye_y - 30], start=200, end=340, fill=outline_col, width=7)

        elif mood == "smug":
            draw.arc([cx - 95, eye_y - 25, cx - 45, eye_y + 25], start=180, end=360, fill=outline_col, width=8)
            draw.arc([cx + 45, eye_y - 25, cx + 95, eye_y + 25], start=180, end=360, fill=outline_col, width=8)
            draw.line([(cx - 110, eye_y - 50), (cx - 35, eye_y - 35)], fill=outline_col, width=7)
            draw.line([(cx + 35, eye_y - 35), (cx + 110, eye_y - 50)], fill=outline_col, width=7)

        elif mood == "alert":
            draw.ellipse([cx - 95, eye_y - 35, cx - 35, eye_y + 25], fill=(255, 255, 255), outline=outline_col, width=6)
            draw.ellipse([cx + 35, eye_y - 35, cx + 95, eye_y + 25], fill=(255, 255, 255), outline=outline_col, width=6)
            draw.ellipse([cx - 75, eye_y - 15, cx - 55, eye_y + 5], fill=outline_col)
            draw.ellipse([cx + 55, eye_y - 15, cx + 75, eye_y + 5], fill=outline_col)
            draw.arc([cx - 105, eye_y - 75, cx - 35, eye_y - 40], start=200, end=340, fill=outline_col, width=7)
            draw.arc([cx + 35, eye_y - 75, cx + 105, eye_y - 40], start=200, end=340, fill=outline_col, width=7)
            draw.ellipse([cx + 130, cy - 60, cx + 150, cy - 35], fill=(56, 189, 248, 230))

        elif mood == "shocked":
            draw.ellipse([cx - 120, eye_y - 50, cx - 25, eye_y + 45], fill=(255, 255, 255), outline=outline_col, width=7)
            draw.ellipse([cx + 25, eye_y - 50, cx + 120, eye_y + 45], fill=(255, 255, 255), outline=outline_col, width=7)
            draw.ellipse([cx - 78, eye_y - 8, cx - 64, eye_y + 6], fill=(220, 38, 38, 255))
            draw.ellipse([cx + 64, eye_y - 8, cx + 78, eye_y + 6], fill=(220, 38, 38, 255))
            draw.arc([cx - 125, eye_y - 95, cx - 20, eye_y - 55], start=200, end=340, fill=outline_col, width=8)
            draw.arc([cx + 20, eye_y - 95, cx + 125, eye_y - 55], start=200, end=340, fill=outline_col, width=8)
            draw.ellipse([cx + 135, cy - 90, cx + 160, cy - 60], fill=(56, 189, 248, 240))
            draw.ellipse([cx - 160, cy - 80, cx - 135, cy - 50], fill=(56, 189, 248, 240))

        elif mood == "devastated":
            draw.ellipse([cx - 85, eye_y - 20, cx - 45, eye_y + 20], fill=(71, 85, 105, 255), outline=outline_col, width=5)
            draw.ellipse([cx + 45, eye_y - 20, cx + 85, eye_y + 20], fill=(71, 85, 105, 255), outline=outline_col, width=5)
            draw.line([(cx - 105, eye_y - 35), (cx - 35, eye_y - 55)], fill=outline_col, width=7)
            draw.line([(cx + 35, eye_y - 55), (cx + 105, eye_y - 35)], fill=outline_col, width=7)
            # Tear
            draw.polygon([(cx - 65, cy + 20), (cx - 75, cy + 80), (cx - 55, cy + 80)], fill=(56, 189, 248, 230))
            draw.ellipse([cx - 75, cy + 70, cx - 55, cy + 95], fill=(56, 189, 248, 230))

        else:  # confident
            draw.arc([cx - 105, eye_y - 65, cx - 35, eye_y - 35], start=200, end=340, fill=outline_col, width=7)
            draw.arc([cx + 35, eye_y - 65, cx + 105, eye_y - 35], start=200, end=340, fill=outline_col, width=7)
            draw.ellipse([cx - 85, eye_y - 25, cx - 55, eye_y + 25], fill=outline_col)
            draw.ellipse([cx + 55, eye_y - 25, cx + 85, eye_y + 25], fill=outline_col)
            draw.ellipse([cx - 78, eye_y - 20, cx - 68, eye_y - 10], fill=(255, 255, 255))
            draw.ellipse([cx + 62, eye_y - 20, cx + 72, eye_y - 10], fill=(255, 255, 255))

        # -------------------------------------------------------------
        # 5. MOUTH FLAPS
        # -------------------------------------------------------------
        mouth_y = cy + 75
        if mouth_state == "closed":
            if mood == "smug":
                draw.arc([cx - 20, mouth_y - 20, cx + 60, mouth_y + 25], start=20, end=160, fill=outline_col, width=7)
            elif mood == "shocked":
                draw.ellipse([cx - 35, mouth_y - 15, cx + 35, mouth_y + 55], fill=outline_col)
            elif mood == "devastated":
                draw.line([(cx - 40, mouth_y + 15), (cx + 40, mouth_y + 15)], fill=outline_col, width=6)
            else:
                draw.arc([cx - 45, mouth_y - 20, cx + 45, mouth_y + 25], start=20, end=160, fill=outline_col, width=7)

        elif mouth_state == "half":
            draw.chord([cx - 40, mouth_y - 15, cx + 40, mouth_y + 45], start=0, end=180, fill=outline_col)
            draw.chord([cx - 25, mouth_y + 15, cx + 25, mouth_y + 45], start=0, end=180, fill=(244, 63, 94, 255))

        elif mouth_state == "open":
            draw.chord([cx - 55, mouth_y - 20, cx + 55, mouth_y + 70], start=0, end=180, fill=outline_col)
            draw.chord([cx - 45, mouth_y - 20, cx + 45, mouth_y + 10], start=0, end=180, fill=(255, 255, 255, 255))
            draw.chord([cx - 35, mouth_y + 20, cx + 35, mouth_y + 70], start=0, end=180, fill=(244, 63, 94, 255))

        # -------------------------------------------------------------
        # 6. MODULAR GESTURES & HANDS
        # -------------------------------------------------------------
        sleeve_col = (outfit_color[0], outfit_color[1], outfit_color[2], 255) if outfit != "suit" else (30, 41, 59, 255)

        if gesture == "hands_on_head":
            # Both hands clutching the sides of the head in utter panic
            # Left arm & hand
            draw.polygon([(cx - 260, cy + 300), (cx - 220, cy), (cx - 170, cy - 30), (cx - 210, cy + 300)], fill=sleeve_col, outline=outline_col)
            # Left white mitten hand over ear
            draw.ellipse([cx - 230, cy - 70, cx - 160, cy + 20], fill=skin_col, outline=outline_col, width=6)

            # Right arm & hand
            draw.polygon([(cx + 260, cy + 300), (cx + 220, cy), (cx + 170, cy - 30), (cx + 210, cy + 300)], fill=sleeve_col, outline=outline_col)
            # Right white mitten hand over ear
            draw.ellipse([cx + 160, cy - 70, cx + 230, cy + 20], fill=skin_col, outline=outline_col, width=6)

        elif gesture == "holding_phone":
            # Right arm raised with glowing smartphone
            draw.polygon([(cx + 220, cy + 350), (cx + 230, cy + 100), (cx + 180, cy + 110), (cx + 160, cy + 350)], fill=sleeve_col, outline=outline_col)
            # Hand holding phone
            px, py = cx + 210, cy + 80
            draw.ellipse([px - 25, py - 20, px + 35, py + 40], fill=skin_col, outline=outline_col, width=5)
            # Phone body (black rounded rect with screen glow)
            draw.rounded_rectangle([(px + 10, py - 90), (px + 90, py + 30)], radius=12, fill=(15, 23, 42, 255), outline=(100, 116, 139, 255), width=4)
            # Glowing screen
            screen_col = (239, 68, 68, 240) if mood == "shocked" else (56, 189, 248, 240)
            draw.rectangle([(px + 18, py - 80), (px + 82, py + 18)], fill=screen_col)

        elif gesture == "holding_money":
            # Right arm holding fan of cash banknotes
            draw.polygon([(cx + 220, cy + 350), (cx + 220, cy + 120), (cx + 170, cy + 130), (cx + 160, cy + 350)], fill=sleeve_col, outline=outline_col)
            # Hand
            hx, hy = cx + 200, cy + 110
            draw.ellipse([hx - 25, hy - 20, hx + 35, hy + 35], fill=skin_col, outline=outline_col, width=5)
            # Banknotes fan
            draw.polygon([(hx, hy - 80), (hx + 80, hy - 60), (hx + 70, hy - 10), (hx - 10, hy - 30)], fill=(34, 197, 94, 255), outline=(22, 101, 52, 255), width=3)
            draw.polygon([(hx - 30, hy - 70), (hx + 50, hy - 80), (hx + 55, hy - 30), (hx - 25, hy - 20)], fill=(74, 222, 128, 255), outline=(22, 101, 52, 255), width=3)

        elif gesture == "pointing":
            # Arm pointing forward/right
            draw.polygon([(cx + 220, cy + 350), (cx + 280, cy + 180), (cx + 230, cy + 160), (cx + 170, cy + 350)], fill=sleeve_col, outline=outline_col)
            # Pointing finger
            draw.ellipse([cx + 260, cy + 150, cx + 320, cy + 200], fill=skin_col, outline=outline_col, width=5)
            draw.rounded_rectangle([(cx + 300, cy + 160), (cx + 360, cy + 185)], radius=10, fill=skin_col, outline=outline_col, width=4)

        return img
