import sys
sys.stdout.reconfigure(encoding="utf-8")
import asyncio
import json
import re
import edge_tts
from pathlib import Path

data = json.loads(Path("scratch/last_qwen.json").read_text(encoding="utf-8"))
script = data["script"]
# Sanitize script
clean = re.sub(r"\[sfx:\s*[^\]]+\]", "", script, flags=re.I)
clean = re.sub(r"[*_#`~>!]", "", clean)
clean = re.sub(r"[\U00010000-\U0010FFFF\u2600-\u27BF\u2300-\u23FF\u2B50-\u2B55\uFE00-\uFE0F]", "", clean)
clean = clean.replace("—", " - ").replace("–", " - ")
clean = re.sub(r"\s+", " ", clean).strip()

async def test():
    out = Path("scratch/test_svetlana_full.mp3")
    print("Testing Svetlana on full Qwen script...")
    comm = edge_tts.Communicate(clean, "ru-RU-SvetlanaNeural")
    await comm.save(str(out))
    print("SVETLANA FULL SCRIPT SUCCESS! Size:", out.stat().st_size)

if __name__ == "__main__":
    asyncio.run(test())
