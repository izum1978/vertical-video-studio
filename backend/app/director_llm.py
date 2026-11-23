"""Режиссёр v2: сценарий + пословные таймкоды -> раскадровка beats.

Что изменилось по сравнению с director.direct_storyboard:
  * режиссёр видит ВСЕ предложения с таймкодами (раньше только первые 80 слов);
  * схема раскадровки принудительная (structured output Ollama), scene_type только из белого списка;
  * одна повторная попытка с текстом ошибок валидатора;
  * явный num_ctx, чтобы Ollama не обрезала запрос молча;
  * ветки для всех провайдеров, включая claude (раньше шёл тихий фолбэк);
  * в meta пишется, кто реально сделал раскадровку (source/model/attempts/errors).
"""
import json
import re
import time

from .config import env
from .scene_resolver import SCENE_CHOICES, SCENE_HINTS, SCENE_RENDERERS, normalize_scene_type

MAX_ATTEMPTS = 2
MODES = ["motion", "kinetic", "dataviz", "chat", "stock"]
CAMERA_SHOTS = ["wide", "medium_pov", "extreme_close_up", "dutch_angle", "overhead"]
CAMERA_MOTIONS = ["zoom_in", "zoom_out", "pan_down", "pan_up"]

OVERLAY_TYPES = ["sticker", "lower_third", "chapter_card"]
OVERLAY_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": OVERLAY_TYPES},
        "text": {"type": "string"}, "title": {"type": "string"}, "sub": {"type": "string"},
        "num": {"type": "string"}, "color": {"type": "string", "enum": ["yellow", "red", "white"]},
        "slot": {"type": "string", "enum": ["left", "center", "right", "top"]},
    },
    "required": ["type"],
}

STORYBOARD_SCHEMA = {
    "type": "object",
    "properties": {
        "beats": {
            "type": "array", "minItems": 3, "maxItems": 16,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "start": {"type": "number"},
                    "end": {"type": "number"},
                    "text": {"type": "string"},
                    "mode": {"type": "string", "enum": MODES},
                    "scene_type": {"type": "string", "enum": list(SCENE_CHOICES)},
                    "title": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "camera_shot": {"type": "string", "enum": CAMERA_SHOTS},
                    "camera_motion": {"type": "string", "enum": CAMERA_MOTIONS},
                    "visual": {"type": "string"},
                    "items": {"type": "array", "maxItems": 4, "items": {"type": "string"}},
                    "overlays": {"type": "array", "maxItems": 3, "items": OVERLAY_SCHEMA},
                },
                "required": ["id", "start", "end", "text", "mode", "scene_type", "title", "subtitle"],
            },
        }
    },
    "required": ["beats"],
}
# hud и overlays необязательные: если модель их не вернула, движок motion_gfx выводит их из текста сам

DIRECTOR_SYSTEM_PROMPT = (
    "Ты режиссёр-раскадровщик вертикальных видео (TikTok / Reels / Shorts). "
    "Тебе дают предложения закадрового текста с точными таймкодами. "
    "Верни монтажную раскадровку JSON. Ты не задаёшь пиксели, ты выбираешь значения из списков.\n\n"
    "mode: motion (анимированная сцена), kinetic (крупный текст), dataviz (чек-лист), chat (мессенджер), stock.\n"
    "scene_type (для mode=motion выбирай по смыслу):\n"
    + "\n".join(f"- {k}: {SCENE_HINTS[k]}" for k in SCENE_CHOICES) + "\n"
    "camera_shot: " + ", ".join(CAMERA_SHOTS) + ". camera_motion: " + ", ".join(CAMERA_MOTIONS) + ".\n"
    "items: до 4 коротких пунктов для сцен-списков (checklist_hud, steps_row, cards_row, timeline, phone_screen, terminal_window).\n"
    "overlays (необязательно): sticker (короткая плашка-подпись), lower_third (имя и роль персонажа), "
    "chapter_card (номер, title, sub для пронумерованных правил).\n\n"
    "ПРАВИЛА:\n"
    "1. Бит = 2-5 секунд. Границы битов совпадают с границами предложений. "
    "Таймкоды непрерывно покрывают аудио от 0.0 до конца без дыр и наложений.\n"
    "2. Два соседних бита не имеют одинаковый scene_type. Чередуй планы камеры.\n"
    "3. Для жанров horror_rules и story не менее 80% битов mode=motion со сценами ночной истории.\n"
    "4. title до 3 слов, subtitle до 5 слов, ЗАГЛАВНЫМИ буквами.\n"
    "5. Последний бит с призывом или анонсом следующей части: scene_type end_card.\n"
    "6. Если подходящей сцены в списке нет, scene_type=custom, а в visual опиши по-русски до 14 слов, что нарисовать: "
    "предметы, место, время суток (например: кухня ночью, на столе сковорода и бутылка молока).\n"
    "7. Ответ только JSON, без пояснений."
)


