"""
F5-TTS Russian GPU Worker (runs inside backend/.venv_f5tts with PyTorch CUDA).
Uses Misha24-10/F5-TTS_RUSSIAN (5,000+ hours Russian zero-shot voice cloning)
+ RUAccent for automatic Russian lexical stress placement.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure FFmpeg is visible to pydub / f5-tts
_FFMPEG_DIR = r"C:\OSPanel\addons\FFMpeg\bin"
if os.path.isdir(_FFMPEG_DIR) and _FFMPEG_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

import numpy as np
import soundfile as sf
import torch


def apply_ru_accent(text: str, accentizer) -> str:
    """Applies automatic '+' stress marks for Russian F5-TTS v2 model."""
    if accentizer is None:
        return text
    try:
        return accentizer.process_all(text)
    except Exception:
        return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, help="Path to JSON job file")
    args = parser.parse_args()

    job_path = Path(args.job)
    job = json.loads(job_path.read_text(encoding="utf-8"))

    sentences = job["sentences"]
    ref_audio = str(job["ref_audio"])
    ref_text_raw = job["ref_text"]
    out_wav = Path(job["out_wav"])
    out_words_json = Path(job["out_words_json"])
    speed = float(job.get("speed", 1.05))
    nfe_step = int(job.get("nfe_step", 32))

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[F5-TTS Worker] Device: {device} ({torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'})")

    # 1. Load RUAccent for crisp natural Russian stress placement
    accentizer = None
    try:
        from ruaccent import RUAccent
        print("[F5-TTS Worker] Загружаем RUAccent (автоударения для русского языка)...")
        accentizer = RUAccent()
        accentizer.load(omograph_model_size="turbo3.1", use_dictionary=True, tiny_mode=False)
    except Exception as e:
        print(f"[F5-TTS Worker] RUAccent пропущен ({e}), синтезируем без доп. разметки ударений.")

    # 2. Download/Locate Misha24-10/F5-TTS_RUSSIAN weights
    from huggingface_hub import hf_hub_download
    print("[F5-TTS Worker] Проверяем/скачиваем веса Misha24-10/F5-TTS_RUSSIAN (v2)...")
    ckpt_path = hf_hub_download(
        repo_id="Misha24-10/F5-TTS_RUSSIAN",
        filename="F5TTS_v1_Base_v2/model_last_inference.safetensors",
    )
    vocab_path = hf_hub_download(
        repo_id="Misha24-10/F5-TTS_RUSSIAN",
        filename="F5TTS_v1_Base/vocab.txt",
    )

    # 3. Initialize F5-TTS pipeline on RTX 4050 GPU
    from f5_tts.api import F5TTS
    print("[F5-TTS Worker] Инициализируем F5-TTS на GPU...")
    f5 = F5TTS(
        model="F5TTS_v1_Base",
        ckpt_file=ckpt_path,
        vocab_file=vocab_path,
        device=device,
    )

    # Accentize reference text
    ref_text = apply_ru_accent(ref_text_raw, accentizer)
    print(f"[F5-TTS Worker] Референс-текст: {ref_text[:80]}...")

    all_chunks = []
    words_data = []
    current_time = 0.0
    sample_rate = 24000
    pause_sec = 0.16

    for idx, sent in enumerate(sentences):
        s_clean = sent.strip()
        if not s_clean:
            continue

        gen_text = apply_ru_accent(s_clean, accentizer)
        print(f"[F5-TTS Worker] Синтез [{idx+1}/{len(sentences)}]: {s_clean}")

        wav, sr, _ = f5.infer(
            ref_file=ref_audio,
            ref_text=ref_text,
            gen_text=gen_text,
            speed=speed,
            nfe_step=nfe_step,
            remove_silence=True,
        )

        # Ensure 1D float32 numpy array
        if isinstance(wav, torch.Tensor):
            wav = wav.detach().cpu().numpy()
        wav = np.asarray(wav, dtype=np.float32).squeeze()
        sample_rate = int(sr)

        # Trim tiny leading/trailing silence softly
        dur = len(wav) / sample_rate

        # Compute word timestamps proportionally across the synthesized sentence
        clean_words = s_clean.replace(".", "").replace("!", "").replace("?", "").replace(",", "").replace("...", "").split()
        if clean_words:
            # Weight words slightly by character length for tighter karaoke sync!
            char_lens = [max(2, len(w)) for w in clean_words]
            total_chars = sum(char_lens)
            w_cursor = current_time
            for w, clen in zip(clean_words, char_lens):
                w_dur = dur * (clen / total_chars)
                words_data.append({
                    "word": w,
                    "start": round(w_cursor, 3),
                    "end": round(w_cursor + w_dur * 0.92, 3),
                })
                w_cursor += w_dur

        all_chunks.append(wav)
        current_time += dur

        # Add natural short breath pause between sentences
        pause_arr = np.zeros(int(pause_sec * sample_rate), dtype=np.float32)
        all_chunks.append(pause_arr)
        current_time += pause_sec

    full_wav = np.concatenate(all_chunks)
    mx = np.max(np.abs(full_wav))
    if mx > 1e-6:
        full_wav = full_wav / mx * 0.94

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_wav), full_wav, sample_rate)

    out_words_json.parent.mkdir(parents=True, exist_ok=True)
    out_words_json.write_text(
        json.dumps({"duration": round(len(full_wav) / sample_rate, 3), "words": words_data}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[F5-TTS Worker] ГОТОВО! Длительность: {len(full_wav)/sample_rate:.2f}s -> {out_wav}")


if __name__ == "__main__":
    main()
