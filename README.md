# Chatterbox Story Narrator

AI-powered story generation and narration with voice cloning using Chatterbox TTS.

**Powered by RunPod Serverless GPU - 100x faster than local synthesis**

## Quick Start (3 Commands)

```bash
# 1. Activate environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Verify setup (optional but recommended)
python check_setup.py

# 3. Run the app
python run_app.py
```

---

## What This Does

1. **Enter a story theme** (e.g., "A dragon who's afraid of heights")
2. **Upload a voice sample** (optional - uses default voice if not provided)
3. **Click Generate** to get a fully narrated story with voice cloning

---

## First Time Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Upgrade pip
python -m pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 3. Configure API Keys (Required)

Copy `.env.example` to `.env` and edit it:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` file and add your API keys:

```env
# Google Gemini (for story generation)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# RunPod (for fast GPU synthesis - REQUIRED)
RUNPOD_API_KEY=your_runpod_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
USE_RUNPOD=true
```

**Get your API keys:**
- Google API: https://makersuite.google.com/app/apikey
- RunPod: https://www.runpod.io/console/serverless (see RunPod Setup below)

### 4. Set Up RunPod Endpoint (Required)

See [RunPod Setup Guide](#runpod-serverless-deployment) below for detailed instructions.

---

## Project Structure

```
VoiceClone/
├── run_app.py                   # Main entry point - START HERE
├── check_setup.py               # System verification script
├── .env                         # Your API keys (create from .env.example)
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── .venv/                       # Virtual environment
│
├── src/
│   ├── chatterbox/              # Core Chatterbox TTS engine
│   │   ├── __init__.py
│   │   ├── tts.py               # Text-to-speech implementation
│   │   ├── vc.py                # Voice conversion
│   │   └── models/              # Model implementations
│   │       ├── t3/              # T3 (Text-to-Token) model
│   │       ├── s3gen/           # S3Gen (Speech synthesis) model
│   │       ├── s3tokenizer/     # Speech tokenizer
│   │       ├── tokenizers/      # Text tokenizers
│   │       ├── voice_encoder/   # Voice encoder
│   │       └── utils.py
│   │
│   ├── story_narrator/          # Story generation & narration
│   │   ├── __init__.py
│   │   ├── story_generator.py   # AI story generation (Gemini)
│   │   ├── text_processor.py    # Text chunking & processing
│   │   ├── audio_synthesizer.py # TTS synthesis orchestrator
│   │   ├── narrator.py          # Main narrator orchestrator
│   │   ├── runpod_client.py     # RunPod serverless client
│   │   ├── logger.py            # Logging configuration
│   │   └── cli.py               # Command-line interface
│   │
│   └── ui/
│       ├── __init__.py
│       └── gradio_app.py        # Web interface (Gradio)
│
├── samples/                     # Sample voice audio files
│   └── *.wav                    # Reference voices for cloning
│
├── scripts/                     # Deployment & utility scripts
│   ├── __init__.py
│   └── deploy_runpod.py         # RunPod deployment helper
│
└── src/output/                  # Generated stories & audio (auto-created)
    ├── story_*.wav              # Generated audio files
    └── story_*.txt              # Story text files
```

---

## Features

- AI Story Generation using Google Gemini
- Voice Cloning using Chatterbox TTS
- Emotion Control - make it dramatic or calm
- Multiple Styles - adventure, fantasy, mystery, sci-fi, horror, romance
- Web Interface - easy-to-use Gradio UI
- RunPod Serverless - 100x faster synthesis with cloud GPUs
- Watermarked Audio - Built-in PerTh watermarking for responsible AI

---

## Usage

### Web Interface (Recommended)

```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Run the application
python run_app.py
```

Then configure:
1. **Story Theme**: "A brave mouse becomes a knight"
2. **Style**: Choose adventure, fantasy, mystery, etc.
3. **Tone**: Dramatic, lighthearted, suspenseful, etc.
4. **Length**: Short (500 words), Medium (1000), Long (2000+)
5. **Voice** (optional): Upload a .wav file for voice cloning
6. **Advanced Settings**:
   - **Exaggeration**: How expressive (0.0 = calm, 1.0 = very expressive)
   - **Temperature**: Randomness (0.8 default)
   - **CFG Weight**: Voice similarity (0.5 default)

Click **"Generate & Narrate"** and wait!

### Command Line Interface

```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows

