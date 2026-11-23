import json
import re
import subprocess
from pathlib import Path

from .config import MUSIC, env

W, H, FPS = 1080, 1920, 60

# Кинематографичный фильтр:
# 1. scale lanczos — максимальная резкость при масштабировании (без мыла)
# 2. crop — точный вертикальный 9:16 фрейм
# 3. fps 60 — плавная частота кадров с округлением без рывков
# 4. unsharp — адаптивная микро-резкость для компенсации сжатия соцсетей
# 5. eq — сочные цвета (+12% saturation, +6% contrast) для экрана смартфонов
VF = (
    f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
    f"crop={W}:{H},setsar=1,"
    f"fps=fps={FPS}:round=near,"
    "unsharp=5:5:0.6:5:5:0.0,"
    "eq=contrast=1.06:saturation=1.12:brightness=0.01"
)


def run(cmd: list, cwd: Path | None = None) -> None:
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, cwd=cwd)
    if p.returncode:
        raise RuntimeError(f"ffmpeg завершился с ошибкой:\n{p.stderr[-800:]}")


def probe_duration(path: Path) -> float:
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
                       capture_output=True, text=True, check=True)
    return float(json.loads(p.stdout)["format"]["duration"])


def _ts(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


SUBTITLE_STYLES = {
    "horror": {
        "label": "Хоррор / Выживание (Нижняя треть, Золото + Коралл)",
        # White &H00FFFFFF, black outline 8px, Alignment 2 (bottom center), MarginV 480
        "style": "&H00FFFFFF,&H00000000,&H00000000,1,1,8,2,2,80,80,480",
        "size": 90,
    },
    "mrbeast": {
        "label": "MrBeast (Ярко-жёлтый)",
        # Yellow &H0000F0FF, black outline 8px, Alignment 2 (bottom center), MarginV 480
        "style": "&H0000F0FF,&H00000000,&H00000000,1,1,8,2,2,80,80,480",
        "size": 92,
    },
    "neon": {
        "label": "Неоновый кибер (Циан)",
        # Cyan &H00FFFF00, dark outline 7px, Alignment 2, MarginV 480
        "style": "&H00FFFF00,&H00000000,&H00441100,1,1,7,3,2,80,80,480",
        "size": 88,
    },
    "clean": {
        "label": "Минимализм (Белый)",
        # White &H00FFFFFF, black outline 5px, Alignment 2, MarginV 480
        "style": "&H00FFFFFF,&H00000000,&H00000000,1,1,6,2,2,80,80,480",
        "size": 84,
    },
    "ref": {
        "label": "Референс: пословно, акценты, приглушённые будущие слова",
        "style": "&H00F8F2F0,&H00000000,&H78000000,1,1,4,3,5,60,60,0",
        "size": 94,
    },
    "gold": {
        "label": "Премиум Золото (Luxury)",
        # Gold &H0024D1FF, black outline 7px, Alignment 2, MarginV 480
        "style": "&H0024D1FF,&H00000000,&H00000000,1,1,7,2,2,80,80,480",
        "size": 90,
    },
}

HORROR_HIGHLIGHTS = {
    "ДАЧЕ", "ОКНА", "ОКНО", "ОКНАМ", "СВЕТ", "ТЕМНОГО", "ФОНАРЬ", "ЛЕСА",
    "ЛЕСТНИЦУ", "ЛЕСТНИЦА", "ЭТАЖ", "НЕЛЬЗЯ", "НЕ ОТВЕЧАЙ", "УДАР", "КРИК",
    "ГОЛОС", "СВЯЗЬ", "СВЯЗИ", "ТЕЛЕГРАМ", "ТЕЛЕГРАМ-КАНАЛЕ", "ЧАСТЬ", "ПОДПИШИСЬ",
    "SURVIVE", "RULES", "NIGHT", "DANGER", "DO NOT", "RUN", "STAIRS", "WINDOW"
}


STYLE_HIGHLIGHTS = {
    "ref": "&H0034BEF7&",       # жёлтый акцент референса
    "mrbeast": "&H0000F0FF&",   # Electric Yellow
    "neon": "&H00FFFF00&",      # Cyan
    "horror": "&H0000F0FF&",    # Electric Yellow / Gold (Alerts are Crimson Red)
    "clean": "&H0024D1FF&",     # Gold
    "gold": "&H0024D1FF&",      # Diamond Gold
}


REF_WHITE, REF_YELLOW, REF_RED, REF_DIM = "&H00F8F2F0&", "&H0034BEF7&", "&H003C4AE4&", "&H00635251&"
REF_POS_Y = 1215          # как в референсе: подпись на уровне ~63% высоты, нижняя треть кадра свободна
_PUNCT_END = (".", "?", "!", "…", ",", ";", ":")


def _ref_chunks(words: list[dict], max_words: int = 4, max_chars: int = 21) -> list[list[dict]]:
    """Фразы по 1-4 слова: рвём по знакам препинания и по длине строки."""
    chunks, cur, chars = [], [], 0
    for w in words:
        token = str(w["word"]).strip()
        if cur and (len(cur) >= max_words or chars + 1 + len(token) > max_chars):
            chunks.append(cur)
            cur, chars = [], 0
        cur.append(w)
        chars += len(token) + (1 if len(cur) > 1 else 0)
        if token.endswith(_PUNCT_END) and len(cur) >= 1:
            chunks.append(cur)
            cur, chars = [], 0
    if cur:
        chunks.append(cur)
    return chunks


def _build_ass_ref(words_info, primary_set, alert_set, duration, out, font, size) -> Path:
    """Субтитры как в референсе: фраза из 1-4 слов, произнесённые слова яркие,
    ещё не произнесённые приглушены, акценты жёлтые (*слово*) и красные (!слово!)."""
    has_markup = bool(primary_set or alert_set)
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV",
        f"Style: Ref,{font},{size},&H00F8F2F0,&H00000000,&H78000000,1,1,4,3,5,60,60,0",
        "", "[Events]", "Format: Layer,Start,End,Style,Text",
    ]
    chunks = _ref_chunks(words_info)
    for ci, chunk in enumerate(chunks):
        clean = [re.sub(r"[^\w]", "", str(w["word"]), flags=re.UNICODE).upper() for w in chunk]
        base = []
        auto = -1
        if not has_markup:
            for j in range(len(chunk) - 1, -1, -1):
                if len(clean[j]) >= 4:
                    auto = j
                    break
        for j, c in enumerate(clean):
            if c in alert_set:
                base.append(REF_RED)
            elif c in primary_set or j == auto:
                base.append(REF_YELLOW)
            else:
                base.append(REF_WHITE)
        next_start = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else duration
        for k, w in enumerate(chunk):
            start = float(w["start"])
            end = float(chunk[k + 1]["start"]) if k < len(chunk) - 1 else min(float(w["end"]) + 0.3, next_start)
            if end <= start:
                end = start + 0.12
            parts = []
            for j, tok in enumerate(chunk):
                word = str(tok["word"]).strip().upper()
                if j < k:
                    parts.append(f"{{\\c{base[j]}}}{word}")
                elif j == k:
                    parts.append(f"{{\\c{base[j]}\\fscx107\\fscy107}}{word}{{\\fscx100\\fscy100}}")
                else:
                    parts.append(f"{{\\c{REF_DIM}}}{word}")
            lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},Ref,{{\\an5\\pos(540,{REF_POS_Y})}}{' '.join(parts)}")
    Path(out).write_text("\n".join(lines), encoding="utf-8")
    return Path(out)


