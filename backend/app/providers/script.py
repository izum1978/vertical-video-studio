import json
import re

try:
    import httpx
except ImportError:
    import requests as httpx

from ..config import env
from .base import ScriptProvider

PRESETS = {
    "horror_rules": (
        "Хоррор / Свод правил выживания",
        "Аналоговый хоррор и свод правил выживания при ночной аномалии. Формат инструкции: нагнетающий тревожный хук, 2–3 строгих правила с нумерацией и жесткий клиффхэнгер на вторую часть в Telegram-канале."
    ),
    "facts": ("Интересные факты / Истории", "Удивительные факты или короткая история с интригой и неожиданной развязкой."),
    "tg_cliffhanger": ("УБТ Перегон в Telegram", "История с максимальным удержанием и резким клиффхэнгером в конце: продолжение или секретные материалы по ссылке в описании профиля."),
    "motivation": ("Мотивация / Дисциплина", "Энергичный мотивационный монолог, короткие сильные фразы, призыв к действию."),
    "ecommerce": ("Товарка / Обзор для магазина", "Продающий ролик: яркая проблема, распаковка/демонстрация решения и призыв заказать по ссылке."),
    "it": ("IT / Образование", "Объясни технический или полезный концепт просто, с наглядным жизненным примером."),
}
LANGS = {"ru": "русский", "en": "English"}

SYSTEM = (
    "Ты сценарист и визуальный режиссёр вирусных вертикальных видео (TikTok / Instagram Reels / YouTube Shorts). "
    "Отвечай ТОЛЬКО валидным JSON без markdown: "
    '{"title": str, "hook": str, "script": str, "keywords": [str], "post_caption": str, "hashtags": [str], '
    '"scenes": [{"id": int, "title": str, "prompt": str, "badge": str, "subtitle": str, "motion": str}]}. '
    "script — закадровый текст на 35–55 секунд (85–130 слов), начинается с мощного цепляющего хука, без ремарок, эмодзи и списков. "
    "В тексте script ОБЯЗАТЕЛЬНО используй вирусную смысловую разметку акцентов: выделяй *слово* звёздочками для главного смыслового акцента (желтый цвет) и !слово! восклицательными знаками для критических моментов, опасности или ключевых цифр (красный цвет). Расставляй по 1-2 таких акцента в каждом предложении (например: 'Если ночью *пропадет связь* — !не выходи! на улицу'). "
    "Также в ключевых моментах переходов и кульминации расставляй звуковые маркеры SFX: [sfx: whoosh], [sfx: glitch], [sfx: boom], [sfx: click], [sfx: riser], [sfx: heartbeat] (2–3 маркера на сценарий). "
    "scenes — список из 4–6 последовательных визуальных сцен, точно соответствующих хронологии и смыслу сценария. "
    "Для каждой сцены: "
    "  id (1, 2, ...), "
    "  title (короткий броский заголовок на русском языке из 2–4 слов, напр. 'ВЕЧНЫЙ МЁД', 'ЛЕСТНИЦА ВВЕРХ', 'МАРИАНСКАЯ БЕЗДНА'), "
    "  badge (короткая плашка, напр. 'ФАКТ #1', 'ПРАВИЛО 01', 'ТАЙНА #3', 'СОВЕТ ДНЯ'), "
    "  subtitle (ключевой тезис или цифра из 2–4 слов, напр. 'БОЛЕЕ 3000 ЛЕТ', 'ГАСИ СВЕТ', 'ГЛУБИНА 11 КМ'), "
    "  prompt (детальный художественный запрос на АНГЛИЙСКОМ языке для генератора фото/иллюстраций: кинематографичное освещение, 8k resolution, vertical 9:16 portrait composition, без надписей), "
    "  motion ('zoom_in', 'zoom_out', 'pan_down', 'pan_up'). "
    "keywords — 4–6 коротких английских запросов для поиска видео. "
    "post_caption — готовый вирусный текст поста для TikTok и Reels с интригой (1-2 предложения). "
    "hashtags — 5-7 релевантных хэштегов без решеток."
)


def build_user_prompt(topic: str, preset: str, lang: str) -> str:
    style = PRESETS.get(preset, PRESETS["facts"])[1]
    return f"Тема: {topic}\nСтиль: {style}\nЯзык текста: {LANGS.get(lang, lang)}"


