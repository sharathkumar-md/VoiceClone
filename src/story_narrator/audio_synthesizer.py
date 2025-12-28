"""
Audio Synthesizer Module - Converts text to speech using Chatterbox TTS
"""

import torch
import torchaudio
from typing import List, Optional, Dict
import os
from .logger import setup_logger

# Import from the chatterbox package
from chatterbox.tts import ChatterboxTTS

# Import RunPod client
try:
    from .runpod_client import RunPodTTSClient
    RUNPOD_AVAILABLE = True
except ImportError:
    RUNPOD_AVAILABLE = False

logger = setup_logger(__name__)


class AudioSynthesizer:
    """
    Handles text-to-speech synthesis using Chatterbox TTS (local or RunPod)
    """
    
    def __init__(
        self,
        device: str = "cuda",
        voice_sample_path: Optional[str] = None,
        exaggeration: float = 0.3,
        temperature: float = 0.6,
        cfg_weight: float = 0.3,
        use_runpod: bool = False,
    ):
        """
        Initialize audio synthesizer
        
        Args:
            device: Device to run TTS on ('cuda', 'cpu', 'mps', or 'auto')
            voice_sample_path: Path to reference voice audio file
            exaggeration: Emotion exaggeration control (0.0 to 1.0)
            temperature: Sampling temperature
            cfg_weight: Classifier-free guidance weight
            use_runpod: If True, use RunPod serverless for faster synthesis
        """
        self.use_runpod = use_runpod
        self.exaggeration = exaggeration
        self.temperature = temperature
        self.cfg_weight = cfg_weight
        self.sr = 24000  # Default sample rate
        
        if use_runpod:
            if not RUNPOD_AVAILABLE:
                raise ImportError("RunPod client not available. Install runpod package.")
            logger.info("Using RunPod serverless for synthesis (100x faster!)")
            self.runpod_client = RunPodTTSClient()
            self.tts_model = None
            self.device = "runpod"
        else:
            # Determine device for local synthesis
            if device == "auto":
                if torch.cuda.is_available():
                    device = "cuda"
                elif torch.backends.mps.is_available():
                    device = "mps"
                else:
                    device = "cpu"

            self.device = device

            # Initialize Chatterbox TTS model
            logger.info(f"Loading Chatterbox TTS model on {device}...")
            self.tts_model = ChatterboxTTS.from_pretrained(device=device)
            self.sr = self.tts_model.sr
            logger.info("Model loaded successfully")
            self.runpod_client = None
        
        # Load voice sample if provided
        self.voice_sample_path = None
        if voice_sample_path:
            self.set_voice(voice_sample_path, exaggeration)
    
    def set_voice(self, voice_sample_path: str, exaggeration: float = None):
        """
        Set the reference voice for cloning
        
        Args:
            voice_sample_path: Path to reference voice audio file (.wav)
            exaggeration: Override exaggeration setting
        """
        if not os.path.exists(voice_sample_path):
            raise FileNotFoundError(f"Voice sample not found: {voice_sample_path}")
        
        self.voice_sample_path = voice_sample_path
        
        if exaggeration is not None:
            self.exaggeration = exaggeration
        
        if self.use_runpod:
            logger.info(f"Voice sample set: {voice_sample_path} (will be sent to RunPod)")
        else:
            logger.info(f"Preparing voice conditionals from {voice_sample_path}...")
            self.tts_model.prepare_conditionals(
                voice_sample_path,
                exaggeration=self.exaggeration
            )
            logger.info("Voice loaded successfully")
    
    def synthesize_text(
        self,
        text: str,
        temperature: Optional[float] = None,
        cfg_weight: Optional[float] = None,
    ) -> torch.Tensor:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            temperature: Override temperature setting
            cfg_weight: Override cfg_weight setting
            
        Returns:
            Audio tensor
        """
        if self.voice_sample_path is None:
            raise ValueError("No voice sample loaded. Call set_voice() first.")
        
        temp = temperature if temperature is not None else self.temperature
        cfg = cfg_weight if cfg_weight is not None else self.cfg_weight
        
        if self.use_runpod:
            # Use RunPod for synthesis
            audio_bytes = self.runpod_client.synthesize_text(
                text=text,
                voice_sample_path=self.voice_sample_path,
                exaggeration=self.exaggeration,
                temperature=temp,
                cfg_weight=cfg
            )
            
            # Convert bytes to tensor
            import io
            buffer = io.BytesIO(audio_bytes)
            wav, _ = torchaudio.load(buffer)
            return wav
        else:
            # Generate audio locally
            wav = self.tts_model.generate(
                text,
                temperature=temp,
                cfg_weight=cfg,
            )
            return wav
    
    def synthesize_chunks(
        self,
        text_chunks: List[str],
        pause_durations: Optional[List[float]] = None,
        show_progress: bool = True
    ) -> List[torch.Tensor]:
        """
        Synthesize multiple text chunks
        
        Args:
            text_chunks: List of text strings to synthesize
            pause_durations: List of pause durations after each chunk (seconds)
            show_progress: Show progress during synthesis
            
        Returns:
            List of audio tensors
        """
        if self.voice_sample_path is None:
            raise ValueError("No voice sample loaded. Call set_voice() first.")
        
        audio_segments = []
        
        if pause_durations is None:
            pause_durations = [0.0] * len(text_chunks)
        
        for idx, (text, pause) in enumerate(zip(text_chunks, pause_durations)):
            if show_progress:
                logger.info(f"Synthesizing chunk {idx + 1}/{len(text_chunks)}...")

            # Generate audio for this chunk
            wav = self.synthesize_text(text)
            audio_segments.append(wav)
            
            # Add pause if needed
            if pause > 0:
                pause_samples = int(pause * self.sr)
                silence = torch.zeros(1, pause_samples)
                audio_segments.append(silence)
        
        return audio_segments
    
    def concatenate_audio(self, audio_segments: List[torch.Tensor]) -> torch.Tensor:
        """
        Concatenate multiple audio segments
        
        Args:
            audio_segments: List of audio tensors
            
        Returns:
            Single concatenated audio tensor
        """
        # Ensure all tensors are on CPU and have same shape
        audio_segments = [seg.cpu() for seg in audio_segments]
        
        # Concatenate along time dimension
        full_audio = torch.cat(audio_segments, dim=-1)
        
        return full_audio
    
    def save_audio(
        self,
        audio: torch.Tensor,
        output_path: str,
        format: str = "wav"
    ):
        """
        Save audio to file
        
        Args:
            audio: Audio tensor
            output_path: Output file path
            format: Audio format ('wav', 'mp3', etc.)
        """
        # Ensure audio is on CPU
        audio = audio.cpu()

        # Save using torchaudio
        torchaudio.save(
            output_path,
            audio,
            self.sr,
            format=format
        )
        logger.info(f"Audio saved to {output_path}")
    
    def synthesize_and_save(
        self,
        text_chunks: List[str],
        output_path: str,
        pause_durations: Optional[List[float]] = None,
        format: str = "wav",
        show_progress: bool = True
    ) -> Dict:
        """
        Complete synthesis pipeline: chunks to audio to save
        
        Args:
            text_chunks: List of text strings
            output_path: Output file path
            pause_durations: Pause durations after each chunk
            format: Output audio format
            show_progress: Show progress
            
        Returns:
            Dictionary with synthesis metadata
        """
        logger.info(f"Synthesizing {len(text_chunks)} chunks...")

        # Synthesize all chunks
        audio_segments = self.synthesize_chunks(
            text_chunks,
            pause_durations,
            show_progress
        )

        logger.info("Concatenating audio...")
        full_audio = self.concatenate_audio(audio_segments)

        # Calculate duration
        duration_seconds = full_audio.shape[-1] / self.sr

        logger.info(f"Saving audio (duration: {duration_seconds:.1f}s)...")
        self.save_audio(full_audio, output_path, format)
        
        return {
            "output_path": output_path,
            "duration_seconds": duration_seconds,
            "sample_rate": self.sr,
            "num_chunks": len(text_chunks),
            "total_samples": full_audio.shape[-1]
        }


# Example usage
if __name__ == "__main__":
    # Example: Synthesize a simple story
    synthesizer = AudioSynthesizer(device="cuda")
    
    # Set voice sample (you need a reference voice file)
    # synthesizer.set_voice("path/to/reference_voice.wav")
    
    # Example text chunks
    text_chunks = [
        "Once upon a time, in a distant galaxy, there lived a brave robot named Zip.",
        "Zip had lost its way home during a cosmic storm.",
        "But with courage and determination, Zip embarked on an incredible journey."
    ]
    
    # Synthesize and save
    # result = synthesizer.synthesize_and_save(
    #     text_chunks,
    #     output_path="story_narration.wav",
    #     pause_durations=[1.0, 1.0, 1.0]  # 1 second pause after each chunk
    # )

    logger.info("Example setup complete!")
