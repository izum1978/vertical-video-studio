"""
Crypto Trader Explainer Scene Generator (30 Seconds).
Story: Trader wakes up at 4 AM to find his 100x leverage position completely liquidated.
Features:
- Dynamic 2D multi-monitor trading room (green candles -> crashing red candles -> flatline)
- Custom trader character with bedhead hair and 4 emotional evolutions (smug -> alert -> horror -> tearful)
- 4-stage evolving gaming HUD & speech bubbles
- Procedural sound design (coins -> phone vibrate -> liquidation boom -> hollow drop)
- High-energy natural voice narration + karaoke subtitles
"""

import math
import subprocess
import wave
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.app.cartoon.ui_engine import (
    draw_floating_badge,
    draw_location_pill,
    draw_speech_bubble,
    draw_top_hud,
    get_font,
    FONT_BOLD,
    FONT_IMPACT,
)
from backend.app.cartoon.silero_voice import synthesize_silero_script
from backend.app.cinematic.subtitles import generate_cinematic_ass
from backend.app.cinematic.voice import generate_cinematic_voice

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


# ---------------------------------------------------------------------------
# 1. PROCEDURAL 2D TRADER ROOM BACKGROUND GENERATOR
# ---------------------------------------------------------------------------

def render_trader_room(stage: str = "green", size: Tuple[int, int] = (1080, 1920)) -> Image.Image:
    """Renders 2D vector dark trader bedroom with dual glowing monitors.
    stage: 'green' (pumping), 'alert' (orange warning), 'crash' (blood red liquidation), 'dead' (dim flatline).
    """
    w, h = size
    img = Image.new("RGBA", (w, h), (15, 17, 26, 255))
    draw = ImageDraw.Draw(img)

    # 1. Ambient wall gradient with neon LED light strip
    for y in range(0, int(h * 0.7)):
        ratio = y / (h * 0.7)
        if stage in ["green", "alert"]:
            r = int(14 + ratio * 20)
            g = int(18 + ratio * 28)
            b = int(36 + ratio * 45)
        elif stage == "crash":
            # Bloody red ambient glow
            r = int(35 + ratio * 55)
            g = int(10 + ratio * 15)
            b = int(18 + ratio * 25)
        else:  # dead
            r = int(10 + ratio * 12)
            g = int(12 + ratio * 15)
            b = int(20 + ratio * 25)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Neon strip on back wall
    neon_col = (56, 189, 248, 220) if stage == "green" else (
        (251, 146, 60, 240) if stage == "alert" else (
            (239, 68, 68, 255) if stage == "crash" else (100, 116, 139, 120)
        )
    )
    draw.line([(80, 360), (1000, 360)], fill=neon_col, width=8)

    # Digital LED Clock on wall: '04:12'
    clock_box = [440, 260, 640, 330]
    draw.rounded_rectangle(clock_box, radius=12, fill=(10, 12, 18, 240), outline=(71, 85, 105, 200), width=2)
    font_clock = get_font(FONT_IMPACT, 42)
    clock_time = "04:12" if stage != "dead" else "04:47"
    draw.text((475, 272), clock_time, fill=(239, 68, 68, 255) if stage == "crash" else (52, 211, 153, 255), font=font_clock)

    # 2. Desk Surface
    desk_y = 780
    draw.rectangle([(0, desk_y), (w, h)], fill=(20, 24, 33, 255))
    draw.line([(0, desk_y), (w, desk_y)], fill=(51, 65, 85, 255), width=4)

    # 3. Dual Ultrawide Monitors Setup
    mon_y = 420
    mon_w, mon_h = 440, 320
    
    # Left Monitor
    lm_x = 80
    draw.rounded_rectangle([(lm_x, mon_y), (lm_x + mon_w, mon_y + mon_h)], radius=18, fill=(10, 14, 23, 255), outline=(71, 85, 105, 255), width=5)
    # Right Monitor
    rm_x = 560
    draw.rounded_rectangle([(rm_x, mon_y), (rm_x + mon_w, mon_y + mon_h)], radius=18, fill=(10, 14, 23, 255), outline=(71, 85, 105, 255), width=5)

    # Monitor stands
    draw.rectangle([(lm_x + mon_w // 2 - 15, mon_y + mon_h), (lm_x + mon_w // 2 + 15, desk_y)], fill=(51, 65, 85, 255))
    draw.rectangle([(rm_x + mon_w // 2 - 15, mon_y + mon_h), (rm_x + mon_w // 2 + 15, desk_y)], fill=(51, 65, 85, 255))

    # Candlestick Charts Drawing on Monitors
    def draw_chart(mx: int, my: int, mw: int, mh: int, chart_type: str):
        # Grid lines
        for gy in range(my + 30, my + mh - 20, 45):
            draw.line([(mx + 10, gy), (mx + mw - 10, gy)], fill=(30, 41, 59, 140), width=1)

        if chart_type in ["green", "alert"]:
            # Green bull market candles climbing up
            candles = [
                (mx + 30, my + 240, 25, 40, True),
                (mx + 70, my + 210, 25, 50, True),
                (mx + 110, my + 225, 25, 30, False),
                (mx + 150, my + 170, 25, 60, True),
                (mx + 190, my + 140, 25, 55, True),
                (mx + 230, my + 150, 25, 35, False),
                (mx + 270, my + 110, 25, 65, True),
                (mx + 310, my + 80, 25, 60, True),
                (mx + 350, my + 50, 25, 50, True),
            ]
            for cx, cy, cw, ch, is_green in candles:
                col = (34, 197, 94, 255) if is_green else (239, 68, 68, 255)
                # Wick
                draw.line([(cx + cw // 2, cy - 15), (cx + cw // 2, cy + ch + 15)], fill=col, width=2)
                # Body
                draw.rectangle([(cx, cy), (cx + cw, cy + ch)], fill=col)

        elif chart_type == "crash":
            # Bloody red waterfall collapse
            candles = [
                (mx + 30, my + 50, 25, 40, True),
                (mx + 70, my + 70, 25, 45, False),
                (mx + 110, my + 110, 25, 70, False),
                (mx + 150, my + 150, 25, 80, False),
                (mx + 190, my + 190, 25, 90, False),
                (mx + 230, my + 220, 25, 75, False),
                (mx + 270, my + 240, 25, 60, False),
                (mx + 310, my + 250, 25, 50, False),
            ]
            for cx, cy, cw, ch, is_green in candles:
                col = (239, 68, 68, 255)
                # Thick aggressive wick
                draw.line([(cx + cw // 2, cy - 20), (cx + cw // 2, cy + ch + 20)], fill=col, width=3)
                draw.rectangle([(cx, cy), (cx + cw, cy + ch)], fill=col)

            # Warning text on screen
            font_warn = get_font(FONT_IMPACT, 32)
            draw.text((mx + 45, my + mh // 2 - 20), "⚠️ MARGIN CALL -100%", fill=(255, 255, 255, 240), font=font_warn)

        else:  # dead
            # Flatline at the very bottom
            draw.line([(mx + 20, my + mh - 40), (mx + mw - 20, my + mh - 40)], fill=(239, 68, 68, 200), width=4)
            font_dead = get_font(FONT_IMPACT, 34)
            draw.text((mx + 80, my + mh // 2 - 20), "LIQUIDATED (0.00$)", fill=(148, 163, 184, 220), font=font_dead)

    draw_chart(lm_x, mon_y, mon_w, mon_h, stage)
    draw_chart(rm_x, mon_y, mon_w, mon_h, stage)

    # 4. Desk items
    # Keyboard & RGB mouse
    draw.rounded_rectangle([(320, desk_y + 40), (760, desk_y + 110)], radius=8, fill=(30, 41, 59, 255), outline=(71, 85, 105, 255), width=2)
    draw.ellipse([(800, desk_y + 50), (850, desk_y + 110)], fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=2)

    # Right desk prop: Coffee mug vs Doshirak Noodles in stage 4!
    if stage != "dead":
        # Coffee mug with steam
        draw.rectangle([(160, desk_y + 30), (220, desk_y + 95)], fill=(241, 245, 249, 255), outline=(15, 23, 42, 255), width=3)
        draw.arc([205, desk_y + 45, 235, desk_y + 80], start=270, end=90, fill=(15, 23, 42, 255), width=4)
    else:
        # Yellow instant noodles bucket (ДОШИРАК)
        nx, ny = 140, desk_y + 15
        draw.polygon([(nx + 10, ny + 90), (nx + 80, ny + 90), (nx + 95, ny), (nx - 5, ny)], fill=(234, 179, 8, 255), outline=(15, 23, 42, 255))
        draw.rectangle([(nx - 8, ny - 6), (nx + 98, ny + 4)], fill=(220, 38, 38, 255))
        font_dosh = get_font(FONT_BOLD, 14)
        draw.text((nx + 12, ny + 35), "ДОШИК", fill=(185, 28, 28, 255), font=font_dosh)

    return img


# ---------------------------------------------------------------------------
# 2. CRYPTO TRADER CHARACTER RIG (WITH HAIR & EMOTIONAL STATES)
# ---------------------------------------------------------------------------

class CryptoTraderRig:
    """Renders the crypto trader with messy bedhead hair and 4 emotional evolutions."""

    def render(
        self,
        mood: str = "smug",  # "smug", "alert", "shocked", "devastated"
        mouth_state: str = "closed",  # "closed", "half", "open"
        offset_y: int = 0,
        size: Tuple[int, int] = (1080, 1920),
    ) -> Image.Image:
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx = 540
        cy = 1200 + offset_y
        outline_col = (15, 20, 32, 255)
        outline_w = 8

        # --- 1. HOODIE (DARK VIOLET / CHARCOAL) ---
        hoodie_col = (76, 29, 149, 255)  # Deep purple crypto hoodie
        draw.polygon(
            [
                (cx - 290, 1920),
                (cx - 270, cy + 310),
                (cx - 160, cy + 190),
                (cx + 160, cy + 190),
                (cx + 270, cy + 310),
                (cx + 290, 1920),
            ],
            fill=hoodie_col,
            outline=outline_col,
        )

        # Bitcoin/Crypto logo on hoodie chest
        draw.ellipse([(cx - 32, cy + 280), (cx + 32, cy + 344)], fill=(245, 158, 11, 240), outline=outline_col, width=3)
        font_btc = get_font(FONT_BOLD, 36)
        draw.text((cx - 12, cy + 292), "₿", fill=(255, 255, 255), font=font_btc)

        # White hoodie drawstrings
        draw.line([(cx - 45, cy + 240), (cx - 45, cy + 390)], fill=(255, 255, 255), width=7)
        draw.line([(cx + 45, cy + 240), (cx + 45, cy + 390)], fill=(255, 255, 255), width=7)

        # --- 2. HEAD & MESSY BEDHEAD HAIR ---
        head_w, head_h = 210, 240
        head_box = [cx - head_w, cy - head_h, cx + head_w, cy + head_h]
        skin_col = (250, 247, 242, 255)
        draw.ellipse(head_box, fill=skin_col, outline=outline_col, width=outline_w)

        # Messy bedhead hair tufts (top and sides)
        hair_col = (30, 41, 59, 255)
        tufts = [
            [(cx - 160, cy - 180), (cx - 190, cy - 250), (cx - 120, cy - 210)],
            [(cx - 120, cy - 210), (cx - 130, cy - 290), (cx - 50, cy - 230)],
            [(cx - 50, cy - 230), (cx, cy - 310), (cx + 50, cy - 230)],
            [(cx + 50, cy - 230), (cx + 130, cy - 290), (cx + 120, cy - 210)],
            [(cx + 120, cy - 210), (cx + 190, cy - 250), (cx + 160, cy - 180)],
        ]
        for t_poly in tufts:
            draw.polygon(t_poly, fill=hair_col, outline=outline_col)

        # --- 3. EYES & BROWS BY MOOD ---
        eye_y = cy - 20

        if mood == "smug":
            # Confident half-closed smirking eyes
            draw.arc([cx - 95, eye_y - 25, cx - 45, eye_y + 25], start=180, end=360, fill=outline_col, width=8)
            draw.arc([cx + 45, eye_y - 25, cx + 95, eye_y + 25], start=180, end=360, fill=outline_col, width=8)
            # Smug angled brows
            draw.line([(cx - 110, eye_y - 50), (cx - 35, eye_y - 35)], fill=outline_col, width=7)
            draw.line([(cx + 35, eye_y - 35), (cx + 110, eye_y - 50)], fill=outline_col, width=7)

        elif mood == "alert":
            # Widened curious/concerned eyes
            draw.ellipse([cx - 95, eye_y - 35, cx - 35, eye_y + 25], fill=(255, 255, 255), outline=outline_col, width=6)
            draw.ellipse([cx + 35, eye_y - 35, cx + 95, eye_y + 25], fill=(255, 255, 255), outline=outline_col, width=6)
            draw.ellipse([cx - 75, eye_y - 15, cx - 55, eye_y + 5], fill=outline_col)
            draw.ellipse([cx + 55, eye_y - 15, cx + 75, eye_y + 5], fill=outline_col)
            # Arched brows + sweat drop
            draw.arc([cx - 105, eye_y - 75, cx - 35, eye_y - 40], start=200, end=340, fill=outline_col, width=7)
            draw.arc([cx + 35, eye_y - 75, cx + 105, eye_y - 40], start=200, end=340, fill=outline_col, width=7)
            # Small sweat drop
            draw.ellipse([cx + 130, cy - 60, cx + 150, cy - 35], fill=(56, 189, 248, 230))

        elif mood == "shocked":
            # Huge bulging horror eyes with tiny dots
            draw.ellipse([cx - 120, eye_y - 50, cx - 25, eye_y + 45], fill=(255, 255, 255), outline=outline_col, width=7)
            draw.ellipse([cx + 25, eye_y - 50, cx + 120, eye_y + 45], fill=(255, 255, 255), outline=outline_col, width=7)
            # Pinprick terror pupils
            draw.ellipse([cx - 78, eye_y - 8, cx - 64, eye_y + 6], fill=(220, 38, 38, 255))
            draw.ellipse([cx + 64, eye_y - 8, cx + 78, eye_y + 6], fill=(220, 38, 38, 255))
            # Extreme high arched brows
            draw.arc([cx - 125, eye_y - 95, cx - 20, eye_y - 55], start=200, end=340, fill=outline_col, width=8)
            draw.arc([cx + 20, eye_y - 95, cx + 125, eye_y - 55], start=200, end=340, fill=outline_col, width=8)
            # Multiple sweat drops
            draw.ellipse([cx + 135, cy - 90, cx + 160, cy - 60], fill=(56, 189, 248, 240))
            draw.ellipse([cx - 160, cy - 80, cx - 135, cy - 50], fill=(56, 189, 248, 240))

        elif mood == "devastated":
            # Dead hollow eyes looking down
            draw.ellipse([cx - 85, eye_y - 20, cx - 45, eye_y + 20], fill=(71, 85, 105, 255), outline=outline_col, width=5)
            draw.ellipse([cx + 45, eye_y - 20, cx + 85, eye_y + 20], fill=(71, 85, 105, 255), outline=outline_col, width=5)
            # Drooping sad brows
            draw.line([(cx - 105, eye_y - 35), (cx - 35, eye_y - 55)], fill=outline_col, width=7)
            draw.line([(cx + 35, eye_y - 55), (cx + 105, eye_y - 35)], fill=outline_col, width=7)
            # Tear running down left cheek
            draw.polygon([(cx - 65, cy + 20), (cx - 75, cy + 80), (cx - 55, cy + 80)], fill=(56, 189, 248, 230))
            draw.ellipse([cx - 75, cy + 70, cx - 55, cy + 95], fill=(56, 189, 248, 230))

        # --- 4. MOUTH FLAPS ---
        mouth_y = cy + 75
        if mouth_state == "closed":
            if mood == "smug":
                # Smug one-sided grin
                draw.arc([cx - 20, mouth_y - 20, cx + 60, mouth_y + 25], start=20, end=160, fill=outline_col, width=7)
            elif mood == "shocked":
                # Screaming wide open oval
                draw.ellipse([cx - 35, mouth_y - 15, cx + 35, mouth_y + 55], fill=outline_col)
            elif mood == "devastated":
                # Straight flat sad line
                draw.line([(cx - 40, mouth_y + 15), (cx + 40, mouth_y + 15)], fill=outline_col, width=6)
            else:
                draw.arc([cx - 40, mouth_y - 15, cx + 40, mouth_y + 25], start=20, end=160, fill=outline_col, width=6)

        elif mouth_state == "half":
            draw.chord([cx - 40, mouth_y - 15, cx + 40, mouth_y + 45], start=0, end=180, fill=outline_col)
            draw.chord([cx - 25, mouth_y + 15, cx + 25, mouth_y + 45], start=0, end=180, fill=(244, 63, 94, 255))

        elif mouth_state == "open":
            draw.chord([cx - 55, mouth_y - 20, cx + 55, mouth_y + 70], start=0, end=180, fill=outline_col)
            draw.chord([cx - 45, mouth_y - 20, cx + 45, mouth_y + 10], start=0, end=180, fill=(255, 255, 255, 255))
            draw.chord([cx - 35, mouth_y + 20, cx + 35, mouth_y + 70], start=0, end=180, fill=(244, 63, 94, 255))

        return img


# ---------------------------------------------------------------------------
# 3. PROCEDURAL SFX SYNTHESIZERS
# ---------------------------------------------------------------------------

def _save_wav(path: Path, data: np.ndarray, sr: int = 44100) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    mx = np.max(np.abs(data))
    if mx > 1e-6:
        data = data / mx * 0.92
    data_int16 = (data * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data_int16.tobytes())
    return path


def synth_phone_vibrate(out_path: Path) -> Path:
    """Double phone vibration buzz (bzzz... bzzz...)."""
    sr = 44100
    dur = 0.9
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    sig = np.zeros_like(t)

    # First buzz 0.0 - 0.35s
    b1 = (t >= 0.0) & (t <= 0.35)
    t1 = t[b1]
    sig[b1] = np.sin(2 * np.pi * 140 * t1) * (0.8 + 0.2 * np.sin(2 * np.pi * 35 * t1))

    # Second buzz 0.45 - 0.8s
    b2 = (t >= 0.45) & (t <= 0.8)
    t2 = t[b2] - 0.45
    sig[b2] = np.sin(2 * np.pi * 140 * t2) * (0.8 + 0.2 * np.sin(2 * np.pi * 35 * t2))

    return _save_wav(out_path, sig)


def synth_liquidation_boom(out_path: Path) -> Path:
    """Heavy low sub-bass explosion + descending alarm screech."""
    sr = 44100
    dur = 2.2
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    # Sub-bass sweep
    f_sub = 85 * np.exp(-3.5 * t) + 28
    sub = np.sin(2 * np.pi * np.cumsum(f_sub) / sr) * np.exp(-2.2 * t)
    # Siren pitch sweep
    f_siren = 680 * np.exp(-4.0 * t) + 120
    siren = np.sin(2 * np.pi * np.cumsum(f_siren) / sr) * np.exp(-3.0 * t)
    noise = np.random.uniform(-0.15, 0.15, len(t)) * np.exp(-4.5 * t)
    sig = 0.65 * sub + 0.25 * siren + 0.1 * noise
    return _save_wav(out_path, sig)


def synth_drip_drop(out_path: Path) -> Path:
    """Sad hollow drip sound with echo."""
    sr = 44100
    dur = 1.0
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    f_drip = 800 + 400 * np.exp(-25 * t)
    drip = np.sin(2 * np.pi * np.cumsum(f_drip) / sr) * np.exp(-18 * t)
    echo = 0.3 * np.roll(drip, int(sr * 0.25))
    return _save_wav(out_path, drip + echo)


def synth_coin_ding(out_path: Path) -> Path:
    sr = 44100
    t = np.linspace(0, 1.2, int(sr * 1.2), endpoint=False)
    sig = 0.5 * np.sin(2 * np.pi * 2093.0 * t) * np.exp(-4.5 * t) + 0.35 * np.sin(2 * np.pi * 3136.0 * t) * np.exp(-6.0 * t)
    return _save_wav(out_path, sig)


# ---------------------------------------------------------------------------
# 4. MASTER 30-SECOND VIDEO ORCHESTRATOR
# ---------------------------------------------------------------------------

def mix_multitrack_audio(
    voice_path: Path,
    sfx_events: List[Tuple[float, Path, float]],
    out_audio_path: Path,
    total_dur: float,
) -> Path:
    sr = 44100
    total_samples = int((total_dur + 0.5) * sr)
    master = np.zeros(total_samples, dtype=np.float32)

    cmd = [FFMPEG_BIN, "-y", "-i", str(voice_path), "-f", "s16le", "-ac", "1", "-ar", str(sr), "pipe:1"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw_voice, _ = p.communicate()
    voice_samples = np.frombuffer(raw_voice, dtype=np.int16).astype(np.float32) / 32768.0
    v_len = min(len(voice_samples), total_samples)
    master[:v_len] += voice_samples[:v_len]

    for ts, sfx_f, vol in sfx_events:
        if not sfx_f.exists():
            continue
        with wave.open(str(sfx_f), "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0 * vol
        s_idx = int(ts * sr)
        e_idx = min(s_idx + len(data), total_samples)
        add_l = e_idx - s_idx
        if add_l > 0:
            master[s_idx:e_idx] += data[:add_l]

    mx = np.max(np.abs(master))
    if mx > 0.95:
        master = master / mx * 0.95

    out_audio_path.parent.mkdir(parents=True, exist_ok=True)
    m_int16 = (master * 32767).astype(np.int16)
    with wave.open(str(out_audio_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(m_int16.tobytes())
    return out_audio_path


def render_crypto_trader_video(
    output_path: Path = Path("output/cartoon_master/crypto_trader_30s.mp4"),
    fps: int = 30,
    voice_engine: str = "silero",  # "silero" or "edge"
    speaker: str = "eugene",       # "eugene", "aidar", "baya", "kseniya", or "ru-RU-DmitryNeural"
) -> Path:
    output_path = Path(output_path)
    work_dir = output_path.parent / "temp_crypto"
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. Script Voiceover
    sentences = [
        "Четыре часа утра.",
        "Я открыл сделку с сотым плечом на всю котлету и спокойно лег спать.",
        "На счете было два миллиона рублей, я уже выбирал цвет новенького Порше.",
        "Внезапно телефон начинает разрываться от уведомлений.",
        "Приходит срочное сообщение от биржи.",
        "Я открываю терминал, а там курс Биткоина рухнул на пятнадцать процентов!",
        "Полная ликвидация. Баланс ноль.",
        "Два миллиона рублей сгорели за три секунды.",
        "Порше отменяется, зато пачка Доширака на полке еще осталась.",
        "Не повторяйте моих ошибок."
    ]

    print(f"[1/5] Синтезируем голос диктора ({voice_engine} / {speaker})...")
    if voice_engine == "silero":
        out_voice = work_dir / f"silero_{speaker}.wav"
        voice_mp3, words, duration = synthesize_silero_script(
            sentences,
            speaker=speaker,
            out_wav=out_voice,
        )
    else:
        script = " ".join(sentences)
        voice_mp3, words, duration = generate_cinematic_voice(
            script,
            work_dir,
            voice=speaker,
            pitch="+0Hz",
            rate="+6%",
        )
    print(f"      Длительность видео: {duration:.2f}s, слов: {len(words)}")

    # 2. SFX Generation
    print("[2/5] Синтезируем процедурные звуковые эффекты (SFX)...")
    sfx_dir = work_dir / "sfx"
    s_coin = synth_coin_ding(sfx_dir / "coin.wav")
    s_phone = synth_phone_vibrate(sfx_dir / "phone.wav")
    s_boom = synth_liquidation_boom(sfx_dir / "boom.wav")
    s_drip = synth_drip_drop(sfx_dir / "drip.wav")

    # Time milestones based on narrative
    t_alert = duration * 0.28   # Телефон разрывается
    t_crash = duration * 0.52   # Ликвидация / рухнул
    t_dead = duration * 0.76    # Доширак

    # Search words for precise timestamp matching
    for w in words:
        wl = w["word"].lower()
        if "телефон" in wl or "разрыват" in wl:
            t_alert = w["start"]
        elif "ликвидац" in wl or "рухнул" in wl:
            t_crash = w["start"]
        elif "доширак" in wl or "отменяет" in wl:
            t_dead = w["start"]

    print(f"      Таймлайны глав: Алерт={t_alert:.2f}s, Краш={t_crash:.2f}s, Доширак={t_dead:.2f}s")

    # Audio Mixing
    print("[3/5] Сводим мастер-аудио с таймингами звуков...")
    sfx_events = [
        (0.4, s_coin, 0.85),
        (t_alert, s_phone, 0.90),
        (t_crash, s_boom, 0.95),
        (t_dead, s_drip, 0.80),
    ]
    master_audio = work_dir / "master_audio.wav"
    mix_multitrack_audio(voice_mp3, sfx_events, master_audio, duration)

    # Subtitles
    print("[4/5] Генерируем караоке-субтитры...")
    ass_path = work_dir / "crypto_subtitles.ass"
    generate_cinematic_ass(
        words,
        ass_path,
        words_per_phrase=3,
        font_name="Arial",
        font_size=66,
        primary_color="&H00FFFFFF",
        highlight_color="&H002BF5FF",
        outline_color="&H00050505",
        margin_v=340,
    )

    # 5. Visual Rendering via FFmpeg pipe
    print("[5/5] Рендерим кадры и собираем финальное видео...")
    # Pre-render 4 backgrounds
    bg_green = render_trader_room(stage="green")
    bg_alert = render_trader_room(stage="alert")
    bg_crash = render_trader_room(stage="crash")
    bg_dead = render_trader_room(stage="dead")

    trader_rig = CryptoTraderRig()
    # Pre-render character sprites
    sprites = {}
    for m in ["smug", "alert", "shocked", "devastated"]:
        for ms in ["closed", "half", "open"]:
            sprites[(m, ms)] = trader_rig.render(mood=m, mouth_state=ms)

    def is_speaking(t: float) -> bool:
        for w in words:
            if w["start"] - 0.05 <= t <= w["end"] + 0.05:
                return True
        return False

    total_frames = int(duration * fps)
    raw_video = work_dir / "raw_crypto.mp4"

    ffmpeg_cmd = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1080x1920",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "pipe:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(raw_video),
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    bubble_rect = (140, 560, 940, 740)
    tail_tip = (540, 930)

    for f in range(total_frames):
        t = f / fps

        # Determine Stage
        if t < t_alert:
            stage_bg = bg_green
            mood = "smug"
            hud_balance = "2 150 000 ₽"
            hud_status = "ЛОНГ С 100x ПЛЕЧОМ"
            loc_pill = "04:12 МСК • КВАРТИРА ТРЕЙДЕРА"
            bubble_text = "«Завтра забираю новенький Порше!»"
            badge = None
        elif t < t_crash:
            stage_bg = bg_alert
            mood = "alert"
            hud_balance = "1 840 000 ₽"
            hud_status = "⚠️ СИГНАЛ ВОЛАТИЛЬНОСТИ"
            loc_pill = "ВХОДЯЩИЙ СИГНАЛ БИРЖИ"
            bubble_text = "«Так, стоп... Что за спам в 4 утра?!»"
            badge = "⚠️"
        elif t < t_dead:
            stage_bg = bg_crash
            mood = "shocked"
            hud_balance = "0.00 ₽"
            hud_status = "💀 ПОЛНАЯ ЛИКВИДАЦИЯ"
            loc_pill = "ПОЗИЦИЯ ПРИНУДИТЕЛЬНО ЗАКРЫТА"
            bubble_text = "«ГДЕ МОИ ДЕНЬГИ?! ОНИ ОБНУЛИЛИ МЕНЯ!»"
            badge = "?!"
        else:
            stage_bg = bg_dead
            mood = "devastated"
            hud_balance = "42 ₽"
            hud_status = "📉 ОСТАТОК: 1 ДОШИРАК"
            loc_pill = "ВЫВОД: НЕ ТОРГУЙ НА ВСЮ КОТЛЕТУ"
            bubble_text = "«Кто-нибудь одолжит сотку на метро?..»"
            badge = None

        # Mouth flap
        if is_speaking(t):
            phase = int((t * 8.5) % 3)
            mouth = ["half", "open", "half"][phase]
            bob_y = int(math.sin(t * 12) * 5)
        else:
            mouth = "closed"
            bob_y = 0

        # Composite frame
        frame = stage_bg.copy()
        sprite = sprites[(mood, mouth)]
        if bob_y != 0:
            shifted = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
            shifted.paste(sprite, (0, bob_y))
            frame = Image.alpha_composite(frame, shifted)
        else:
            frame = Image.alpha_composite(frame, sprite)

        # UI Overlays
        draw_top_hud(frame, balance_text=hud_balance, status_text=hud_status)
        draw_location_pill(frame, text=loc_pill)
        draw_speech_bubble(frame, bubble_text, box_rect=bubble_rect, tail_tip=tail_tip)

        if badge:
            badge_col = (251, 146, 60) if badge == "⚠️" else (239, 68, 68)
            draw_floating_badge(frame, text=badge, center_pos=(740, 980), badge_color=badge_col)

        rgb_bytes = frame.convert("RGB").tobytes()
        proc.stdin.write(rgb_bytes)

    proc.stdin.close()
    proc.wait()

    # Final multiplex with audio and subtitles
    print("      Финальная сборка MP4 со звуковой дорожкой и субтитрами...")
    ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
    final_cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(raw_video),
        "-i", str(master_audio),
        "-vf", f"ass='{ass_escaped}'",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path),
    ]
    res = subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        fallback_cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(raw_video),
            "-i", str(master_audio),
            "-c:v", "copy",
            "-c:a", "aac",
            str(output_path),
        ]
        subprocess.run(fallback_cmd, check=True)

    print(f"[OK] 30-секундный ролик успешно создан: {output_path}")
    return output_path
