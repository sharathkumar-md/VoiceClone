"""
Text Processor Module - Prepares story text for TTS synthesis
"""

import re
from typing import List, Dict
from dataclasses import dataclass
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class TextChunk:
    """Represents a chunk of text for TTS processing"""
    text: str
    chunk_id: int
    is_paragraph_end: bool = False
    pause_after: float = 0.0  # Pause duration in seconds after this chunk


class TextProcessor:
    """
    Processes story text for optimal TTS synthesis
    - Splits long text into manageable chunks
    - Cleans and normalizes text
    - Adds appropriate pauses
    """
    
    def __init__(
        self,
        max_chunk_length: int = 500,  # Max characters per chunk
        paragraph_pause: float = 1.0,  # Pause between paragraphs (seconds)
        sentence_pause: float = 0.3,   # Pause between sentences (seconds)
    ):
        """
        Initialize text processor
        
        Args:
            max_chunk_length: Maximum characters per TTS chunk
            paragraph_pause: Pause duration after paragraphs
            sentence_pause: Pause duration after sentences
        """
        self.max_chunk_length = max_chunk_length
        self.paragraph_pause = paragraph_pause
        self.sentence_pause = sentence_pause
    
    def clean_text(self, text: str) -> str:
        """
        Clean text for TTS processing
        
        Args:
            text: Raw story text
            
        Returns:
            Cleaned text
        """
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix common punctuation issues
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', text)  # Add space after punctuation
        
        # Remove markdown formatting that might interfere with TTS
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
        text = re.sub(r'__([^_]+)__', r'\1', text)  # Underline
        
        # Convert numbers to words for better TTS (optional - can be expanded)
        # This is a simple version, can be enhanced with num2words library
        
        return text.strip()
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs
        
        Args:
            text: Story text
            
        Returns:
            List of paragraphs
        """
        # Split on double newlines or more
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Clean each paragraph
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Paragraph text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with spaCy or NLTK)
        # Handles common abbreviations
        text = re.sub(r'(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|etc|vs|i\.e|e\.g)\.', r'\1<DOT>', text)
        
        # Split on sentence endings
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Restore dots in abbreviations
        sentences = [s.replace('<DOT>', '.').strip() for s in sentences if s.strip()]
        
        return sentences
    
    def create_chunks(self, text: str) -> List[TextChunk]:
        """
        Create optimized chunks for TTS processing
        
        Args:
            text: Story text
            
        Returns:
            List of TextChunk objects
        """
        # Clean text first
        text = self.clean_text(text)
        
        # Split into paragraphs
        paragraphs = self.split_into_paragraphs(text)
        
        chunks = []
        chunk_id = 0
        
        for para_idx, paragraph in enumerate(paragraphs):
            # If paragraph is short enough, keep it as one chunk
            if len(paragraph) <= self.max_chunk_length:
                chunks.append(TextChunk(
                    text=paragraph,
                    chunk_id=chunk_id,
                    is_paragraph_end=True,
                    pause_after=self.paragraph_pause
                ))
                chunk_id += 1
            else:
                # Split long paragraphs into sentences
                sentences = self.split_into_sentences(paragraph)
                
                current_chunk = ""
                for sent_idx, sentence in enumerate(sentences):
                    # If adding this sentence exceeds max length, save current chunk
                    if len(current_chunk) + len(sentence) + 1 > self.max_chunk_length and current_chunk:
                        is_last_in_para = sent_idx == len(sentences)
                        chunks.append(TextChunk(
                            text=current_chunk.strip(),
                            chunk_id=chunk_id,
                            is_paragraph_end=False,
                            pause_after=self.sentence_pause
                        ))
                        chunk_id += 1
                        current_chunk = sentence
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
                
                # Add remaining text
                if current_chunk:
                    chunks.append(TextChunk(
                        text=current_chunk.strip(),
                        chunk_id=chunk_id,
                        is_paragraph_end=True,
                        pause_after=self.paragraph_pause
                    ))
                    chunk_id += 1
        
        return chunks
    
    def process_story(self, story_text: str) -> Dict:
        """
        Process complete story text
        
        Args:
            story_text: Raw story text
            
        Returns:
            Dictionary with processed chunks and metadata
        """
        chunks = self.create_chunks(story_text)
        
        return {
            "chunks": chunks,
            "metadata": {
                "total_chunks": len(chunks),
                "total_characters": sum(len(c.text) for c in chunks),
                "total_words": sum(len(c.text.split()) for c in chunks),
                "estimated_duration_seconds": self._estimate_duration(chunks)
            }
        }
    
    def _estimate_duration(self, chunks: List[TextChunk]) -> float:
        """
        Estimate total audio duration based on text
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Estimated duration in seconds
        """
        # Average speaking rate: ~150 words per minute = 2.5 words per second
        words_per_second = 2.5
        
        total_words = sum(len(c.text.split()) for c in chunks)
        speech_time = total_words / words_per_second
        
        # Add pause times
        pause_time = sum(c.pause_after for c in chunks)
        
        return speech_time + pause_time
    
    def chunks_to_text_list(self, chunks: List[TextChunk]) -> List[str]:
        """
        Convert chunks to simple list of text strings
        
        Args:
            chunks: List of TextChunk objects
            
        Returns:
            List of text strings
        """
        return [chunk.text for chunk in chunks]


# Example usage
if __name__ == "__main__":
    sample_story = """
    Once upon a time, in a bustling futuristic city, there lived a small robot named Zip. 
    Zip had been separated from its family during a power surge that swept through the city's main hub.
    
    Now alone and confused, Zip wandered through the neon-lit streets, searching for familiar landmarks. 
    The towering skyscrapers seemed endless, and the flying vehicles whizzed by without noticing the little robot below.
    
    But Zip didn't give up. With determination in its circuits, it began to follow the faint signal that reminded it of home.
    """
    
    processor = TextProcessor(max_chunk_length=200)
    result = processor.process_story(sample_story)

    logger.info("Processed Story Chunks:")
    logger.info("=" * 50)
    for chunk in result["chunks"]:
        logger.info(f"[Chunk {chunk.chunk_id}] {chunk.text}")
        logger.info(f"  - Paragraph end: {chunk.is_paragraph_end}, Pause: {chunk.pause_after}s")

    logger.info("Metadata:")
    logger.info(f"Total chunks: {result['metadata']['total_chunks']}")
    logger.info(f"Total words: {result['metadata']['total_words']}")
    logger.info(f"Estimated duration: {result['metadata']['estimated_duration_seconds']:.1f} seconds")
