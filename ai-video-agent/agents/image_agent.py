import json
import requests
import urllib.parse
import time

with open("data/scenes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for scene in data["scenes"]:
    scene_no = scene["scene"]

    for prompt_no, prompt in enumerate(
        scene["image_prompts"],
        start=1
    ):

        filename = f"outputs/images/scene_{scene_no}_{prompt_no}.jpg"

        print(f"Generating {filename}...")

        url = (
            "https://image.pollinations.ai/prompt/"
            + urllib.parse.quote(prompt)
        )

        try:
            response = requests.get(
                url,
                timeout=60
            )

            if response.status_code == 200:

                with open(filename, "wb") as img:
                    img.write(response.content)

                print(f"✅ Created {filename}")

            else:
                print(
                    f"❌ Failed {filename}"
                )

        except Exception as e:
            print(
                f"❌ Error generating {filename}: {e}"
            )

        time.sleep(2)

print("🎉 All images generated")