#!/usr/bin/env python
"""
CLI interface for Story Narrator system
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path to import story_narrator
sys.path.insert(0, str(Path(__file__).parent.parent))

from story_narrator import StoryNarrator, StoryPrompt
from story_narrator.logger import setup_logger

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="AI-powered Story Narrator - Generate and narrate stories with voice cloning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate and narrate a story:
  python cli.py generate \\
    --theme "A robot's journey home" \\
    --voice my_voice.wav \\
    --output story.wav
  
  # Narrate existing story:
  python cli.py narrate \\
    --text story.txt \\
    --voice my_voice.wav \\
    --output narration.wav
  
  # Use custom parameters:
  python cli.py generate \\
    --theme "Space adventure" \\
    --style sci-fi \\
    --tone dramatic \\
    --length long \\
    --voice voice.wav \\
    --output output.wav \\
    --exaggeration 0.7 \\
    --temperature 0.9
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate a new story and narrate it'
    )
    generate_parser.add_argument(
        '--theme',
        required=True,
        help='Story theme/topic (e.g., "A robot finding its way home")'
    )
    generate_parser.add_argument(
        '--style',
        default='adventure',
        choices=['fantasy','adventure', 'mystery', 'fantasy', 'sci-fi', 'horror', 'romance'],
        help='Story style (default: adventure)'
    )
    generate_parser.add_argument(
        '--tone',
        default='engaging',
        choices=['engaging', 'suspenseful', 'lighthearted', 'dramatic', 'humorous'],
        help='Narrative tone (default: engaging)'
    )
    generate_parser.add_argument(
        '--length',
        default='medium',
        choices=['short', 'medium', 'long'],
        help='Story length: short (~500 words), medium (~1000), long (~2000) (default: medium)'
    )
    generate_parser.add_argument(
        '--audience',
        default='general',
        choices=['children', 'teens', 'adults', 'general'],
        help='Target audience (default: general)'
    )
    generate_parser.add_argument(
        '--details',
        help='Additional story details or requirements'
    )
    
    # Text-only command (generate story without narration)
    text_parser = subparsers.add_parser(
        'text-only',
        help='Generate story text without narration (for testing)'
    )
    text_parser.add_argument(
        '--theme',
        required=True,
        help='Story theme/topic (e.g., "A robot finding its way home")'
    )
    text_parser.add_argument(
        '--style',
        default='adventure',
        choices=['adventure', 'mystery', 'fantasy', 'sci-fi', 'horror', 'romance'],
        help='Story style (default: adventure)'
    )
    text_parser.add_argument(
        '--tone',
        default='engaging',
        choices=['engaging', 'suspenseful', 'lighthearted', 'dramatic', 'humorous'],
        help='Narrative tone (default: engaging)'
    )
    text_parser.add_argument(
        '--length',
        default='medium',
        choices=['short', 'medium', 'long'],
        help='Story length: short (~500 words), medium (~1000), long (~2000) (default: medium)'
    )
    text_parser.add_argument(
        '--audience',
        default='general',
        choices=['children', 'teens', 'adults', 'general'],
        help='Target audience (default: general)'
    )
    text_parser.add_argument(
        '--details',
        help='Additional story details or requirements'
    )
    text_parser.add_argument(
        '--output',
        required=True,
        help='Output path for story text file'
    )
    text_parser.add_argument(
        '--llm-provider',
        default='gemini',
        choices=['gemini', 'openai', 'anthropic', 'local'],
        help='LLM provider for story generation (default: gemini)'
    )
    text_parser.add_argument(
        '--llm-model',
        help='Specific model to use (optional)'
    )
    text_parser.add_argument(
        '--llm-api-key',
        help='API key for the LLM provider (if not in environment)'
    )
    
    # Narrate command
    narrate_parser = subparsers.add_parser(
        'narrate',
        help='Narrate an existing story'
    )
    narrate_parser.add_argument(
        '--text',
        required=True,
        help='Path to text file containing the story'
    )
    
    # Common arguments for both commands
    for p in [generate_parser, narrate_parser]:
        p.add_argument(
            '--voice',
            required=True,
            help='Path to reference voice audio file (.wav)'
        )
        p.add_argument(
            '--output',
            required=True,
            help='Output path for narrated audio'
        )
        p.add_argument(
            '--llm-provider',
            default='gemini',
            choices=['gemini', 'openai', 'anthropic', 'local'],
            help='LLM provider for story generation (default: gemini)'
        )
        p.add_argument(
            '--llm-model',
            help='Specific LLM model to use (optional, uses defaults)'
        )
        p.add_argument(
            '--llm-api-key',
            help='API key for LLM provider (or set GOOGLE_API_KEY/GEMINI_API_KEY/OPENAI_API_KEY/ANTHROPIC_API_KEY env var)'
        )
        p.add_argument(
            '--device',
            default='cuda',
            choices=['auto', 'cuda', 'cpu', 'mps'],
            help='Device for TTS (default: cuda, ignored if --use-runpod is set)'
        )
        p.add_argument(
            '--use-runpod',
            action='store_true',
            help='Use RunPod serverless for 100x faster synthesis (requires RUNPOD_API_KEY in .env)'
        )
        p.add_argument(
            '--exaggeration',
            type=float,
            default=0.5,
            help='Emotion exaggeration (0.0-1.0, default: 0.5)'
        )
        p.add_argument(
            '--temperature',
            type=float,
            default=0.8,
            help='TTS sampling temperature (default: 0.8)'
        )
        p.add_argument(
            '--cfg-weight',
            type=float,
            default=0.5,
            help='Classifier-free guidance weight (default: 0.5)'
        )
        p.add_argument(
            '--format',
            default='wav',
            choices=['wav', 'mp3'],
            help='Output audio format (default: wav)'
        )
        p.add_argument(
            '--no-save-text',
            action='store_true',
            help='Do not save story text to file'
        )
        p.add_argument(
            '--quiet',
            action='store_true',
            help='Suppress progress messages'
        )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Text-only command doesn't need voice file
    if args.command == 'text-only':
        try:
            logger.info("Generating story text...")
            from story_generator import StoryGenerator

            generator = StoryGenerator(
                provider=args.llm_provider,
                api_key=args.llm_api_key,
                model=args.llm_model
            )

            prompt = StoryPrompt(
                theme=args.theme,
                style=args.style,
                tone=args.tone,
                length=args.length,
                target_audience=args.audience,
                additional_details=args.details
            )

            result = generator.generate_story(prompt)

            # Save to file
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result['story'])

            logger.info(f"Story saved to: {args.output}")
            logger.info(f"Word count: {len(result['story'].split())} words")
            logger.info(f"Model used: {result['metadata']['model']}")

        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
        return
    
    # Validate voice file exists for generate/narrate commands
    if not os.path.exists(args.voice):
        logger.error(f"Voice file not found: {args.voice}")
        return

    # Initialize narrator
    try:
        logger.info("Initializing Story Narrator...")
        narrator = StoryNarrator(
            llm_provider=args.llm_provider,
            llm_api_key=args.llm_api_key,
            llm_model=args.llm_model,
            device=args.device,
            use_runpod=args.use_runpod
        )
    except Exception as e:
        logger.error(f"Error initializing narrator: {e}")
        return
    
    # Execute command
    try:
        if args.command == 'generate':
            # Generate new story
            prompt = StoryPrompt(
                theme=args.theme,
                style=args.style,
                tone=args.tone,
                length=args.length,
                target_audience=args.audience,
                additional_details=args.details
            )
            
            result = narrator.create_story_narration(
                story_prompt=prompt,
                voice_sample_path=args.voice,
                output_path=args.output,
                exaggeration=args.exaggeration,
                temperature=args.temperature,
                cfg_weight=args.cfg_weight,
                audio_format=args.format,
                save_story_text=not args.no_save_text,
                show_progress=not args.quiet
            )
        
        elif args.command == 'narrate':
            # Narrate existing story
            if not os.path.exists(args.text):
                logger.error(f"Text file not found: {args.text}")
                return

            with open(args.text, 'r', encoding='utf-8') as f:
                story_text = f.read()

            result = narrator.narrate_existing_story(
                story_text=story_text,
                voice_sample_path=args.voice,
                output_path=args.output,
                exaggeration=args.exaggeration,
                temperature=args.temperature,
                cfg_weight=args.cfg_weight,
                audio_format=args.format,
                show_progress=not args.quiet
            )

        if not args.quiet:
            logger.info("="*60)
            logger.info("SUCCESS!")
            logger.info("="*60)
            logger.info(f"Audio saved to: {result['audio']['output_path']}")
            logger.info(f"Duration: {result['audio']['duration_seconds']:.1f} seconds")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
