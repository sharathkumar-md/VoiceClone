"""
Database Models
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json


@dataclass
class Story:
    """Story database model"""
    id: str
    title: str
    text: str
    theme: str
    style: str
    tone: str
    length: str
    word_count: int
    thumbnail_color: str
    preview_text: str
    created_at: str
    updated_at: str
    audio_url: Optional[str] = None
    metadata: Optional[dict] = None

    @classmethod
    def from_db_row(cls, row):
        """Create Story from database row"""
        return cls(
            id=row['id'],
            title=row['title'] or '',
            text=row['text'],
            theme=row['theme'],
            style=row['style'],
            tone=row['tone'],
            length=row['length'],
            word_count=row['word_count'],
            thumbnail_color=row['thumbnail_color'] or '',
            preview_text=row['preview_text'] or '',
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            audio_url=row['audio_url'],
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'theme': self.theme,
            'style': self.style,
            'tone': self.tone,
            'length': self.length,
            'word_count': self.word_count,
            'thumbnail_color': self.thumbnail_color,
            'preview_text': self.preview_text,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'audio_url': self.audio_url,
            'metadata': self.metadata
        }
