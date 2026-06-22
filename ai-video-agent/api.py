import os
import json
import uuid
import subprocess
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Blazly AI Video Engine")

# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("progress", exist_ok=True)
os.makedirs("jobs", exist_ok=True)

def update_progress(job_id: str, stage: str, progress: int):
    with open(f"progress/{job_id}.json", "w", encoding="utf-8") as f:
        json.dump({"stage": stage, "progress": progress}, f)

def run_pipeline(job_id: str, pdf_path: str, avatar_mode: str):
    """Background task to run the video generation pipeline"""
    update_progress(job_id, "Initializing Pipeline", 5)
    try:
        # Run the main.py pipeline, passing the job_id so it can isolate outputs
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        
        # We will modify main.py to accept --job_id and --mode
        cmd = ["uv", "run", "python", "main.py", "--pdf", pdf_path, "--job_id", job_id, "--mode", avatar_mode]
        subprocess.run(cmd, env=env, check=True)
        
        update_progress(job_id, "Completed", 100)
    except subprocess.CalledProcessError as e:
        print(f"Pipeline error for {job_id}: {e}")
        update_progress(job_id, "Error", -1)
    except Exception as e:
        print(f"Unexpected error for {job_id}: {e}")
        update_progress(job_id, "Error", -1)

@app.post("/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    mode: str = Form("wav2lip")
):
    """Uploads PDF and starts the generation job"""
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    job_dir = f"jobs/{job_id}"
    os.makedirs(job_dir, exist_ok=True)
    
    # Save uploaded PDF
    pdf_path = os.path.join(job_dir, file.filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
        
    update_progress(job_id, "Queued", 0)
    
    # Start pipeline in background
    background_tasks.add_task(run_pipeline, job_id, pdf_path, mode)
    
    return {"job_id": job_id, "message": "Job queued", "mode": mode}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    """Returns the current progress of the job"""
    progress_file = f"progress/{job_id}.json"
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"stage": "Not Found", "progress": 0}

@app.get("/download/{job_id}")
def download_video(job_id: str):
    """Serves the final generated video"""
    video_path = f"jobs/{job_id}/outputs/videos/final_video.mp4"
    if os.path.exists(video_path):
        return FileResponse(video_path, media_type="video/mp4", filename=f"blazly_{job_id}.mp4")
    return {"error": "Video not ready or not found"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
