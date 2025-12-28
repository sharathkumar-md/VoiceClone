# VoiceClone Frontend

A modern Next.js frontend for the VoiceClone Story Narrator application.

## Features

- **Story Generation**: Create AI-powered stories with customizable themes, styles, and tones
- **Story Editing**: Rich text editor with Tiptap for manual story editing
- **Voice Cloning**: Upload voice samples for personalized narration
- **Audio Generation**: Generate audio narration with customizable settings
- **Audio Playback**: Built-in audio player with controls and visualization

## Tech Stack

- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod validation
- **API**: TanStack Query (React Query)
- **Text Editor**: Tiptap
- **Audio**: Wavesurfer.js (for future waveform visualization)
- **File Upload**: React Dropzone

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (default: http://localhost:8000)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Configuration

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js app directory
│   │   ├── page.tsx              # Home page
│   │   ├── layout.tsx            # Root layout
│   │   ├── globals.css           # Global styles
│   │   └── story/
│   │       ├── create/           # Story creation page
│   │       └── [id]/             # Story detail page
│   │
│   ├── components/
│   │   ├── ui/                   # Reusable UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── slider.tsx
│   │   │   ├── card.tsx
│   │   │   ├── select.tsx
│   │   │   └── textarea.tsx
│   │   │
│   │   ├── story/                # Story-related components
│   │   │   ├── StoryForm.tsx     # Story generation form
│   │   │   ├── StoryDisplay.tsx  # Story display
│   │   │   └── StoryEditor.tsx   # Story editor
│   │   │
│   │   └── audio/                # Audio-related components
│   │       ├── VoiceUpload.tsx   # Voice sample upload
│   │       ├── AudioSettings.tsx # Audio generation settings
│   │       └── AudioPlayer.tsx   # Audio playback
│   │
│   ├── lib/
│   │   ├── api/                  # API client functions
│   │   │   └── client.ts
│   │   ├── stores/               # Zustand stores
│   │   │   ├── storyStore.ts
│   │   │   └── audioStore.ts
│   │   └── providers/            # React providers
│   │       └── QueryProvider.tsx
│   │
│   └── types/                    # TypeScript type definitions
│       ├── story.ts
│       └── audio.ts
│
├── public/                       # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.ts
```

## User Flow

1. **Create Story**: Navigate to `/story/create` and fill in the story details
2. **Review & Edit**: View the generated story and optionally edit it
3. **Configure Audio**: Upload a voice sample or use the default voice
4. **Generate Audio**: Adjust audio settings and generate narration
5. **Playback & Download**: Listen to the audio and download in preferred format

## API Endpoints Used

The frontend communicates with the following backend endpoints:

- `POST /api/v1/story/generate` - Generate a new story
- `PUT /api/v1/story/{id}/edit` - Update a story
- `POST /api/v1/story/ai-improve` - AI-assisted story improvement
- `POST /api/v1/tts/generate` - Generate audio narration
- `GET /api/v1/tts/status/{task_id}` - Check generation status
- `POST /api/v1/voice/upload` - Upload voice sample
- `GET /api/v1/voice/library` - Get saved voice samples

## Development Notes

- The app uses Next.js 16 with Turbopack for faster development
- All components are TypeScript for better type safety
- Tailwind CSS is used for styling with dark mode support
- Forms use React Hook Form with Zod validation
- API calls are managed with TanStack Query for caching and error handling

## Troubleshooting

### API Connection Issues

If you're having trouble connecting to the backend:

1. Ensure the backend is running at the URL specified in `.env.local`
2. Check CORS settings in the backend
3. Verify the API endpoints are correct

### Build Errors

If you encounter build errors:

1. Clear the Next.js cache: `rm -rf .next`
2. Reinstall dependencies: `rm -rf node_modules package-lock.json && npm install`
3. Check for TypeScript errors: `npm run build`

## Future Enhancements

- [ ] AI-assisted story editing modal
- [ ] Waveform visualization with Wavesurfer.js
- [ ] Text-audio synchronization during playback
- [ ] Voice library management
- [ ] Story history and saved drafts
- [ ] Dark mode toggle
- [ ] Export options (PDF, combined packages)
- [ ] User authentication
