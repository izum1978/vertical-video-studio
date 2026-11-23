import math
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30

def _get_font(name: str, size: int):
    for f in [name, "arialbd.ttf", "arial.ttf", "segoeui.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            continue
    return ImageFont.load_default()

def _draw_ticket_hud(scene_idx: int, total_scenes: int, badge: str, title: str, subtitle: str, glow_color=(235, 60, 50)) -> Image.Image:
    cw, ch = 800, 160
    card = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card)
    c_draw.rounded_rectangle([20, 20, cw + 15, ch + 15], radius=18, fill=(0, 0, 0, 130))
    c_draw.rounded_rectangle([15, 12, cw, ch + 2], radius=18, fill=(245, 246, 250, 255))
    c_draw.rounded_rectangle([15, 12, 190, ch + 2], radius=18, fill=glow_color + (255,))
    c_draw.rectangle([160, 12, 190, ch + 2], fill=glow_color + (255,))
    for py in range(20, ch, 14):
        c_draw.ellipse([188, py, 194, py + 6], fill=(20, 24, 34, 200))
    f_num = _get_font("arialbd.ttf", 64)
    f_tit = _get_font("arialbd.ttf", 36)
    f_sub = _get_font("arialbd.ttf", 22)
    num_str = f"{scene_idx + 1:02d}"
    c_draw.text((45, 45), num_str, fill=(255, 255, 255, 255), font=f_num)
    c_draw.text((220, 34), title.upper()[:24], fill=(20, 25, 38, 255), font=f_tit)
    c_draw.text((222, 94), subtitle.upper()[:34], fill=(110, 120, 140, 255), font=f_sub)
    return card.rotate(1.8, resample=Image.Resampling.BICUBIC, expand=True)

