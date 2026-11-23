import os
import platform
import shutil
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

OUTPUT = ROOT / "output"
WORK = ROOT / "work"
BACKGROUNDS = ROOT / "backend" / "assets" / "backgrounds"
MUSIC = ROOT / "backend" / "assets" / "music"
SFX = ROOT / "backend" / "assets" / "sfx"
for _p in (OUTPUT, WORK, BACKGROUNDS, MUSIC, SFX):
    _p.mkdir(parents=True, exist_ok=True)


COMMON_FFMPEG_PATHS = [
    r"C:\OSPanel\addons\FFMpeg\bin",
    r"C:\ffmpeg\bin",
    r"C:\Program Files\ffmpeg\bin",
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
]
for _p in COMMON_FFMPEG_PATHS:
    if os.path.isdir(_p) and (Path(_p) / "ffmpeg.exe").exists():
        if _p not in os.environ["PATH"]:
            os.environ["PATH"] = _p + os.pathsep + os.environ["PATH"]
        break


def env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


INSTALL_HINTS = {
    "Windows": "winget install Gyan.FFmpeg   (или choco install ffmpeg)",
    "Darwin": "brew install ffmpeg",
    "Linux": "sudo apt install ffmpeg   (Fedora: sudo dnf install ffmpeg)",
}


def check_ffmpeg() -> None:
    missing = [b for b in ("ffmpeg", "ffprobe") if not shutil.which(b)]
    if missing:
        hint = INSTALL_HINTS.get(platform.system(), "https://ffmpeg.org/download.html")
        raise SystemExit(
            f"\n[ОШИБКА] Не найдено в PATH: {', '.join(missing)}.\n"
            f"Установите ffmpeg: {hint}\nПосле установки перезапустите терминал и бэкенд.\n"
        )
