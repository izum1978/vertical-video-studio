"""
Part 3 (Season Finale) of the Autodealer Mini-Series (v3 PRO Full-Body Multi-Character Engine):
"ФИНАЛ: Босс автосалона приехал на разборку — но я открыл свой честный бизнес!"

4 brand-new 2x-supersampled locations + new Mafia Boss character + floating viral likes/hearts:
1. Underground Parking — Hero's white car vs Black SUV + Dealership Boss in trench coat & gold chain
2. Viral Livestream Studio — Giant LIVE 3.0M views monitor + floating red hearts/likes + Hero & Lawyer
3. Sealed Dealership — Crisscrossed yellow-black ОПЕЧАТАНО tape + "ЗАКРЫТО!" stamp + Police arresting Boss & Manager
4. Honest Auto-Check Service — Hero's own brand-new studio ("ЧЕСТНЫЙ АВТОПОДБОР") + Hero in shades + Lawyer + raining cash!
Voiceover: Live F5-TTS Russian GPU voice cloning (consistent trilogy narrator!).
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
from backend.app.cartoon.v3_part2 import render_special_character
from backend.app.cinematic.subtitles import generate_cinematic_ass

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


# ---------------------------------------------------------------------------
# 1. NEW CHARACTER (DEALERSHIP NETWORK BOSS) & VIRAL HEARTS PARTICLE FX
# ---------------------------------------------------------------------------

def render_boss_character(
    mood: str = "shady",
    mouth_state: str = "closed",
    gesture: str = "hold_money",
    facing: str = "left",
    scale: float = 0.96,
) -> Image.Image:
    """Renders the intimidating Dealership Network Boss (black coat, gold chain, dark shades)."""
    base = render_full_body_character(
        outfit="suit", hair_style="slicked",
        mood=mood, mouth_state=mouth_state, gesture=gesture,
        blink=False, facing=facing, scale=1.0,
    )
    d = ImageDraw.Draw(base, "RGBA")
    cx = base.width // 2
    shift = 10 if facing == "right" else -10

    # Gold chain around neck over dark suit!
    d.arc([cx - 32, 260, cx + 32, 325], start=15, end=165, fill=(250, 204, 21, 255), width=6)

    # Dark intimidating sunglasses (unless shocked with wide eyes!)
    if mood != "shocked":
        ey = 186
        d.rounded_rectangle([(cx - 48 + shift, ey - 13), (cx - 4 + shift, ey + 13)], radius=5, fill=(15, 23, 42, 250), outline=INK, width=3)
        d.rounded_rectangle([(cx + 4 + shift, ey - 13), (cx + 48 + shift, ey + 13)], radius=5, fill=(15, 23, 42, 250), outline=INK, width=3)
        d.line([(cx - 4 + shift, ey - 3), (cx + 4 + shift, ey - 3)], fill=INK, width=4)

    return base.resize((int(base.width * scale), int(base.height * scale)), Image.Resampling.LANCZOS)


def draw_viral_likes_rain(frame: Image.Image, t: float) -> Image.Image:
    """Floating rising red hearts / viral notification bubbles for the 3M views scene!"""
    w, h = frame.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    for i in range(14):
        speed = 190 + (i % 5) * 48
        # Rise upward from bottom-mid toward top!
        start_y = (i * 173) % (h + 160)
        y = h - (((start_y + t * speed) % (h + 160)) - 80)
        base_x = (i * 89 + 70) % (w - 140)
        x = base_x + math.sin(t * 2.8 + i * 1.7) * 38
        r = 14 + (i % 3) * 4
        # Crisp red heart icon (two circles + bottom triangle)
        col = (239, 68, 68, 215) if i % 2 == 0 else (244, 63, 94, 200)
        d.ellipse([x - r, y - r // 2, x, y + r // 2], fill=col)
        d.ellipse([x, y - r // 2, x + r, y + r // 2], fill=col)
        d.polygon([(x - r, y + 1), (x + r, y + 1), (x, y + int(r * 1.35))], fill=col)

    return Image.alpha_composite(frame, overlay)


def _draw_black_suv(d: ImageDraw.ImageDraw, cx: int, wheel_y: int, S: int) -> None:
    """Draws an intimidating boxy black G-Wagon style SUV."""
    ink_w = 5 * S
    d.ellipse([cx - 250 * S, wheel_y + 18 * S, cx + 250 * S, wheel_y + 44 * S], fill=(15, 23, 42, 95))
    # Boxy SUV upper body
    d.rounded_rectangle([(cx - 230 * S, wheel_y - 165 * S), (cx + 195 * S, wheel_y + 8 * S)], radius=14 * S, fill=(24, 30, 42, 255), outline=INK, width=ink_w)
    # Front hood extension
    d.rounded_rectangle([(cx - 260 * S, wheel_y - 88 * S), (cx - 190 * S, wheel_y + 8 * S)], radius=10 * S, fill=(24, 30, 42, 255), outline=INK, width=ink_w)
    # Dark tinted windows
    for wx1, wx2 in [(cx - 195 * S, cx - 80 * S), (cx - 60 * S, cx + 55 * S), (cx + 75 * S, cx + 170 * S)]:
        d.rounded_rectangle([(wx1, wheel_y - 148 * S), (wx2, wheel_y - 82 * S)], radius=6 * S, fill=(51, 65, 85, 255), outline=INK, width=4 * S)
    # Bright LED headlights on left (facing hero!)
    d.ellipse([cx - 258 * S, wheel_y - 68 * S, cx - 226 * S, wheel_y - 36 * S], fill=(254, 240, 138, 255), outline=INK, width=3 * S)
    # Big off-road wheels
    for wx in [cx - 145 * S, cx + 125 * S]:
        d.ellipse([wx - 48 * S, wheel_y - 40 * S, wx + 48 * S, wheel_y + 48 * S], fill=(15, 20, 30, 255), outline=INK, width=ink_w)
        d.ellipse([wx - 22 * S, wheel_y - 14 * S, wx + 22 * S, wheel_y + 22 * S], fill=(148, 163, 184, 255), outline=INK, width=3 * S)


# ---------------------------------------------------------------------------
# 2. 4 BRAND-NEW 2x-SUPERSAMPLED LOCATIONS FOR PART 3
# ---------------------------------------------------------------------------

def build_part3_backgrounds() -> Dict[str, Image.Image]:
    S = 2
    W, H = 1080 * S, 1920 * S
    bgs = {}

    # ------------------------------------------------------------------
    # LOC 1: UNDERGROUND PARKING GARAGE (White Car + Black SUV!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (45, 52, 64, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1230 * S

    # Moody concrete parking garage wall
    d.rectangle([(0, 0), (W, floor_y)], fill=(58, 66, 80, 255))
    # Overhead fluorescent tube lamps
    for lx in [220 * S, 540 * S, 860 * S]:
        d.rounded_rectangle([(lx - 90 * S, 245 * S), (lx + 90 * S, 268 * S)], radius=8 * S, fill=(248, 250, 252, 245), outline=INK, width=3 * S)

    # Concrete support pillars with yellow-black safety stripes
    for px in [110 * S, 970 * S]:
        d.rectangle([(px - 52 * S, 200 * S), (px + 52 * S, floor_y)], fill=(100, 116, 139, 255), outline=INK, width=5 * S)
        d.rectangle([(px - 52 * S, 960 * S), (px + 52 * S, 1080 * S)], fill=(250, 204, 21, 255), outline=INK, width=4 * S)
        for sy in [975 * S, 1015 * S, 1055 * S]:
            d.line([(px - 50 * S, sy), (px + 50 * S, sy - 18 * S)], fill=INK, width=10 * S)

    # Wall sign "ПАРКИНГ -2 ЭТАЖ"
    d.rounded_rectangle([(320 * S, 310 * S), (760 * S, 385 * S)], radius=12 * S, fill=(30, 41, 59, 255), outline=(250, 204, 21, 255), width=4 * S)
    f_p = _font(FONT_BOLD, 34 * S)
    pt = "ПАРКИНГ • -2 ЭТАЖ"
    pbb = f_p.getbbox(pt)
    d.text(((W - (pbb[2] - pbb[0])) // 2, 328 * S), pt, fill=(254, 240, 138, 255), font=f_p)

    # Clean light concrete floor
    d.rectangle([(0, floor_y), (W, H)], fill=(214, 218, 224, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)

    # Black intimidating SUV parked on right-center!
    _draw_black_suv(d, cx=660 * S, wheel_y=1145 * S, S=S)

    bgs["parking"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 2: VIRAL LIVESTREAM STUDIO (Giant 3,000,000 Views Trend Board!)
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (226, 232, 246, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1230 * S

    # Modern clean studio wall
    d.rectangle([(0, 0), (W, floor_y)], fill=(230, 236, 248, 255))
    # Giant Studio Screen displaying Viral Broadcast Stats!
    sx1, sy1, sx2, sy2 = 130 * S, 270 * S, 950 * S, 760 * S
    d.rounded_rectangle([(sx1, sy1), (sx2, sy2)], radius=22 * S, fill=(15, 23, 42, 255), outline=INK, width=6 * S)

    # Red LIVE badge inside screen
    d.rounded_rectangle([(sx1 + 32 * S, sy1 + 28 * S), (sx1 + 210 * S, sy1 + 84 * S)], radius=12 * S, fill=(220, 38, 38, 255))
    d.ellipse([sx1 + 50 * S, sy1 + 46 * S, sx1 + 70 * S, sy1 + 66 * S], fill=(255, 255, 255, 255))
    d.text((sx1 + 82 * S, sy1 + 38 * S), "LIVE", fill=(255, 255, 255, 255), font=_font(FONT_BOLD, 32 * S))

    # Big Viral View Counter
    f_big = _font(FONT_IMPACT, 74 * S)
    vt = "3 000 000"
    vbb = f_big.getbbox(vt)
    d.text(((W - (vbb[2] - vbb[0])) // 2, sy1 + 115 * S), vt, fill=(74, 222, 128, 255), font=f_big)

    f_sub = _font(FONT_BOLD, 30 * S)
    st = "ПРОСМОТРОВ ЗА ОДНУ НОЧЬ • #1 В ТРЕНДАХ"
    sbb = f_sub.getbbox(st)
    d.text(((W - (sbb[2] - sbb[0])) // 2, sy1 + 225 * S), st, fill=(226, 232, 240, 255), font=f_sub)

    # Skyrocketing green graph inside screen
    pts = [(200 * S, 700 * S), (340 * S, 680 * S), (480 * S, 640 * S), (620 * S, 560 * S), (760 * S, 470 * S), (880 * S, 360 * S)]
    d.line(pts, fill=(34, 197, 94, 255), width=10 * S, joint="curve")
    for px, py in pts:
        d.ellipse([px - 10 * S, py - 10 * S, px + 10 * S, py + 10 * S], fill=(255, 255, 255, 255), outline=(34, 197, 94, 255), width=4 * S)

    # Clean studio floor
    d.rectangle([(0, floor_y), (W, H)], fill=(242, 240, 236, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)

    bgs["livestream"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 3: SEALED SCAM DEALERSHIP (Crisscrossed ОПЕЧАТАНО Tape!)
    # ------------------------------------------------------------------
    from backend.app.cartoon.v3_engine import build_v3_backgrounds
    base_salon = build_v3_backgrounds()["showroom"].resize((W, H), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(base_salon)

    # Dim slightly with dramatic overlay
    dim = Image.new("RGBA", (W, H), (30, 14, 18, 70))
    base_salon = Image.alpha_composite(base_salon, dim)
    d = ImageDraw.Draw(base_salon)

    # Crisscrossed yellow-black police seal tape across the entire dealership!
    for (p1, p2) in [((0, 720 * S), (W, 1140 * S)), ((0, 1140 * S), (W, 720 * S))]:
        d.line([p1, p2], fill=(250, 204, 21, 240), width=42 * S)
        d.line([p1, p2], fill=INK, width=4 * S)

    # Red Seal Banner over old sign
    d.rounded_rectangle([(200 * S, 260 * S), (880 * S, 355 * S)], radius=18 * S, fill=(30, 41, 59, 255), outline=(239, 68, 68, 255), width=6 * S)
    f_seal = _font(FONT_BOLD, 42 * S)
    sl_t = "ОПЕЧАТАНО • ПОЛИЦИЯ РФ"
    sl_b = f_seal.getbbox(sl_t)
    d.text(((W - (sl_b[2] - sl_b[0])) // 2, 281 * S), sl_t, fill=(248, 113, 113, 255), font=f_seal)

    bgs["sealed_salon"] = base_salon.resize((1080, 1920), Image.Resampling.LANCZOS)

    # ------------------------------------------------------------------
    # LOC 4: HERO'S OWN HONEST AUTO-CHECK SERVICE ("ЧЕСТНЫЙ АВТОПОДБОР")
    # ------------------------------------------------------------------
    img = Image.new("RGBA", (W, H), (224, 242, 254, 255))
    d = ImageDraw.Draw(img)
    floor_y = 1230 * S

    # Bright clean modern garage studio
    d.rectangle([(0, 0), (W, floor_y)], fill=(232, 244, 252, 255))
    # Subtle garage grid wall
    for gx in range(0, W, 180 * S):
        d.line([(gx, 0), (gx, floor_y)], fill=(208, 228, 242, 255), width=3 * S)

    # Prestigious Brand Sign: "ЧЕСТНЫЙ АВТОПОДБОР"
    d.rounded_rectangle([(170 * S, 255 * S), (910 * S, 370 * S)], radius=22 * S, fill=(29, 78, 216, 255), outline=INK, width=6 * S)
    f_brand = _font(FONT_BOLD, 48 * S)
    bt = "ЧЕСТНЫЙ АВТОПОДБОР"
    bbb = f_brand.getbbox(bt)
    d.text(((W - (bbb[2] - bbb[0])) // 2, 274 * S), bt, fill=(255, 255, 255, 255), font=f_brand)
    f_bsub = _font(FONT_BOLD, 22 * S)
    bst = "100% ПРОВЕРКА • БЕЗ ПЕРЕКУПОВ"
    bsb = f_bsub.getbbox(bst)
    d.text(((W - (bsb[2] - bsb[0])) // 2, 330 * S), bst, fill=(254, 240, 138, 255), font=f_bsub)

    # Hydraulic Car Lift Columns in center-back!
    for lx in [320 * S, 760 * S]:
        d.rectangle([(lx - 18 * S, 560 * S), (lx + 18 * S, floor_y)], fill=(37, 99, 235, 255), outline=INK, width=5 * S)
    # Lift platform
    d.rectangle([(290 * S, 1080 * S), (790 * S, 1106 * S)], fill=(71, 85, 105, 255), outline=INK, width=4 * S)

    # Clean glossy service floor
    d.rectangle([(0, floor_y), (W, H)], fill=(240, 242, 245, 255))
    d.line([(0, floor_y), (W, floor_y)], fill=INK, width=5 * S)

    # Gleaming emerald-green inspected car on lift!
    _draw_car(d, cx=540 * S, wheel_y=1040 * S, S=S, body_color=(22, 163, 74), split_gap=0)
    # Green check badge above car
    d.rounded_rectangle([(385 * S, 815 * S), (695 * S, 872 * S)], radius=14 * S, fill=(22, 163, 74, 255), outline=INK, width=4 * S)
    f_ok = _font(FONT_BOLD, 26 * S)
    okt = "ПРОВЕРЕНО • 100% ОК"
    okb = f_ok.getbbox(okt)
    d.text(((W - (okb[2] - okb[0])) // 2, 828 * S), okt, fill=(255, 255, 255, 255), font=f_ok)

    bgs["honest_service"] = img.resize((1080, 1920), Image.Resampling.LANCZOS)
    return bgs


# ---------------------------------------------------------------------------
# 3. MASTER PART 3 (SEASON FINALE) RENDERER
# ---------------------------------------------------------------------------

def render_autodealer_part3(
    output_path: Path = Path("output/cartoon_master/autodealer_part3_finale.mp4"),
    speaker: str = "f5",
    fps: int = 30,
) -> Path:
    """Renders Part 3 (Season Finale) in v3 PRO Full-Body Multi-Character style."""
    output_path = Path(output_path)
    work_dir = output_path.parent / "temp_part3"
    work_dir.mkdir(parents=True, exist_ok=True)

    chapters = [
        {
            "loc": "parking",
            "sentences": [
                "Часть третья. Через неделю после суда на подземной парковке меня поджидал владелец всей сети автосалонов.",
                "Он вышел из чёрного внедорожника и предложил миллион, чтобы я удалил видео из сети.",
            ],
            "hud_bal": "1 250 000 ₽",
            "hud_st": "ОПАСНАЯ ВСТРЕЧА!",
            "theme": "alert",
            "pill": "ПОДЗЕМНЫЙ ПАРКИНГ • 23:10",
            "sfx": "phone",
        },
        {
            "loc": "livestream",
            "sentences": [
                "Но он не знал, что у меня уже шёл прямой эфир!",
                "Ролик за одну ночь набрал три миллиона просмотров, а люди начали просить проверить их машины перед покупкой.",
            ],
            "hud_bal": "1 250 000 ₽",
            "hud_st": "3 000 000 ПРОСМОТРОВ!",
            "theme": "green",
            "pill": "ПРЯМОЙ ЭФИР • #1 В ТРЕНДАХ",
            "sfx": "coin",
        },
        {
            "loc": "sealed_salon",
            "sentences": [
                "После такого скандала налоговая и полиция опечатали все пять точек этих перекупов за один день!",
                "Владелец отправился вслед за своим менеджером.",
            ],
            "hud_bal": "2 900 000 ₽",
            "hud_st": "СЕТЬ ОПЕЧАТАНА!",
            "theme": "danger",
            "pill": "ВСЕ 5 САЛОНОВ ЗАКРЫТЫ",
            "sfx": "boom",
        },
        {
            "loc": "honest_service",
            "sentences": [
                "А я на выигранные деньги открыл свой честный сервис автоподбора! За первый месяц мы спасли от обмана сорок человек.",
                "Пишите в комментариях, про какую схему снять следующий сезон!",
            ],
            "hud_bal": "4 750 000 ₽",
            "hud_st": "СВОЙ БИЗНЕС!",
            "theme": "green",
            "pill": "ЧЕСТНЫЙ АВТОПОДБОР • ФИНАЛ СЕЗОНА",
            "sfx": "coin",
        },
    ]

    all_sentences = []
    chapter_word_counts = []
    for ch in chapters:
        cnt = 0
        for s in ch["sentences"]:
            all_sentences.append(s)
            cnt += len(s.replace(".", "").replace("!", "").replace("?", "").replace(",", "").replace("...", "").replace("—", "").split())
        chapter_word_counts.append(cnt)

    # Synthesize voice via F5-TTS Russian GPU (or reuse cache if already generated!)
    voice_wav = work_dir / f"voice_part3_{speaker}.wav"
    cached_words = work_dir / f"words_f5_voice_part3_{speaker}.json"

    if speaker == "f5" and voice_wav.exists() and cached_words.exists():
        print("[PART 3] 1. Используем готовую озвучку Части 3 (F5-TTS GPU) из кэша...")
        voice_file = voice_wav
        meta = json.loads(cached_words.read_text(encoding="utf-8"))
        words = meta["words"]
        duration = float(meta["duration"])
    elif speaker == "f5" and is_f5_available():
        print("[PART 3] 1. Синтезируем живую озвучку Части 3 через F5-TTS Russian (RTX 4050 GPU)...")
        voice_file, words, duration = synthesize_f5_script(all_sentences, out_wav=voice_wav, speed=1.06)
    else:
        print(f"[PART 3] 1. Синтезируем озвучку Silero v5.6 ({speaker})...")
        voice_file, words, duration = synthesize_silero_script(all_sentences, speaker=speaker, out_wav=voice_wav)

    ch_starts = [0.0]
    wc = 0
    for i in range(len(chapters) - 1):
        wc += chapter_word_counts[i]
        ch_starts.append(max(ch_starts[-1] + 1.5, words[wc]["start"] - 0.12) if wc < len(words) else (i + 1) * (duration / 4.0))
    ch_ends = ch_starts[1:] + [duration]
    print(f"         Длительность: {duration:.2f}s | Смены локаций: {[round(x, 2) for x in ch_starts]}s")

    # Mix SFX
    print("[PART 3] 2. Сводим звук + SFX (whoosh, звон монет, удар закрытия)...")
    sfx_dir = work_dir / "sfx"
    sfx_map = {
        "coin": synth_coin_ding(sfx_dir / "coin.wav"),
        "phone": synth_phone_vibrate(sfx_dir / "phone.wav"),
        "boom": synth_liquidation_boom(sfx_dir / "boom.wav"),
        "whoosh": synth_whoosh(sfx_dir / "whoosh.wav"),
    }
    sfx_events = []
    for i, ch in enumerate(chapters):
        if i > 0:
            sfx_events.append((max(0.0, ch_starts[i] - 0.10), sfx_map["whoosh"], 0.72))
        sfx_events.append((ch_starts[i] + 0.25, sfx_map[ch["sfx"]], 0.90 if ch["sfx"] == "boom" else 0.75))

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

    # Subtitles
    print("[PART 3] 3. Генерируем караоке-субтитры...")
    ass_path = work_dir / "part3_subtitles.ass"
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

    print("[PART 3] 4. Строим 4 новые 2x-суперсэмплированные локации...")
    bgs = build_part3_backgrounds()
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
        blink = (t % 2.8) > 2.67
        mouth = (["half", "open", "half"][int((t * 9.5) % 3)]) if speaking else "closed"
        ch_prog = max(0.0, min(1.0, t_local / max(0.1, ch_dur)))

        # ------------------ SCENE 1: UNDERGROUND PARKING CONFRONTATION ------------------
        if ch_idx == 0:
            # Hero on LEFT holding smartphone discreetly recording!
            hero = render_full_body_character(
                outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
                mood="confident", mouth_state="closed", gesture="hold_phone",
                blink=blink, facing="right", scale=0.92,
            )
            # Intimidating Dealership Boss walks up from RIGHT holding cash bribe!
            wp = min(1.0, t_local / 1.1)
            boss_x = int(1040 - ease_out_back(wp) * 200)
            boss = render_boss_character(
                mood="shady", mouth_state=mouth, gesture="hold_money",
                facing="left", scale=0.96,
            )
            frame = paste_char(frame, hero, 230, 1295)
            frame = paste_char(frame, boss, boss_x, 1298)
            frame = camera.apply(frame, zoom=1.00 + 0.06 * ch_prog, focal_point=(540, 1020), t=t)

            if t_local > 0.55:
                pop = ease_out_back(min(1.0, (t_local - 0.55) / 0.25))
                draw_smart_bubble(frame, "«Удаляй видео — и миллион твой!»", anchor_x=boss_x - 30, anchor_y=790, align="right", pop_scale=pop)

        # ------------------ SCENE 2: VIRAL LIVESTREAM 3M VIEWS ------------------
        elif ch_idx == 1:
            # Rising red hearts / viral likes everywhere!
            frame = draw_viral_likes_rain(frame, t)

            hero = render_full_body_character(
                outfit="hoodie", outfit_color=(59, 130, 246), hair_style="undercut",
                mood="smug", mouth_state=mouth, gesture="hold_phone",
                blink=blink, facing="right", scale=0.93,
            )
            lawyer = render_special_character(
                role="lawyer", mood="smug", mouth_state="closed",
                gesture="point_left", blink=((t + 1.1) % 3.0) > 2.88, facing="left", scale=0.93,
            )
            frame = paste_char(frame, hero, 270, 1300)
            frame = paste_char(frame, lawyer, 820, 1300)
            frame = camera.apply(frame, zoom=1.01 + 0.05 * ch_prog, focal_point=(540, 960), t=t)

            if t_local > 0.45:
                pop = ease_out_back(min(1.0, (t_local - 0.45) / 0.25))
                draw_smart_bubble(frame, "«Поздно, босс — вся страна в эфире!»", anchor_x=310, anchor_y=800, align="left", pop_scale=pop)

        # ------------------ SCENE 3: ALL 5 SALONS SEALED! ------------------
        elif ch_idx == 2:
            # 3 Characters: Police Officer on LEFT, Panicked Boss in CENTER, Panicked Manager on RIGHT!
            cop = render_special_character(
                role="police", mood="alert", mouth_state=mouth,
                gesture="point_right", facing="right", scale=0.93,
            )
            boss = render_boss_character(
                mood="shocked", mouth_state="open", gesture="hands_on_head",
                facing="left", scale=0.92,
            )
            mgr = render_full_body_character(
                outfit="suit", hair_style="slicked",
                mood="sad", mouth_state="closed", gesture="hands_on_head",
                blink=False, facing="left", scale=0.88,
            )
            frame = paste_char(frame, cop, 195, 1300)
            frame = paste_char(frame, boss, 590, 1295)
            frame = paste_char(frame, mgr, 885, 1295)

            frame = draw_siren_flash(frame, t)
            shake = ((1.0 - t_local / 0.55) ** 1.4) if t_local <= 0.55 else 0.0
            frame = camera.apply(frame, zoom=1.03 + 0.05 * ch_prog, focal_point=(540, 1020), shake_intensity=shake, t=t)

            # Slamming Red Rubber Stamp cleanly above characters!
            frame = draw_animated_stamp(frame, "ЗАКРЫТО!", t_local - 0.18, center=(540, 560))

            if t_local > 0.40:
                pop = ease_out_back(min(1.0, (t_local - 0.40) / 0.22))
                draw_smart_bubble(frame, "«Все пять салонов закрыты. Пройдёмте!»", anchor_x=240, anchor_y=805, align="left", pop_scale=pop)

        # ------------------ SCENE 4: HERO'S OWN HONEST AUTO-CHECK BUSINESS ------------------
        else:
            frame = draw_money_rain(frame, t)

            # Cool Hero in sunglasses on LEFT + Proud Lawyer Partner on RIGHT!
            wp = min(1.0, t_local / 1.0)
            hero_x = int(120 + ease_out_back(wp) * 145)
            hero = render_special_character(
                role="hero_cool", mood="smug", mouth_state=mouth,
                gesture="hold_money", walk_phase=(t * 10.0 if wp < 0.95 else 0.0),
                facing="right", scale=0.95,
            )
            lawyer = render_special_character(
                role="lawyer", mood="smug", mouth_state="closed",
                gesture="hold_money", blink=blink, facing="left", scale=0.93,
            )
            frame = paste_char(frame, hero, hero_x, 1305)
            frame = paste_char(frame, lawyer, 835, 1305)
            frame = camera.apply(frame, zoom=1.00 + 0.05 * ch_prog, focal_point=(540, 1000), t=t)

            if t_local > 0.45:
                pop = ease_out_back(min(1.0, (t_local - 0.45) / 0.25))
                draw_smart_bubble(frame, "«Теперь перекупы обходят нас за километр!»", anchor_x=hero_x + 70, anchor_y=795, align="left", pop_scale=pop)

        draw_sleek_hud(frame, balance_text=ch["hud_bal"], status_text=ch["hud_st"], theme=ch["theme"])
        draw_compact_pill(frame, text=ch["pill"])
        return frame

    print("[PART 3] 5. Рендерим анимацию Части 3 (Паркинг -> Эфир 3М -> Опечатано -> Свой бизнес)...")
    total_frames = int(duration * fps)
    raw_video = work_dir / "raw_part3.mp4"

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

    print("[PART 3] 6. Финальная сборка MP4 с живой озвучкой F5-TTS и субтитрами...")
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

    print(f"[OK] Часть 3 (Финал сезона!) готова: {output_path}")
    return output_path
