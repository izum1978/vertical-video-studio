"""Датасет художника сцен: фраза -> описание сцены (JSON).

Сильная модель (Claude, Gemini, GPT или большая локальная) рисует сцены по фразам через тот же
промпт и схему, что и в бою. В датасет попадают только сцены, прошедшие нормализацию,
критик композиции и проверку смысла (предметы из фразы есть в сцене).

  python training/build_scene_dataset.py --sentences training/scene_sentences.txt --provider claude

Дальше обучение тем же скриптом, что и для режиссёра:
  python training/train_director.py --train training/data/scene_train.jsonl --val training/data/scene_val.jsonl \\
      --out training/out_scene --tag qwen2.5-scene-v1
и в .env:  OLLAMA_SCENE_MODEL=qwen2.5-scene-v1
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.motion_gfx import designer as D  # noqa: E402
from app.motion_gfx.scene_dsl import normalize_spec, to_compact  # noqa: E402

MIN_RELEVANCE = 0.6
MIN_OBJECTS, MAX_OBJECTS = 3, 10


def split_of(key: str, val_share: float = 0.1) -> str:
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % 1000
    return "val" if h < val_share * 1000 else "train"


def build_record(preset: str, text: str, llm, provider: str = "claude", title: str = "", max_attempts: int = 2):
    """Возвращает (запись | None, причина отказа | None). llm(provider, system, user, schema) -> (json_text, model)."""
    ctx = {"title": title or text[:40], "preset": preset, "provider": provider, "prev": ""}
    beat = {"id": 1, "text": text, "mode": "motion", "scene_type": "custom"}
    spec, src, notes = D.design_scene(beat, ctx, mode="auto", llm=llm, use_cache=False)
    if src != "llm" or not spec:
        return None, f"сцену не нарисовала LLM ({src}): " + "; ".join(notes[:2])
    n = len(spec["objects"])
    if not MIN_OBJECTS <= n <= MAX_OBJECTS:
        return None, f"число деталей {n} вне диапазона {MIN_OBJECTS}-{MAX_OBJECTS}"
    rel = D.relevance(spec, text)
    if rel < MIN_RELEVANCE:
        return None, f"смысл: в сцене только {rel:.0%} предметов из фразы"
    compact = to_compact(spec)
    assert normalize_spec(compact, preset)[0] is not None   # запись должна читаться обратно
    return {"messages": [{"role": "system", "content": D.system_prompt()},
                         {"role": "user", "content": D.build_user_prompt(text, "", ctx)},
                         {"role": "assistant", "content": json.dumps(compact, ensure_ascii=False)}],
            "meta": {"preset": preset, "text": text, "relevance": round(rel, 2), "objects": n,
                     "split": split_of(text)}}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sentences", default=str(ROOT / "training" / "scene_sentences.txt"))
    ap.add_argument("--out", default=str(ROOT / "training" / "data"))
    ap.add_argument("--provider", default="claude", help="кто рисует: claude, gemini, openai, qwen")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    files = {"train": out / "scene_train.jsonl", "val": out / "scene_val.jsonl", "rejected": out / "scene_rejected.jsonl"}
    done = set()
    for f in files.values():
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                try:
                    done.add(json.loads(line)["meta"]["text"])
                except Exception:  # noqa: BLE001
                    pass
    rows = [l.split("|", 1) for l in Path(a.sentences).read_text(encoding="utf-8").splitlines() if "|" in l and not l.startswith("#")]
    ok = bad = 0
    for preset, text in rows[: a.limit or None]:
        preset, text = preset.strip(), text.strip()
        if text in done:
            continue
        try:
            rec, why = build_record(preset, text, D.call_scene_llm, a.provider)
        except Exception as e:  # noqa: BLE001
            rec, why = None, f"{type(e).__name__}: {e}"
        target = files[rec["meta"]["split"]] if rec else files["rejected"]
        row = rec or {"meta": {"preset": preset, "text": text, "reason": why}}
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        ok, bad = ok + bool(rec), bad + (not rec)
        print(f"[{ok} ok / {bad} отбраковано] {text[:60]}")


if __name__ == "__main__":
    main()