# From project root
python -m story_narrator.cli --theme "A robot discovers emotions" --style adventure --voice samples/test_voice.wav

# Or navigate to src directory first
cd src
python -m story_narrator.cli --theme "A robot discovers emotions" --style adventure --voice ../samples/test_voice.wav
```

---

## RunPod Serverless Deployment

This system uses RunPod cloud GPUs for fast synthesis (reduces generation time from 6-7 hours to just minutes).

### Quick Setup

1. **Create RunPod Account**: https://www.runpod.io/console/serverless

2. **Create New Endpoint**:
   - Name: `chatterbox-tts`
   - Template: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel`
   - Container Disk: 20 GB
   - GPU: NVIDIA A100 (40GB) or RTX 4090 (24GB)

3. **Configure Repository**:
   - Repository URL: `https://github.com/sharathkumar-md/VoiceClone`
   - Branch: `main`
   - Handler: `runpod_handler.handler`

4. **Environment Variables**:
   ```
   GOOGLE_API_KEY=your_google_api_key
   GEMINI_MODEL=gemini-2.0-flash-exp
   ```

5. **GPU Settings**:
   - Min Workers: `0` (saves money when idle)
   - Max Workers: `3`
   - Idle Timeout: `10 seconds`
   - Max Wait Time: `600 seconds`

6. **Get Your Endpoint ID** and add to `.env`:
   ```env
   RUNPOD_API_KEY=your_runpod_api_key
   RUNPOD_ENDPOINT_ID=your_endpoint_id
   ```

### Using the System

RunPod is enabled by default. Just use the system normally:

```python
from story_narrator import StoryNarrator, StoryPrompt

# RunPod is automatically used (reads USE_RUNPOD=true from .env)
narrator = StoryNarrator(llm_provider="gemini")

prompt = StoryPrompt(
    theme="A brave robot on a mission",
    style="adventure",
    tone="lighthearted",
    length="short"
)

result = narrator.create_story_narration(
    story_prompt=prompt,
    voice_sample_path="samples/test_voice.wav",
    output_path="output/my_story.wav"
)
```

**To use local GPU instead** (very slow), set `USE_RUNPOD=false` in `.env`

### Cost Estimation

**Per Story (Short ~500 words):**
- **A100 40GB**: ~$0.50 - $1.00 per story (1-2 minutes)
- **RTX 4090**: ~$0.25 - $0.50 per story (2-3 minutes)
- **RTX 3090**: ~$0.15 - $0.30 per story (3-5 minutes)

**Comparison:**
- RunPod: 1-5 minutes, ~$0.50
- Local RTX 3050: 6-7 hours, free but extremely slow

With `Min Workers = 0`, you only pay when actively generating.

**Cold start:** First request takes ~30-60 seconds to load models, then subsequent chunks are fast.

---

## Example Prompts

- "A lonely robot discovers emotions"
- "A chef who can cook with magic"
- "Time travelers stuck in ancient Rome"
- "A detective cat solves neighborhood mysteries"
- "A dragon who's afraid of heights becomes a pilot"

---

## Troubleshooting

### Error: "GOOGLE_API_KEY not set"
- Edit `.env` file
- Add your API key from https://makersuite.google.com/app/apikey

### Error: "Failed to load model"
- First run downloads models (~2GB) - this is normal
- Make sure you have enough disk space
- GPU recommended but CPU works too (slower)

### Audio not playing
- Check output folder: `src/output/story_*.wav`
- Try downloading the file directly

