import json
import os
from moviepy import *

# Load scenes
with open("data/scenes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

os.makedirs("outputs/videos", exist_ok=True)

AVATAR_VIDEO = "outputs/avatar/avatar--d0.mp4"
HAS_AVATAR   = os.path.exists(AVATAR_VIDEO)

all_clips = []

for scene in data["scenes"]:

    scene_no  = scene["scene"]
    narration = scene["narration"]

    # --- Audio ---
    audio_file = f"outputs/audio/scene_{scene_no}.mp3"
    audio      = AudioFileClip(audio_file)
    duration   = audio.duration

    # --- Slide as background (with subtle Ken Burns zoom) ---
    slide_file = f"outputs/slides/slide_{scene_no}.png"
    slide = (
        ImageClip(slide_file)
        .resized(lambda t: 1 + 0.02 * t / duration)   # subtle slow zoom
        .with_duration(duration)
    )

    layers = [slide]

    # --- Avatar overlay (bottom-right corner) ---
    if HAS_AVATAR:
        avatar_raw = VideoFileClip(AVATAR_VIDEO, audio=False)

        # Loop avatar if shorter than audio
        if avatar_raw.duration < duration:
            loops = int(duration / avatar_raw.duration) + 1
            avatar_raw = concatenate_videoclips([avatar_raw] * loops)

        avatar = (
            avatar_raw
            .subclipped(0, duration)
            .resized(width=300)
            .with_position((940, 370))   # bottom-right area
        )
        layers.append(avatar)

    # --- Subtitle bar + text ---
    subtitle_bg = (
        ColorClip(size=(1280, 80), color=(0, 0, 0))
        .with_duration(duration)
        .with_opacity(0.72)
        .with_position(("center", 640))
    )

    subtitle = (
        TextClip(
            text=narration,
            font_size=19,
            color="white",
            method="caption",
            size=(1150, None)
        )
        .with_duration(duration)
        .with_position(("center", 652))
    )

    layers += [subtitle_bg, subtitle]

    # --- Composite ---
    scene_clip = (
        CompositeVideoClip(layers, size=(1280, 720))
        .with_audio(audio)
    )

    all_clips.append(scene_clip)
    print(f"✅ Scene {scene_no} composited")

# --- Final video ---
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

print("\n✅ Final educational video created!")
print("📁 outputs/videos/final_video.mp4")