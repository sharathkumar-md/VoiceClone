import { useState } from 'react';
import TextToSpeech from './components/TextToSpeech';
import VoiceConversion from './components/VoiceConversion';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('tts');

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎙️ Chatterbox Voice Clone</h1>
        <p className="subtitle">
          Production-grade Text-to-Speech and Voice Conversion
        </p>
      </header>

      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'tts' ? 'active' : ''}`}
          onClick={() => setActiveTab('tts')}
        >
          Text-to-Speech
        </button>
        <button
          className={`tab-btn ${activeTab === 'vc' ? 'active' : ''}`}
          onClick={() => setActiveTab('vc')}
        >
          Voice Conversion
        </button>
      </div>

      <main className="app-main">
        {activeTab === 'tts' ? <TextToSpeech /> : <VoiceConversion />}
      </main>

      <footer className="app-footer">
        <p>
          Powered by{' '}
          <a
            href="https://github.com/resemble-ai/chatterbox"
            target="_blank"
            rel="noopener noreferrer"
          >
            Resemble AI Chatterbox
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
