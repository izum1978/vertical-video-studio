from pathlib import Path

files = [
    Path("backend/app/providers/script.py"),
    Path("backend/app/providers/tts.py"),
    Path("backend/app/providers/visuals.py"),
]

for f in files:
    if f.exists():
        txt = f.read_text(encoding="utf-8")
        if "try:\n    import httpx\nexcept ImportError:\n    import requests as httpx" not in txt:
            txt = txt.replace("import httpx", "try:\n    import httpx\nexcept ImportError:\n    import requests as httpx")
            f.write_text(txt, encoding="utf-8")
            print(f"Patched {f.name}")

