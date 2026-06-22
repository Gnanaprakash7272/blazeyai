import subprocess
import sys

agents = [
    "agents/pdf_agent.py",
    "agents/planner.py",
    "agents/slide_agent.py",
    "agents/voice_agent.py",
    "agents/image_agent.py",
    "agents/avatar_agent.py",
    "agents/video_agent.py"
]
print("🚀 Starting AI Course Generator")
print("=" * 50)

for agent in agents:

    print(f"\n▶ Running: {agent}")

    result = subprocess.run(
        [sys.executable, agent]
    )

    if result.returncode != 0:
        print(f"\n❌ Failed: {agent}")
        sys.exit(1)

    print(f"✅ Completed: {agent}")

print("\n🎉 Course Generation Complete!")
print("📁 Slides : outputs/slides/")
print("📁 Images : outputs/images/")
print("📁 Audio  : outputs/audio/")
print("📁 Video  : outputs/videos/")