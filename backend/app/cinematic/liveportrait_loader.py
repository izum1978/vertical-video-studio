"""Загрузчик весов ONNX моделей для LivePortrait из Hugging Face (warmshao/FasterLivePortrait).
Загружает только необходимые легковесные модели для людей (~650 МБ), экономя трафик и место.
"""
import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
CHECKPOINTS_DIR = WORKSPACE_ROOT / "backend" / "app" / "cinematic" / "liveportrait" / "checkpoints" / "liveportrait_onnx"
CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

REPO_ID = "warmshao/FasterLivePortrait"

REQUIRED_FILES = [
    "appearance_feature_extractor.onnx",
    "face_2dpose_106_static.onnx",
    "landmark.onnx",
    "motion_extractor.onnx",
    "retinaface_det_static.onnx",
    "stitching.onnx",
    "stitching_eye.onnx",
    "stitching_lip.onnx",
    "warping_spade.onnx",
]


def ensure_liveportrait_checkpoints() -> bool:
    """Проверяет наличие всех чекпоинтов ONNX и докачивает недостающие."""
    missing = [f for f in REQUIRED_FILES if not (CHECKPOINTS_DIR / f).exists()]
    if not missing:
        print("[LivePortrait] Все необходимые ONNX модели уже загружены.")
        return True

    print(f"[LivePortrait] Загрузка {len(missing)} моделей из Hugging Face ({REPO_ID})...")
    for fname in missing:
        remote_path = f"liveportrait_onnx/{fname}"
        local_dest = CHECKPOINTS_DIR / fname
        print(f"  -> Скачивание {fname}...")
        try:
            downloaded = hf_hub_download(
                repo_id=REPO_ID,
                filename=remote_path,
                local_dir=str(CHECKPOINTS_DIR.parent),
                local_dir_use_symlinks=False,
            )
            print(f"     Успешно: {fname} ({os.path.getsize(downloaded) // (1024*1024)} MB)")
        except Exception as e:
            print(f"     [Ошибка] Не удалось скачать {fname}: {e}")
            return False

    return True


if __name__ == "__main__":
    ensure_liveportrait_checkpoints()
