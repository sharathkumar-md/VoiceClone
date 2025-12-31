"""
API Models
"""
from .story import StoryGenerateRequest, StoryGenerateResponse, StoryEditRequest, AIImproveRequest, AIImproveResponse
from .tts import TTSGenerateRequest, TTSGenerateResponse, TTSStatusResponse
from .voice import VoiceUploadResponse, VoiceLibraryResponse

__all__ = [
    'StoryGenerateRequest',
    'StoryGenerateResponse',
    'StoryEditRequest',
    'AIImproveRequest',
    'AIImproveResponse',
    'TTSGenerateRequest',
    'TTSGenerateResponse',
    'TTSStatusResponse',
    'VoiceUploadResponse',
    'VoiceLibraryResponse',
]
