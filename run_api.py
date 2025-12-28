#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher for the VoiceClone FastAPI backend
"""
import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Fix Windows console encoding
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

    # Load environment
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
    logger.info("VOICECLONE - FastAPI Backend")
    logger.info("=" * 60)
    logger.info("")

    # Check environment
    if not check_env():
        logger.info("\nPlease fix the issues above and run again.")
        return

    logger.info("\nStarting API server...")
    logger.info("\nAPI will be available at:")
    logger.info("   -> http://localhost:8000")
    logger.info("\nAPI documentation at:")
    logger.info("   -> http://localhost:8000/docs")
    logger.info("\nMake sure frontend is running at:")
    logger.info("   -> http://localhost:3000")
    logger.info("\nPress Ctrl+C to stop the server\n")

    # Import and run
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
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
