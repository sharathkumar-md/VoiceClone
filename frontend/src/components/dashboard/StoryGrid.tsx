'use client';

import { Story } from '@/lib/api/stories';
import { StoryCard } from './StoryCard';

interface StoryGridProps {
  stories: Story[];
  onCreateSimilar?: (storyId: string) => void;
}

export function StoryGrid({ stories, onCreateSimilar }: StoryGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {stories.map((story) => (
        <StoryCard
          key={story.id}
          story={story}
          onCreateSimilar={onCreateSimilar}
        />
      ))}
    </div>
  );
}
