import os
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path('.').resolve()
DESKTOP_PATH = Path(r"C:\Users\Lenovo\OneDrive\Desktop")

zip_dest = DESKTOP_PATH / "vertical_video_studio_ai_pack.zip"
workspace_copy = PROJECT_ROOT / "vertical_video_studio_ai_pack.zip"

print(f"Creating AI Studio zip archive at: {zip_dest}")

EXCLUDE_DIRS = {
    "node_modules",
    ".venv",
    ".venv_f5tts",
    "backend/.venv",
    "backend/.venv_f5tts",
    "output",
    "work",
    ".git",
    ".git_repo",
    ".my_git",
    ".cache",
    "__pycache__",
    ".idea",
    ".vscode",
    "dist",
}

EXCLUDE_EXTS = {
    ".mp4",
    ".zip",
    ".pyc",
    ".pyo",
    ".gguf",
}

EXCLUDE_FILES = {
    ".env",
    ".env.local",
}

def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    # check dir exclusions
    for ex in EXCLUDE_DIRS:
        ex_parts = Path(ex).parts
        for i in range(len(parts) - len(ex_parts) + 1):
            if parts[i:i+len(ex_parts)] == ex_parts:
                return True
    
    # check extension
    if rel_path.suffix.lower() in EXCLUDE_EXTS:
        return True
        
    # check file names
    if rel_path.name in EXCLUDE_FILES:
        return True
        
    return False

# Write zip directly
count = 0
total_size = 0

with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Prune dirs in-place for speed
        dirs[:] = [d for d in dirs if not should_exclude(Path(root, d).relative_to(PROJECT_ROOT))]
        
        for f in files:
            file_path = Path(root, f)
            rel_path = file_path.relative_to(PROJECT_ROOT)
            
            if should_exclude(rel_path):
                continue
                
            try:
                zf.write(file_path, arcname=str(rel_path))
                count += 1
                total_size += file_path.stat().st_size
            except Exception as e:
                print(f"Warning skipping {rel_path}: {e}")

zip_size_mb = zip_dest.stat().st_size / (1024 * 1024)
orig_size_mb = total_size / (1024 * 1024)

print(f"\n🎉 Archive created successfully!")
print(f"Files included: {count}")
print(f"Original size: {orig_size_mb:.2f} MB")
print(f"Compressed zip size: {zip_size_mb:.2f} MB")
print(f"Saved to: {zip_dest}")

# Also copy a backup inside the workspace
import shutil
shutil.copy2(zip_dest, workspace_copy)
print(f"Workspace backup saved to: {workspace_copy}")