def _synthesize_scenes(script: str, keywords: list[str], preset: str, title: str) -> list[dict]:
    """Разбивает сценарий на 4–6 сцен, если модель вернула старый формат без scenes."""
    sentences = [s.strip() for s in re.split(r"[.!?]+", script) if len(s.strip()) > 8]
    if not sentences:
        sentences = [script]
    
    count = max(3, min(6, len(sentences)))
    step = len(sentences) / count
    scenes = []
    motions = ["zoom_in", "pan_down", "zoom_out", "pan_up", "zoom_in", "zoom_out"]
    
    for i in range(count):
        idx = min(int(i * step), len(sentences) - 1)
        sent = sentences[idx]
        words = sent.split()
        kw = keywords[i % len(keywords)] if keywords else "cinematic visual"
        
        badge = f"ФАКТ #{i+1}" if preset == "facts" else (f"ПРАВИЛО {i+1:02d}" if preset == "horror_rules" else f"ЭТАП #{i+1}")
        sub_title = " ".join(words[:3]).upper()
        subtitle = " ".join(words[3:7]).upper() if len(words) > 3 else "СМОТРИ ДАЛЬШЕ"
        
        scenes.append({
            "id": i + 1,
            "title": sub_title[:24],
            "badge": badge,
            "subtitle": subtitle[:24],
            "prompt": f"Cinematic 8k photorealistic vertical 9:16 portrait of {kw}, dramatic lighting, highly detailed, atmospheric composition",
            "motion": motions[i % len(motions)],
        })
    return scenes


def parse_json(raw: str, preset: str = "facts") -> dict:
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    data = json.loads(raw)
    for k in ("title", "hook", "script", "keywords"):
        if k not in data:
            raise ValueError(f"В ответе модели нет обязательного поля '{k}'")
    if "post_caption" not in data:
        data["post_caption"] = data.get("title", "")
    if "hashtags" not in data:
        data["hashtags"] = ["факты", "рек", "fyp", "тренды", "шортс"]
    if "scenes" not in data or not isinstance(data["scenes"], list) or not data["scenes"]:
        data["scenes"] = _synthesize_scenes(data["script"], data.get("keywords", []), preset, data.get("title", ""))
    return data


class OpenAIScript(ScriptProvider):
    def generate(self, topic, preset, lang):
        key = env("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("Не задан OPENAI_API_KEY (см. .env.example)")
        r = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": env("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": build_user_prompt(topic, preset, lang)},
                ],
                "response_format": {"type": "json_object"},
            },
            timeout=90,
        )
        r.raise_for_status()
        return parse_json(r.json()["choices"][0]["message"]["content"], preset=preset)


class ClaudeScript(ScriptProvider):
    def generate(self, topic, preset, lang):
        key = env("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("Не задан ANTHROPIC_API_KEY (см. .env.example)")
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            json={
                "model": env("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
                "max_tokens": 1500,
                "system": SYSTEM,
                "messages": [{"role": "user", "content": build_user_prompt(topic, preset, lang)}],
            },
            timeout=90,
        )
        r.raise_for_status()
        return parse_json(r.json()["content"][0]["text"], preset=preset)


class GeminiScript(ScriptProvider):
    def generate(self, topic, preset, lang):
        key = env("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("Не задан GEMINI_API_KEY (см. .env.example)")
        model = env("GEMINI_MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{SYSTEM}\n\n{build_user_prompt(topic, preset, lang)}"}]}
            ],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        r = httpx.post(url, json=payload, timeout=90)
        r.raise_for_status()
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return parse_json(raw, preset=preset)


