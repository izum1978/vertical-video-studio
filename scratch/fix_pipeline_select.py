from pathlib import Path

path = Path("backend/app/pipeline.py")
text = path.read_text(encoding="utf-8")

old_s = """        count = max(len(beats), max(3, min(12, round(dur / 4))))
        if vis_req in ("ai_scenes", "ai_video", "auto"):
            vis_prov = P.get(P.VISUALS, "ai_scenes")"""

new_s = """        count = max(len(beats), max(3, min(12, round(dur / 4))))
        if vis_req == "ai_video":
            vis_prov = P.get(P.VISUALS, "ai_video")
        elif vis_req in ("ai_scenes", "auto"):
            vis_prov = P.get(P.VISUALS, "ai_scenes")"""

text = text.replace(old_s, new_s)
path.write_text(text, encoding="utf-8")
print("Successfully fixed pipeline.py visual provider selection")

