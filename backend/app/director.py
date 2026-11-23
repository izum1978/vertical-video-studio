"""Модуль Режиссёра-раскадровщика (Director) и Валидатора схемы раскадровки.

Превращает текст сценария и пословные таймкоды TTS в строгую монтажную раскадровку (beats)
с валидацией таймкодов, оверлеев и защитой от падений.
"""
import json
import re
from pathlib import Path

from .config import env
from .scene_resolver import normalize_scene_type

# Белый список режимов визуала и оверлеев согласно спецификации
WHITE_LIST_VISUALS = {"motion", "kinetic", "dataviz", "stock", "icons", "chat"}
WHITE_LIST_OVERLAYS = {
    "chapter_card", "lower_third", "sticker", "icon_chip",
    "map", "gauge", "counter", "end_card", "hud"
}

DIRECTOR_SYSTEM_PROMPT = (
    "Ты главный режиссёр-постановщик вертикальных видео (TikTok / Reels / Shorts). "
    "Твоя задача: взять реплики озвучки с точными таймкодами слов и превратить их в динамичную кинематографичную монтажную раскадровку JSON. "
    "Каждый бит должен визуализировать то, о чем говорит диктор в этот момент.\n\n"
    "РЕЖИМЫ ВИЗУАЛА (mode):\n"
    "- motion: динамическая кинематографическая сцена (окружение, персонажи, ключевое действие темы)\n"
    "- kinetic: акцентная типографика на кинематографичном фоне\n"
    "- dataviz: инфографика / важный чек-лист / таймер / счетчик\n"
    "- stock: реалистичный фото-ассет окружения\n\n"
    "ПРАВИЛА МОНТАЖА:\n"
    "1. Бит = 2.5–5 секунд. Таймкоды должны непрерывно покрывать всё аудио от 0.0 до конца без дыр.\n"
    "2. Смена визуала каждые 3-4 секунды для удержания внимания.\n"
    "3. Визуал должен ТОЧНО отражать суть реплики (если речь о ракетах — ракета в небе, если убежище — вход в укрытие, если сирена — тревожные огни).\n"
    "4. В поле prompt пиши подробное англоязычное описание сцены для кинематографичной генерации.\n\n"
    "ФОРМАТ ОТВЕТА - только валидный JSON:\n"
    '{"meta":{"title":str,"preset":str,"total_duration":float},'
    '"beats":[{"id":int,"start":float,"end":float,"text":str,"mode":"motion|kinetic|dataviz|stock",'
    '"title":str,"subtitle":str,"prompt":str,"fallbacks":["kinetic"]}]}'
)


def validate_and_repair_storyboard(storyboard: dict, total_duration: float) -> tuple[bool, str, dict]:
    """Валидирует раскадровку и автоматически устраняет мелкие огрехи LLM

    (дыры в таймкодах, выход за пределы длительности, опечатки в режимах).
    """
    if not isinstance(storyboard, dict) or "beats" not in storyboard or not isinstance(storyboard["beats"], list):
        return False, "Отсутствует массив beats в раскадровке", storyboard

    beats = storyboard["beats"]
    if not beats:
        return False, "Массив beats пуст", storyboard

    repaired_beats = []
    current_time = 0.0

    for i, b in enumerate(beats):
        b_id = b.get("id", i + 1)
        raw_start = float(b.get("start", current_time))
        raw_end = float(b.get("end", raw_start + 4.0))

        # Защита от дыр и инверсий
        start = round(max(current_time, raw_start), 2)
        end = round(max(start + 1.5, raw_end), 2)

        # Режим визуала из белого списка
        mode = b.get("mode", "kinetic").lower()
        if mode not in WHITE_LIST_VISUALS:
            mode = "kinetic"

        fallbacks = b.get("fallbacks", ["kinetic"])
        if not isinstance(fallbacks, list):
            fallbacks = ["kinetic"]
        if "kinetic" not in fallbacks:
            fallbacks.append("kinetic")

        repaired_b = {
            "id": b_id,
            "start": start,
            "end": end,
            "duration": round(end - start, 2),
            "text": b.get("text", ""),
            "mode": mode,
            "scene_type": normalize_scene_type(b.get("scene_type")) or normalize_scene_type(mode) or "",
            "camera_shot": b.get("camera_shot", ""),
            "camera_motion": b.get("camera_motion", ""),
            "title": (b.get("title") or b.get("text", "")[:24]).upper(),
            "subtitle": (b.get("subtitle") or "СМОТРИ ДАЛЬШЕ")[:32].upper(),
            "prompt": b.get("prompt", "cinematic dramatic scene, 35mm film photography, volumetric lighting, photorealistic, vertical 9:16, 8k"),
            "fallbacks": fallbacks,
        }
        repaired_beats.append(repaired_b)
        current_time = end

    # Подгоняем последний бит под точную длительность аудио
    if repaired_beats:
        repaired_beats[-1]["end"] = round(total_duration, 2)
        repaired_beats[-1]["duration"] = round(total_duration - repaired_beats[-1]["start"], 2)

    storyboard["beats"] = repaired_beats
    storyboard["meta"] = storyboard.get("meta", {})
    storyboard["meta"]["total_duration"] = round(total_duration, 2)
    return True, "OK", storyboard