# ---------- вход: предложения с таймкодами ----------
def clean_for_tts(script_text: str) -> str:
    s = re.sub(r"\[sfx:\s*\w+\]", "", script_text, flags=re.I)
    return re.sub(r"[*!]", "", s)


def split_sentences_with_timing(script_text: str, word_timestamps: list | None, total: float) -> list[dict]:
    sents = [s.strip() for s in re.split(r"(?<=[.?…])\s+", clean_for_tts(script_text)) if s.strip()]
    if not sents:
        sents = [clean_for_tts(script_text).strip() or "..."]
    counts = [max(1, len(s.split())) for s in sents]
    total_words = sum(counts)
    out, cum = [], 0
    words = [w for w in (word_timestamps or []) if isinstance(w, dict)]
    for s, c in zip(sents, counts):
        if words:
            i0 = min(len(words) - 1, round(cum * len(words) / total_words))
            i1 = min(len(words), max(i0 + 1, round((cum + c) * len(words) / total_words)))
            start = float(words[i0].get("start", 0.0))
            end = float(words[i1 - 1].get("end", start))
        else:
            start, end = total * cum / total_words, total * (cum + c) / total_words
        out.append({"text": s, "start": round(start, 2), "end": round(end, 2)})
        cum += c
    out[0]["start"] = 0.0
    out[-1]["end"] = round(total, 2)
    for a, b in zip(out, out[1:]):  # стыкуем без дыр
        a["end"] = b["start"] = round(max(a["start"], (a["end"] + b["start"]) / 2), 2)
    return out


def build_user_prompt(title: str, preset: str, total: float, sentences: list[dict]) -> str:
    """ЕДИНСТВЕННОЕ место, где собирается запрос режиссёра. Его же использует сборщик датасета."""
    lines = [f"S{i + 1} [{s['start']:.2f}-{s['end']:.2f}] {s['text']}" for i, s in enumerate(sentences)]
    return (
        f"Тема: {title}\nЖанр: {preset}\nДлительность аудио: {total:.2f} сек.\n"
        "Предложения с таймкодами:\n" + "\n".join(lines) +
        f"\n\nСформируй beats от 0.0 до {total:.2f} сек без дыр и наложений."
    )


# ---------- проверка ----------
def check_storyboard(sb, total: float) -> list[str]:
    """Строгая проверка. Пустой список = ответ годный. Мелкие дыры чинит validate_and_repair."""
    beats = sb.get("beats") if isinstance(sb, dict) else None
    if not isinstance(beats, list) or not beats:
        return ["в ответе нет непустого массива beats"]
    errs, prev_type, prev_end = [], None, 0.0
    for i, b in enumerate(beats):
        if not isinstance(b, dict):
            return [f"бит {i + 1} не объект"]
        st = normalize_scene_type(b.get("scene_type"))
        if b.get("mode") == "motion" and not st:
            errs.append(f"бит {i + 1}: scene_type '{b.get('scene_type')}' вне списка")
        try:
            s, e = float(b.get("start", prev_end)), float(b.get("end", 0))
        except (TypeError, ValueError):
            errs.append(f"бит {i + 1}: start/end не числа")
            continue
        if e - s > 6.0:
            errs.append(f"бит {i + 1}: длиннее 6 секунд")
        if abs(s - prev_end) > 0.5:
            errs.append(f"бит {i + 1}: дыра или наложение (начало {s}, ожидалось {prev_end})")
        if st and st == prev_type:
            errs.append(f"биты {i} и {i + 1}: одинаковый scene_type")
        prev_type, prev_end = st, e
    if abs(prev_end - total) > 1.5:
        errs.append(f"раскадровка заканчивается на {prev_end}, а аудио {total:.1f} сек")
    return errs


def parse_json_loose(raw: str) -> dict:
    raw = re.sub(r"^```(?:json)?|```$", "", (raw or "").strip(), flags=re.M).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, flags=re.S)  # JSON внутри лишнего текста
        if not m:
            raise
        return json.loads(m.group(0))


# ---------- вызовы моделей ----------
def _ollama_native_base() -> str:
    base = env("OLLAMA_BASE_URL", "http://localhost:11434/v1").rstrip("/")
    return base[:-3] if base.endswith("/v1") else base


