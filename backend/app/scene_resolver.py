"""Выбор 2D-рендерера для бита раскадровки.

Приоритет: 1) scene_type от режиссёра (если он в белом списке);
2) mode == "chat"; 3) ключевые слова, но только по границам слов;
4) пресет; 5) ротация. Решение режиссёра больше не перебивается подстрокой.
"""
import re

SCENE_RENDERERS = (
    "window_stalker", "corridor_flashlight", "door_breach", "candle_paranoia",
    "peephole_stalker", "bedroom_peace", "underbed_claws", "underbed_twin",
    "creature_turn", "drag_void",
    "cyber_chip", "atomic_orbit", "dynamic_canvas",
    "kinetic_punch", "checklist_hud", "chat_messenger",
    "city_night", "phone_screen", "map_route", "timeline",
    "counter_stat", "comparison_split", "office_desk", "quote_card",
    # сцены движка motion_gfx (стиль референсов)
    "night_village", "radio_alert", "neighbor_fence", "sound_rings", "ladder_house",
    "bathtub_water", "pressure_gauge", "highway_jam", "lit_window_house", "icon_chips",
    "kinetic_text", "terminal_window", "steps_row", "cards_row", "end_card", "custom", "ai_scene",
)
# Эти имена видит LLM-режиссёр (структурированный вывод и промпт). Старые имена
# по-прежнему принимаются и приводятся к ним в motion_gfx.engine.LEGACY.
SCENE_CHOICES = (
    "night_village", "radio_alert", "neighbor_fence", "sound_rings", "ladder_house", "bathtub_water",
    "pressure_gauge", "highway_jam", "map_route", "lit_window_house", "icon_chips",
    "kinetic_text", "counter_stat", "checklist_hud", "timeline", "comparison_split", "quote_card",
    "phone_screen", "terminal_window", "steps_row", "cards_row", "city_night", "office_desk", "end_card", "custom", "ai_scene",
)
SCENE_HINTS = {
    "night_village": "ночной посёлок, дома, огни", "radio_alert": "радио, срочное сообщение, эфир",
    "neighbor_fence": "персонаж у забора, сосед", "sound_rings": "звук, шум, расходящиеся круги, толпа",
    "ladder_house": "лестница, этажи, взобраться", "bathtub_water": "вода, ванна, запас воды",
    "pressure_gauge": "давление, напор, счётчик-стрелка", "highway_jam": "трасса, пробка, машины",
    "map_route": "карта, маршрут, путь", "lit_window_house": "дом, свет в окне, силуэт",
    "icon_chips": "пара иконок-подсказок и дом", "kinetic_text": "крупный текст-удар, универсальная сцена",
    "counter_stat": "большая цифра, процент, сумма", "checklist_hud": "правила, список с галочками",
    "timeline": "даты, хронология", "comparison_split": "сравнение двух вещей",
    "quote_card": "цитата, тезис", "phone_screen": "телефон, сообщения, соцсети",
    "terminal_window": "код, терминал, технологии", "steps_row": "этапы, шаги по порядку",
    "cards_row": "три пункта карточками", "city_night": "город, небоскрёбы ночью",
    "office_desk": "работа, офис, ноутбук", "end_card": "финал, часть 2, подпишись",
    "custom": "своя сцена: нужной нет в списке, опиши в visual, что нарисовать",
    "ai_scene": "нейросетевая кинематографичная сцена под любой сюжет (локация, персонаж, пейзаж)",
}
NIGHT_STORY_PRESETS = ("horror_rules", "story", "tg_cliffhanger")
HORROR_SCENES = SCENE_RENDERERS[:10] + (
    "night_village", "radio_alert", "neighbor_fence", "sound_rings", "ladder_house",
    "bathtub_water", "pressure_gauge", "highway_jam", "lit_window_house", "icon_chips", "map_route",
)
HORROR_ROTATION = (
    "night_village", "neighbor_fence", "lit_window_house", "sound_rings", "highway_jam", "ladder_house",
)
NEEDS_PRESET = {
    "dynamic_canvas", "kinetic_punch", "checklist_hud", "chat_messenger",
    "city_night", "phone_screen", "map_route", "timeline",
    "counter_stat", "comparison_split", "office_desk", "quote_card",
}

