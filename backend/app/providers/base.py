"""Интерфейсы этапов пайплайна. Любой провайдер подменяется или мокается."""
from abc import ABC, abstractmethod
from pathlib import Path


class ScriptProvider(ABC):
    @abstractmethod
    def generate(self, topic: str, preset: str, lang: str) -> dict:
        """-> {title, hook, script, keywords: [str]}"""


class TTSProvider(ABC):
    @abstractmethod
    def synth(self, text: str, voice: str, lang: str, out: Path) -> Path:
        """Синтезирует речь в файл out (mp3/wav) и возвращает путь."""


class VisualProvider(ABC):
    @abstractmethod
    def fetch(self, keywords: list[str], count: int, workdir: Path, script_data: dict | None = None) -> list[Path]:
        """Возвращает список видеофайлов (любого размера/пропорций)."""