class QwenLocalScript(ScriptProvider):
    """Локальный провайдер на базе Qwen 2.5 / DeepSeek через Ollama, LM Studio или vLLM."""

    def generate(self, topic, preset, lang):
        base_url = env("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        candidates = [env("OLLAMA_SCRIPT_MODEL"), env("OLLAMA_MODEL", "qwen2.5:7b")]
        candidates = [m for m in dict.fromkeys(candidates) if m]
        api_key = env("OLLAMA_API_KEY", "ollama")
        endpoint = base_url.rstrip("/") + "/chat/completions"

        last_error = None
        for model in candidates:
            try:
                r = httpx.post(
                    endpoint,
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": SYSTEM},
                            {"role": "user", "content": build_user_prompt(topic, preset, lang)},
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.7,
                    },
                    timeout=120,
                )
                if r.status_code == 200:
                    content = r.json()["choices"][0]["message"]["content"]
                    return parse_json(content, preset=preset)
                last_error = f"HTTP {r.status_code}: {r.text}"
            except httpx.ConnectError:
                raise RuntimeError(
                    f"Локальный сервер Ollama / Qwen недоступен по адресу {base_url}!\n"
                    f"1. Убедитесь, что Ollama запущена на порту 11434\n"
                    f"2. Модели: qwen2.5-director:latest или qwen2.5:7b"
                )
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"Ошибка локальной генерации через Qwen: {last_error}")


