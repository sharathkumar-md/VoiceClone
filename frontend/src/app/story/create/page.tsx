import { StoryForm } from '@/components/story/StoryForm';

export default function CreateStoryPage() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Story Generator</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Create amazing stories powered by AI
          </p>
        </div>
        <StoryForm />
      </div>
    </div>
  );
}
