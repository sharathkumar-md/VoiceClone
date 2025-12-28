'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { generateStory } from '@/lib/api/client';
import { useStoryStore } from '@/lib/stores/storyStore';

const storySchema = z.object({
  theme: z.string().min(10, 'Theme must be at least 10 characters'),
  style: z.enum(['adventure', 'fantasy', 'mystery', 'sci-fi', 'horror', 'romance']),
  tone: z.enum(['dramatic', 'lighthearted', 'suspenseful', 'humorous']),
  length: z.enum(['short', 'medium', 'long']),
  additionalDetails: z.string().optional(),
});

type StoryFormData = z.infer<typeof storySchema>;

const styleOptions = [
  { value: 'adventure', label: 'Adventure' },
  { value: 'fantasy', label: 'Fantasy' },
  { value: 'mystery', label: 'Mystery' },
  { value: 'sci-fi', label: 'Sci-Fi' },
  { value: 'horror', label: 'Horror' },
  { value: 'romance', label: 'Romance' },
];

const toneOptions = [
  { value: 'dramatic', label: 'Dramatic' },
  { value: 'lighthearted', label: 'Lighthearted' },
  { value: 'suspenseful', label: 'Suspenseful' },
  { value: 'humorous', label: 'Humorous' },
];

export function StoryForm() {
  const router = useRouter();
  const { setStory } = useStoryStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<StoryFormData>({
    resolver: zodResolver(storySchema),
    defaultValues: {
      style: 'adventure',
      tone: 'dramatic',
      length: 'medium',
    },
  });

  const selectedLength = watch('length');

  const onSubmit = async (data: StoryFormData) => {
    setIsGenerating(true);
    setError(null);

    try {
      const result = await generateStory(data);

      setStory({
        id: result.story_id,
        text: result.story_text,
        theme: data.theme,
        style: data.style,
        tone: data.tone,
        length: data.length,
        wordCount: result.word_count,
        createdAt: new Date().toISOString(),
      });

      router.push(`/story/${result.story_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate story');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Card variant="bordered" className="max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>Create Your Story</CardTitle>
        <CardDescription>
          Fill in the details below to generate an AI-powered story
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Theme Input */}
          <Textarea
            label="Story Theme *"
            placeholder="A dragon who's afraid of heights..."
            rows={3}
            error={errors.theme?.message}
            {...register('theme')}
          />

          {/* Style and Tone Selects */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Style *"
              options={styleOptions}
              error={errors.style?.message}
              {...register('style')}
            />
            <Select
              label="Tone *"
              options={toneOptions}
              error={errors.tone?.message}
              {...register('tone')}
            />
          </div>

          {/* Length Radio Buttons */}
          <div>
            <label className="block text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">
              Length *
            </label>
            <div className="flex gap-4">
              {['short', 'medium', 'long'].map((lengthOption) => (
                <label
                  key={lengthOption}
                  className="flex items-center space-x-2 cursor-pointer"
                >
                  <input
                    type="radio"
                    value={lengthOption}
                    {...register('length')}
                    className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="capitalize text-sm">
                    {lengthOption}
                    {lengthOption === 'short' && ' (300-500 words)'}
                    {lengthOption === 'medium' && ' (500-1000 words)'}
                    {lengthOption === 'long' && ' (1000-2000 words)'}
                  </span>
                </label>
              ))}
            </div>
            {errors.length && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {errors.length.message}
              </p>
            )}
          </div>

          {/* Additional Details */}
          <Textarea
            label="Additional Details (Optional)"
            placeholder="Any specific elements you'd like to include..."
            rows={4}
            {...register('additionalDetails')}
          />

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={isGenerating}
              className="w-full md:w-auto"
            >
              {isGenerating ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating Story...
                </>
              ) : (
                'Generate Story'
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
