import json
import os
from google import genai

# Gemini Client
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

# Read PDF extracted content
with open("data/content.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Limit content size
content = content[:15000]

prompt = f"""
You are an expert educational video creator.

Read the training material below and create a professional
course video plan.

IMPORTANT:
Return ONLY valid JSON.
Do not use markdown.
Do not include explanations.
Do not include text before JSON.
Do not include text after JSON.

Format:

{{
  "title": "...",
  "scenes": [
    {{
      "scene": 1,
      "duration": 12,
      "slide_title": "Scene title",
      "bullet_points": [
        "Point 1",
        "Point 2",
        "Point 3"
      ],
      "image_prompts": [
        "visual prompt 1",
        "visual prompt 2",
        "visual prompt 3"
      ],
      "narration": "professional voiceover narration"
    }}
  ]
}}

Rules:

- Create exactly 5 scenes
- Each scene must contain:
  - slide_title
  - 3 to 5 bullet_points
  - 3 image_prompts
  - narration
- Bullet points should be short and presentation-friendly
- Image prompts should represent beginning, middle and end of the scene
- Narration should sound like a professional trainer
- Narration should expand on the bullet points
- Image prompts should be cinematic, realistic and educational
- Duration should be 12 seconds

Training Material:

{content}
"""

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text

    # Remove markdown
    text = (
        text.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # Extract first JSON object
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == 0:
        raise Exception("No JSON found in Gemini response")

    json_text = text[start:end]

    # Debug
    print("✅ JSON extracted")

    data = json.loads(json_text)

    with open(
        "data/scenes.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("✅ Saved scenes.json")
    print("🎬 Title:", data["title"])
    print("📚 Scenes:", len(data["scenes"]))

except json.JSONDecodeError as e:
    print("❌ JSON Decode Error")
    print(e)

    with open(
        "data/debug_response.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(text)

    print("📄 Full Gemini response saved to debug_response.txt")

except Exception as e:
    print("❌ Error:", e)