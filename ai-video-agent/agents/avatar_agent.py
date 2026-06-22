import os
import sys
import json
import shutil
import subprocess
import glob

# ── Environment Variables ─────────────────────────────────────
JOB_DIR = os.environ.get("BLAZLY_JOB_DIR", ".")
MODE    = os.environ.get("BLAZLY_MODE", "wav2lip")

# ── Output folders ────────────────────────────────────────────
AUDIO_DIR        = os.path.join(JOB_DIR, "outputs", "audio")
AVATAR_OUT_DIR   = os.path.abspath(os.path.join(JOB_DIR, "outputs", "avatar"))
os.makedirs(AVATAR_OUT_DIR, exist_ok=True)

# ── Assets ────────────────────────────────────────────────────
AVATAR_IMAGE     = os.path.abspath("assets/avatar.png")
TEMPLATE_VIDEO   = os.path.abspath("assets/presenters/professional_male.mp4")

# ── Engine Paths ──────────────────────────────────────────────
SADTALKER_PATH   = r"F:\MINI PROJECTS\blazly ai\LivePortrait\SadTalker"
SADTALKER_PYTHON = os.path.join(SADTALKER_PATH, ".venv", "Scripts", "python.exe")
SADTALKER_INFER  = os.path.join(SADTALKER_PATH, "inference.py")
CHECKPOINT_DIR   = os.path.join(SADTALKER_PATH, "checkpoints")

WAV2LIP_PATH     = os.path.abspath("third_party/Wav2Lip")
WAV2LIP_PYTHON   = "python" # Assuming global/uv python has torch
WAV2LIP_INFER    = os.path.join(WAV2LIP_PATH, "inference.py")
WAV2LIP_CKPT     = os.path.join(WAV2LIP_PATH, "checkpoints", "wav2lip_gan.pth")

# ── Load scenes ───────────────────────────────────────────────
data_path = os.path.join(JOB_DIR, "data", "scenes.json")
with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

scenes = data["scenes"]

print(f"🧑 Generating lip-synced avatar ({MODE} mode) for {len(scenes)} scenes...")

for scene in scenes:
    scene_no   = scene["scene"]
    audio_file = os.path.abspath(f"{AUDIO_DIR}/scene_{scene_no}.mp3")
    out_file   = os.path.join(AVATAR_OUT_DIR, f"avatar_scene_{scene_no}.mp4")

    if os.path.exists(out_file):
        print(f"⏭  Skipping scene {scene_no} (already exists)")
        continue

    if not os.path.exists(audio_file):
        print(f"❌ Audio not found: {audio_file}")
        continue

    if MODE == "wav2lip":
        print(f"\n🎤 Scene {scene_no}: Lip-syncing with Wav2Lip (Template Video)...")
        # Wav2Lip usage: python inference.py --checkpoint_path ... --face ... --audio ... --outfile ...
        if not os.path.exists(TEMPLATE_VIDEO):
            print(f"⚠️ Template video missing at {TEMPLATE_VIDEO}. Creating dummy.")
            shutil.copy(audio_file, out_file) # Dummy fallback
            continue
            
        cmd = [
            WAV2LIP_PYTHON,
            WAV2LIP_INFER,
            "--checkpoint_path", WAV2LIP_CKPT,
            "--face", TEMPLATE_VIDEO,
            "--audio", audio_file,
            "--outfile", out_file
        ]
        
        # NOTE: For MVP we print command, in prod we run it
        print(" ".join(cmd))
        # result = subprocess.run(cmd, cwd=WAV2LIP_PATH)
        
        # Creating a dummy file just to allow pipeline to proceed for MVP UI testing
        with open(out_file, "w") as dummy:
            dummy.write("dummy wav2lip output")
        print(f"✅ Scene {scene_no} Wav2Lip dummy created → {out_file}")

    else:
        # SadTalker / LivePortrait logic
        print(f"\n🎤 Scene {scene_no}: Lip-syncing with SadTalker (Image)...")
        tmp_result = os.path.join(AVATAR_OUT_DIR, f"sadtalker_tmp_{scene_no}")
        os.makedirs(tmp_result, exist_ok=True)

        cmd = [
            SADTALKER_PYTHON,
            SADTALKER_INFER,
            "--source_image",   AVATAR_IMAGE,
            "--driven_audio",   audio_file,
            "--checkpoint_dir", CHECKPOINT_DIR,
            "--result_dir",     tmp_result,
            "--still",
            "--preprocess",     "crop",
        ]

        result = subprocess.run(cmd, cwd=SADTALKER_PATH, capture_output=False)

        if result.returncode == 0:
            generated = glob.glob(os.path.join(tmp_result + "*.mp4"))
            if not generated:
                generated = glob.glob(os.path.join(tmp_result, "*.mp4"))
            if generated:
                shutil.copy(generated[0], out_file)
                print(f"✅ Scene {scene_no} avatar → avatar_scene_{scene_no}.mp4")
            else:
                print(f"⚠️  Scene {scene_no}: output file not found")
        else:
            print(f"❌ Scene {scene_no}: SadTalker failed")

        if os.path.exists(tmp_result):
            shutil.rmtree(tmp_result, ignore_errors=True)

print("\n🎉 All avatar scenes processed!")