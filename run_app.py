#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple launcher for the Story Narrator web interface
"""
import os
import sys
from pathlib import Path
import logging

# Configure simple logging for launcher
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add src to path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

def check_env():
    """Check if environment is set up correctly"""
    env_file = ROOT / ".env"
    if not env_file.exists():
        logger.warning("WARNING: .env file not found!")
        logger.info("Creating from .env.example...")

        example_file = ROOT / ".env.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            logger.info("[OK] Created .env file")
            logger.info("IMPORTANT: Edit .env and add your GOOGLE_API_KEY!")
            logger.info(f"File location: {env_file}")
            return False

    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        logger.error("ERROR: GOOGLE_API_KEY not set in .env file!")
        logger.info(f"Please edit: {env_file}")
        logger.info("Get your API key from: https://makersuite.google.com/app/apikey")
        return False

    logger.info("[OK] Environment check passed!")
    return True

def main():
    logger.info("=" * 60)
    logger.info("STORY NARRATOR - Web Interface")
    logger.info("=" * 60)
    logger.info("")

    # Check environment
    if not check_env():
        logger.info("\nPlease fix the issues above and run again.")
        return

    logger.info("\nLoading application...")

    # Import and launch Gradio app
    from ui.gradio_app import demo

    logger.info("\nStarting web server...")
    logger.info("\nOpen your browser to:")
    logger.info("   -> http://localhost:7860")
    logger.info("\nPress Ctrl+C to stop the server\n")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nShutting down...")
    except Exception as e:
        logger.error(f"\nError: {e}")
        import traceback
        traceback.print_exc()
