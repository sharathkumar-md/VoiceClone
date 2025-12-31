"""
TTS API Models
"""
from pydantic import BaseModel, Field
from typing import Optional


class TTSGenerateRequest(BaseModel):
    storyId: str = Field(..., description="Story ID")
    text: str = Field(..., description="Text to synthesize")
    voiceSample: Optional[str] = Field(None, description="Base64 encoded voice sample")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Playback speed")
    exaggeration: float = Field(0.3, ge=0.0, le=1.0, description="Voice exaggeration (Gradio default: 0.3)")
    temperature: float = Field(0.6, ge=0.0, le=1.5, description="Generation temperature (Gradio default: 0.6)")
    cfgWeight: float = Field(0.3, ge=0.0, le=1.0, description="CFG weight (Gradio default: 0.3)")


class TTSGenerateResponse(BaseModel):
    task_id: str = Field(..., description="Task ID for tracking generation")
    message: str = Field(default="Audio generation started", description="Status message")


class TTSStatusResponse(BaseModel):
    status: str = Field(..., description="Task status (processing, completed, failed)")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage")
    estimated_time: Optional[int] = Field(None, description="Estimated time remaining in seconds")
    audio_url: Optional[str] = Field(None, description="URL to generated audio file")
    error: Optional[str] = Field(None, description="Error message if failed")
