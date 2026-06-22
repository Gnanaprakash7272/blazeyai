import json
import requests
import urllib.parse
import time
import os

with open("data/scenes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

os.makedirs("outputs/images", exist_ok=True)

TIMEOUT   = 45    # seconds per image
RETRY     = 2     # retries per image

for scene in data["scenes"]:
    scene_no = scene["scene"]

    for prompt_no, prompt in enumerate(scene["image_prompts"], start=1):

        filename = f"outputs/images/scene_{scene_no}_{prompt_no}.jpg"

        # Skip if already generated
        if os.path.exists(filename):
            print(f"⏭  Skipping {filename} (already exists)")
            continue

        # Add quality params to Pollinations URL
        encoded = urllib.parse.quote(prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1280&height=720&model=flux&nologo=true"
        )

        print(f"🎨 Generating {filename}...")

        success = False
        for attempt in range(1, RETRY + 1):
            try:
                response = requests.get(url, timeout=TIMEOUT)

                if response.status_code == 200 and len(response.content) > 1000:
                    with open(filename, "wb") as img:
                        img.write(response.content)
                    print(f"✅ Created {filename}")
                    success = True
                    break
                else:
                    print(f"⚠️  Attempt {attempt} failed (status {response.status_code})")

            except requests.exceptions.Timeout:
                print(f"⏱  Timeout on attempt {attempt} for {filename}")
            except Exception as e:
                print(f"❌ Error attempt {attempt}: {e}")

            time.sleep(3)

        if not success:
            # Use a solid colored placeholder so pipeline doesn't break
            print(f"⚠️  Using placeholder for {filename}")
            from PIL import Image
            img = Image.new("RGB", (1280, 720), (20, 30, 55))
            img.save(filename)

        time.sleep(2)

print("🎉 All images generated")