import json
from moviepy import *

# Load scenes
with open("data/scenes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

all_clips = []

for scene in data["scenes"]:

    scene_no = scene["scene"]
    narration = scene["narration"]

    audio_file = f"outputs/audio/scene_{scene_no}.mp3"
    audio = AudioFileClip(audio_file)

    # 3 images per scene
    image_files = [
        f"outputs/images/scene_{scene_no}_1.jpg",
        f"outputs/images/scene_{scene_no}_2.jpg",
        f"outputs/images/scene_{scene_no}_3.jpg"
    ]

    image_duration = audio.duration / len(image_files)

    scene_clips = []

    for image_file in image_files:

        image_clip = (
            ImageClip(image_file)
            .resized(lambda t: 1 + 0.08 * t / image_duration)
            .with_duration(image_duration)
        )

        scene_clips.append(image_clip)

    # Merge 3 images
    merged_scene = concatenate_videoclips(
        scene_clips,
        method="compose"
    )

    # Subtitle background
    subtitle_bg = (
        ColorClip(
            size=(1280, 90),
            color=(0, 0, 0)
        )
        .with_duration(audio.duration)
        .with_opacity(0.6)
        .with_position(("center", 630))
    )

    # Subtitle
    subtitle = (
        TextClip(
            text=narration,
            font_size=20,
            color="white",
            method="caption",
            size=(1100, None)
        )
        .with_duration(audio.duration)
        .with_position(("center", 650))
    )

    final_scene = (
        CompositeVideoClip([
            merged_scene,
            subtitle_bg,
            subtitle
        ])
        .with_audio(audio)
    )

    all_clips.append(final_scene)

# Merge all scenes
final_video = concatenate_videoclips(
    all_clips,
    method="compose"
)

final_video.write_videofile(
    "outputs/videos/final_video.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac"
)

print("✅ Documentary-style video created!")