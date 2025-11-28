"""
Project Orpheus - Production API Backend  
FastAPI-based REST API for music generation service
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import uuid
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from transformers import MusicgenForConditionalGeneration, AutoProcessor
import scipy.io.wavfile
import numpy as np

from planner import MusicPlanner
from lyrics import LyricGenerator
from audio_processor import AudioProcessor
from audio_stitcher import AudioStitcher

app = FastAPI(title="Project Orpheus API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state
print("Loading models...")
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
planner = MusicPlanner()
lyric_gen = LyricGenerator()
audio_proc = AudioProcessor(sample_rate=32000)
stitcher = AudioStitcher(sample_rate=32000)
print("Models loaded successfully!")

# Output directory
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# In-memory job storage
jobs = {}

class GenerationRequest(BaseModel):
    prompt: str
    use_lyrics: bool = True
    duration: str = "short"  # "short" (~10s), "medium" (~30s), "long" (~2min)
    apply_fades: bool = True
    normalize: bool = True
    plan: Optional[dict] = None

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    audio_url: Optional[str] = None
    metadata: Optional[dict] = None

@app.get("/")
async def root():
    """Serve the home page."""
    return FileResponse("index.html")

@app.get("/generator.html")
async def generator_page():
    """Serve the generator page."""
    return FileResponse("generator.html")

@app.post("/plan")
async def get_plan(request: GenerationRequest):
    """Return a song plan for the given prompt without generating audio."""
    plan = planner.plan(request.prompt)
    return {"plan": plan}

@app.post("/generate", response_model=GenerationResponse)
async def generate_music(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate music from a text prompt.
    Returns a job ID immediately; processing happens in background.
    """
    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "request": request.dict()}
    
    # Start background task
    background_tasks.add_task(process_generation, job_id, request)
    
    return GenerationResponse(
        job_id=job_id,
        status="processing"
    )

@app.get("/status/{job_id}", response_model=GenerationResponse)
async def get_status(job_id: str):
    """Check the status of a generation job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    response = GenerationResponse(
        job_id=job_id,
        status=job["status"]
    )
    
    if job["status"] == "completed":
        response.audio_url = f"/download/{job_id}"
        response.metadata = job.get("metadata")
    elif job["status"] == "failed":
        response.metadata = {"error": job.get("error", "Unknown error")}
    
    return response

@app.get("/download/{job_id}")
async def download_audio(job_id: str):
    """Download the generated audio file."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Generation not complete")
    
    filepath = job.get("filepath")
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(filepath, media_type="audio/wav", filename=f"{job_id}.wav")

def process_generation(job_id: str, request: GenerationRequest):
    """Background task for music generation."""
    try:
        # Step 1: Get plan (from request or generate new)
        plan = request.plan if request.plan else planner.plan(request.prompt)
        
        # Step 2: Create conditioning
        # Note: MusicGen-small is an INSTRUMENTAL model - it cannot generate vocals/singing
        # The conditioning describes the musical style, mood, and instruments
        conditioning = f"{plan['genre']} music, {plan['mood']} mood, {plan['key']}, {plan['bpm']} BPM, instruments: {plan['instruments']}"
        
        # Step 3: Determine number of segments based on duration
        duration_config = {
            "short": {"segments": 1, "tokens": 256},      # ~8s
            "medium": {"segments": 3, "tokens": 512},     # ~48s  
            "long": {"segments": 3, "tokens": 768}        # ~72s with longer segments (reduced to 3 segments for fewer transitions)
        }
        
        config = duration_config.get(request.duration, duration_config["short"])
        num_segments = config["segments"]
        max_tokens = config["tokens"]
        
        # Step 4: Generate audio segments
        segments = []
        
        for i in range(num_segments):
            # Update job status with progress
            jobs[job_id]["metadata"] = {
                "progress": f"{i+1}/{num_segments}",
                "current_segment": i + 1,
                "total_segments": num_segments
            }
            
            inputs = processor(
                text=[conditioning],
                padding=True,
                return_tensors="pt",
            )
            
            audio_values = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=True)
            segment = audio_values[0][0].cpu().numpy()
            segments.append(segment)
        
        # Step 5: Stitch segments if multiple
        if len(segments) > 1:
            # Match loudness across segments
            segments = stitcher.match_loudness(segments)
            # Stitch with maximum 6-second crossfading for imperceptible transitions
            audio_data = stitcher.stitch_segments(segments, fade_duration=6.0, use_beat_align=True)
        else:
            audio_data = segments[0]
        
        # Step 6: Post-process
        if request.normalize or request.apply_fades:
            audio_data = audio_proc.process(
                audio_data,
                normalize=request.normalize,
                fades=request.apply_fades,
                compress=False
            )
        
        # Step 7: Save
        filepath = OUTPUT_DIR / f"{job_id}.wav"
        sampling_rate = model.config.audio_encoder.sampling_rate
        
        # Convert float32 audio to int16 for WAV compatibility
        # MusicGen outputs float32 in range [-1, 1], we need int16 [-32768, 32767]
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        scipy.io.wavfile.write(str(filepath), rate=sampling_rate, data=audio_int16)
        
        # Update job
        jobs[job_id].update({
            "status": "completed",
            "filepath": str(filepath),
            "metadata": {
                "prompt": request.prompt,
                "plan": plan,
                "duration_sec": len(audio_data) / sampling_rate,
                "sample_rate": sampling_rate,
                "num_segments": num_segments
            }
        })
        
    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PROJECT ORPHEUS API SERVER")
    print("="*60)
    print("\nStarting server on http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