def render_2d_window_stalker(duration: float, out_path: Path, scene_meta: dict, scene_idx: int = 0, total_scenes: int = 5):
    total_frames = max(1, int(duration * FPS))
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    card = _draw_ticket_hud(scene_idx, total_scenes, scene_meta.get("badge", "ПРАВИЛО 01"), scene_meta.get("title", "ОКНО ВО ТЬМУ"), scene_meta.get("subtitle", "НЕ ПОДХОДИ К СТЕКЛУ"), glow_color=(210, 40, 40))
    rain_rng = random.Random(42)
    rain_drops = [(rain_rng.randint(0, W), rain_rng.randint(-400, H), rain_rng.uniform(18, 32)) for _ in range(75)]
    for f in range(total_frames):
        t = f / FPS
        flash_intensity = 0.85 if (1.1 < (t % 3.2) < 1.3 or 2.4 < (t % 4.8) < 2.52) else 0.0
        wall_col = (int(10 + flash_intensity * 70), int(12 + flash_intensity * 80), int(18 + flash_intensity * 110), 255)
        frame = Image.new("RGBA", (W, H), wall_col)
        draw = ImageDraw.Draw(frame)
        for sx in range(0, W, 48):
            draw.line([(sx, 0), (sx, H)], fill=(int(wall_col[0] * 0.85), int(wall_col[1] * 0.85), int(wall_col[2] * 0.85), 255), width=2)
        wx1, wy1, wx2, wy2 = 180, 360, 900, 1440
        sky_col = (int(4 + flash_intensity * 140), int(6 + flash_intensity * 180), int(14 + flash_intensity * 220), 255)
        draw.rectangle([wx1, wy1, wx2, wy2], fill=sky_col)
        stalker_alpha = int(70 + flash_intensity * 185)
        stalker_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d_stalk = ImageDraw.Draw(stalker_layer)
        st_x = 540 + int(math.sin(t * 1.5) * 8)
        st_y = 660
        d_stalk.ellipse([st_x - 70, st_y, st_x + 70, st_y + 190], fill=(4, 5, 8, stalker_alpha))
        d_stalk.polygon([(st_x - 140, st_y + 200), (st_x + 140, st_y + 200), (st_x + 180, wy2), (st_x - 180, wy2)], fill=(4, 5, 8, stalker_alpha))
        for finger_i in range(4):
            fy = wy1 + 620 + finger_i * 26
            d_stalk.line([(wx1 + 100, fy), (wx1 + 160, fy + 12)], fill=(4, 5, 8, stalker_alpha), width=6)
        eye_col = (255, 50, 30, int(210 + math.sin(t * 6.0) * 45)) if (f % 50 > 6) else (0, 0, 0, 0)
        d_stalk.ellipse([st_x - 32, st_y + 80, st_x - 16, st_y + 102], fill=eye_col)
        d_stalk.ellipse([st_x + 16, st_y + 80, st_x + 32, st_y + 102], fill=eye_col)
        frame = Image.alpha_composite(frame, stalker_layer)
        draw = ImageDraw.Draw(frame)
        for r_x, r_y, r_spd in rain_drops:
            cur_y = int((r_y + t * r_spd * 60) % (wy2 - wy1) + wy1)
            cur_x = int(r_x % (wx2 - wx1) + wx1 + (cur_y - wy1) * 0.18)
            draw.line([(cur_x, cur_y), (cur_x + 3, cur_y + 28)], fill=(180, 205, 235, int(45 + flash_intensity * 60)), width=2)
        frame_color = (28, 18, 14, 255)
        draw.rectangle([wx1 - 24, wy1 - 24, wx2 + 24, wy1], fill=frame_color)
        draw.rectangle([wx1 - 24, wy2, wx2 + 24, wy2 + 36], fill=frame_color)
        draw.rectangle([wx1 - 24, wy1, wx1, wy2], fill=frame_color)
        draw.rectangle([wx2, wy1, wx2 + 24, wy2], fill=frame_color)
        draw.rectangle([(wx1 + wx2) // 2 - 12, wy1, (wx1 + wx2) // 2 + 12, wy2], fill=frame_color)
        draw.rectangle([wx1, (wy1 + wy2) // 2 - 10, wx2, (wy1 + wy2) // 2 + 10], fill=frame_color)
        draw.rectangle([0, 1500, W, H], fill=(12, 10, 14, 255))
        frame.paste(card, (140, 100), card)
        proc.stdin.write(frame.tobytes("raw", "RGBA"))
    proc.stdin.close()
    proc.wait()

def render_2d_corridor_flashlight(duration: float, out_path: Path, scene_meta: dict, scene_idx: int = 1, total_scenes: int = 5):
    total_frames = max(1, int(duration * FPS))
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    card = _draw_ticket_hud(scene_idx, total_scenes, scene_meta.get("badge", "ПРАВИЛО 02"), scene_meta.get("title", "ТЕМНЫЙ КОРИДОР"), scene_meta.get("subtitle", "ЛУЧ ФОНАРЯ ДРОЖИТ"), glow_color=(220, 90, 30))
    vp_x, vp_y = 540, 680
    for f in range(total_frames):
        t = f / FPS
        frame = Image.new("RGBA", (W, H), (10, 12, 16, 255))
        draw = ImageDraw.Draw(frame)
        # Perspective walls
        draw.polygon([(0, 0), (W, 0), (vp_x + 160, vp_y - 120), (vp_x - 160, vp_y - 120)], fill=(16, 18, 24, 255)) # ceiling
        draw.polygon([(0, H), (W, H), (vp_x + 160, vp_y + 120), (vp_x - 160, vp_y + 120)], fill=(24, 18, 14, 255)) # floor
        # Floor lines
        for fx in range(-400, W + 600, 160):
            draw.line([(fx, H), (vp_x, vp_y + 120)], fill=(34, 26, 20, 255), width=2)
        # Doors along hallway
        draw.polygon([(80, 520), (180, 590), (180, 1340), (80, 1500)], fill=(38, 25, 18, 255), outline=(50, 32, 22, 255), width=3)
        draw.polygon([(W - 80, 520), (W - 180, 590), (W - 180, 1340), (W - 80, 1500)], fill=(38, 25, 18, 255), outline=(50, 32, 22, 255), width=3)
        # Flashlight beam cone swaying nervously
        fl_x = 540 + int(math.sin(t * 2.8) * 90 + math.cos(t * 4.2) * 40)
        fl_y = 760 + int(math.cos(t * 2.2) * 50)
        beam_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d_beam = ImageDraw.Draw(beam_layer)
        d_beam.polygon([(540, 1920), (fl_x - 220, fl_y - 60), (fl_x + 220, fl_y + 120)], fill=(255, 240, 170, 48))
        d_beam.ellipse([fl_x - 190, fl_y - 110, fl_x + 190, fl_y + 110], fill=(255, 245, 190, 85))
        d_beam.ellipse([fl_x - 90, fl_y - 55, fl_x + 90, fl_y + 55], fill=(255, 255, 230, 140))
        # Creeping shadow silhouette at end of corridor
        shad_x = int(vp_x - 40 + math.sin(t * 1.8) * 60)
        shad_y = vp_y + 40
        d_beam.ellipse([shad_x - 30, shad_y - 90, shad_x + 30, shad_y - 20], fill=(6, 6, 8, 230))
        d_beam.polygon([(shad_x - 45, shad_y - 20), (shad_x + 45, shad_y - 20), (shad_x + 60, shad_y + 80), (shad_x - 60, shad_y + 80)], fill=(6, 6, 8, 230))
        # Shadow eyes in flashlight beam
        d_beam.ellipse([shad_x - 12, shad_y - 60, shad_x - 4, shad_y - 48], fill=(255, 240, 120, 220))
        d_beam.ellipse([shad_x + 4, shad_y - 60, shad_x + 12, shad_y - 48], fill=(255, 240, 120, 220))
        frame = Image.alpha_composite(frame, beam_layer)
        frame.paste(card, (140, 100), card)
        proc.stdin.write(frame.tobytes("raw", "RGBA"))
    proc.stdin.close()
    proc.wait()

def render_2d_door_breach(duration: float, out_path: Path, scene_meta: dict, scene_idx: int = 2, total_scenes: int = 5):
    total_frames = max(1, int(duration * FPS))
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    card = _draw_ticket_hud(scene_idx, total_scenes, scene_meta.get("badge", "ПРАВИЛО 03"), scene_meta.get("title", "ЗА ДВЕРЬЮ"), scene_meta.get("subtitle", "РУЧКА МЕДЛЕННО ОПУСКАЕТСЯ"), glow_color=(220, 30, 70))
    for f in range(total_frames):
        t = f / FPS
        frame = Image.new("RGBA", (W, H), (14, 16, 22, 255))
        draw = ImageDraw.Draw(frame)
        # Door frame & panels
        dx1, dy1, dx2, dy2 = 200, 280, 880, 1680
        draw.rectangle([dx1 - 30, dy1 - 30, dx2 + 30, dy2 + 10], fill=(26, 18, 14, 255))
        draw.rectangle([dx1, dy1, dx2, dy2], fill=(42, 28, 20, 255))
        # Door panels
        for py_box in [dy1 + 40, dy1 + 460, dy1 + 880]:
            draw.rounded_rectangle([dx1 + 40, py_box, dx1 + 300, py_box + 360], radius=12, fill=(34, 22, 16, 255), outline=(52, 34, 26, 255), width=4)
            draw.rounded_rectangle([dx2 - 300, py_box, dx2 - 40, py_box + 360], radius=12, fill=(34, 22, 16, 255), outline=(52, 34, 26, 255), width=4)
        # Door handle rotating down
        hx, hy = dx2 - 100, dy1 + 720
        h_angle = min(35.0, max(0.0, math.sin(t * 3.5) * 35.0))
        rad = math.radians(h_angle)
        draw.ellipse([hx - 25, hy - 25, hx + 25, hy + 25], fill=(180, 150, 70, 255))
        h_end_x = int(hx - 85 * math.cos(rad))
        h_end_y = int(hy + 85 * math.sin(rad))
        draw.line([(hx, hy), (h_end_x, h_end_y)], fill=(210, 175, 80, 255), width=18)
        draw.ellipse([h_end_x - 12, h_end_y - 12, h_end_x + 12, h_end_y + 12], fill=(210, 175, 80, 255))
        # Dark mist leaking from bottom door crack
        for mx in range(dx1, dx2, 35):
            mist_h = int(30 + math.sin(t * 4.0 + mx) * 20)
            draw.line([(mx, dy2), (mx + int(math.sin(t * 2.0) * 15), dy2 + mist_h)], fill=(80, 40, 100, 160), width=8)
        # Pale creepy fingers curling over door edge if t > 1.5
        if t > 1.2:
            f_prog = min(1.0, (t - 1.2) * 1.5)
            fx_base = dx1 - 10 + int(f_prog * 35)
            for fi in range(4):
                f_y = dy1 + 540 + fi * 38
                draw.polygon([(dx1 - 5, f_y), (fx_base + 35, f_y + 4), (fx_base + 30, f_y + 22), (dx1 - 5, f_y + 18)], fill=(225, 220, 215, 255))
                draw.polygon([(fx_base + 30, f_y + 4), (fx_base + 55, f_y + 14), (fx_base + 35, f_y + 22)], fill=(40, 30, 30, 255)) # black claw
        frame.paste(card, (140, 100), card)
        proc.stdin.write(frame.tobytes("raw", "RGBA"))
    proc.stdin.close()
    proc.wait()

def render_2d_candle_paranoia(duration: float, out_path: Path, scene_meta: dict, scene_idx: int = 3, total_scenes: int = 5):
    total_frames = max(1, int(duration * FPS))
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    card = _draw_ticket_hud(scene_idx, total_scenes, scene_meta.get("badge", "АТМОСФЕРА"), scene_meta.get("title", "ДРОЖАЩАЯ СВЕЧА"), scene_meta.get("subtitle", "ТЕНЬ НА СТЕНЕ ОЖИВАЕТ"), glow_color=(240, 140, 20))
    for f in range(total_frames):
        t = f / FPS
        frame = Image.new("RGBA", (W, H), (12, 10, 16, 255))
        draw = ImageDraw.Draw(frame)
        cx, cy = 540, 1180
        # Giant shadow on back wall
        shad_twist = (t > duration * 0.45)
        sw_head_x = 540 + int(math.sin(t * 1.2) * 20)
        sw_head_y = 520
        draw.ellipse([sw_head_x - 140, sw_head_y - 140, sw_head_x + 140, sw_head_y + 140], fill=(6, 5, 8, 240))
        draw.polygon([(sw_head_x - 260, 1100), (sw_head_x + 260, 1100), (sw_head_x + 320, 1400), (sw_head_x - 320, 1400)], fill=(6, 5, 8, 240))
        if shad_twist:
            # Shadow turns its head and looks with piercing white dots
            draw.ellipse([sw_head_x - 45, sw_head_y - 20, sw_head_x - 30, sw_head_y - 5], fill=(255, 255, 255, 240))
            draw.ellipse([sw_head_x + 30, sw_head_y - 20, sw_head_x + 45, sw_head_y - 5], fill=(255, 255, 255, 240))
        # Warm golden light halo
        flicker = 1.0 + 0.15 * math.sin(t * 14.0) + 0.08 * math.cos(t * 22.0)
        light_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d_light = ImageDraw.Draw(light_layer)
        for r_g in range(int(360 * flicker), 30, -30):
            d_light.ellipse([cx - r_g, cy - r_g, cx + r_g, cy + r_g], fill=(255, 180, 60, int((1.0 - r_g / (360 * flicker)) * 50)))
        frame = Image.alpha_composite(frame, light_layer)
        draw = ImageDraw.Draw(frame)
        # Table & candle
        draw.rectangle([0, 1340, W, H], fill=(24, 16, 12, 255))
        draw.rectangle([cx - 25, cy + 40, cx + 25, cy + 180], fill=(225, 220, 205, 255)) # wax candle
        draw.ellipse([cx - 45, cy + 170, cx + 45, cy + 200], fill=(160, 130, 60, 255)) # brass base
        # Flame
        flame_y = cy - int(math.sin(t * 18.0) * 8)
        draw.ellipse([cx - 18, flame_y - 35, cx + 18, flame_y + 35], fill=(255, 140, 20, 255))
        draw.ellipse([cx - 9, flame_y - 20, cx + 9, flame_y + 25], fill=(255, 245, 120, 255))
        frame.paste(card, (140, 100), card)
        proc.stdin.write(frame.tobytes("raw", "RGBA"))
    proc.stdin.close()
    proc.wait()

def render_2d_peephole_stalker(duration: float, out_path: Path, scene_meta: dict, scene_idx: int = 4, total_scenes: int = 5):
    total_frames = max(1, int(duration * FPS))
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    card = _draw_ticket_hud(scene_idx, total_scenes, scene_meta.get("badge", "ФИНАЛ"), scene_meta.get("title", "ВЗГЛЯД В ГЛАЗОК"), scene_meta.get("subtitle", "ОНО СТОИТ ЗА ДВЕРЬЮ"), glow_color=(230, 20, 20))
    center_x, center_y, radius = 540, 960, 420
    for f in range(total_frames):
        t = f / FPS
        frame = Image.new("RGBA", (W, H), (6, 6, 8, 255)) # outer door darkness
        # Inside peephole aperture
        ph = Image.new("RGBA", (radius * 2, radius * 2), (0, 0, 0, 0))
        d_ph = ImageDraw.Draw(ph)
        # Corridor outside
        corridor_col = (40, 36, 28, 255) if (f % 30 > 2) else (15, 12, 10, 255) # flickering bulb
        d_ph.ellipse([0, 0, radius * 2, radius * 2], fill=corridor_col)
        # Distorted figure approaching lens
        approach = min(1.0, (t / duration) * 1.3)
        fig_size = int(140 + approach * 380)
        fig_x = radius + int(math.sin(t * 2.0) * 12)
        fig_y = radius + int(math.cos(t * 1.5) * 8)
        d_ph.ellipse([fig_x - fig_size // 2, fig_y - fig_size // 2, fig_x + fig_size // 2, fig_y + fig_size // 2], fill=(8, 8, 12, 255))
        # Wide grinning white face at the peephole when close
        if approach > 0.4:
            face_alpha = int(min(255, (approach - 0.4) * 400))
            face_w = int(fig_size * 0.7)
            d_ph.ellipse([fig_x - face_w // 2, fig_y - face_w // 2, fig_x + face_w // 2, fig_y + face_w // 2], fill=(215, 210, 200, face_alpha))
            # Black eyes and smile
            d_ph.ellipse([fig_x - face_w // 3, fig_y - 20, fig_x - face_w // 6, fig_y + 15], fill=(10, 10, 12, face_alpha))
            d_ph.ellipse([fig_x + face_w // 6, fig_y - 20, fig_x + face_w // 3, fig_y + 15], fill=(10, 10, 12, face_alpha))
            d_ph.arc([fig_x - face_w // 3, fig_y + 10, fig_x + face_w // 3, fig_y + 70], 0, 180, fill=(10, 10, 12, face_alpha), width=8)
        # Paste peephole into frame
        frame.paste(ph, (center_x - radius, center_y - radius), ph)
        draw = ImageDraw.Draw(frame)
        # Brass bezel ring around peephole
        draw.ellipse([center_x - radius - 15, center_y - radius - 15, center_x + radius + 15, center_y + radius + 15], outline=(180, 145, 60, 255), width=18)
        frame.paste(card, (140, 100), card)
        proc.stdin.write(frame.tobytes("raw", "RGBA"))
    proc.stdin.close()
    proc.wait()

print("ALL 5 SCENE DEFINITIONS VALID!")