def build_ass(
    text: str,
    duration: float,
    out: Path,
    group: int = 3,
    style_name: str = "mrbeast",
    preset: str = "facts",
    word_timestamps: list[dict] | None = None,
    hook_text: str = "",
    cta_text: str = "",
) -> Path:
    """Генерация ASS субтитров с пословным караоке-эффектом и точной синхронизацией."""
    font = env("SUBTITLE_FONT", "Arial")
    is_horror = (preset == "horror_rules")
    effective_style = style_name if style_name in SUBTITLE_STYLES else ("horror" if is_horror else "mrbeast")
    st = SUBTITLE_STYLES.get(effective_style, SUBTITLE_STYLES["mrbeast"])
    font_size = st["size"]
    style_params = st["style"]
    highlight_color = STYLE_HIGHLIGHTS.get(effective_style, "&H0000F0FF&")

    # Извлечение разметки акцентов из текста:
    # *слово* — главный акцент (желтый/стиль)
    # !слово! — алерт / опасность / число (красный)
    primary_matches = re.findall(r"\*([^*]+)\*", text)
    alert_matches = re.findall(r"!([^!]+)!", text)

    def _extract_words(phrases: list[str]) -> set[str]:
        res = set()
        for p in phrases:
            for w in p.split():
                cw = re.sub(r"[^\w]", "", w, flags=re.UNICODE).upper()
                if cw:
                    res.add(cw)
        return res

    primary_accent_set = _extract_words(primary_matches)
    alert_accent_set = _extract_words(alert_matches)

    # Подготовка таймингов слов: если есть word_timestamps — используем их, иначе пропорциональный расчет
    words_info: list[dict] = []
    if word_timestamps and len(word_timestamps) > 0:
        words_info = word_timestamps
    else:
        # Очищаем текст от символов разметки перед разбиением на слова
        clean_text = re.sub(r"[*!]", "", text)
        words = clean_text.split()
        weights = [len(w) + 2 for w in words]
        total = sum(weights) if weights else 1
        cur_t = 0.0
        for w, weight in zip(words, weights):
            w_dur = duration * weight / total
            words_info.append({"word": w, "start": round(cur_t, 3), "end": round(cur_t + w_dur, 3)})
            cur_t += w_dur

    if effective_style == "ref":
        return _build_ass_ref(words_info, primary_accent_set, alert_accent_set, duration, out, font, st["size"])

    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV",
        f"Style: Tik,{font},{font_size},{style_params}",
        f"Style: IntroBadge,{font},40,&H00D7FF,&H00000000,&H90000000,1,1,4,2,8,80,80,240",
        f"Style: OutroBadge,{font},42,&H00D7FF,&H00000000,&HA0000000,1,1,5,2,2,80,80,480",
    ]

    if is_horror:
        lines.append(f"Style: StatusBadge,{font},38,&H00E0E0E0,&H00000000,&H90000000,1,1,3,2,7,70,70,95")
        lines.append(f"Style: RuleCard,{font},46,&H00FFFFFF,&H00000000,&HA0000000,1,1,5,2,8,80,80,240")
        lines.append(f"Style: CliffCard,{font},44,&H0024D1FF,&H00000000,&HA0000000,1,1,5,2,8,80,80,240")

    lines.extend(["", "[Events]", "Format: Layer,Start,End,Style,Text"])

    # Intro хук карточка в начале видео
    if hook_text:
        clean_hook = re.sub(r"[*!]", "", hook_text).replace("\n", " ").strip()
        intro_end = min(2.0, duration * 0.25)
        lines.append(f"Dialogue: 2,0:00:00.10,{_ts(intro_end)},IntroBadge,{{\\an8\\pos(540,240)\\fad(150,150)\\b1\\c&H00D7FF&}}⚡ ВНИМАНИЕ ⚡\\N{{\\fs36\\c&HFFFFFF&}}{clean_hook[:60]}")

    # Караоке-субтитры с пословной подсветкой и универсальными акцентами
    for i in range(0, len(words_info), group):
        chunk = words_info[i:i + group]
        if not chunk:
            continue
        for k, target in enumerate(chunk):
            w_start = target["start"]
            if k < len(chunk) - 1:
                w_end = max(target["end"], min(chunk[k + 1]["start"], target["end"] + 0.15))
            else:
                w_end = target["end"]

            if w_end <= w_start:
                w_end = w_start + 0.12

            formatted = []
            for j, w in enumerate(chunk):
                w_str = w["word"].strip().upper()
                clean = re.sub(r"[^\w]", "", w_str, flags=re.UNICODE)

                is_alert = clean in alert_accent_set
                is_primary = clean in primary_accent_set
                # Фолбэк для хоррора, если в тексте сценария не было никакой разметки
                if not alert_accent_set and not primary_accent_set and is_horror and clean in HORROR_HIGHLIGHTS:
                    is_alert = True

                if j == k:
                    # Текущее произносимое слово (караоке зум-эффект)
                    word_color = "&H0022EE&" if is_alert else highlight_color
                    formatted.append(f"{{\\c{word_color}\\fscx108\\fscy108}}{w_str}{{\\fscx100\\fscy100\\c&H00FFFFFF&}}")
                elif is_alert:
                    # Тревожный / критический акцент (красный цвет)
                    formatted.append(f"{{\\c&H0022EE&}}{w_str}{{\\c&H00FFFFFF&}}")
                elif is_primary:
                    # Главный смысловой акцент (желтый цвет / акцент стиля)
                    formatted.append(f"{{\\c{highlight_color}}}{w_str}{{\\c&H00FFFFFF&}}")
                else:
                    formatted.append(f"{{\\c&H00FFFFFF&}}{w_str}")

            lines.append(f"Dialogue: 0,{_ts(w_start)},{_ts(w_end)},Tik,{' '.join(formatted)}")

    # Outro CTA карточка в конце ролика
    if cta_text and duration > 4.5 and not is_horror:
        outro_start = max(1.5, duration - 2.5)
        clean_cta = cta_text.replace("\n", " ").strip()
        lines.append(f"Dialogue: 2,{_ts(outro_start)},{_ts(duration)},OutroBadge,{{\\an2\\pos(540,1660)\\fad(250,150)\\b1\\c&H00D7FF&}}👉 ПОДПИСЫВАЙСЯ\\N{{\\fs30\\c&HFFFFFF&}}{clean_cta[:60]}")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


