import asyncio
import subprocess

try:
    import httpx
except ImportError:
    import requests as httpx

from ..config import env
from .base import TTSProvider

VOICES = {
    "ru": [
        ("ru-RU-SvetlanaNeural", "Светлана (Студия, жен.)"),
        ("ru-RU-DmitryNeural", "Дмитрий (Студия, муж.)"),
        ("onyx", "OpenAI: Onyx (Глубокий кино-бас / Хоррор)"),
        ("echo", "OpenAI: Echo (Напряженный саспенс)"),
        ("fable", "OpenAI: Fable (Выразительный нарратив)"),
        ("nova", "OpenAI: Nova (Энергичная драма)"),
        ("pNInz6obpgDQGcFmaJgB", "ElevenLabs: Adam (Хоррор / Триллер)"),
        ("21m00Tcm4TlvDq8ikWAM", "ElevenLabs: Rachel (Шепот / Драма)"),
        ("JBFqnCBsd6RMkjVDRZzb", "ElevenLabs: George (Глубокий нарратив)"),
    ],
    "en": [
        ("onyx", "OpenAI: Onyx (Deep Cinema Narrator)"),
        ("echo", "OpenAI: Echo (Suspense Male)"),
        ("fable", "OpenAI: Fable (Storyteller)"),
        ("nova", "OpenAI: Nova (Energetic Female)"),
        ("en-US-GuyNeural", "Guy (Studio, male)"),
        ("en-US-JennyNeural", "Jenny (Studio, female)"),
        ("en-US-AriaNeural", "Aria (Studio, female)"),
        ("pNInz6obpgDQGcFmaJgB", "ElevenLabs: Adam (Deep Thriller)"),
        ("21m00Tcm4TlvDq8ikWAM", "ElevenLabs: Rachel (Whisper)"),
    ],
}


class EdgeTTS(TTSProvider):
    def synth(self, text, voice, lang, out):
        import json
        import re
        import edge_tts

        # 1. Тщательно очищаем текст от эмодзи, SFX маркеров, нечитаемых символов
        clean_text = re.sub(r"\[sfx:\s*[^\]]+\]", "", text, flags=re.I)
        clean_text = re.sub(r"[*_#`~>!]", "", clean_text)
        clean_text = re.sub(r"[\U00010000-\U0010FFFF\u2600-\u27BF\u2300-\u23FF\u2B50-\u2B55\uFE00-\uFE0F]", "", clean_text)
        clean_text = clean_text.replace("—", " - ").replace("–", " - ")
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # Если передан ID голоса от ElevenLabs, подбираем ближайший качественный EdgeTTS
        primary_voice = voice
        if not primary_voice or "Neural" not in primary_voice:
            primary_voice = "ru-RU-SvetlanaNeural" if lang == "ru" else "en-US-GuyNeural"

        fallback_voice = "ru-RU-SvetlanaNeural" if lang == "ru" else "en-US-AriaNeural"
        voices_to_try = []
        for v in [primary_voice, fallback_voice, "ru-RU-SvetlanaNeural" if lang == "ru" else "en-US-GuyNeural"]:
            if v and v not in voices_to_try:
                voices_to_try.append(v)

        async def _speak():
            from ..render import probe_duration
            from ..timing import marks_to_words, proportional_timing, restore_punctuation
            last_err = None
            for attempt, cur_voice in enumerate(voices_to_try, start=1):
                try:
                    try:
                        comm = edge_tts.Communicate(clean_text, cur_voice, boundary="WordBoundary")
                    except TypeError:            # старая версия edge-tts без параметра boundary
                        comm = edge_tts.Communicate(clean_text, cur_voice)
                    marks = []
                    with open(out, "wb") as f:
                        async for ch in comm.stream():
                            if ch["type"] == "audio":
                                f.write(ch["data"])
                            elif ch["type"] in ("WordBoundary", "SentenceBoundary"):
                                start = ch["offset"] / 1e7
                                marks.append({
                                    "word": ch["text"],
                                    "start": round(start, 3),
                                    "end": round(start + ch["duration"] / 1e7, 3),
                                    "kind": ch["type"],
                                })
                    if out.exists() and out.stat().st_size > 1000:
                        try:
                            dur = probe_duration(out)
                            words = marks_to_words(marks) if marks else proportional_timing(clean_text, dur)
                            words = restore_punctuation(words, clean_text)
                            out.with_suffix(".words.json").write_text(
                                json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8"
                            )
                        except Exception:
                            pass
                        return
                except Exception as e:
                    last_err = e
                    await asyncio.sleep(0.6 * attempt)

            # Если все голоса Microsoft временно недоступны — генерируем аварийную речь
            if last_err and not (out.exists() and out.stat().st_size > 1000):
                dur = max(len(clean_text.split()) / 2.6, 5)
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=180:duration={dur:.2f}",
                     "-af", "volume=0.04", str(out)],
                    check=True, capture_output=True,
                )

        asyncio.run(_speak())
        return out


