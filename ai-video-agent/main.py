import subprocess
import sys
import os
import argparse

# ── Output folders ──────────────────────────────────────────
for folder in [
    "outputs/slides",
    "outputs/audio",
    "outputs/images",
    "outputs/avatar",
    "outputs/videos",
    "data"
]:
    os.makedirs(folder, exist_ok=True)

# ── Argument: PDF path ───────────────────────────────────────
parser = argparse.ArgumentParser(description="Blazly AI Video Generator")
parser.add_argument("--pdf", type=str, help="Path to input PDF file")
args = parser.parse_args()

# ── Pipeline stages ──────────────────────────────────────────
agents = [
    ("📄 PDF Extraction",      "agents/pdf_agent.py",    args.pdf),
    ("🧠 Scene Planning",      "agents/planner.py",      None),
    ("🖼️  Slide Generation",   "agents/slide_agent.py",  None),
    ("🎤 Voice Generation",    "agents/voice_agent.py",  None),
    ("🌄 Image Generation",    "agents/image_agent.py",  None),
    ("🧑 Avatar Generation",   "agents/avatar_agent.py", None),
    ("🎬 Video Assembly",      "agents/video_agent.py",  None),
]

print("\n🚀 Blazly AI — Educational Video Generator")
print("=" * 50)

for label, agent, extra_arg in agents:

    print(f"\n▶  {label}")

    cmd = [sys.executable, agent]
    if extra_arg:
        cmd += [extra_arg]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"\n❌ Failed at: {label}")
        sys.exit(1)

    print(f"✅ Done: {label}")

print("\n" + "=" * 50)
print("🎉 Video generation complete!")
print("📁 Final video → outputs/videos/final_video.mp4")