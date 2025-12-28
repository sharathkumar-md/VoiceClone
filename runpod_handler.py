"""
RunPod Serverless Handler for Chatterbox TTS
Deploy this to your RunPod endpoint for fast GPU-based synthesis
"""
import runpod
import torch
import torchaudio
import base64
import io
import os
from chatterbox.tts import ChatterboxTTS

# Global model instance (loaded once on cold start)
tts_model = None

def load_model():
    """Load Chatterbox TTS model (called once on cold start)"""
    global tts_model
    if tts_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Chatterbox TTS model on {device}...")
        tts_model = ChatterboxTTS.from_pretrained(device=device)
        print("Model loaded successfully!")
    return tts_model

def handler(job):
    """
    RunPod handler function

    Expected input format:
    {
        "task": "tts",
        "text": "Text to synthesize",
        "ref_audio_b64": "base64_encoded_voice_sample",
        "exaggeration": 0.3,
        "temperature": 0.6,
        "cfg_weight": 0.3
    }

    Returns:
    {
        "audio_b64": "base64_encoded_wav_audio"
    }
    """
    try:
        job_input = job["input"]

        # Validate input
        if job_input.get("task") != "tts":
            return {"error": "Invalid task type. Expected 'tts'"}

        text = job_input.get("text")
        ref_audio_b64 = job_input.get("ref_audio_b64")
        exaggeration = job_input.get("exaggeration", 0.3)
        temperature = job_input.get("temperature", 0.6)
        cfg_weight = job_input.get("cfg_weight", 0.3)

        if not text:
            return {"error": "Missing 'text' parameter"}
        if not ref_audio_b64:
            return {"error": "Missing 'ref_audio_b64' parameter"}

        # Load model
        model = load_model()

        # Decode reference audio
        print("Decoding reference audio...")
        ref_audio_bytes = base64.b64decode(ref_audio_b64)
        ref_audio_buffer = io.BytesIO(ref_audio_bytes)

        # Save reference audio temporarily
        temp_ref_path = "/tmp/ref_audio.wav"
        with open(temp_ref_path, "wb") as f:
            f.write(ref_audio_bytes)

        # Prepare voice conditionals
        print(f"Preparing voice conditionals with exaggeration={exaggeration}...")
        model.prepare_conditionals(temp_ref_path, exaggeration=exaggeration)

        # Generate audio
        print(f"Generating audio for text: {text[:50]}...")
        wav = model.generate(
            text,
            temperature=temperature,
            cfg_weight=cfg_weight,
        )

        # Convert tensor to WAV bytes
        print("Converting to WAV...")
        output_buffer = io.BytesIO()
        torchaudio.save(
            output_buffer,
            wav.cpu(),
            model.sr,
            format="wav"
        )
        output_buffer.seek(0)
        audio_bytes = output_buffer.read()

        # Encode as base64
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

        print(f"Success! Generated {len(audio_bytes)} bytes of audio")

        # Clean up
        if os.path.exists(temp_ref_path):
            os.remove(temp_ref_path)

        return {
            "audio_b64": audio_b64,
            "audio_size_bytes": len(audio_bytes),
            "sample_rate": model.sr
        }

    except Exception as e:
        print(f"Error in handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# Start the RunPod serverless worker
runpod.serverless.start({"handler": handler})
