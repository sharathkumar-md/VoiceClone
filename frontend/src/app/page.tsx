'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { StoryGrid } from '@/components/dashboard/StoryGrid';
import { EmptyState } from '@/components/dashboard/EmptyState';
import { CreateSimilarDialog } from '@/components/dashboard/CreateSimilarDialog';
import { fetchStories, Story } from '@/lib/api/stories';

export default function DashboardPage() {
  const router = useRouter();
  const [stories, setStories] = useState<Story[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalStories, setTotalStories] = useState(0);

  // Create Similar Dialog State
  const [showCreateSimilar, setShowCreateSimilar] = useState(false);
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);

  // Load stories on mount
  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const result = await fetchStories(20, 0);

      // Deduplicate stories by ID to prevent duplicates
      const uniqueStories = result.stories.filter(
        (story, index, self) => index === self.findIndex((s) => s.id === story.id)
      );

      console.log('Loaded stories:', {
        original: result.stories.length,
        unique: uniqueStories.length,
        total: result.total,
        hasDuplicates: result.stories.length !== uniqueStories.length,
      });

      setStories(uniqueStories);
      setTotalStories(result.total);
    } catch (err) {
      console.error('Failed to load stories:', err);
      setError(err instanceof Error ? err.message : 'Failed to load stories');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSimilar = (storyId: string) => {
    const story = stories.find((s) => s.id === storyId);
    if (story) {
      setSelectedStory(story);
      setShowCreateSimilar(true);
    }
  };

  const handleCloseCreateSimilar = () => {
    setShowCreateSimilar(false);
    setSelectedStory(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                My Stories
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {totalStories > 0
                  ? `${totalStories} ${totalStories === 1 ? 'story' : 'stories'} created`
                  : 'Start creating amazing stories with AI'}
              </p>
            </div>
            <Button
              variant="primary"
              size="lg"
              onClick={() => router.push('/story/create')}
              className="gap-2"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              New Story
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center space-y-4">
              <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading stories...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center space-y-4 max-w-md">
              <div className="text-red-500 text-5xl">!</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Failed to load stories
              </h3>
              <p className="text-gray-600 dark:text-gray-400">{error}</p>
              <Button variant="outline" onClick={loadStories}>
                Try Again
              </Button>
            </div>
          </div>
        ) : stories.length === 0 ? (
          <EmptyState />
        ) : (
          <StoryGrid stories={stories} onCreateSimilar={handleCreateSimilar} />
        )}
      </div>

      {/* Create Similar Dialog */}
      {showCreateSimilar && selectedStory && (
        <CreateSimilarDialog
          storyId={selectedStory.id}
          storyTitle={selectedStory.title}
          onClose={handleCloseCreateSimilar}
        />
      )}
    </div>
  );
}
