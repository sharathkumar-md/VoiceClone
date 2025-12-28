'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { createSimilarStory } from '@/lib/api/stories';

interface CreateSimilarDialogProps {
  storyId: string;
  storyTitle: string;
  onClose: () => void;
}

export function CreateSimilarDialog({ storyId, storyTitle, onClose }: CreateSimilarDialogProps) {
  const router = useRouter();
  const [instruction, setInstruction] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const quickPrompts = [
    { label: 'Different setting', value: 'change the setting to a completely different location' },
    { label: 'Different character', value: 'change the main character to someone completely different' },
    { label: 'Different ending', value: 'create a completely different ending' },
    { label: 'More action', value: 'add more action and excitement to the story' },
    { label: 'Shorter version', value: 'make this story shorter while keeping the main plot' },
  ];

  const handleQuickPrompt = (value: string) => {
    setInstruction(value);
  };

  const handleSubmit = async () => {
    if (!instruction.trim()) {
      setError('Please enter an instruction or select a quick prompt');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      console.log('🎨 Creating similar story:', {
        storyId,
        instruction: instruction.trim(),
      });

      const result = await createSimilarStory(storyId, instruction.trim());

      console.log('✅ Similar story created:', {
        newStoryId: result.story_id,
        wordCount: result.word_count,
      });

      // Redirect to new story
      router.push(`/story/${result.story_id}`);
    } catch (err) {
      console.error('❌ Failed to create similar story:', err);
      setError(err instanceof Error ? err.message : 'Failed to create similar story');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle>♻️ Create Similar Story</CardTitle>
          <CardDescription>
            Create a new story similar to <strong>"{storyTitle}"</strong> with your modifications
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Quick Prompts */}
          <div>
            <label className="text-sm font-medium mb-2 block">Quick modifications:</label>
            <div className="flex flex-wrap gap-2">
              {quickPrompts.map((prompt) => (
                <Button
                  key={prompt.label}
                  variant="outline"
                  size="sm"
                  onClick={() => handleQuickPrompt(prompt.value)}
                  disabled={isLoading}
                >
                  {prompt.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Custom Instruction */}
          <div>
            <label htmlFor="instruction" className="text-sm font-medium mb-2 block">
              Your modification:
            </label>
            <textarea
              id="instruction"
              value={instruction}
              onChange={(e) => setInstruction(e.target.value)}
              placeholder="E.g., 'change the setting to outer space' or 'make the hero a princess instead'"
              className="w-full min-h-[120px] p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 mt-1">
              The AI will create a NEW story with the same theme, style, and tone, but with your modifications applied.
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSubmit}
              disabled={isLoading || !instruction.trim()}
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Creating...
                </span>
              ) : (
                'Create Similar Story'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
