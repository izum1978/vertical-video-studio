"""Реестр провайдеров для Vertical Video Studio."""
from .script import ClaudeScript, GeminiScript, MockScript, OpenAIScript, QwenLocalScript
from .tts import EdgeTTS, ElevenLabsTTS, MockTTS, OpenAITTS
from .motion_gfx import MotionGraphicsVisual
from .visuals import AISceneVisual, AIVideoVisual, AIVideoStub, MockVisual

SCRIPTS = {
    "qwen": QwenLocalScript,
    "qwen_local": QwenLocalScript,
    "gemini": GeminiScript,
    "openai": OpenAIScript,
    "claude": ClaudeScript,
    "mock": MockScript,
}

TTS = {
    "edge": EdgeTTS,
    "openai": OpenAITTS,
    "elevenlabs": ElevenLabsTTS,
    "mock": MockTTS,
}

VISUALS = {
    # Стиль референсов: тёмная векторная анимация с HUD, карточками и субтитрами по словам. Без GPU и сети.
    "motion_gfx": MotionGraphicsVisual,
    # Кинематографичная видеодиффузия на GPU
    "ai_video": AIVideoVisual,
    # Быстрый превью-режим: качественный AI кадр + Ken Burns
    "ai_scenes": AISceneVisual,
    # Алиасы для совместимости
    "vector_2d": MotionGraphicsVisual,
    "cartoon": MotionGraphicsVisual,
    "reference": MotionGraphicsVisual,
    "motion": MotionGraphicsVisual,
    "pexels": AISceneVisual,
    "pixabay": AISceneVisual,
    "mock": MockVisual,
    # Внешние топ-видеосети
    "kling": lambda: AIVideoStub("Kling AI"),
    "runway": lambda: AIVideoStub("Runway Gen-3"),
    "luma": lambda: AIVideoStub("Luma Dream Machine"),
    "haiper": lambda: AIVideoStub("Haiper Video"),
}


def get(registry: dict, name: str):
    if name not in registry:
        # По умолчанию отдаем флагманский ai_video
        if registry is VISUALS:
            return AIVideoVisual()
        raise ValueError(f"Неизвестный провайдер: {name}")
    val = registry[name]
    return val() if callable(val) else val