def call_ollama(model: str, system: str, user: str, schema: dict | None, timeout: float) -> str:
    import httpx
    if env("OLLAMA_API", "native") == "openai":  # LM Studio / vLLM
        r = httpx.post(
            env("OLLAMA_BASE_URL", "http://localhost:11434/v1").rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {env('OLLAMA_API_KEY', 'ollama')}"},
            json={"model": model, "temperature": 0.3,
                  "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                  "response_format": {"type": "json_object"}},
            timeout=timeout)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    r = httpx.post(
        _ollama_native_base() + "/api/chat",
        json={"model": model, "stream": False,
              "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
              "format": schema or "json",
              "options": {"temperature": 0.3,
                          "num_ctx": int(env("OLLAMA_NUM_CTX", "8192")),
                          "num_predict": int(env("OLLAMA_NUM_PREDICT", "3000"))}},
        timeout=timeout)
    r.raise_for_status()
    return r.json()["message"]["content"]


def call_gemini(model: str, system: str, user: str, schema, timeout: float) -> str:
    import httpx
    key = env("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    r = httpx.post(url, json={"contents": [{"role": "user", "parts": [{"text": f"{system}\n\n{user}"}]}],
                              "generationConfig": {"response_mime_type": "application/json"}}, timeout=timeout)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def call_openai(model: str, system: str, user: str, schema, timeout: float) -> str:
    import httpx
    r = httpx.post("https://api.openai.com/v1/chat/completions",
                   headers={"Authorization": f"Bearer {env('OPENAI_API_KEY')}"},
                   json={"model": model, "temperature": 0.3,
                         "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                         "response_format": {"type": "json_object"}}, timeout=timeout)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_claude(model: str, system: str, user: str, schema, timeout: float) -> str:
    import httpx
    r = httpx.post("https://api.anthropic.com/v1/messages",
                   headers={"x-api-key": env("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"},
                   json={"model": model, "max_tokens": 3000, "temperature": 0.3, "system": system,
                         "messages": [{"role": "user", "content": user}]}, timeout=timeout)
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json()["content"] if b.get("type") == "text")


def _models_for(provider: str) -> tuple:
    if provider in ("qwen", "qwen_local"):
        names = [env("OLLAMA_DIRECTOR_MODEL"), env("OLLAMA_MODEL", "qwen2.5:7b")]
        return call_ollama, [n for n in dict.fromkeys(names) if n]
    if provider == "gemini":
        return call_gemini, [env("GEMINI_MODEL", "gemini-2.5-flash")]
    if provider == "openai":
        return call_openai, [env("OPENAI_MODEL", "gpt-4o-mini")]
    if provider in ("claude", "anthropic"):
        return call_claude, [env("ANTHROPIC_MODEL", "claude-sonnet-4-6")]
    raise ValueError(f"Режиссёр не поддерживает провайдера '{provider}'")


def call_llm(provider: str, system: str, user: str, schema: dict | None) -> tuple[str, str]:
    """Возвращает (текст ответа, имя модели, которая ответила)."""
    fn, models = _models_for(provider)
    timeout = float(env("DIRECTOR_TIMEOUT", "180"))
    last = None
    for model in models:
        try:
            return fn(model, system, user, schema, timeout), model
        except Exception as e:  # noqa: BLE001 пробуем следующую модель, ошибку запоминаем
            last = e
    raise RuntimeError(f"{provider}: {last}")


# ---------- главная функция ----------
def direct_storyboard_v2(script_data, word_timestamps, total_duration, preset="facts",
                         provider_name="qwen", mock=False, log=print,
                         fallback=None, repair=None, llm=call_llm) -> dict:
    """fallback и repair передаются из director.py (create_fallback_storyboard и
    validate_and_repair_storyboard); llm можно подменить в тестах."""
    script_text, title = script_data.get("script", ""), script_data.get("title", "")
    info = {"source": None, "model": None, "attempts": 0, "errors": [], "latency_s": 0.0}

    def finish(sb, source):
        info["source"] = source
        sb.setdefault("meta", {})["director"] = info
        return sb

    if mock:
        sb = fallback(script_text, total_duration, preset=preset, title=title)
        return finish(repair(sb, total_duration)[2], "mock")

    sentences = split_sentences_with_timing(script_text, word_timestamps, total_duration)
    user_prompt = build_user_prompt(title, preset, total_duration, sentences)
    feedback, t0 = "", time.time()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        info["attempts"] = attempt
        try:
            raw, model = llm(provider_name, DIRECTOR_SYSTEM_PROMPT, user_prompt + feedback, STORYBOARD_SCHEMA)
            info["model"] = model
            parsed = parse_json_loose(raw)
            errs = check_storyboard(parsed, total_duration)
            if errs:
                info["errors"] += [f"попытка {attempt}: {e}" for e in errs]
                if attempt < MAX_ATTEMPTS:
                    feedback = ("\n\nПредыдущий ответ содержал ошибки: " + "; ".join(errs[:5]) +
                                ". Исправь и верни полный JSON.")
                    continue
            ok, msg, repaired = repair(parsed, total_duration)
            if ok:
                info["latency_s"] = round(time.time() - t0, 1)
                log(f"Режиссёр: {provider_name}/{model}, попыток {attempt}, замечаний {len(errs)}")
                return finish(repaired, provider_name)
            info["errors"].append(f"попытка {attempt}: {msg}")
        except Exception as e:  # noqa: BLE001
            info["errors"].append(f"попытка {attempt}: {type(e).__name__}: {e}")
    info["latency_s"] = round(time.time() - t0, 1)
    log(f"⚠ Режиссёр: LLM не дала валидную раскадровку, включён шаблон. Причины: {'; '.join(info['errors'][-3:])}")
    sb = fallback(script_text, total_duration, preset=preset, title=title)
    return finish(repair(sb, total_duration)[2], "fallback")
