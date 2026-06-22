import subprocess
import sys
import os
import argparse
import json

# Fix Windows Unicode/emoji encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# ── Arguments ───────────────────────────────────────
parser = argparse.ArgumentParser(description="Blazly AI Video Generator")
parser.add_argument("--pdf", type=str, help="Path to input PDF file")
parser.add_argument("--job_id", type=str, help="Job ID for isolated processing", default="local")
parser.add_argument("--mode", type=str, help="Avatar mode: liveportrait or wav2lip", default="wav2lip")
args = parser.parse_args()

job_dir = f"jobs/{args.job_id}" if args.job_id != "local" else "."
os.environ["BLAZLY_JOB_DIR"] = job_dir
os.environ["BLAZLY_MODE"] = args.mode
os.environ["BLAZLY_PDF"] = args.pdf if args.pdf else ""

# ── Output folders ──────────────────────────────────────────
for folder in [
    f"{job_dir}/outputs/slides",
    f"{job_dir}/outputs/audio",
    f"{job_dir}/outputs/images",
    f"{job_dir}/outputs/avatar",
    f"{job_dir}/outputs/videos",
    f"{job_dir}/data"
]:
    os.makedirs(folder, exist_ok=True)

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

def update_progress(stage, percentage):
    if args.job_id != "local":
        prog_file = f"progress/{args.job_id}.json"
        with open(prog_file, "w", encoding="utf-8") as f:
            json.dump({"stage": stage, "progress": percentage}, f)

print(f"\n🚀 Blazly AI — Job: {args.job_id} | Mode: {args.mode}")
print("=" * 50)

total_agents = len(agents)
for i, (label, agent, extra_arg) in enumerate(agents):
    
    print(f"\n▶  {label}")
    progress_pct = int((i / total_agents) * 100)
    update_progress(label, progress_pct)

    cmd = [sys.executable, agent]
    # We will pass the job info through env variables now, but keep extra_arg for backward compat
    if extra_arg and agent == "agents/pdf_agent.py":
        cmd += [extra_arg]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"\n❌ Failed at: {label}")
        update_progress(f"Failed at {label}", -1)
        sys.exit(1)

    print(f"✅ Done: {label}")

update_progress("Finalizing", 95)
print("\n" + "=" * 50)
print("🎉 Video generation complete!")
print(f"📁 Final video → {job_dir}/outputs/videos/final_video.mp4")
update_progress("Completed", 100)