# Короткие имена, которые модель могла выдать (из старых промптов и датасета)
ALIASES = {
    "bedroom": "bedroom_peace", "creature": "creature_turn", "void": "drag_void",
    "chat": "chat_messenger", "kinetic": "kinetic_punch", "dataviz": "checklist_hud",
    "city": "city_night", "phone": "phone_screen", "map": "map_route",
    "route": "map_route", "stat": "counter_stat", "counter": "counter_stat",
    "comparison": "comparison_split", "split": "comparison_split",
    "office": "office_desk", "desk": "office_desk", "quote": "quote_card",
    "village": "night_village", "radio": "radio_alert", "fence": "neighbor_fence", "rings": "sound_rings",
    "ladder": "ladder_house", "bath": "bathtub_water", "bathtub": "bathtub_water", "gauge": "pressure_gauge",
    "highway": "highway_jam", "road": "highway_jam", "house": "lit_window_house", "chips": "icon_chips",
    "text": "kinetic_text", "title": "kinetic_text", "terminal": "terminal_window", "steps": "steps_row",
    "cards": "cards_row", "end": "end_card", "outro": "end_card", "checklist": "checklist_hud",
}


def normalize_scene_type(value) -> str | None:
    v = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    v = ALIASES.get(v, v)
    return v if v in SCENE_RENDERERS else None


def _rx(exact=(), prefix=()):
    """Короткие слова ищем по точным формам, длинные уникальные основы по префиксу.
    Границы слов (?<!\\w) и (?!\\w) работают с кириллицей."""
    parts = [re.escape(f) for f in exact] + [re.escape(p) + r"\w*" for p in prefix]
    return re.compile(r"(?<!\w)(?:" + "|".join(parts) + r")(?!\w)", re.IGNORECASE)


NIGHT_RULES = [
    ("radio_alert", _rx(exact=("радио", "эфир", "эфира", "эфире", "приёмник", "приемник", "приёмника", "приемника"))),
    ("pressure_gauge", _rx(prefix=("насос", "давлен", "напор", "манометр"))),
    ("bathtub_water", _rx(exact=("ванна", "ванны", "ванну", "ванной", "вода", "воды", "воду", "водой", "воде"))),
    ("ladder_house", _rx(exact=("лестница", "лестницы", "лестницу", "лестнице", "лестницей", "лестниц"))),
    ("highway_jam", _rx(exact=("трасса", "трассы", "трассе", "трассу", "пробка", "пробки", "пробке",
                               "бензин", "бензина", "бак", "бака", "баком"))),
    ("sound_rings", _rx(exact=("звук", "звука", "звуку", "звуком", "шум", "шума", "шуму", "шумом"))),
    ("neighbor_fence", _rx(exact=("сосед", "соседа", "соседу", "соседом", "соседи", "соседей",
                                  "забор", "забора", "забору", "забором"))),
]
PRIMARY_RULES = [
    ("window_stalker", _rx(exact=(
        "окно", "окна", "окне", "окну", "окном", "окон", "стекло", "стекла", "стекле",
        "стеклом", "дождь", "дождя", "дождю", "дождём", "дожде", "дожди", "ливень", "ливня"))),
    ("corridor_flashlight", _rx(exact=(
        "коридор", "коридора", "коридоре", "коридору", "коридором", "фонарь", "фонаря",
        "фонарём", "фонарик", "фонарика", "фонариком", "луч", "луча", "лучи", "лучом", "лучу"))),
    ("door_breach", _rx(exact=(
        "дверь", "двери", "дверью", "дверей", "дверям", "ручка", "ручку", "ручки", "ручкой",
        "замок", "замка", "замку", "замком", "замке", "порог", "порога", "пороге", "порогом"))),
    ("candle_paranoia", _rx(exact=(
        "свеча", "свечи", "свечу", "свечой", "свечей", "тень", "тени", "тенью", "теней",
        "стол", "стола", "столу", "столом", "столе", "пламя", "пламени", "пламенем"))),
    ("peephole_stalker", _rx(exact=(
        "глазок", "глазка", "глазку", "глазком", "глазке"))),
    ("bedroom_peace", _rx(exact=(
        "кровать", "кровати", "кроватью", "ночник", "ночника", "ночником",
        "заяц", "зайца", "зайцем", "спальня", "спальни", "спальне", "спальню"))),
    ("underbed_claws", _rx(exact=(
        "когти", "когтей", "когтями", "коготь", "шелест", "шелеста", "шелестом",
        "шорох", "шороха", "шорохи", "шорохов"), prefix=("полз",))),
    ("underbed_twin", _rx(exact=(
        "двойник", "двойника", "двойнику", "двойником", "тссс", "тсс",
        "ребёнок", "ребенок", "ребёнка", "ребенка", "ребёнку", "ребенку", "ребёнком", "ребенком"))),
    ("creature_turn", _rx(
        exact=("существо", "существа", "существу", "существом", "существе",
               "зуб", "зубы", "зубов", "зубами", "зубах", "зуба"),
        prefix=("метаморфоз", "улыб", "монстр"))),
    ("drag_void", _rx(prefix=("финал", "погас", "утаскива", "бездн"))),
    ("chat_messenger", _rx(
        exact=("смс", "чат", "чата", "чате", "чату", "чатом", "звонок"),
        prefix=("сообщен", "переписк", "telegram"))),
    ("cyber_chip", _rx(
        exact=("чип", "чипа", "чипы", "чипов", "код", "кода", "коду", "кодом", "коде"),
        prefix=("нейро",))),
    ("atomic_orbit", _rx(
        exact=("наука", "науки", "науку", "науке", "наукой"),
        prefix=("атом", "космос", "планет"))),
    ("city_night", _rx(
        exact=("город", "города", "городе", "городу", "городом", "ночь", "ночи", "ночью", "улица", "улицы", "улице"),
        prefix=("небоскреб", "мегаполис"))),
    ("phone_screen", _rx(
        exact=("телефон", "телефона", "телефоне", "телефону", "смартфон", "смартфона", "уведомление", "уведомления"),
        prefix=("соцсет", "приложен"))),
    ("map_route", _rx(
        exact=("карта", "карты", "карте", "карту", "маршрут", "маршрута", "путь", "пути", "траектория"),
        prefix=("навигац", "геолокац"))),
    ("timeline", _rx(
        exact=("хронология", "хронологии", "эпоха", "эпохи", "веха", "вехи", "таймлайн"),
        prefix=("столет", "тысячелет"))),
    ("counter_stat", _rx(
        exact=("процент", "процента", "процентов", "статистика", "статистики", "показатель", "рекорд"),
        prefix=("миллиард", "миллион"))),
    ("comparison_split", _rx(
        exact=("сравнение", "сравнения", "разница", "разницы", "против"),
        prefix=("сравни", "сопостав"))),
    ("office_desk", _rx(
        exact=("офис", "офиса", "офисе", "ноутбук", "ноутбука", "аналитика"),
        prefix=("рабоч",))),
    ("quote_card", _rx(
        exact=("цитата", "цитаты", "мудрость", "мудрости", "афоризм", "афоризма"),
        prefix=("высказыван",))),
]
SECONDARY_RULES = [
    ("checklist_hud", _rx(exact=(
        "правило", "правила", "правил", "правилу", "правилом", "правилах",
        "список", "списка", "списку", "списком"))),
    ("kinetic_punch", _rx(exact=("шок", "шока", "шоком"), prefix=("панч", "шокир"))),
]
HORROR_WORDS = _rx(exact=("страх", "страха", "страху", "страхом"), prefix=("хоррор", "монстр"))
ROTATION = (
    "kinetic_punch", "checklist_hud", "dynamic_canvas", "chat_messenger",
    "city_night", "phone_screen", "map_route", "timeline",
    "counter_stat", "comparison_split", "office_desk", "quote_card",
)


