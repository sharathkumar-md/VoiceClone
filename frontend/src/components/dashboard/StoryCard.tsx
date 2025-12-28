'use client';

import { Story } from '@/lib/api/stories';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

interface StoryCardProps {
  story: Story;
  onCreateSimilar?: (storyId: string) => void;
}

export function StoryCard({ story, onCreateSimilar }: StoryCardProps) {
  const router = useRouter();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const handleView = () => {
    router.push(`/story/${story.id}`);
  };

  const handleCreateSimilar = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onCreateSimilar) {
      onCreateSimilar(story.id);
    }
  };

  return (
    <Card
      className="group cursor-pointer hover:shadow-lg transition-all duration-200 overflow-hidden"
      onClick={handleView}
    >
      {/* Gradient Header */}
      <div
        className="h-32 relative"
        style={{
          background: `linear-gradient(135deg, ${story.thumbnail_color}dd, ${story.thumbnail_color}66)`,
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />

        {/* Theme Badge */}
        <div className="absolute top-3 left-3">
          <span className="px-3 py-1 bg-white/90 backdrop-blur-sm text-xs font-semibold rounded-full text-gray-800">
            {story.theme}
          </span>
        </div>

        {/* Audio Indicator */}
        {story.audio_url && (
          <div className="absolute top-3 right-3">
            <span className="px-2 py-1 bg-green-500/90 backdrop-blur-sm text-xs font-semibold rounded-full text-white flex items-center gap-1">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
              </svg>
              Audio
            </span>
          </div>
        )}
      </div>

      <CardContent className="p-4 space-y-3">
        {/* Title */}
        <h3 className="font-semibold text-lg line-clamp-2 group-hover:text-blue-600 transition-colors">
          {story.title}
        </h3>

        {/* Preview Text */}
        <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
          {story.text_preview || story.preview_text}
        </p>

        {/* Metadata */}
        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            {story.word_count} words
          </span>
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {formatDate(story.created_at)}
          </span>
        </div>

        {/* Style & Tone Pills */}
        <div className="flex gap-2 flex-wrap">
          <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
            {story.style}
          </span>
          <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded-full">
            {story.tone}
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={handleView}
          >
            View
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={handleCreateSimilar}
          >
            Similar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