### RunPod: "Handler not found"
- Verify handler path is exactly: `runpod_handler.handler`
- Check that `runpod_handler.py` exists in repository root

### RunPod: Timeout on first request
- Increase **Max Wait Time** to 600 seconds (10 min)
- First request loads models (~30-60 seconds on A100)
- Subsequent requests are fast (~1-2 min per chunk)

### Virtual Environment Issues
```bash
# If activation fails, recreate the environment
rm -rf .venv  # Linux/Mac
# rmdir /s .venv  # Windows

# Recreate
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## System Verification

Verify your setup is correct before running:

```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows

# Run verification
python check_setup.py
```

This will check:
- Python version and virtual environment
- GPU availability (local - optional)
- All required dependencies (including RunPod)
- .env configuration (Google API + RunPod keys)
- Project modules can be imported
- Sample files and directories exist

---

## Advanced Configuration

### Voice Settings

- **Exaggeration** (0.0-1.0): Controls emotion intensity
  - 0.0 = Calm, neutral delivery
  - 0.5 = Moderate expression (default)
  - 1.0 = Very expressive, dramatic

- **Temperature** (0.0-1.5): Controls randomness
  - Lower = More consistent, predictable
  - Higher = More varied, creative

- **CFG Weight** (0.0-1.0): Voice similarity to reference
  - Lower = Faster speech, less similar
  - Higher = More similar to reference voice

### Tips for Best Results

**General Use (TTS and Voice Agents):**
- Default settings (`exaggeration=0.5`, `cfg_weight=0.5`) work well
- If reference speaker has fast speaking style, lower `cfg_weight` to ~0.3

**Expressive or Dramatic Speech:**
- Try lower `cfg_weight` (~0.3) and increase `exaggeration` to 0.7+
- Higher `exaggeration` speeds up speech; reducing `cfg_weight` helps compensate

---

## Built-in PerTh Watermarking

Every audio file includes [Resemble AI's Perth Watermarker](https://github.com/resemble-ai/perth) - imperceptible neural watermarks for responsible AI.

### Extract Watermark

```python
import perth
import librosa

# Load audio
audio, sr = librosa.load("src/output/story.wav", sr=None)

# Extract watermark
watermarker = perth.PerthImplicitWatermarker()
watermark = watermarker.get_watermark(audio, sample_rate=sr)
print(f"Watermark: {watermark}")  # 0.0 or 1.0
```

---

## About Chatterbox TTS

Chatterbox is Resemble AI's first production-grade open source TTS model (MIT License).

**Key Features:**
- SoTA zero-shot TTS
- 0.5B Llama backbone
- Unique emotion exaggeration control
- Ultra-stable with alignment-informed inference
- Trained on 0.5M hours of cleaned data
- Outperforms ElevenLabs

**Links:**
- [Demo Samples](https://resemble-ai.github.io/chatterbox_demopage/)
- [Hugging Face Space](https://huggingface.co/spaces/ResembleAI/Chatterbox)
- [Discord Community](https://discord.gg/rJq9cRJBJ6)

---

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

---

## License

This project uses Chatterbox TTS which is licensed under MIT License.

---

## Acknowledgements

- [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) by Resemble AI
- [Cosyvoice](https://github.com/FunAudioLLM/CosyVoice)
- [Real-Time-Voice-Cloning](https://github.com/CorentinJ/Real-Time-Voice-Cloning)
- [HiFT-GAN](https://github.com/yl4579/HiFTNet)
- [Llama 3](https://github.com/meta-llama/llama3)
- [S3Tokenizer](https://github.com/xingchensong/S3Tokenizer)

---

## Disclaimer

Don't use this model to do bad things. Use responsibly and ethically.

---

## Support

- Check [GitHub Issues](https://github.com/sharathkumar-md/VoiceClone/issues)
- Join [Discord Community](https://discord.gg/rJq9cRJBJ6)

---

**Enjoy creating stories!**
