"""
TTS API Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
import uuid
import asyncio
from datetime import datetime
import base64
import os
from pathlib import Path
import re
import logging

from ..models.tts import (
    TTSGenerateRequest,
    TTSGenerateResponse,
    TTSStatusResponse,
)
from story_narrator.text_processor import TextProcessor

# AudioSynthesizer requires torch - make it optional
try:
    from story_narrator.audio_synthesizer import AudioSynthesizer
    _has_audio_synthesizer = True
except ImportError:
    _has_audio_synthesizer = False
    AudioSynthesizer = None

# Set up logger
logger = logging.getLogger(__name__)

# Initialize text processor (same as Gradio)
text_processor = TextProcessor(
    max_chunk_length=500,  # 500 chars per chunk (not words!)
    paragraph_pause=1.0,   # 1 second pause between paragraphs
    sentence_pause=0.3     # 0.3 second pause between sentences
)

router = APIRouter(prefix="/api/v1/tts", tags=["tts"])

# Task storage (in production, use Redis or a database)
tasks: Dict[str, Dict] = {}

# Initialize audio synthesizer
audio_synthesizer = None

def get_audio_synthesizer():
    global audio_synthesizer
    if not _has_audio_synthesizer:
        raise ImportError(
            "AudioSynthesizer is not available. "
            "This usually means torch is not installed. "
            "For Render deployment, TTS functionality requires RunPod or external GPU service."
        )
    if audio_synthesizer is None:
        # Use RunPod for fast serverless GPU generation (100x faster than CPU)
        audio_synthesizer = AudioSynthesizer(
            device="cpu",  # Device doesn't matter when using RunPod
            use_runpod=True  # Enable RunPod serverless
        )
    return audio_synthesizer


def sanitize_text_for_tts(text: str) -> str:
    """
    Sanitize text to make it more suitable for TTS synthesis.
    Removes special characters and formatting that might confuse the model.
    """
    # Replace smart quotes with regular quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    # Replace em dashes and en dashes with regular hyphens
    text = text.replace('—', '-').replace('–', '-')

    # Replace ellipsis with three periods
    text = text.replace('…', '...')

    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove any remaining non-ASCII characters that might cause issues
    # But keep common punctuation
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    return text.strip()


def convert_to_mono(audio_path: Path) -> Path:
    """
    Convert audio file to mono and resample to 24kHz (Chatterbox TTS requirement).
    Returns path to processed audio file.
    """
    import librosa
    import soundfile as sf
    import numpy as np

    # Read audio file and resample to 24kHz
    target_sr = 24000  # Chatterbox TTS expects 24kHz
    audio, sr = sf.read(str(audio_path))

    # Convert to mono if stereo (2 channels)
    if len(audio.shape) > 1 and audio.shape[1] == 2:
        audio = np.mean(audio, axis=1)

    # Resample to target sample rate if needed
    if sr != target_sr:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)

    # Save processed audio
    processed_path = audio_path.with_stem(f"{audio_path.stem}_processed")
    sf.write(str(processed_path), audio, target_sr)
    return processed_path


async def generate_audio_task(task_id: str, request: TTSGenerateRequest):
    """
    Background task to generate audio
    """
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10

        synthesizer = get_audio_synthesizer()

        # Get voice sample path from voice ID or base64
        voice_sample_path = None
        if request.voiceSample:
            # Check if it's a voice ID (UUID format) or base64 data
            if len(request.voiceSample) < 100:  # Likely a voice ID
                # Look up the voice file from voice samples directory
                voice_samples_dir = Path("src/output/voice_samples")
                voice_files = list(voice_samples_dir.glob(f"{request.voiceSample}.*"))
                if voice_files:
                    voice_sample_path = voice_files[0]
                    tasks[task_id]["progress"] = 20
                else:
                    tasks[task_id]["status"] = "failed"
                    tasks[task_id]["error"] = f"Voice sample not found: {request.voiceSample}"
                    return
            else:
                # It's base64 encoded data
                try:
                    voice_data = base64.b64decode(request.voiceSample)
                    voice_sample_path = Path("src/output") / f"voice_sample_{task_id}.wav"
                    voice_sample_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(voice_sample_path, "wb") as f:
                        f.write(voice_data)
                    tasks[task_id]["progress"] = 20
                except Exception as e:
                    tasks[task_id]["status"] = "failed"
                    tasks[task_id]["error"] = f"Failed to decode voice sample: {str(e)}"
                    return

        # Set voice sample if provided
        if voice_sample_path:
            tasks[task_id]["progress"] = 30

            # Use original audio file without conversion
            # The RunPod handler seems to work better with original format
            # voice_sample_path = convert_to_mono(Path(voice_sample_path))

            synthesizer.set_voice(
                str(voice_sample_path),
                exaggeration=request.exaggeration
            )
        else:
            # Use a default voice sample or handle the case where no voice is provided
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = "Voice sample is required for TTS generation"
            return

        # Update progress
        tasks[task_id]["progress"] = 40

        # Generate audio
        output_dir = Path("src/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"narration_{task_id}.wav"

        # Update progress
        tasks[task_id]["progress"] = 50

        # Process text using TextProcessor (same as working Gradio UI)
        logger.info(f"Processing text ({len(request.text)} chars)...")
        processed = text_processor.process_story(request.text)

        # Extract text chunks and pause durations
        chunks = processed["chunks"]
        text_chunks = [c.text for c in chunks]
        pause_durations = [c.pause_after for c in chunks]

        logger.info(f"Text processed into {len(text_chunks)} chunks")
        logger.info(f"Estimated duration: {processed['metadata']['estimated_duration_seconds']:.1f}s")

        # Log first few chunks for debugging
        for i, chunk in enumerate(text_chunks[:3], 1):
            logger.info(f"Chunk {i}: {len(chunk)} chars - {chunk[:100]}...")

        # Generate the audio using synthesize_and_save
        result = synthesizer.synthesize_and_save(
            text_chunks=text_chunks,
            output_path=str(output_path),
            pause_durations=pause_durations,  # Use proper pause durations
            format="wav",
            show_progress=False
        )

        tasks[task_id]["progress"] = 90

        # Generate URL for the audio file
        audio_url = f"/output/narration_{task_id}.wav"

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["audio_url"] = audio_url
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        tasks[task_id]["duration"] = result.get("duration_seconds", 0)

    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["progress"] = 0


@router.post("/generate", response_model=TTSGenerateResponse)
async def generate_audio(request: TTSGenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate audio narration for a story
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Initialize task
        tasks[task_id] = {
            "status": "queued",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "story_id": request.storyId,
        }

        # Start background task
        background_tasks.add_task(generate_audio_task, task_id, request)

        return TTSGenerateResponse(
            task_id=task_id,
            message="Audio generation started"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start audio generation: {str(e)}")


@router.get("/status/{task_id}", response_model=TTSStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of an audio generation task
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]

    # Calculate estimated time remaining
    estimated_time = None
    if task["status"] == "processing" and task["progress"] > 0:
        # Rough estimate: assume 2 minutes total, calculate based on progress
        total_time = 120  # seconds
        elapsed_percentage = task["progress"] / 100
        if elapsed_percentage > 0:
            estimated_time = int(total_time * (1 - elapsed_percentage))

    return TTSStatusResponse(
        status=task["status"],
        progress=task["progress"],
        estimated_time=estimated_time,
        audio_url=task.get("audio_url"),
        error=task.get("error"),
    )