def create_fallback_storyboard(script_text: str, total_duration: float, preset: str = "facts", title: str = "") -> dict:
    """Детерминированный генератор раскадровки на случай сбоя модели."""
    sentences = [s.strip() for s in re.split(r"[.!?]+", script_text) if len(s.strip()) > 6]
    if not sentences:
        sentences = [script_text]

    count = max(3, min(8, len(sentences)))
    seg_dur = total_duration / count

    # Чередуем визуальные режимы из белого списка
    modes_cycle = ["kinetic", "dataviz", "chat", "motion", "kinetic", "dataviz"]
    horror_presets = [
        ("motion", "window_stalker", "ОКНО ВО ТЬМУ", "НЕ СМОТРИ НА СТЕКЛО"),
        ("motion", "corridor_flashlight", "ТЕМНЫЙ КОРИДОР", "ЛУЧ ФОНАРЯ ДРОЖИТ"),
        ("motion", "door_breach", "ЗА ДВЕРЬЮ", "РУЧКА МЕДЛЕННО ОПУСКАЕТСЯ"),
        ("chat", "chat", "СООБЩЕНИЕ", "НЕОТВЕЧЕННЫЙ ВЫЗОВ"),
        ("motion", "candle_paranoia", "ДРОЖАЩАЯ СВЕЧА", "ТЕНЬ НА СТЕНЕ ОЖИВАЕТ"),
        ("motion", "peephole_stalker", "ВЗГЛЯД В ГЛАЗОК", "ОНО СТОИТ ЗА ДВЕРЬЮ"),
        ("motion", "underbed_claws", "ПОД КРОВАТЬЮ", "КОГТИ ТЯНУТСЯ ВВЕРХ"),
        ("motion", "drag_void", "ФИНАЛ", "ПОЛНАЯ ТЕМНОТА"),
    ]

    beats = []
    for i in range(count):
        start = round(i * seg_dur, 2)
        end = round(total_duration if i == count - 1 else (i + 1) * seg_dur, 2)
        sent = sentences[i % len(sentences)]
        words = sent.split()

        # scene_type пустой: сцену выберет resolve_scene по смыслу текста (слова-подсказки, затем ротация).
        # Прежние заготовленные подписи («ОКНО ВО ТЬМУ» и т. п.) не относились к тексту ролика.
        mode_val = "motion" if (preset == "horror_rules" or i % 4 != 3) else "kinetic"   # каждый 4-й бит крупным текстом
        stype = ""
        sub_title = (" ".join(words[:3]) if words else "ФАКТ").upper()
        subtitle = (" ".join(words[3:7]) if len(words) > 3 else "СМОТРИ ДО КОНЦА").upper()

        beats.append({
            "id": i + 1,
            "start": start,
            "end": end,
            "duration": round(end - start, 2),
            "text": sent,
            "mode": mode_val,
            "scene_type": stype,
            "title": sub_title[:24],
            "subtitle": subtitle[:32],
            "prompt": f"2D stylized dark animation illustration of {sub_title}, graphic novel comic style, bold clean lineart, cel-shaded, vertical 9:16, masterpiece artwork, no 3d render, no realistic photo",
            "fallbacks": ["stock", "kinetic"],
        })

    return {
        "meta": {"title": title or "РОЛИК", "preset": preset, "total_duration": round(total_duration, 2)},
        "beats": beats,
    }


def direct_storyboard(
    script_data: dict,
    word_timestamps: list[dict] | None,
    total_duration: float,
    preset: str = "facts",
    provider_name: str = "qwen",
    mock: bool = False,
    log=print,
) -> dict:
    """Тонкая обёртка: вся логика в director_llm.direct_storyboard_v2."""
    from .director_llm import direct_storyboard_v2
    return direct_storyboard_v2(
        script_data, word_timestamps, total_duration, preset=preset,
        provider_name=provider_name, mock=mock, log=log,
        fallback=create_fallback_storyboard, repair=validate_and_repair_storyboard,
    )

