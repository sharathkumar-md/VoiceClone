import torch
import torchaudio
import io
import base64
import runpod
import tempfile
import os
import time
import gc
import traceback

# --- Global State ---
MODELS = {
    "tts_model": None,
    "vc_model": None,
    "device": None
}
MODELS_LOADED = {
    "tts": None,
    "vc": None
}
DEVICE_CHECKED = False

# --- 1. init() function - Minimal ---
def init():
    """Minimal init. Device check moved to load_model."""
    print(f"--- [{time.time():.2f}] init() function started (Lazy Loading Mode) ---")
    print(f"--- [{time.time():.2f}] init() finished successfully. ---")
    return True

# --- Helper to determine device ---
def determine_device():
    global MODELS, DEVICE_CHECKED
    if DEVICE_CHECKED:
        return MODELS["device"]

    print(f"--- [{time.time():.2f}] Determining device...")
    try:
        if torch.cuda.is_available():
            MODELS["device"] = "cuda"
            print(f"--- [{time.time():.2f}] CUDA is available. Device set to cuda.")
            total_vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"--- [{time.time():.2f}] Total VRAM: {total_vram:.2f} GB")
        else:
            MODELS["device"] = "cpu"
            print(f"--- [{time.time():.2f}] CUDA not available. Device set to cpu.")
        DEVICE_CHECKED = True
        return MODELS["device"]
    except Exception as e_device:
        print(f"--- [{time.time():.2f}] ❌ CRITICAL: Error during device check: {e_device}")
        MODELS["device"] = "cpu"
        DEVICE_CHECKED = True
        return "cpu"

# --- Helper function to load models on demand ---
def load_model(model_type):
    global MODELS, MODELS_LOADED
    
    device = determine_device()
    if device is None:
        print(f"--- [{time.time():.2f}] ❌ ERROR: Device could not be determined. Aborting load.")
        return False

    if MODELS_LOADED.get(model_type) is False:
        print(f"--- [{time.time():.2f}] Model '{model_type}' failed to load previously. Skipping.")
        return False
        
    if MODELS_LOADED.get(model_type) is True:
         print(f"--- [{time.time():.2f}] Model '{model_type}' already loaded.")
         return True

    print(f"--- [{time.time():.2f}] LAZY LOAD: Attempting to load {model_type.upper()} model onto device: {device} ---")
    MODELS_LOADED[model_type] = False
    
    try:
        if model_type == "tts":
            from src.chatterbox.tts import ChatterboxTTS
            print(f"--- [{time.time():.2f}] Calling ChatterboxTTS.from_pretrained...")
            MODELS["tts_model"] = ChatterboxTTS.from_pretrained(device=device)
            print(f"--- [{time.time():.2f}] ✅ LAZY LOAD: ChatterboxTTS loaded successfully.")
            
        elif model_type == "vc":
            from src.chatterbox.vc import ChatterboxVC
            print(f"--- [{time.time():.2f}] Calling ChatterboxVC.from_pretrained...")
            MODELS["vc_model"] = ChatterboxVC.from_pretrained(device=device)
            print(f"--- [{time.time():.2f}] ✅ LAZY LOAD: ChatterboxVC loaded successfully.")
            
        else:
            print(f"--- [{time.time():.2f}] ❌ Invalid model_type requested: {model_type}")
            return False

        MODELS_LOADED[model_type] = True
        gc.collect()
        if device == 'cuda': torch.cuda.empty_cache()
        return True

    except Exception as e:
        print(f"--- [{time.time():.2f}] ❌ LAZY LOAD FAILED: {model_type.upper()}: {e}")
        traceback.print_exc()
        MODELS[f"{model_type}_model"] = None
        MODELS_LOADED[model_type] = False
        return False

# --- 2. handler() function ---
def handler(job):
    """Process one inference job, loading the required model if necessary."""
    job_input = job['input']
    task_type = job_input.get("task", "tts")
    print(f"\n--- [{time.time():.2f}] Handler received job ID: {job.get('id', 'N/A')}, Task: {task_type} ---")

    model_loaded_successfully = load_model(task_type)

    if not model_loaded_successfully:
        error_msg = f"Failed to load or access required model ({task_type}). Check worker logs for specific errors during loading."
        print(f"--- [{time.time():.2f}] {error_msg} ---")
        return {"error": error_msg}
        
    try:
        print(f"--- [{time.time():.2f}] Model for task '{task_type}' ready. Proceeding with handler...")
        if task_type == "tts":
            result = handle_tts(job_input)
        elif task_type == "vc":
            result = handle_vc(job_input)
        else:
            result = {"error": f"Unknown task type: {task_type}"}
        
        print(f"--- [{time.time():.2f}] Handler finished for job ID: {job.get('id', 'N/A')} ---")
        return result
        
    except Exception as e:
        print(f"--- [{time.time():.2f}] ❌ Unhandled exception in handler: {e}")
        traceback.print_exc()
        return {"error": f"Handler error: {str(e)}"}

# --- Handle TTS ---
def handle_tts(job_input):
    """Handles the Text-to-Speech task."""
    model = MODELS["tts_model"]
    text = job_input.get("text")
    ref_audio_b64 = job_input.get("ref_audio_b64")
    
    if not text or not ref_audio_b64:
        return {"error": "Missing 'text' or 'ref_audio_b64'"}
    
    audio_bytes = base64.b64decode(ref_audio_b64)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        tmp_audio.write(audio_bytes)
        tmp_audio.flush()
        
        model.prepare_conditionals(
            tmp_audio.name,
            exaggeration=job_input.get("exaggeration", 0.5)
        )
        wav_tensor = model.generate(
            text,
            temperature=job_input.get("temperature", 0.8),
            cfg_weight=job_input.get("cfg_weight", 0.5),
            max_new_tokens=job_input.get("max_new_tokens", 250)
        )
    
    buffer = io.BytesIO()
    torchaudio.save(buffer, wav_tensor.cpu(), model.sr, format="wav")
    buffer.seek(0)
    output_audio_b64 = base64.b64encode(buffer.read()).decode('utf-8')
    return {"audio_b64": output_audio_b64, "content_type": "audio/wav"}

# --- Handle VC ---
def handle_vc(job_input):
    """Handles the Voice Conversion task."""
    model = MODELS["vc_model"]
    source_audio_b64 = job_input.get("source_audio_b64")
    target_voice_b64 = job_input.get("target_voice_b64")
    
    if not source_audio_b64 or not target_voice_b64:
        return {"error": "Missing 'source_audio_b64' or 'target_voice_b64'"}
    
    source_bytes = base64.b64decode(source_audio_b64)
    target_bytes = base64.b64decode(target_voice_b64)
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_source, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_target:
        tmp_source.write(source_bytes)
        tmp_source.flush()
        tmp_target.write(target_bytes)
        tmp_target.flush()
        
        model.set_target_voice(tmp_target.name)
        wav_tensor = model.generate(audio=tmp_source.name)
    
    buffer = io.BytesIO()
    torchaudio.save(buffer, wav_tensor.cpu(), model.sr, format="wav")
    buffer.seek(0)
    output_audio_b64 = base64.b64encode(buffer.read()).decode('utf-8')
    return {"audio_b64": output_audio_b64, "content_type": "audio/wav"}

# --- Start the RunPod worker ---
if __name__ == "__main__":
    print("Starting RunPod Serverless Worker (Lazy Loading Mode)...")
    runpod.serverless.start({
        "handler": handler
    })
