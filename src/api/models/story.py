"""
Story API Models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StoryGenerateRequest(BaseModel):
    theme: str = Field(..., min_length=10, description="Story theme or prompt")
    style: str = Field(..., description="Story style (adventure, fantasy, mystery, etc.)")
    tone: str = Field(..., description="Story tone (dramatic, lighthearted, etc.)")
    length: str = Field(..., description="Story length (short, medium, long)")
    additionalDetails: Optional[str] = Field(None, description="Additional story details")


class StoryGenerateResponse(BaseModel):
    story_id: str = Field(..., description="Unique story identifier")
    story_text: str = Field(..., description="Generated story text")
    word_count: int = Field(..., description="Number of words in the story")
    metadata: dict = Field(default_factory=dict, description="Story metadata")


class StoryEditRequest(BaseModel):
    text: str = Field(..., description="Updated story text")


class AIImproveRequest(BaseModel):
    text: str = Field(..., description="Story text to improve")
    improvementType: str = Field(..., description="Type of improvement to apply")
    customInstruction: Optional[str] = Field(None, description="Custom AI instruction")


class AIImproveResponse(BaseModel):
    original: str = Field(..., description="Original story text")
    improved: str = Field(..., description="Improved story text")
    changes_summary: str = Field(..., description="Summary of changes made")


class RepromptRequest(BaseModel):
    story_id: str = Field(..., description="Story ID being reprompted")
    original_text: str = Field(..., description="Original story text")
    instruction: str = Field(..., min_length=5, description="How to modify the story (e.g., 'make it shorter', 'add more action')")


class RepromptResponse(BaseModel):
    story_id: str = Field(..., description="Story ID")
    original_text: str = Field(..., description="Original story text")
    modified_text: str = Field(..., description="AI-modified story text")
    instruction: str = Field(..., description="The instruction that was applied")
    word_count: int = Field(..., description="Word count of modified story")
    created_at: str = Field(..., description="Timestamp of modification")
