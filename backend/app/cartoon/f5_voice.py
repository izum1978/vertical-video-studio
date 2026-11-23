"""
F5-TTS Russian Voice Engine Wrapper (ElevenLabs-tier local GPU voice cloning).
Invokes backend/.venv_f5tts GPU worker and applies studio broadcast mastering.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
F5_VENV_PYTHON = WORKSPACE_ROOT / "backend" / ".venv_f5tts" / "Scripts" / "python.exe"
F5_WORKER_SCRIPT = Path(__file__).resolve().parent / "f5_worker.py"
DEFAULT_REF_WAV = WORKSPACE_ROOT / "backend" / "assets" / "voices" / "ref_narrator.wav"
DEFAULT_REF_TXT = WORKSPACE_ROOT / "backend" / "assets" / "voices" / "ref_narrator.txt"

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"


def is_f5_available() -> bool:
    return F5_VENV_PYTHON.exists() and DEFAULT_REF_WAV.exists()


def synthesize_f5_script(
    sentences: List[str],
    out_wav: Path,
    ref_audio: Optional[Path] = None,
    ref_text: Optional[str] = None,
    speed: float = 1.05,
    nfe_step: int = 32,
) -> Tuple[Path, List[Dict], float]:
    """Synthesizes Russian sentences via F5-TTS Russian GPU voice cloning."""
    if not F5_VENV_PYTHON.exists():
        raise RuntimeError(f"F5-TTS GPU venv not found at {F5_VENV_PYTHON}")

    out_wav = Path(out_wav).resolve()
    out_wav.parent.mkdir(parents=True, exist_ok=True)

    ref_wav_path = Path(ref_audio).resolve() if ref_audio else DEFAULT_REF_WAV.resolve()
    if ref_text is None:
        if DEFAULT_REF_TXT.exists():
            ref_text = DEFAULT_REF_TXT.read_text(encoding="utf-8").strip()
        else:
            ref_text = ""

    raw_wav = out_wav.parent / f"raw_f5_{out_wav.name}"
    words_json = out_wav.parent / f"words_f5_{out_wav.stem}.json"
    job_json = out_wav.parent / f"job_f5_{out_wav.stem}.json"

    job = {
        "sentences": sentences,
        "ref_audio": str(ref_wav_path),
        "ref_text": ref_text,
        "out_wav": str(raw_wav),
        "out_words_json": str(words_json),
        "speed": speed,
        "nfe_step": nfe_step,
    }
    job_json.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")

    cmd = [str(F5_VENV_PYTHON), str(F5_WORKER_SCRIPT), "--job", str(job_json)]
    subprocess.run(cmd, check=True)

    # Studio podcast / YouTube Shorts mastering (crisp presence, gentle compression, -14 LUFS)
    master_filters = (
        "highpass=f=75,"
        "equalizer=f=3800:width_type=o:w=1.2:g=1.8,"
        "acompressor=threshold=-16dB:ratio=2.8:attack=10:release=80,"
        "loudnorm=I=-14:LRA=7:TP=-1.5"
    )
    subprocess.run(
        [FFMPEG_BIN, "-y", "-i", str(raw_wav), "-af", master_filters, "-ar", "44100", "-ac", "1", str(out_wav)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if raw_wav.exists():
        raw_wav.unlink()

    meta = json.loads(words_json.read_text(encoding="utf-8"))
    return out_wav, meta["words"], float(meta["duration"])
