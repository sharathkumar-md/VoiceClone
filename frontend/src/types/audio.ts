export interface AudioSettings {
  speed: number;
  exaggeration: number;
  temperature: number;
  cfgWeight: number;
}

export interface VoiceSample {
  id: string;
  name: string;
  url: string;
  uploadedAt: string;
  duration: number;
  sampleRate: number;
}

export interface AudioGenerationTask {
  id: string;
  storyId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  currentStep: string;
  estimatedTimeRemaining?: number;
  audioUrl?: string;
  error?: string;
}
