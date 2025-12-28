"""
System Check Script - Verify Chatterbox Story Narrator Setup
Run this script to verify everything is working correctly
"""
import sys
import os
from pathlib import Path
import logging

# Configure logging for check_setup - simple format without timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_header(text):
    """Print a formatted header"""
    logger.info("\n" + "=" * 60)
    logger.info(f"  {text}")
    logger.info("=" * 60)

def print_check(name, status, message=""):
    """Print a check result"""
    symbol = "[PASS]" if status else "[FAIL]"
    status_text = "OK" if status else "ERROR"

    logger.info(f"{symbol} {name:40} {status_text}")
    if message:
        logger.info(f"       -> {message}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 10
    print_check(
        "Python Version (3.10+)",
        is_valid,
        f"Current: {version.major}.{version.minor}.{version.micro}"
    )
    return is_valid

def check_virtual_env():
    """Check if running in virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    venv_path = sys.prefix if in_venv else "Not in virtual environment"
    print_check("Virtual Environment", in_venv, venv_path)
    return in_venv

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(__file__).parent / ".env"
    exists = env_path.exists()

    if exists:
        from dotenv import load_dotenv
        load_dotenv()

        google_key = os.getenv("GOOGLE_API_KEY")
        has_google = google_key and google_key != "your_google_api_key_here"

        print_check(".env File Exists", True)
        print_check("  GOOGLE_API_KEY Set", has_google, "Required for story generation")

        # Required RunPod keys
        runpod_key = os.getenv("RUNPOD_API_KEY")
        runpod_endpoint = os.getenv("RUNPOD_ENDPOINT_ID")
        has_runpod = runpod_key and runpod_endpoint and runpod_key != "your_runpod_api_key_here"
        print_check("  RUNPOD_API_KEY Set", has_runpod, "Required for fast synthesis")
        print_check("  RUNPOD_ENDPOINT_ID Set", has_runpod, "Required for fast synthesis")

        return has_google and has_runpod
    else:
        print_check(".env File Exists", False, "Copy .env.example to .env and configure")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'torch': 'PyTorch',
        'torchaudio': 'TorchAudio',
        'transformers': 'Transformers',
        'librosa': 'Librosa',
        'gradio': 'Gradio',
        'google.generativeai': 'Google Generative AI',
        'dotenv': 'Python Dotenv',
        'runpod': 'RunPod',
    }

    all_installed = True
    for package, name in required_packages.items():
        try:
            __import__(package)
            print_check(f"  {name}", True)
        except ImportError:
            print_check(f"  {name}", False, "REQUIRED - run: pip install -r requirements.txt")
            all_installed = False

    return all_installed

def check_imports():
    """Check if project modules can be imported"""
    modules = {
        'chatterbox.tts': 'Chatterbox TTS',
        'story_narrator': 'Story Narrator',
        'story_narrator.audio_synthesizer': 'Audio Synthesizer',
        'story_narrator.narrator': 'Narrator',
        'story_narrator.story_generator': 'Story Generator',
    }

    all_imported = True
    for module, name in modules.items():
        try:
            __import__(module)
            print_check(f"  {name}", True)
        except Exception as e:
            print_check(f"  {name}", False, f"Error: {str(e)[:50]}")
            all_imported = False

    return all_imported

def check_gpu():
    """Check GPU availability"""
    try:
        import torch
        cuda_available = torch.cuda.is_available()

        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print_check("GPU (CUDA) Available", True, f"{gpu_name} ({gpu_memory:.1f} GB)")
        else:
            print_check("GPU (CUDA) Available", False, "Will use CPU (slower)")

        return cuda_available
    except Exception as e:
        print_check("GPU Check", False, str(e))
        return False

def check_sample_files():
    """Check if sample audio files exist"""
    samples_dir = Path(__file__).parent / "samples"

    if not samples_dir.exists():
        print_check("Samples Directory", False, "samples/ directory not found")
        return False

    files = list(samples_dir.glob("*.wav"))
    has_samples = len(files) > 0

    print_check("Sample Audio Files", has_samples, f"Found {len(files)} .wav files" if has_samples else "No .wav files in samples/")

    if has_samples:
        for f in files:
            logger.info(f"    - {f.name}")

    return has_samples

def check_output_directory():
    """Check/create output directory"""
    output_dir = Path(__file__).parent / "src" / "output"

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print_check("Output Directory", True, "Created src/output/")
    else:
        print_check("Output Directory", True, "src/output/ exists")

    return True

def run_quick_test():
    """Run a quick functionality test"""
    try:
        from story_narrator import StoryPrompt

        # Just test object creation
        prompt = StoryPrompt(
            theme="Test story",
            style="adventure",
            tone="lighthearted",
            length="short"
        )

        print_check("StoryPrompt Creation", True, "Can create story prompts")
        return True
    except Exception as e:
        print_check("StoryPrompt Creation", False, str(e))
        return False

def main():
    """Main check function"""
    print_header("CHATTERBOX STORY NARRATOR - SYSTEM CHECK")

    results = {}

    # System checks
    print_header("1. System Environment")
    results['python'] = check_python_version()
    results['venv'] = check_virtual_env()
    results['gpu'] = check_gpu()

    # Configuration checks
    print_header("2. Configuration")
    results['env'] = check_env_file()

    # Dependencies
    print_header("3. Python Dependencies")
    results['deps'] = check_dependencies()

    # Project imports
    print_header("4. Project Modules")
    results['imports'] = check_imports()

    # Files
    print_header("5. Project Files")
    results['samples'] = check_sample_files()
    results['output'] = check_output_directory()

    # Quick test
    print_header("6. Functionality Test")
    results['test'] = run_quick_test()

    # Summary
    print_header("SUMMARY")

    critical_checks = ['python', 'env', 'deps', 'imports']
    critical_passed = all(results.get(k, False) for k in critical_checks)

    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)

    logger.info(f"\nPassed: {passed_checks}/{total_checks} checks")

    if critical_passed:
        logger.info("\n[SUCCESS] System is ready! You can run:")
        logger.info("  python run_app.py")
        logger.info("\nThen open: http://localhost:7860")
        logger.info("\nMode: RunPod Serverless (100x faster than local GPU)")

        if not results.get('gpu', False):
            logger.info("\n[INFO] No local GPU detected - using RunPod cloud GPU")

        if not results.get('samples', False):
            logger.info("\n[WARNING] No sample voice files found")
            logger.info("  Add .wav files to samples/ directory for voice cloning")

        return 0
    else:
        logger.error("\n[ERROR] System check failed! Please fix the issues above.")
        logger.info("\nCommon fixes:")
        logger.info("  1. Activate virtual environment: source .venv/Scripts/activate")
        logger.info("  2. Install dependencies: pip install -r requirements.txt")
        logger.info("  3. Configure .env file:")
        logger.info("     - Copy .env.example to .env")
        logger.info("     - Add GOOGLE_API_KEY from https://makersuite.google.com/app/apikey")
        logger.info("     - Add RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID from https://www.runpod.io")
        logger.info("     - See README.md for RunPod setup instructions")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n\nCheck interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
