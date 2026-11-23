"""Модуль нейросетевой транскрибации речи с пословными таймкодами (faster-whisper).

Локальная высокоскоростная транскрибация любого аудиофайла (озвучка, подкаст, диалог)
на видеокарте NVIDIA RTX или процессоре без обращения к внешним серверам.
Извлекает пословные метки времени (word-level timestamps) для вирусных караоке-субтитров.
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
MODEL_CACHE_DIR = WORKSPACE_ROOT / ".cache" / "whisper"
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_CACHED_MODEL = None


def get_whisper_model(model_size: str = "base"):
    """Инициализирует и кэширует модель Whisper на GPU или CPU с автоматическим фоллбеком."""
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    from faster_whisper import WhisperModel
    import ctranslate2

    # Пробуем инициализировать CUDA, при нехватке библиотек откатываемся на быстрый CPU int8
    model = None
    if ctranslate2.get_cuda_device_count() > 0:
        try:
            print(f"[Whisper] Пробуем запуск '{model_size}' на CUDA GPU...")
            model = WhisperModel(
                model_size,
                device="cuda",
                compute_type="float16",
                download_root=str(MODEL_CACHE_DIR),
            )
            # Пробный вызов
            _CACHED_MODEL = model
            return _CACHED_MODEL
        except Exception as e:
            print(f"[Whisper] CUDA драйвер требует cuBLAS ({e}), переключаемся на оптимизированный CPU (int8)...")

    print(f"[Whisper] Загрузка '{model_size}' на многопоточный CPU (int8)...")
    _CACHED_MODEL = WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8",
        cpu_threads=max(1, (os.cpu_count() or 4) - 1),
        download_root=str(MODEL_CACHE_DIR),
    )
    return _CACHED_MODEL



def transcribe_audio_words(
    audio_path: Path,
    model_size: str = "base",
    language: Optional[str] = "ru",
) -> Tuple[str, List[Dict]]:
    """Транскрибирует аудиофайл и возвращает (полный_текст, список_слов_с_таймкодами).
    
    Каждый элемент слова содержит:
    {
        "word": str,
        "start": float,
        "end": float,
        "confidence": float
    }
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Аудиофайл не найден: {audio_path}")

    full_text_parts = []
    word_list = []

    try:
        model = get_whisper_model(model_size=model_size)
        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=400),
        )
        for seg in segments:
            full_text_parts.append(seg.text.strip())
            if seg.words:
                for w in seg.words:
                    clean_word = w.word.strip()
                    if clean_word:
                        word_list.append({
                            "word": clean_word,
                            "start": round(w.start, 3),
                            "end": round(w.end, 3),
                            "confidence": round(w.probability, 3),
                        })
    except Exception as e:
        print(f"[Whisper] Переключение на CPU из-за ошибки рантайма ({e})...")
        from faster_whisper import WhisperModel
        cpu_model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            download_root=str(MODEL_CACHE_DIR),
        )
        segments, _ = cpu_model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=True,
            vad_filter=True,
        )
        full_text_parts.clear()
        word_list.clear()
        for seg in segments:
            full_text_parts.append(seg.text.strip())
            if seg.words:
                for w in seg.words:
                    clean_word = w.word.strip()
                    if clean_word:
                        word_list.append({
                            "word": clean_word,
                            "start": round(w.start, 3),
                            "end": round(w.end, 3),
                            "confidence": round(w.probability, 3),
                        })



    full_text = " ".join(full_text_parts)
    return full_text, word_list


if __name__ == "__main__":
    test_audio = WORKSPACE_ROOT / "output" / "test_voice" / "cinematic_voice.mp3"
    if test_audio.exists():
        print(f"Тестирование транскрибации {test_audio.name}...")
        text, words = transcribe_audio_words(test_audio, model_size="tiny")
        print(f"Распознанный текст:\n{text}")
        print(f"\nИзвлечено слов: {len(words)}")
        if words:
            print("Первые 5 слов:", words[:5])
