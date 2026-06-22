import os
import subprocess
import json

LIVEPORTRAIT_PATH = r"F:\MINI PROJECTS\LivePortrait"
LIVEPORTRAIT_PYTHON = r"F:\MINI PROJECTS\LivePortrait\.venv310\Scripts\python.exe"

AVATAR_IMAGE = r"assets\avatar.png"
DRIVING_VIDEO = rf"{LIVEPORTRAIT_PATH}\assets\examples\driving\d0.mp4"

with open("data/scenes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

os.makedirs("outputs/avatar", exist_ok=True)

avatar_file = "outputs/avatar/avatar--d0.mp4"

if os.path.exists(avatar_file):
    print("✅ Avatar already exists. Skipping generation.")

else:
    print("🚀 Generating avatar...")

    cmd = [
        LIVEPORTRAIT_PYTHON,
        rf"{LIVEPORTRAIT_PATH}\inference.py",
        "-s", AVATAR_IMAGE,
        "-d", DRIVING_VIDEO,
        "-o", r"outputs\avatar"
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("✅ Avatar generated successfully")
    else:
        print("❌ Avatar generation failed")