PROGRESS_COLORS = {
    "horror_rules": "red@0.95",
    "facts": "yellow@0.95",
    "it": "cyan@0.95",
    "motivation": "orange@0.95",
    "ecommerce": "green@0.95",
    "tg_cliffhanger": "yellow@0.95",
}


def render(
    clips: list[Path],
    audio: Path,
    ass: Path,
    out: Path,
    duration: float,
    workdir: Path,
    preset: str = "facts",
    sfx_events: list[dict] | None = None,
    progress_bar: bool = True,
    fps: int | None = None,
    clean: bool = False,
) -> Path:
    """Ультра-качественный 60 FPS рендер:

    - lanczos + unsharp + color pop
    - Плавные xfade переходы между сценами
    - Retention Progress Bar (динамическая полоска удержания снизу)
    - Жанровая фоновая музыка + динамический Audio Ducking под голос
    - Процедурные кинематографичные SFX (переходы, хук, клики)
    - Нормализация громкости EBU R128 (-14 LUFS)
    - CRF 17 (visually lossless студийный стандарт) + AAC 320k
    """
    out_fps = fps or FPS
    is_horror = (preset == "horror_rules")
    N = len(clips)
    trans_dur = 0.35 if N > 1 else 0.0
    seg = (duration + (N - 1) * trans_dur) / N

    vf = VF.replace(f"fps=fps={FPS}", f"fps=fps={out_fps}")
    if is_horror:
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{H},setsar=1,"
            f"fps=fps={out_fps}:round=near,"
            "unsharp=5:5:0.6:5:5:0.0,"
            "eq=contrast=1.06:saturation=1.05:brightness=0.0"
        )
    if clean:
        # Векторная графика motion_gfx: без резкости и цветокоррекции, они дают ореолы на плоских формах
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{H},setsar=1,fps=fps={out_fps}:round=near"
        )

    parts = []
    for i, c in enumerate(clips):
        p = (workdir / f"seg{i}.mp4").resolve()
        run([
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", Path(c).resolve(),
            "-t", f"{seg:.3f}", "-vf", vf, "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(out_fps), p
        ])
        parts.append(p)

    # Видеоряд: применяем xfade переходы для мягких стыков (с fallback на concat)
    merged_v = (workdir / "merged_video.mp4").resolve()
    xfade_success = False
    if N > 1:
        try:
            inputs = []
            for p in parts:
                inputs.extend(["-i", str(p)])
            filter_chains = []
            last_label = "0:v"
            for i in range(1, N):
                out_label = f"v{i}" if i < N - 1 else "vout"
                offset = i * (seg - trans_dur)
                filter_chains.append(f"[{last_label}][{i}:v]xfade=transition=fade:duration={trans_dur:.2f}:offset={offset:.3f}[{out_label}]")
                last_label = out_label
            filter_str = ";".join(filter_chains)
            run([
                "ffmpeg", "-y", *inputs,
                "-filter_complex", filter_str,
                "-map", f"[{last_label}]",
                "-t", f"{duration:.3f}",
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(out_fps),
                merged_v
            ], cwd=workdir)
            xfade_success = True
        except Exception:
            xfade_success = False

    if not xfade_success:
        lst = workdir / "list.txt"
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst.resolve(),
            "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(out_fps),
            merged_v
        ], cwd=workdir)

    # 1. Формируем финальный видеофильтр: Retention Progress Bar + Субтитры
    bar_color = PROGRESS_COLORS.get(preset, "yellow@0.95")
    if progress_bar:
        final_vf = (
            f"drawbox=x=0:y=1910:w=iw:h=8:color=black@0.45:t=fill,"
            f"drawbox=x=0:y=1910:w='min(iw,iw*(t/{duration:.3f}))':h=8:color={bar_color}:t=fill,"
            f"subtitles={Path(ass).name}"
        )
    else:
        final_vf = f"subtitles={Path(ass).name}"

    # 2. Подбор жанрового фонового трека
    bgm_path = (MUSIC / f"{preset}.mp3").resolve()
    if not bgm_path.exists():
        avail = list(MUSIC.glob("*.mp3"))
        if avail:
            bgm_path = avail[0].resolve()

    # 3. Подготовка звуковых эффектов (SFX)
    sfx_inputs = []
    sfx_chains = []
    sfx_labels = []
    base_sfx_idx = 3 if bgm_path.exists() else 2

    if sfx_events:
        for idx, ev in enumerate(sfx_events[:8]):
            f_path = Path(ev["file"]).resolve()
            if f_path.exists():
                sfx_inputs.extend(["-i", str(f_path)])
                in_idx = base_sfx_idx + len(sfx_labels)
                delay_ms = max(0, int(ev["offset"] * 1000))
                vol = ev.get("volume", 0.35)
                lbl = f"sfx{idx}"
                sfx_chains.append(f"[{in_idx}:a]aformat=channel_layouts=stereo,adelay={delay_ms}|{delay_ms},volume={vol:.2f}[{lbl}]")
                sfx_labels.append(f"[{lbl}]")

    has_sfx = bool(sfx_labels)
    if has_sfx:
        if len(sfx_labels) == 1:
            sfx_filter_str = f"{sfx_chains[0]};{sfx_labels[0]}anull[sfx_mix]"
        else:
            sfx_filter_str = f"{';'.join(sfx_chains)};{''.join(sfx_labels)}amix=inputs={len(sfx_labels)}:dropout_transition=0,volume=1.0[sfx_mix]"

    fade_start = max(0.5, duration - 1.5)
    bgm_volume = 0.28 if is_horror else 0.32

    # Студийная обработка диктора (Mastering Vocal Chain): срез низов, утепление баса, компрессия и яркость
    vocal_fx = (
        "highpass=f=75,"
        "equalizer=f=200:t=q:w=1.2:g=3.0,"
        "equalizer=f=3400:t=q:w=1.0:g=1.8,"
        "compand=attacks=0.02:decays=0.2:points=-60/-60|-24/-12|0/-3:gain=2.5"
    )

    # 4. Финальный сэндвич: Видео + Диктор + Музыка (Ducking) + SFX + Loudnorm
    if bgm_path.exists():
        if has_sfx:
            fc = (
                f"[1:a]{vocal_fx},asplit=2[voc][sc];"
                f"[2:a]aloop=loop=-1:size=2e+09,volume={bgm_volume:.2f},afade=t=out:st={fade_start:.2f}:d=1.5[bgm_raw];"
                f"[bgm_raw][sc]sidechaincompress=threshold=0.07:ratio=5:attack=25:release=300[ducked_bgm];"
                f"{sfx_filter_str};"
                f"[voc][ducked_bgm][sfx_mix]amix=inputs=3:duration=first:dropout_transition=0,loudnorm=I=-14:LRA=7:TP=-1.5[aout]"
            )
        else:
            fc = (
                f"[1:a]{vocal_fx},asplit=2[voc][sc];"
                f"[2:a]aloop=loop=-1:size=2e+09,volume={bgm_volume:.2f},afade=t=out:st={fade_start:.2f}:d=1.5[bgm_raw];"
                f"[bgm_raw][sc]sidechaincompress=threshold=0.07:ratio=5:attack=25:release=300[ducked_bgm];"
                f"[voc][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:LRA=7:TP=-1.5[aout]"
            )

        cmd = [
            "ffmpeg", "-y", "-i", merged_v,
            "-i", Path(audio).resolve(),
            "-i", bgm_path,
            *sfx_inputs,
            "-vf", final_vf,
            "-filter_complex", fc,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "17",
            "-profile:v", "high", "-level:v", "4.2", "-tune", "film",
            "-pix_fmt", "yuv420p", "-r", str(out_fps),
            "-c:a", "aac", "-b:a", "320k",
            "-t", f"{duration:.3f}", "-movflags", "+faststart", out.resolve()
        ]
        run(cmd, cwd=workdir)
    else:
        # Fallback без фоновой музыки (только диктор + SFX)
        if has_sfx:
            fc = (
                f"{sfx_filter_str};"
                f"[1:a]{vocal_fx}[voc];"
                f"[voc][sfx_mix]amix=inputs=2:duration=first:dropout_transition=0,loudnorm=I=-14:LRA=7:TP=-1.5[aout]"
            )
            cmd = [
                "ffmpeg", "-y", "-i", merged_v,
                "-i", Path(audio).resolve(),
                *sfx_inputs,
                "-vf", final_vf,
                "-filter_complex", fc,
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                "-profile:v", "high", "-level:v", "4.2", "-tune", "film",
                "-pix_fmt", "yuv420p", "-r", str(out_fps),
                "-c:a", "aac", "-b:a", "320k",
                "-t", f"{duration:.3f}", "-movflags", "+faststart", out.resolve()
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-i", merged_v,
                "-i", Path(audio).resolve(),
                "-vf", final_vf,
                "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                "-profile:v", "high", "-level:v", "4.2", "-tune", "film",
                "-pix_fmt", "yuv420p", "-r", str(out_fps),
                "-c:a", "aac", "-b:a", "320k",
                "-af", f"{vocal_fx},loudnorm=I=-14:LRA=7:TP=-1.5",
                "-t", f"{duration:.3f}", "-movflags", "+faststart", out.resolve()
            ]
        run(cmd, cwd=workdir)

    return out