class ElevenLabsTTS(TTSProvider):
    def synth(self, text, voice, lang, out):
        import json
        import re

        key = env("ELEVENLABS_API_KEY")
        if not key:
            # Если бесплатный ключ ElevenLabs ещё не введен в .env, плавно используем
            # наш бесплатный EdgeTTS со студийным мастерингом
            print("[ElevenLabs] ELEVENLABS_API_KEY не задан. Используем студийный голос с аналоговым мастерингом.")
            return EdgeTTS().synth(text, voice, lang, out)

        # Чистим текст перед отправкой
        clean_text = re.sub(r"\[sfx:\s*[^\]]+\]", "", text, flags=re.I)
        clean_text = re.sub(r"[*_#`~>!]", "", clean_text)
        clean_text = re.sub(r"[\U00010000-\U0010FFFF\u2600-\u27BF\u2300-\u23FF\u2B50-\u2B55\uFE00-\uFE0F]", "", clean_text)
        clean_text = clean_text.replace("—", " - ").replace("–", " - ")
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # Выбираем ID голоса: если передан Neural голос от Edge, заменяем на кинематографичный Adam
        voice_id = voice
        if not voice_id or "Neural" in voice_id:
            voice_id = env("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")

        payload = {
            "text": clean_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.42, "similarity_boost": 0.85, "style": 0.40, "use_speaker_boost": True},
        }
        try:
            from ..render import probe_duration
            from ..timing import alignment_to_words, proportional_timing
            words = []
            try:
                # Реальное выравнивание по символам: слова и паузы совпадают с голосом
                import base64
                r = httpx.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
                               headers={"xi-api-key": key}, json=payload, timeout=120)
                r.raise_for_status()
                data = r.json()
                out.write_bytes(base64.b64decode(data["audio_base64"]))
                words = alignment_to_words(data.get("alignment") or data.get("normalized_alignment"))
            except Exception as e:
                print(f"[ElevenLabs] with-timestamps недоступен ({e}), обычный синтез.")
                r = httpx.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                               headers={"xi-api-key": key}, json=payload, timeout=120)
                r.raise_for_status()
                out.write_bytes(r.content)
            try:
                if not words:
                    words = proportional_timing(clean_text, probe_duration(out))
                out.with_suffix(".words.json").write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass
            return out
        except Exception as e:
            print(f"[ElevenLabs Warning: {e}]. Автоматический переход на студийный голос.")
            return EdgeTTS().synth(text, voice, lang, out)


class OpenAITTS(TTSProvider):
    """Кинематографичная озвучка OpenAI (прямой аналог ElevenLabs по качеству речи).

    Модели: tts-1, tts-1-hd. Голоса: onyx (глубокий драматичный бас), echo, fable, nova, shimmer, alloy.
    """

    def synth(self, text, voice, lang, out):
        import json
        import re

        key = env("OPENAI_API_KEY")
        if not key:
            print("[OpenAITTS] OPENAI_API_KEY не задан в .env. Используем студийный голос с аналоговым мастерингом.")
            return EdgeTTS().synth(text, voice, lang, out)

        clean_text = re.sub(r"\[sfx:\s*[^\]]+\]", "", text, flags=re.I)
        clean_text = re.sub(r"[*_#`~>!]", "", clean_text)
        clean_text = clean_text.replace("—", " - ").replace("–", " - ")
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # Выбираем голос OpenAI
        valid_voices = {"onyx", "echo", "fable", "nova", "shimmer", "alloy"}
        voice_id = voice.lower() if voice.lower() in valid_voices else "onyx"

        try:
            r = httpx.post(
                "https://api.openai.com/v1/audio/speech",
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": "tts-1-hd",
                    "input": clean_text,
                    "voice": voice_id,
                    "response_format": "mp3",
                    "speed": 0.98 if "horror" in clean_text.lower() else 1.0,
                },
                timeout=90,
            )
            r.raise_for_status()
            out.write_bytes(r.content)

            # OpenAI не отдаёт таймкоды: оценка с паузами на знаках препинания (точнее равномерных весов)
            from ..render import probe_duration
            from ..timing import proportional_timing
            try:
                words = proportional_timing(clean_text, probe_duration(out))
                if words:
                    out.with_suffix(".words.json").write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass

            return out
        except Exception as e:
            print(f"[OpenAI TTS Error: {e}]. Плавный переход на студийный голос.")
            return EdgeTTS().synth(text, voice, lang, out)


class MockTTS(TTSProvider):
    """Генерирует живой бесплатный голос через EdgeTTS с ретраями. Если интернета нет — резервный тон."""

    def synth(self, text, voice, lang, out):
        try:
            return EdgeTTS().synth(text, voice, lang, out)
        except Exception:
            dur = max(len(text.split()) / 2.6, 5)
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=180:duration={dur:.2f}",
                 "-af", "volume=0.04", str(out)],
                check=True, capture_output=True,
            )
            return out
