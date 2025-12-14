"""
Story Generator Module - Uses LLM to create stories based on user prompts
"""

import os
from typing import Dict, Optional, List
from dataclasses import dataclass
import json
from .logger import setup_logger

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system environment variables

logger = setup_logger(__name__)


@dataclass
class StoryPrompt:
    """Story generation prompt configuration"""
    theme: str
    style: str = "adventure"  # adventure, mystery, fantasy, sci-fi, horror, romance
    tone: str = "engaging"  # engaging, suspenseful, lighthearted, dramatic, humorous
    length: str = "medium"  # short (500 words), medium (1000 words), long (2000+ words)
    target_audience: str = "general"  # children, teens, adults, general
    additional_details: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "theme": self.theme,
            "style": self.style,
            "tone": self.tone,
            "length": self.length,
            "target_audience": self.target_audience,
            "additional_details": self.additional_details
        }


class StoryGenerator:
    """
    Generates stories using LLM providers (OpenAI, Anthropic, or local models)
    """
    
    WORD_COUNT_MAP = {
        "short": 500,
        "medium": 1000,
        "long": 2000
    }
    
    def __init__(
        self, 
        provider: str = "gemini",  # gemini, openai, anthropic, local
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize story generator
        
        Args:
            provider: LLM provider to use
            api_key: API key for the provider (reads from env if not provided)
            model: Model name (uses defaults if not provided)
        """
        self.provider = provider.lower()
        
        # Handle API key - Gemini can use GOOGLE_API_KEY or GEMINI_API_KEY
        if self.provider == "gemini":
            self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        else:
            self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        
        # Default models
        self.model = model or {
            "gemini": "gemini-2.5-flash",  # Faster with higher rate limits
            "openai": "gpt-4-turbo-preview",
            "anthropic": "claude-3-5-sonnet-20241022",
            "local": "llama3"  # for Ollama
        }.get(self.provider, "gemini-2.5-flash")
        
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the LLM client based on provider"""
        if self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                raise ImportError("Please install google-generativeai: pip install google-generativeai")
        
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _build_prompt(self, story_prompt: StoryPrompt) -> str:
        """Build the LLM prompt for story generation"""
        word_count = self.WORD_COUNT_MAP.get(story_prompt.length, 1000)
        
        prompt = f"""You are a creative storyteller. Generate an engaging story based on the following requirements:

**Theme:** {story_prompt.theme}
**Style:** {story_prompt.style}
**Tone:** {story_prompt.tone}
**Target Audience:** {story_prompt.target_audience}
**Target Length:** Approximately {word_count} words

"""
        
        if story_prompt.additional_details:
            prompt += f"**Additional Details:** {story_prompt.additional_details}\n\n"
        
        prompt += """
**Requirements:**
1. Create a complete story with a clear beginning, middle, and end
2. Use vivid descriptions and engaging dialogue where appropriate
3. Maintain consistent narrative voice throughout
4. Structure the story with proper paragraphs for natural narration
5. Ensure the story is suitable for audio narration (avoid heavy use of special characters, lists, or complex formatting)
6. Make it captivating and immersive for the listener

Generate the story now:"""
        
        return prompt
    
    def generate_story(self, story_prompt: StoryPrompt) -> Dict:
        """
        Generate a story using the LLM
        
        Args:
            story_prompt: StoryPrompt object with generation parameters
            
        Returns:
            Dictionary containing:
                - story: The generated story text
                - metadata: Generation metadata (prompt, model, etc.)
        """
        prompt = self._build_prompt(story_prompt)
        
        try:
            if self.provider == "gemini":
                story_text = self._generate_gemini(prompt)
            elif self.provider == "openai":
                story_text = self._generate_openai(prompt)
            elif self.provider == "anthropic":
                story_text = self._generate_anthropic(prompt)
            elif self.provider == "local":
                story_text = self._generate_local(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            return {
                "story": story_text.strip(),
                "metadata": {
                    "provider": self.provider,
                    "model": self.model,
                    "prompt_config": story_prompt.to_dict(),
                    "prompt_used": prompt
                }
            }
        
        except Exception as e:
            raise Exception(f"Error generating story with {self.provider}: {str(e)}")
    
    def _generate_gemini(self, prompt: str) -> str:
        """Generate story using Google Gemini API"""
        import google.generativeai as genai
        
        # Configure safety settings to be less restrictive
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        model = self._client.GenerativeModel(
            model_name=self.model,
            system_instruction="You are a creative storyteller who crafts engaging narratives.",
            safety_settings=safety_settings
        )
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,
                "max_output_tokens": 3000,
            }
        )
        
        # Handle blocked content
        if not response.candidates or response.candidates[0].finish_reason != 1:
            # Try with lower temperature
            logger.warning("Content filtered, retrying with adjusted settings...")
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.5,
                    "max_output_tokens": 3000,
                }
            )
        
        return response.text
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate story using OpenAI API"""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a creative storyteller who crafts engaging narratives."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=3000
        )
        return response.choices[0].message.content
    
    def _generate_anthropic(self, prompt: str) -> str:
        """Generate story using Anthropic Claude API"""
        response = self._client.messages.create(
            model=self.model,
            max_tokens=3000,
            temperature=0.8,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _generate_local(self, prompt: str) -> str:
        """Generate story using local model (Ollama)"""
        response = self._client.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": 0.8,
                "num_predict": 3000
            }
        )
        return response['response']
    
    def generate_from_simple_prompt(
        self, 
        theme: str,
        style: str = "adventure",
        tone: str = "engaging",
        length: str = "medium"
    ) -> Dict:
        """
        Convenience method to generate story from simple parameters
        
        Args:
            theme: Main theme/topic of the story
            style: Story style
            tone: Narrative tone
            length: Story length
            
        Returns:
            Generated story dictionary
        """
        prompt = StoryPrompt(
            theme=theme,
            style=style,
            tone=tone,
            length=length
        )
        return self.generate_story(prompt)


# Example usage
if __name__ == "__main__":
    # Example with Gemini (set GOOGLE_API_KEY or GEMINI_API_KEY environment variable)
    generator = StoryGenerator(provider="gemini")
    
    # Create a story prompt
    prompt = StoryPrompt(
        theme="A lost robot finding its way home in a futuristic city",
        style="sci-fi",
        tone="hopeful",
        length="short",
        target_audience="general"
    )
    
    # Generate story
    result = generator.generate_story(prompt)
    logger.info("Generated Story:")
    logger.info("=" * 50)
    logger.info(result["story"])
    logger.info("=" * 50)
    logger.info(f"Model: {result['metadata']['model']}")
