import json
import asyncio
import edge_tts

with open("data/scenes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

VOICE = "en-US-AndrewNeural"

async def generate():

    for scene in data["scenes"]:

        scene_no = scene["scene"]
        narration = scene["narration"]

        communicate = edge_tts.Communicate(
            text=narration,
            voice=VOICE
        )

        await communicate.save(
            f"outputs/audio/scene_{scene_no}.mp3"
        )

        print(
            f"✅ scene_{scene_no}.mp3 created"
        )

asyncio.run(generate())