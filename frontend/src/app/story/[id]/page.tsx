'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import { useStoryStore } from '@/lib/stores/storyStore';
import { StoryDisplay } from '@/components/story/StoryDisplay';
import { AudioSettings } from '@/components/audio/AudioSettings';
import { Button } from '@/components/ui/button';

// Dynamically import StoryEditor with no SSR to avoid Tiptap hydration issues
const StoryEditor = dynamic(
  () => import('@/components/story/StoryEditor').then((mod) => ({ default: mod.StoryEditor })),
  { ssr: false, loading: () => <div className="p-8 text-center text-gray-500">Loading editor...</div> }
);

export default function StoryPage() {
  const params = useParams();
  const { currentStory, isEditing, setEditing, updateStoryText } = useStoryStore();
  const [showAudioSettings, setShowAudioSettings] = useState(false);

  if (!currentStory) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Story not found</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            The story you're looking for doesn't exist or has been removed.
          </p>
          <Button onClick={() => window.location.href = '/story/create'}>
            Create New Story
          </Button>
        </div>
      </div>
    );
  }

  const handleSave = (content: string) => {
    updateStoryText(content);
    setEditing(false);
  };

  const handleGenerateAudio = () => {
    setShowAudioSettings(true);
  };

  const handleReprompt = (modifiedText: string) => {
    console.log('🔄 Updating story with reprompted text:', {
      length: modifiedText.length,
      preview: modifiedText.substring(0, 100),
    });
    updateStoryText(modifiedText);
    console.log('✅ Story updated in store');
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {isEditing ? (
          <StoryEditor
            key={`editor-${currentStory.id}`}
            initialContent={currentStory.text}
            onSave={handleSave}
            onCancel={() => setEditing(false)}
            onChange={(text) => {
              // Auto-save could be implemented here
            }}
          />
        ) : (
          <StoryDisplay
            key={`story-${currentStory.id}-${currentStory.updatedAt}`}
            story={currentStory}
            onEdit={() => setEditing(true)}
            onGenerateAudio={handleGenerateAudio}
            onReprompt={handleReprompt}
          />
        )}

        {showAudioSettings && (
          <AudioSettings storyText={currentStory.text} storyId={currentStory.id} />
        )}
      </div>
    </div>
  );
}