def _first_match(rules, text):
    for scene, rx in rules:
        m = rx.search(text)
        if m:
            return scene, f"keyword:{m.group(0).lower()}"
    return None


def resolve_scene(beat: dict, preset: str = "facts", index: int = 0) -> tuple[str, str]:
    """Возвращает (имя рендерера, причина). Причину пишем в meta для отладки."""
    st = normalize_scene_type(beat.get("scene_type"))
    if st:
        return st, "scene_type"

    mode = str(beat.get("mode") or "").lower()
    if mode == "chat":
        return "chat_messenger", "mode"

    # Англоязычный prompt оператора в поиск не берём: он только добавляет шум
    text = " ".join(str(beat.get(k) or "") for k in ("title", "subtitle", "text"))

    if preset in NIGHT_STORY_PRESETS:
        hit = _first_match(NIGHT_RULES, text)
        if hit:
            return hit
    hit = _first_match(PRIMARY_RULES, text)
    if hit:
        if hit[0] == "city_night" and preset in NIGHT_STORY_PRESETS:
            return "night_village", hit[1]   # в сюжетных роликах «ночь» это посёлок, а не мегаполис
        return hit
    if preset in ("it", "tech"):
        return "cyber_chip", "preset"
    if preset in NIGHT_STORY_PRESETS or HORROR_WORDS.search(text):
        return HORROR_ROTATION[index % len(HORROR_ROTATION)], "horror_rotation"
    if mode == "dataviz":
        return "checklist_hud", "mode"
    hit = _first_match(SECONDARY_RULES, text)
    if hit:
        return hit
    if mode == "kinetic":
        return "kinetic_punch", "mode"
    return ROTATION[index % len(ROTATION)], "rotation"
