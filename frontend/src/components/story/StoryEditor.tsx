'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useEffect, useState } from 'react';

interface StoryEditorProps {
  initialContent: string;
  onChange?: (content: string) => void;
  onSave?: (content: string) => void;
  onCancel?: () => void;
}

export function StoryEditor({ initialContent, onChange, onSave, onCancel }: StoryEditorProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const editor = useEditor({
    extensions: [StarterKit],
    content: initialContent,
    editorProps: {
      attributes: {
        class: 'prose prose-gray dark:prose-invert max-w-none focus:outline-none min-h-[400px] p-4',
      },
    },
    onUpdate: ({ editor }) => {
      onChange?.(editor.getText());
    },
    immediatelyRender: false,
  });

  useEffect(() => {
    if (editor && mounted && initialContent && initialContent !== editor.getText()) {
      editor.commands.setContent(initialContent);
    }
  }, [initialContent, editor, mounted]);

  const handleSave = () => {
    if (editor) {
      onSave?.(editor.getText());
    }
  };

  if (!mounted || !editor) {
    return <div className="p-8 text-center text-gray-500">Loading editor...</div>;
  }

  const wordCount = editor.getText().split(/\s+/).filter(Boolean).length || 0;
  const charCount = editor.getText().length || 0;

  return (
    <Card variant="bordered">
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Edit Story</CardTitle>
            <div className="mt-2 flex gap-4 text-sm text-gray-600 dark:text-gray-400">
              <span>{wordCount} words</span>
              <span>{charCount} characters</span>
            </div>
          </div>
          <div className="flex gap-2">
            {/* Formatting toolbar */}
            <div className="flex gap-1 mr-4">
              <Button
                variant={editor.isActive('bold') ? 'primary' : 'outline'}
                size="sm"
                onClick={() => editor.chain().focus().toggleBold().run()}
                type="button"
              >
                B
              </Button>
              <Button
                variant={editor.isActive('italic') ? 'primary' : 'outline'}
                size="sm"
                onClick={() => editor.chain().focus().toggleItalic().run()}
                type="button"
              >
                I
              </Button>
              <Button
                variant={editor.isActive('heading', { level: 2 }) ? 'primary' : 'outline'}
                size="sm"
                onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                type="button"
              >
                H2
              </Button>
            </div>
            {onCancel && (
              <Button variant="outline" size="sm" onClick={onCancel}>
                Cancel
              </Button>
            )}
            {onSave && (
              <Button variant="primary" size="sm" onClick={handleSave}>
                Save Changes
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="border border-gray-300 dark:border-gray-700 rounded-lg">
          <EditorContent editor={editor} />
        </div>
      </CardContent>
    </Card>
  );
}
