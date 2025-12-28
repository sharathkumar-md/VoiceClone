export interface Story {
  id: string;
  text: string;
  theme: string;
  style: string;
  tone: string;
  length: string;
  wordCount: number;
  createdAt: string;
  updatedAt?: string;
}

export interface StoryPrompt {
  theme: string;
  style: 'adventure' | 'fantasy' | 'mystery' | 'sci-fi' | 'horror' | 'romance';
  tone: 'dramatic' | 'lighthearted' | 'suspenseful' | 'humorous';
  length: 'short' | 'medium' | 'long';
  additionalDetails?: string;
}

export interface StoryRevision {
  id: string;
  storyId: string;
  text: string;
  timestamp: string;
  source: 'manual' | 'ai';
}
