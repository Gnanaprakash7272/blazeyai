import json
import os
from moviepy import *

with open("data/scenes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

os.makedirs("outputs/videos", exist_ok=True)

# ── Must match slide_agent.py avatar zone exactly ────────────
HEADER_H    = 62
FOOTER_H    = 90
DIVIDER     = 2
CONTENT_TOP = HEADER_H + DIVIDER

AV_X1, AV_Y1 = 840, CONTENT_TOP + 160
AV_X2, AV_Y2 = 1240, 720 - FOOTER_H - DIVIDER - 10
AV_W = AV_X2 - AV_X1   # 400
AV_H = AV_Y2 - AV_Y1

# Per-scene lip-synced avatars from SadTalker
AVATAR_DIR = "outputs/avatar"

all_clips = []

for scene in data["scenes"]:

    scene_no  = scene["scene"]
    narration = scene["narration"]

    # ── Audio ────────────────────────────────────────────────
    audio_file = f"outputs/audio/scene_{scene_no}.mp3"
    audio      = AudioFileClip(audio_file)
    duration   = audio.duration

    # ── Slide background (subtle Ken Burns zoom) ─────────────
    slide_file = f"outputs/slides/slide_{scene_no}.png"
    slide = (
        ImageClip(slide_file)
        .resized(lambda t: 1 + 0.015 * (t / duration))
        .with_duration(duration)
    )

    layers = [slide]

    # ── Per-scene lip-synced avatar from SadTalker ────────────
    avatar_file = os.path.join(AVATAR_DIR, f"avatar_scene_{scene_no}.mp4")

    if os.path.exists(avatar_file):
        avatar_clip = VideoFileClip(avatar_file, audio=False)

        # Loop if shorter than audio
        if avatar_clip.duration < duration:
            loops = int(duration / avatar_clip.duration) + 1
            avatar_clip = concatenate_videoclips([avatar_clip] * loops)

        avatar = (
            avatar_clip
            .subclipped(0, duration)
            .resized((AV_W, AV_H))
            .with_position((AV_X1, AV_Y1))
        )
        layers.append(avatar)
        print(f"🧑 Scene {scene_no}: lip-synced avatar loaded ✅")
    else:
        print(f"⚠️  Scene {scene_no}: no avatar found, slide-only")

    # ── Composite ─────────────────────────────────────────────
    scene_clip = (
        CompositeVideoClip(layers, size=(1280, 720))
        .with_audio(audio)
    )

    all_clips.append(scene_clip)
    print(f"✅ Scene {scene_no} composited  ({duration:.1f}s)")


# ── Render final video ────────────────────────────────────────
print("\n🎬 Rendering final video...")

final_video = concatenate_videoclips(all_clips, method="compose")

final_video.write_videofile(
    "outputs/videos/final_video.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac",
    threads=4,
    logger="bar"
)

print("\n✅ Final educational video ready!")
print("📁 outputs/videos/final_video.mp4")