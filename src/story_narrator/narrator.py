"""
Story Narrator - Main orchestrator for the complete story narration pipeline
"""

from typing import Dict, Optional, List
from pathlib import Path
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from .logger import setup_logger

from .story_generator import StoryGenerator, StoryPrompt
from .text_processor import TextProcessor
from .audio_synthesizer import AudioSynthesizer

# Load environment variables
load_dotenv()
logger = setup_logger(__name__)


class StoryNarrator:
    """
    Complete story narration system:
    1. Generate story from prompt using LLM
    2. Process text for TTS
    3. Synthesize with voice cloning
    4. Export final audio
    """
    
    def __init__(
        self,
        llm_provider: str = "gemini",
        llm_api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
        device: str = "cuda",
        use_runpod: Optional[bool] = None,
        max_chunk_length: int = 500,
        paragraph_pause: float = 1.0,
        sentence_pause: float = 0.3,
    ):
        """
        Initialize Story Narrator system
        
        Args:
            llm_provider: LLM provider ('gemini', 'openai', 'anthropic', 'local')
            llm_api_key: API key for LLM provider
            llm_model: Model name (uses defaults if not provided)
            device: Device for TTS ('cuda', 'cpu', 'mps', 'auto')
            use_runpod: If True, use RunPod serverless for 100x faster synthesis
            max_chunk_length: Max characters per TTS chunk
            paragraph_pause: Pause between paragraphs (seconds)
            sentence_pause: Pause between sentences (seconds)
        """
        logger.info("Initializing Story Narrator system...")

        # Determine if we should use RunPod
        # Priority: explicit parameter > environment variable > default (True)
        if use_runpod is None:
            use_runpod_env = os.getenv("USE_RUNPOD", "true").lower()
            self.use_runpod = use_runpod_env in ("true", "1", "yes")
        else:
            self.use_runpod = use_runpod

        if self.use_runpod:
            logger.info("Using RunPod serverless for 100x faster synthesis!")
        else:
            logger.warning(f"Using local {device} (slow) - consider enabling RunPod")
        
        # Initialize components
        self.story_generator = StoryGenerator(
            provider=llm_provider,
            api_key=llm_api_key,
            model=llm_model
        )
        
        self.text_processor = TextProcessor(
            max_chunk_length=max_chunk_length,
            paragraph_pause=paragraph_pause,
            sentence_pause=sentence_pause
        )

        self.audio_synthesizer = AudioSynthesizer(
            device=device,
            use_runpod=self.use_runpod
        )

        logger.info("Story Narrator initialized successfully")
    
    def create_story_narration(
        self,
        story_prompt: StoryPrompt,
        voice_sample_path: str,
        output_path: str,
        exaggeration: float = 0.5,
        temperature: float = 0.8,
        cfg_weight: float = 0.5,
        audio_format: str = "wav",
        save_story_text: bool = True,
        show_progress: bool = True
    ) -> Dict:
        """
        Complete pipeline: Generate story and create narration
        
        Args:
            story_prompt: StoryPrompt object with generation parameters
            voice_sample_path: Path to reference voice audio file
            output_path: Output path for narrated audio
            exaggeration: Emotion exaggeration (0.0-1.0)
            temperature: TTS sampling temperature
            cfg_weight: Classifier-free guidance weight
            audio_format: Output audio format
            save_story_text: Save story text to file
            show_progress: Show progress updates
            
        Returns:
            Dictionary with complete narration metadata
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Step 1: Generate story
        if show_progress:
            logger.info("="*60)
            logger.info("STEP 1: Generating story with LLM...")
            logger.info("="*60)

        story_result = self.story_generator.generate_story(story_prompt)
        story_text = story_result["story"]

        if show_progress:
            logger.info(f"Story generated ({len(story_text.split())} words)")
            logger.info(f"Story preview: {story_text[:200]}...")
        
        # Save story text if requested
        if save_story_text:
            text_output_path = str(Path(output_path).with_suffix('.txt'))
            with open(text_output_path, 'w', encoding='utf-8') as f:
                f.write(story_text)
            if show_progress:
                logger.info(f"Story text saved to {text_output_path}")

        # Step 2: Process text
        if show_progress:
            logger.info("="*60)
            logger.info("STEP 2: Processing text for TTS...")
            logger.info("="*60)

        processed = self.text_processor.process_story(story_text)
        chunks = processed["chunks"]
        text_list = [c.text for c in chunks]
        pause_list = [c.pause_after for c in chunks]

        if show_progress:
            logger.info(f"Text processed into {len(chunks)} chunks")
            logger.info(f"Estimated duration: {processed['metadata']['estimated_duration_seconds']:.1f}s")

        # Step 3: Load voice and synthesize
        if show_progress:
            logger.info("="*60)
            logger.info("STEP 3: Synthesizing narration with voice cloning...")
            logger.info("="*60)
        
        # Set voice
        self.audio_synthesizer.set_voice(voice_sample_path, exaggeration)
        
        # Update TTS parameters
        self.audio_synthesizer.temperature = temperature
        self.audio_synthesizer.cfg_weight = cfg_weight
        
        # Synthesize and save
        audio_result = self.audio_synthesizer.synthesize_and_save(
            text_chunks=text_list,
            output_path=output_path,
            pause_durations=pause_list,
            format=audio_format,
            show_progress=show_progress
        )
        
        # Step 4: Compile results
        if show_progress:
            logger.info("="*60)
            logger.info("NARRATION COMPLETE!")
            logger.info("="*60)
            logger.info(f"Audio file: {audio_result['output_path']}")
            logger.info(f"Duration: {audio_result['duration_seconds']:.1f}s")
            logger.info(f"Chunks synthesized: {audio_result['num_chunks']}")
        
        # Create complete metadata
        metadata = {
            "timestamp": timestamp,
            "story": {
                "prompt": story_prompt.to_dict(),
                "text": story_text,
                "word_count": len(story_text.split()),
                "llm_metadata": story_result["metadata"]
            },
            "processing": {
                "chunks": len(chunks),
                "total_characters": processed['metadata']['total_characters'],
                "estimated_duration": processed['metadata']['estimated_duration_seconds']
            },
            "audio": {
                "output_path": audio_result['output_path'],
                "duration_seconds": audio_result['duration_seconds'],
                "sample_rate": audio_result['sample_rate'],
                "voice_sample": voice_sample_path,
                "exaggeration": exaggeration,
                "temperature": temperature,
                "cfg_weight": cfg_weight
            }
        }
        
        # Save metadata
        metadata_path = str(Path(output_path).with_suffix('.json'))
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        if show_progress:
            logger.info(f"Metadata saved to {metadata_path}")
        
        return metadata
    
    def narrate_from_simple_prompt(
        self,
        theme: str,
        voice_sample_path: str,
        output_path: str,
        style: str = "adventure",
        tone: str = "engaging",
        length: str = "medium",
        **kwargs
    ) -> Dict:
        """
        Convenience method for simple story narration
        
        Args:
            theme: Story theme/topic
            voice_sample_path: Reference voice audio file
            output_path: Output audio path
            style: Story style
            tone: Narrative tone
            length: Story length ('short', 'medium', 'long')
            **kwargs: Additional parameters for create_story_narration
            
        Returns:
            Narration metadata
        """
        prompt = StoryPrompt(
            theme=theme,
            style=style,
            tone=tone,
            length=length
        )
        
        return self.create_story_narration(
            story_prompt=prompt,
            voice_sample_path=voice_sample_path,
            output_path=output_path,
            **kwargs
        )
    
    def narrate_existing_story(
        self,
        story_text: str,
        voice_sample_path: str,
        output_path: str,
        exaggeration: float = 0.5,
        temperature: float = 0.8,
        cfg_weight: float = 0.5,
        audio_format: str = "wav",
        show_progress: bool = True
    ) -> Dict:
        """
        Narrate an existing story (skip LLM generation)
        
        Args:
            story_text: Pre-written story text
            voice_sample_path: Reference voice audio file
            output_path: Output audio path
            exaggeration: Emotion exaggeration
            temperature: TTS temperature
            cfg_weight: CFG weight
            audio_format: Output format
            show_progress: Show progress
            
        Returns:
            Narration metadata
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if show_progress:
            logger.info("="*60)
            logger.info("Narrating existing story...")
            logger.info("="*60)

        # Process text
        processed = self.text_processor.process_story(story_text)
        chunks = processed["chunks"]
        text_list = [c.text for c in chunks]
        pause_list = [c.pause_after for c in chunks]

        if show_progress:
            logger.info(f"Text processed into {len(chunks)} chunks")
        
        # Load voice and synthesize
        self.audio_synthesizer.set_voice(voice_sample_path, exaggeration)
        self.audio_synthesizer.temperature = temperature
        self.audio_synthesizer.cfg_weight = cfg_weight
        
        audio_result = self.audio_synthesizer.synthesize_and_save(
            text_chunks=text_list,
            output_path=output_path,
            pause_durations=pause_list,
            format=audio_format,
            show_progress=show_progress
        )
        
        metadata = {
            "timestamp": timestamp,
            "story": {
                "text": story_text,
                "word_count": len(story_text.split()),
                "source": "existing_text"
            },
            "processing": processed['metadata'],
            "audio": {
                "output_path": audio_result['output_path'],
                "duration_seconds": audio_result['duration_seconds'],
                "sample_rate": audio_result['sample_rate'],
                "voice_sample": voice_sample_path
            }
        }
        
        return metadata


# Example usage
if __name__ == "__main__":
    # Initialize narrator (requires GOOGLE_API_KEY or GEMINI_API_KEY environment variable)
    narrator = StoryNarrator(
        llm_provider="gemini",
        device="cuda"  # or "cpu"
    )
    
    # Create narration from prompt
    # result = narrator.narrate_from_simple_prompt(
    #     theme="A lost robot finding its way home in a futuristic city",
    #     voice_sample_path="path/to/reference_voice.wav",
    #     output_path="my_story_narration.wav",
    #     style="sci-fi",
    #     tone="hopeful",
    #     length="short"
    # )

    logger.info("Story Narrator ready!")