class MockScript(ScriptProvider):
    TEXT = {
        "ru": "Знаете ли вы, что *мёд никогда не портится*? Археологи находили горшки с мёдом в египетских гробницах, "
              "и ему было !более трёх тысяч лет!. Он всё ещё оставался *съедобным*. Секрет в том, что в мёде почти нет воды, "
              "а ещё он содержит *природный антисептик*. Бактерии просто !не могут! в нём жить. "
              "Так что если найдёте в шкафу старую банку мёда, смело добавляйте его в чай. *Подпишись*, чтобы узнать больше!",
        "en": "Did you know *honey never spoils*? Archaeologists found pots of honey in Egyptian tombs, !over three thousand! "
              "years old, and it was still *edible*. The secret is that honey has almost no water and contains a natural "
              "*antiseptic*, so bacteria simply !cannot live! in it. So if you find an old jar in your cupboard, add it to your "
              "tea without worry. *Follow for more*!",
    }

    HORROR_TEXT = {
        "ru": "Если ты находишься на даче, и ровно в полночь внезапно *пропадет мобильная связь* — !не пытайся перезагрузить! телефон. Времени у тебя *меньше пяти минут*. "
              "Правило первое: немедленно *потуши весь свет* в доме и !отойди от окон!. Если увидишь фонарь со стороны темного леса — это !не соседи!. "
              "Правило второе: поднимись на второй этаж и *заблокируй лестницу*. Запомни: первый этаж ты уже !не удержишь!. "
              "Правило третье: если из коридора раздастся голос близкого человека, который зовет тебя по имени — !не отвечай!. Настоящие люди сейчас не могут сюда войти. "
              "Что делать, если они начали подниматься по лестнице? Вторая часть: Что в доме напротив уже в Telegram-канале в шапке профиля. *Подпишись*, чтобы не пропустить.",
        "en": "If you are at a country house and mobile signal suddenly disappears at midnight, !do not try to restart! your phone. You have *less than five minutes*. "
              "Rule number one: extinguish *all lights* and !step away! from windows immediately. If you see a lantern from the woods, it is !not your neighbors!. "
              "Rule number two: go up to the second floor and *barricade the stairs*. You !cannot hold! the ground floor. "
              "Rule number three: if you hear a family member calling your name from the hallway, !do not respond!. Real people cannot enter right now. "
              "Part two: What is in the opposite house is already posted in our Telegram channel linked in the profile bio. *Follow to survive*."
    }

    def generate(self, topic, preset, lang):
        if preset == "horror_rules":
            text = self.HORROR_TEXT.get(lang, self.HORROR_TEXT["ru"])
            return {
                "title": f"[ХОРРОР] {topic}",
                "hook": "Если ночью пропадет связь — у тебя меньше пяти минут.",
                "script": text,
                "keywords": ["dark creepy house night", "foggy forest mystery", "flashlight shadows", "abandoned stairs"],
                "post_caption": f"⚠️ Свод правил выживания: {topic}. Сохрани это видео и перешли близким!",
                "hashtags": ["хоррор", "правилавыживания", "аналоговыйхоррор", "страшныеистории", "мистика", "рек", "fyp"],
                "scenes": [
                    {
                        "id": 1,
                        "title": "ТИШИНА В ДОМЕ",
                        "badge": "ПРАВИЛО 01",
                        "subtitle": "НИ СВЕТА, НИ ЗВУКА",
                        "prompt": "Dark eerie wooden house in deep forest at midnight, dense creeping fog, glowing moon, cinematic 8k photorealistic, vertical 9:16 portrait",
                        "motion": "zoom_in",
                    },
                    {
                        "id": 2,
                        "title": "ЛЕСТНИЦА ВВЕРХ",
                        "badge": "ПРАВИЛО 02",
                        "subtitle": "ПЕРВЫЙ ЭТАЖ НЕ УДЕРЖАТЬ",
                        "prompt": "Barricaded wooden stairs inside an old dark house, heavy shadows, dim flashlight beam illuminating dust motes, vertical 9:16",
                        "motion": "pan_up",
                    },
                    {
                        "id": 3,
                        "title": "НЕ ОТВЕЧАЙ",
                        "badge": "ПРАВИЛО 03",
                        "subtitle": "ГОЛОСА В КОРИДОРЕ",
                        "prompt": "Closed wooden room door in a pitch black hallway, ominous crimson light leaking under the crack, analog horror aesthetic, vertical 9:16",
                        "motion": "zoom_in",
                    },
                    {
                        "id": 4,
                        "title": "ДОМ НАПРОТИВ",
                        "badge": "ТАЙНА",
                        "subtitle": "СЕКТОР АНОМАЛИИ",
                        "prompt": "Mysterious illuminated window in abandoned cottage across overgrown road through mist, chilling atmosphere, 8k vertical 9:16",
                        "motion": "pan_down",
                    },
                    {
                        "id": 5,
                        "title": "ЧТО ВНУТРИ?",
                        "badge": "ФИНАЛ",
                        "subtitle": "ССЫЛКА В ШАПКЕ",
                        "prompt": "Emergency broadcast system warning screen, static noise, crimson red alert lights, analog horror, vertical 9:16",
                        "motion": "zoom_out",
                    },
                ],
            }

        text = self.TEXT.get(lang, self.TEXT["en"])
        return {
            "title": f"[MOCK] {topic}",
            "hook": text.split("?")[0] + "?",
            "script": text,
            "keywords": ["honey", "nature", "ancient egypt", "science"],
            "post_caption": f"Шокирующая правда: {topic}! Сохрани, чтобы не потерять 📌",
            "hashtags": ["факты", "истории", "тикток", "рилс", "рек", "fyp"],
            "scenes": [
                {
                    "id": 1,
                    "title": "ГРОБНИЦЫ ФАРАОНОВ",
                    "badge": "ФАКТ #1",
                    "subtitle": "БОЛЕЕ 3000 ЛЕТ",
                    "prompt": "Ancient Egyptian tomb interior with golden treasures and clay jars, warm torch flame illumination, cinematic photorealism, vertical 9:16",
                    "motion": "zoom_in",
                },
                {
                    "id": 2,
                    "title": "ЗАПЕЧАТАННЫЙ МЁД",
                    "badge": "ОТКРЫТИЕ",
                    "subtitle": "ИДЕАЛЬНАЯ СВЕЖЕСТЬ",
                    "prompt": "Ancient ceramic amphora with dripping golden liquid honey, glowing warm light, hyper-detailed macro shot, vertical 9:16",
                    "motion": "pan_down",
                },
                {
                    "id": 3,
                    "title": "ПРИРОДНЫЙ ЩИТ",
                    "badge": "НАУКА",
                    "subtitle": "БЕЗ БАКТЕРИЙ",
                    "prompt": "Microscopic scientific visual of golden honey molecules with natural antibiotic properties destroying bacteria, vertical 9:16",
                    "motion": "zoom_out",
                },
                {
                    "id": 4,
                    "title": "ЧАЙ С МЁДОМ",
                    "badge": "СОВЕТ ДНЯ",
                    "subtitle": "ПОЛЬЗА И ВКУС",
                    "prompt": "Cozy rustic kitchen counter, vintage jar of honey with wooden dipper, steaming herbal tea, soft golden morning sunlight, vertical 9:16",
                    "motion": "pan_up",
                },
                {
                    "id": 5,
                    "title": "ПОДПИШИСЬ",
                    "badge": "СЕКРЕТЫ",
                    "subtitle": "БОЛЬШЕ ФАКТОВ",
                    "prompt": "Golden hexagon honeycomb pattern glowing with warm futuristic golden light particles floating in dark void, vertical 9:16",
                    "motion": "zoom_in",
                },
            ],
        }
